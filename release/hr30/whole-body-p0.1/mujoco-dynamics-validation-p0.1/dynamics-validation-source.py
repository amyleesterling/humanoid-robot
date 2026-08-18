"""Execute bounded whole-body MuJoCo tracking/contact screens for HR-30.

The controller and six-degree-of-freedom mocap fixture in this package are
numerical test equipment.  They are not robot firmware, a fall-restraint
design, or evidence that the free robot can balance or walk.
"""

from __future__ import annotations

import csv
import hashlib
import html
import json
import math
import shutil
import time
import xml.etree.ElementTree as ET
from collections import defaultdict
from pathlib import Path

import mujoco
import numpy as np

import generate_hr30_system_package_p01 as system


ROOT = Path(__file__).resolve().parents[1]
BODY = ROOT / "hr30" / "whole-body-p0.1"
KIN = BODY / "walking-sequence-p0.1"
OUT = BODY / "mujoco-dynamics-validation-p0.1"
REL = ROOT / "release" / "hr30" / "whole-body-p0.1" / OUT.name
IDENTIFIER = "HR30-MUJOCO-DYNAMICS-VALIDATION-P0.1"
WARNING = "PRELIMINARY - IDEAL-FIXTURE SIMULATION ONLY - NOT APPROVED FOR CONNECTION, POWERED TESTING, MOTION, WALKING, OR ENERGIZATION"
DT = 0.002
SETTLE_S = 0.5
MAX_ROTARY_ERROR_DEG = 5.0
MAX_PRISMATIC_ERROR_MM = 2.0
MAX_ROTARY_SATURATION_FRACTION = 0.10
MIN_DECLARED_SUPPORT_COVERAGE = 0.99


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_csv(path: Path) -> list[dict]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        raise RuntimeError(f"refusing empty CSV: {path}")
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def build_fixture_model(caps: dict[str, float]) -> Path:
    source = KIN / "hr30_tether_walking_keyframes.xml"
    tree = ET.parse(source)
    root = tree.getroot()
    option = root.find("option")
    if option is None:
        raise RuntimeError("source MJCF has no option element")
    option.set("timestep", f"{DT:.6f}")
    option.set("integrator", "implicitfast")
    option.set("solver", "Newton")
    option.set("iterations", "100")
    option.set("tolerance", "1e-10")
    world = root.find("worldbody")
    if world is None:
        raise RuntimeError("source MJCF has no worldbody")
    ET.SubElement(world, "body", name="trajectory_fixture", mocap="true", pos="0 0 0.390000")
    equality = ET.Element("equality")
    ET.SubElement(
        equality, "weld", name="ideal_6dof_trajectory_fixture",
        body1="trajectory_fixture", body2="base_link",
        solref="0.01 1", solimp="0.90 0.95 0.001",
    )
    actuator = root.find("actuator")
    if actuator is None:
        raise RuntimeError("source MJCF has no actuator block")
    root.insert(list(root).index(actuator), equality)
    for motor in actuator.findall("motor"):
        axis = motor.attrib["joint"]
        cap = 1.0 if axis.endswith("_GRIPPER") else caps[axis]
        motor.set("ctrlrange", f"{-cap:.9f} {cap:.9f}")
    for joint in root.findall(".//joint"):
        if joint.attrib.get("name", "").endswith("_GRIPPER"):
            joint.set("stiffness", "100")
            joint.set("springref", "0.010")
            joint.set("damping", "5")
    ET.indent(root)
    target = OUT / "hr30_tether_ideal_fixture.xml"
    target.write_text(ET.tostring(root, encoding="unicode") + "\n", encoding="utf-8", newline="\n")
    return target


def trajectory_data() -> tuple[dict[str, list[dict]], dict[str, dict[str, list[dict]]]]:
    base: dict[str, list[dict]] = defaultdict(list)
    for row in read_csv(KIN / "trajectory-samples.csv"):
        base[row["sequence_id"]].append(row)
    joints: dict[str, dict[str, list[dict]]] = defaultdict(lambda: defaultdict(list))
    for row in read_csv(KIN / "joint-trajectory.csv"):
        joints[row["sequence_id"]][row["joint_id"]].append(row)
    for rows in base.values():
        rows.sort(key=lambda row: int(row["sample_index"]))
    for axes in joints.values():
        for rows in axes.values():
            rows.sort(key=lambda row: int(row["sample_index"]))
    return dict(base), {sequence: dict(axes) for sequence, axes in joints.items()}


def numeric_series(rows: list[dict], field: str) -> tuple[np.ndarray, np.ndarray]:
    """Parse one controlled trajectory column once for the full simulation.

    The previous implementation rebuilt both arrays on every 2 ms controller
    step. With 25 joints and two requested fields, that repeated hundreds of
    millions of Python-to-float conversions during an otherwise small model
    integration. Keeping immutable arrays preserves the same linear
    interpolation while making execution time proportional to the MuJoCo work.
    """
    times = np.fromiter((float(row["time_s"]) for row in rows), dtype=float)
    values = np.fromiter((float(row[field]) for row in rows), dtype=float)
    return times, values


def interpolate(series: tuple[np.ndarray, np.ndarray], time_s: float) -> float:
    return float(np.interp(time_s, series[0], series[1]))


def expected_support(mode: str) -> set[str]:
    if mode == "DOUBLE":
        return {"L", "R"}
    return {mode.split()[0]}


def controls(
    model: mujoco.MjModel, data: mujoco.MjData, axes: list[str],
    desired_position: dict[str, float], desired_velocity: dict[str, float], caps: dict[str, float],
) -> tuple[dict[str, float], dict[str, bool]]:
    commands: dict[str, float] = {}
    saturated: dict[str, bool] = {}
    for axis in axes:
        joint_id = mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_JOINT, axis)
        actuator_id = mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_ACTUATOR, f"M_{axis}")
        qpos_address = model.jnt_qposadr[joint_id]
        dof_address = model.jnt_dofadr[joint_id]
        error = desired_position[axis] - data.qpos[qpos_address]
        velocity_error = desired_velocity[axis] - data.qvel[dof_address]
        if axis.endswith("_GRIPPER"):
            cap, kp, kd = 1.0, 100.0, 5.0
            feedforward = 0.0
        else:
            cap = caps[axis]
            kp, kd = 40.0 * cap, 2.0 * cap
            feedforward = data.qfrc_bias[dof_address]
        raw = feedforward + kp * error + kd * velocity_error
        command = float(np.clip(raw, -cap, cap))
        data.ctrl[actuator_id] = command
        commands[axis] = command
        saturated[axis] = abs(raw) >= cap * (1.0 - 1e-10)
    return commands, saturated


def contact_state(model: mujoco.MjModel, data: mujoco.MjData) -> tuple[set[str], float, float, set[str], float]:
    active_feet: set[str] = set()
    left_force = right_force = 0.0
    unexpected: set[str] = set()
    minimum_distance = math.inf
    for index in range(data.ncon):
        contact = data.contact[index]
        name1 = mujoco.mj_id2name(model, mujoco.mjtObj.mjOBJ_GEOM, contact.geom1)
        name2 = mujoco.mj_id2name(model, mujoco.mjtObj.mjOBJ_GEOM, contact.geom2)
        pair = tuple(sorted((name1, name2)))
        minimum_distance = min(minimum_distance, float(contact.dist))
        force = np.zeros(6)
        mujoco.mj_contactForce(model, data, index, force)
        if pair == ("G_L_foot", "floor"):
            active_feet.add("L")
            left_force += max(0.0, float(force[0]))
        elif pair == ("G_R_foot", "floor"):
            active_feet.add("R")
            right_force += max(0.0, float(force[0]))
        else:
            unexpected.add("::".join(pair))
    return active_feet, left_force, right_force, unexpected, 0.0 if math.isinf(minimum_distance) else minimum_distance


def simulate(model: mujoco.MjModel, caps: dict[str, float]) -> tuple[list[dict], list[dict], list[dict], dict]:
    base_by_sequence, joints_by_sequence = trajectory_data()
    axes = sorted(joints_by_sequence[next(iter(joints_by_sequence))])
    sample_rows: list[dict] = []
    summary_rows: list[dict] = []
    axis_rows: list[dict] = []
    global_unexpected: set[str] = set()
    all_finite = True
    for sequence_id in sorted(base_by_sequence):
        base_rows = base_by_sequence[sequence_id]
        joint_rows = joints_by_sequence[sequence_id]
        root_series = {
            field: numeric_series(base_rows, field)
            for field in ("root_x_m", "root_y_m", "root_z_m")
        }
        joint_position_series = {
            axis: numeric_series(rows, "position_si")
            for axis, rows in joint_rows.items()
        }
        joint_velocity_series = {
            axis: numeric_series(rows, "velocity_si_s")
            for axis, rows in joint_rows.items()
        }
        duration = float(base_rows[-1]["time_s"])
        data = mujoco.MjData(model)
        first_root = np.array([float(base_rows[0][field]) for field in ("root_x_m", "root_y_m", "root_z_m")])
        data.qpos[:3] = first_root
        data.qpos[3:7] = [1.0, 0.0, 0.0, 0.0]
        data.mocap_pos[0] = first_root
        data.mocap_quat[0] = [1.0, 0.0, 0.0, 0.0]
        for axis in axes:
            joint_id = mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_JOINT, axis)
            data.qpos[model.jnt_qposadr[joint_id]] = float(joint_rows[axis][0]["position_si"])
        mujoco.mj_forward(model, data)

        def desired(time_s: float) -> tuple[dict[str, float], dict[str, float], np.ndarray, dict]:
            nearest = min(int(round(time_s / 0.02)), len(base_rows) - 1)
            root = np.array([interpolate(root_series[field], time_s) for field in ("root_x_m", "root_y_m", "root_z_m")])
            position = {axis: interpolate(joint_position_series[axis], time_s) for axis in axes}
            velocity = {axis: interpolate(joint_velocity_series[axis], time_s) for axis in axes}
            return position, velocity, root, base_rows[nearest]

        initial_position, initial_velocity, _, _ = desired(0.0)
        for _ in range(round(SETTLE_S / DT)):
            data.mocap_pos[0] = first_root
            mujoco.mj_forward(model, data)
            controls(model, data, axes, initial_position, initial_velocity, caps)
            mujoco.mj_step(model, data)
        data.time = 0.0

        axis_error_sq = defaultdict(float)
        axis_error_max = defaultdict(float)
        axis_torque_sq = defaultdict(float)
        axis_torque_max = defaultdict(float)
        axis_saturation = defaultdict(int)
        axis_work = defaultdict(float)
        integration_steps = int(round(duration / DT)) + 1
        support_covered_steps = unexpected_contact_steps = 0
        max_fixture_force = max_fixture_moment = max_rot_error = max_prism_error = 0.0
        for step in range(integration_steps):
            time_s = min(step * DT, duration)
            desired_position, desired_velocity, root_target, nearest_base = desired(time_s)
            data.mocap_pos[0] = root_target
            data.mocap_quat[0] = [1.0, 0.0, 0.0, 0.0]
            mujoco.mj_forward(model, data)
            command, saturated = controls(model, data, axes, desired_position, desired_velocity, caps)
            mujoco.mj_forward(model, data)
            active_feet, left_force, right_force, unexpected, minimum_contact_distance = contact_state(model, data)
            global_unexpected.update(unexpected)
            if unexpected:
                unexpected_contact_steps += 1
            if expected_support(nearest_base["support_mode"]).issubset(active_feet):
                support_covered_steps += 1
            root_force = float(np.linalg.norm(data.qfrc_constraint[:3]))
            root_moment = float(np.linalg.norm(data.qfrc_constraint[3:6]))
            max_fixture_force = max(max_fixture_force, root_force)
            max_fixture_moment = max(max_fixture_moment, root_moment)
            errors: dict[str, float] = {}
            for axis in axes:
                joint_id = mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_JOINT, axis)
                qpos_address = model.jnt_qposadr[joint_id]
                dof_address = model.jnt_dofadr[joint_id]
                error_si = desired_position[axis] - data.qpos[qpos_address]
                display_error = abs(error_si) * (1000.0 if axis.endswith("_GRIPPER") else 180.0 / math.pi)
                errors[axis] = display_error
                axis_error_sq[axis] += display_error**2
                axis_error_max[axis] = max(axis_error_max[axis], display_error)
                axis_torque_sq[axis] += command[axis] ** 2
                axis_torque_max[axis] = max(axis_torque_max[axis], abs(command[axis]))
                axis_saturation[axis] += int(saturated[axis])
                axis_work[axis] += abs(command[axis] * data.qvel[dof_address]) * DT
                if axis.endswith("_GRIPPER"):
                    max_prism_error = max(max_prism_error, display_error)
                else:
                    max_rot_error = max(max_rot_error, display_error)
            all_finite = all_finite and bool(
                np.isfinite(data.qpos).all() and np.isfinite(data.qvel).all()
                and np.isfinite(data.qacc).all() and np.isfinite(data.ctrl).all()
            )
            if step % round(0.02 / DT) == 0 or step == integration_steps - 1:
                sample_rows.append({
                    "sequence_id": sequence_id, "time_s": f"{time_s:.3f}",
                    "declared_support": nearest_base["support_mode"], "active_floor_contacts": "+".join(sorted(active_feet)) or "NONE",
                    "left_normal_force_n": f"{left_force:.6f}", "right_normal_force_n": f"{right_force:.6f}",
                    "unexpected_contact_pairs": ";".join(sorted(unexpected)) or "NONE",
                    "minimum_contact_distance_m": f"{minimum_contact_distance:.9f}",
                    "root_position_error_mm": f"{np.linalg.norm(data.qpos[:3] - root_target) * 1000.0:.6f}",
                    "maximum_rotary_tracking_error_deg": f"{max((value for axis, value in errors.items() if not axis.endswith('_GRIPPER')), default=0.0):.6f}",
                    "maximum_gripper_tracking_error_mm": f"{max((value for axis, value in errors.items() if axis.endswith('_GRIPPER')), default=0.0):.6f}",
                    "root_constraint_force_norm_n": f"{root_force:.6f}", "root_constraint_moment_norm_nm": f"{root_moment:.6f}",
                    "com_x_m": f"{data.subtree_com[1, 0]:.9f}", "com_y_m": f"{data.subtree_com[1, 1]:.9f}", "com_z_m": f"{data.subtree_com[1, 2]:.9f}",
                    "simulation_boundary": "IDEAL 6DOF MOCAP/WELD FIXTURE; NOT FREE BALANCE OR PHYSICAL RESTRAINT",
                    "warning": WARNING,
                })
            if step < integration_steps - 1:
                mujoco.mj_step(model, data)

        rotary_saturation_max = 0.0
        for axis in axes:
            saturation_fraction = axis_saturation[axis] / integration_steps
            if not axis.endswith("_GRIPPER"):
                rotary_saturation_max = max(rotary_saturation_max, saturation_fraction)
            axis_rows.append({
                "sequence_id": sequence_id, "axis_id": axis,
                "control_limit": f"{(1.0 if axis.endswith('_GRIPPER') else caps[axis]):.6f}",
                "control_unit": "N NUMERICAL HOLD ONLY" if axis.endswith("_GRIPPER") else "Nm CURRENT-LIMITED LINEAR ENDPOINT; NOT CONTINUOUS RATING",
                "maximum_abs_control": f"{axis_torque_max[axis]:.6f}",
                "rms_control": f"{math.sqrt(axis_torque_sq[axis] / integration_steps):.6f}",
                "maximum_tracking_error": f"{axis_error_max[axis]:.6f}",
                "rms_tracking_error": f"{math.sqrt(axis_error_sq[axis] / integration_steps):.6f}",
                "tracking_error_unit": "mm" if axis.endswith("_GRIPPER") else "deg",
                "saturation_fraction": f"{saturation_fraction:.9f}", "absolute_mechanical_work_j": f"{axis_work[axis]:.9f}",
                "screen_state": "PRISMATIC FORCE CALIBRATION OPEN" if axis.endswith("_GRIPPER") else ("PASS BOUNDED NUMERICAL SCREEN" if saturation_fraction <= MAX_ROTARY_SATURATION_FRACTION and axis_error_max[axis] <= MAX_ROTARY_ERROR_DEG else "FAIL BOUNDED NUMERICAL SCREEN"),
                "authority": "NO HARDWARE CONTROL OR MOTION AUTHORITY", "warning": WARNING,
            })
        coverage = support_covered_steps / integration_steps
        sequence_pass = (
            all_finite and unexpected_contact_steps == 0
            and max_rot_error <= MAX_ROTARY_ERROR_DEG
            and max_prism_error <= MAX_PRISMATIC_ERROR_MM
            and rotary_saturation_max <= MAX_ROTARY_SATURATION_FRACTION
            and coverage >= MIN_DECLARED_SUPPORT_COVERAGE
        )
        summary_rows.append({
            "sequence_id": sequence_id, "duration_s": f"{duration:.3f}", "integration_timestep_s": f"{DT:.6f}",
            "integration_step_count": integration_steps, "logged_sample_count": sum(row["sequence_id"] == sequence_id for row in sample_rows),
            "maximum_rotary_tracking_error_deg": f"{max_rot_error:.6f}", "maximum_gripper_tracking_error_mm": f"{max_prism_error:.6f}",
            "maximum_rotary_saturation_fraction": f"{rotary_saturation_max:.9f}",
            "declared_support_coverage_fraction": f"{coverage:.9f}", "unexpected_contact_step_count": unexpected_contact_steps,
            "maximum_root_constraint_force_norm_n": f"{max_fixture_force:.6f}", "maximum_root_constraint_moment_norm_nm": f"{max_fixture_moment:.6f}",
            "numerically_finite": str(all_finite).upper(),
            "result": "PASS IDEAL-FIXTURE NUMERICAL SCREEN" if sequence_pass else "FAIL IDEAL-FIXTURE NUMERICAL SCREEN",
            "scope": "DOES NOT ESTABLISH FREE BALANCE, PHYSICAL RESTRAINT, ACTUATOR CONTINUOUS CAPACITY, OR WALKING",
            "warning": WARNING,
        })
    status = {
        "numerically_finite": all_finite,
        "unexpected_contact_pairs": sorted(global_unexpected),
        "all_sequences_pass_bounded_ideal_fixture_screen": all(row["result"].startswith("PASS") for row in summary_rows),
    }
    return sample_rows, axis_rows, summary_rows, status


def render_page(summary_rows: list[dict], status: dict) -> None:
    cards = "".join(
        f'<article class="card"><h3>{html.escape(row["sequence_id"])}</h3><div class="metric">{float(row["maximum_rotary_tracking_error_deg"]):.2f}°</div><p>Maximum rotary tracking error; saturation {100*float(row["maximum_rotary_saturation_fraction"]):.1f}%; declared-support coverage {100*float(row["declared_support_coverage_fraction"]):.1f}%.</p><strong>{html.escape(row["result"])}</strong></article>'
        for row in summary_rows
    )
    page = f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>HR-30 MuJoCo dynamics validation</title><style>:root{{--deep:#071d36;--blue:#0b4f91;--sky:#84d8ff;--gold:#f2b91d;--paper:#eef8fe;--ink:#142a40;--line:#9acfe8}}*{{box-sizing:border-box}}body{{margin:0;background:var(--paper);color:var(--ink);font:17px/1.55 system-ui,Segoe UI,sans-serif}}header,main{{padding:28px 20px}}header{{background:var(--deep);color:#fff}}header>div,main{{max-width:1180px;margin:auto}}h1{{font-size:clamp(38px,6vw,68px);line-height:1.04}}h2{{font-size:clamp(27px,4vw,42px)}}.warning{{background:var(--gold);color:#17243a;border:3px solid #805600;padding:15px 18px;font-weight:900}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:16px}}.card,.panel{{background:#fff;border:2px solid var(--line);border-radius:16px;padding:18px;margin:18px 0}}.metric{{font-size:clamp(30px,5vw,48px);font-weight:900;color:var(--blue)}}label,select,input{{font:inherit}}select{{padding:10px;border:2px solid var(--blue);border-radius:8px}}input[type=range]{{width:100%}}canvas{{width:100%;height:320px;background:#f8fcff;border:2px solid var(--line);border-radius:12px}}a{{color:#075b9b;font-weight:800}}small{{font-size:14px}}@media(max-width:700px){{body{{font-size:16px}}header,main{{padding-inline:13px}}}}</style></head><body><header><div><div class="warning">{WARNING}</div><h1>The whole robot now runs in a real physics engine.</h1><p>MuJoCo compiles the 9.990 kg tether-first model and executes both 10.72 s sequences with a numerical six-degree-of-freedom trajectory fixture. This is a model-integration test—not proof of free walking.</p></div></header><main><section><h2>Bounded results</h2><div class="grid">{cards}</div></section><section class="panel"><h2>Scrub recorded physics data</h2><p><label for="sequence"><strong>Sequence:</strong></label> <select id="sequence">{''.join(f'<option>{row["sequence_id"]}</option>' for row in summary_rows)}</select></p><input id="scrub" type="range" min="0" max="1" value="0"><p id="readout">Loading simulation samples…</p><canvas id="chart" width="1000" height="320" aria-label="Tracking error and foot contact force chart"></canvas></section><section class="panel"><h2>Download the evidence</h2><p><a href="sequence-dynamics-summary.csv">sequence summary</a> · <a href="axis-dynamics-register.csv">all 25 axes</a> · <a href="simulation-samples.csv">50 Hz simulation samples</a> · <a href="simulation-preview.json">interactive preview data</a> · <a href="hr30_tether_ideal_fixture.xml">derived MuJoCo model</a> · <a href="runtime-provenance.json">runtime provenance</a> · <a href="open-holds.csv">open holds</a></p></section><section class="panel"><h2>What the ideal fixture hides</h2><p>The fixture can apply arbitrary six-axis constraint load to the pelvis path. Consequently this run cannot establish free balance, recoverability, physical tether forces, sole friction, contact compliance, real actuator tracking, current or thermal capacity, stopping behavior, or safety. Its value is narrower: the dynamics tree compiles, mass/inertia is positive, contact topology is explicit, torque-limited numerical control executes, and failures are measurable.</p></section></main><script>fetch('simulation-preview.json').then(r=>{{if(!r.ok)throw new Error(`HTTP ${{r.status}}`);return r.json()}}).then(rows=>{{const sel=document.getElementById('sequence'),range=document.getElementById('scrub'),out=document.getElementById('readout'),canvas=document.getElementById('chart'),ctx=canvas.getContext('2d');function group(){{return rows.filter(r=>r.sequence_id===sel.value)}}function draw(){{const g=group(),i=Math.min(+range.value,g.length-1),r=g[i];range.max=g.length-1;out.textContent=`${{r.time_s}} s · support ${{r.declared_support}} · contacts ${{r.active_floor_contacts}} · max error ${{Number(r.maximum_rotary_tracking_error_deg).toFixed(2)}}° · left/right normal force ${{Number(r.left_normal_force_n).toFixed(1)}} / ${{Number(r.right_normal_force_n).toFixed(1)}} N`;ctx.clearRect(0,0,1000,320);const max=Math.max(1,...g.map(x=>Math.max(+x.maximum_rotary_tracking_error_deg,+x.left_normal_force_n/20,+x.right_normal_force_n/20)));[['maximum_rotary_tracking_error_deg','#c82828',1],['left_normal_force_n','#0b4f91',20],['right_normal_force_n','#f2a900',20]].forEach(([key,color,scale])=>{{ctx.beginPath();ctx.strokeStyle=color;ctx.lineWidth=3;g.forEach((x,j)=>{{const px=j/(g.length-1)*980+10,py=300-(+x[key]/scale)/max*280;(j?ctx.lineTo(px,py):ctx.moveTo(px,py))}});ctx.stroke()}});ctx.fillStyle='#142a40';ctx.font='16px system-ui';ctx.fillText('red: max joint error (deg) · blue/gold: left/right normal force ÷20',18,24);ctx.strokeStyle='#071d36';ctx.beginPath();ctx.moveTo(i/(g.length-1)*980+10,30);ctx.lineTo(i/(g.length-1)*980+10,305);ctx.stroke()}}sel.addEventListener('change',()=>{{range.value=0;draw()}});range.addEventListener('input',draw);draw()}}).catch(error=>{{document.getElementById('readout').textContent=`Preview failed to load: ${{error.message}}`;}});</script></body></html>'''
    (OUT / "index.html").write_text(page, encoding="utf-8", newline="\n")


def write_manifest() -> None:
    rows = []
    for path in sorted(OUT.iterdir(), key=lambda value: value.name):
        if path.is_file() and path.name != "file-manifest.csv":
            rows.append({"file": path.name, "sha256": sha(path), "bytes": path.stat().st_size, "warning": WARNING})
    write_csv(OUT / "file-manifest.csv", rows)


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    torque_rows = read_csv(BODY / "current-constrained-actuation-p0.1" / "axis-current-torque-register.csv")
    caps = {row["axis_id"]: float(row["current_limited_linear_endpoint_nm"]) for row in torque_rows}
    mass_summary = json.loads((BODY / "mass-reconciliation-summary.json").read_text(encoding="utf-8"))
    expected_mass_kg = float(mass_summary["active_tether_dynamics_planning_mass_kg"])
    model_path = build_fixture_model(caps)
    model = mujoco.MjModel.from_xml_path(str(model_path.resolve()))
    if (model.nq, model.nv, model.nu, model.nkey, model.nexclude, model.nmocap) != (32, 31, 25, 12, 35, 1):
        raise RuntimeError("compiled MuJoCo topology differs from controlled HR-30 model")
    physical_body_ids = np.flatnonzero((np.arange(model.nbody) > 0) & (model.body_mocapid < 0))
    if abs(float(model.body_subtreemass[1]) - expected_mass_kg) > 5e-6 or np.min(model.body_mass[physical_body_ids]) <= 0 or np.min(model.body_inertia[physical_body_ids]) <= 0:
        raise RuntimeError("compiled model mass/inertia is not positive and reconciled")
    simulation_started = time.perf_counter()
    sample_rows, axis_rows, summary_rows, execution = simulate(model, caps)
    simulation_wall_time_s = time.perf_counter() - simulation_started
    write_csv(OUT / "simulation-samples.csv", sample_rows)
    preview_fields = ("sequence_id", "time_s", "declared_support", "active_floor_contacts", "maximum_rotary_tracking_error_deg", "left_normal_force_n", "right_normal_force_n")
    preview_rows = [{key: row[key] for key in preview_fields} for row in sample_rows]
    (OUT / "simulation-preview.json").write_text(json.dumps(preview_rows, separators=(",", ":")) + "\n", encoding="utf-8")
    write_csv(OUT / "axis-dynamics-register.csv", axis_rows)
    write_csv(OUT / "sequence-dynamics-summary.csv", summary_rows)
    source_rows = []
    for role, path in (
        ("active tether MJCF", BODY / "hr30_tether.xml"),
        ("keyframed walking MJCF", KIN / "hr30_tether_walking_keyframes.xml"),
        ("trajectory samples", KIN / "trajectory-samples.csv"),
        ("joint trajectory", KIN / "joint-trajectory.csv"),
        ("current torque limits", BODY / "current-constrained-actuation-p0.1" / "axis-current-torque-register.csv"),
        ("mass reconciliation", BODY / "mass-reconciliation-summary.json"),
        ("generator", Path(__file__)),
    ):
        source_rows.append({"role": role, "path": path.relative_to(ROOT).as_posix(), "sha256": sha(path), "state": "BOUND", "warning": WARNING})
    write_csv(OUT / "source-binding.csv", source_rows)
    holds = [
        ("MD-H01", "ideal six-degree-of-freedom mocap/weld fixture is not a selected or physically characterized fall restraint"),
        ("MD-H02", "current-limited linear stall endpoint is not a continuous actuator torque or thermal rating"),
        ("MD-H03", "gripper numerical hold force is not mapped to a selected rack/pinion force calibration"),
        ("MD-H04", "sole friction, compliance, wear, floor variation and eight physical load-cell channels remain uncharacterized"),
        ("MD-H05", "controller gains are numerical test settings, not firmware gains or stability evidence"),
        ("MD-H06", "free-balance, capture point, ZMP, disturbance recovery and fall behavior are not validated"),
        ("MD-H07", "electrical current, regeneration, bus timing, latency, backlash and thermal behavior are not simulated"),
        ("MD-H08", "received hardware, physical correlation and qualified review remain unexecuted"),
    ]
    write_csv(OUT / "open-holds.csv", [{"hold_id": item, "unresolved": text, "state": "OPEN", "authority": "BLOCKS HARDWARE MOTION AND WALKING", "warning": WARNING} for item, text in holds])
    provenance = {
        "identifier": IDENTIFIER, "warning": WARNING, "executed_utc": __import__("datetime").datetime.now(__import__("datetime").timezone.utc).isoformat(),
        "python": __import__("sys").version, "mujoco_version": mujoco.__version__, "numpy_version": np.__version__,
        "official_runtime_source": "https://pypi.org/project/mujoco/3.10.0/", "official_source_accessed": "2026-08-17",
        "integration_timestep_s": DT, "settle_time_s": SETTLE_S, "integrator": "implicitfast", "solver": "Newton",
        "simulation_wall_time_s": round(simulation_wall_time_s, 6),
        "controller": {"rotary_kp": "40 * candidate endpoint Nm per rad", "rotary_kd": "2 * candidate endpoint Nm per rad/s", "gripper_kp_n_m": 100, "gripper_kd_n_s_m": 5},
        "fixture": "ideal six-degree-of-freedom mocap body welded numerically to base_link; not physical hardware",
    }
    (OUT / "runtime-provenance.json").write_text(json.dumps(provenance, indent=2) + "\n", encoding="utf-8")
    status = {
        "identifier": IDENTIFIER, "warning": WARNING, "mujoco_model_compiles": True, "mujoco_version": mujoco.__version__,
        "mass_kg": float(model.body_subtreemass[1]), "nq": model.nq, "nv": model.nv, "actuator_count": model.nu,
        "keyframe_count": model.nkey, "contact_exclusion_count": model.nexclude, "mocap_fixture_count": model.nmocap,
        "all_moving_bodies_positive_mass_inertia": True, "sequence_count": len(summary_rows),
        "simulation_logged_sample_count": len(sample_rows), "axis_result_count": len(axis_rows), **execution,
        "free_balance_validated": False, "physical_restraint_validated": False, "continuous_actuator_capacity_validated": False,
        "physical_execution_count": 0, "connection_authority": False, "powered_test_authority": False,
        "motion_authority": False, "walking_authority": False, "energization_authority": False,
    }
    (OUT / "dynamics-validation-status.json").write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8")
    shutil.copy2(__file__, OUT / "dynamics-validation-source.py")
    readme = f"""# HR-30 MuJoCo dynamics validation P0.1

**{WARNING}**

MuJoCo {mujoco.__version__} compiles the corrected 9.990 kg active tether-first model with 32 generalized positions, 31 velocities, 25 torque/force inputs, 35 named interface exclusions, 12 walking keyframes and one numerical six-degree-of-freedom trajectory fixture. Both 10.72 s sequences are integrated at 2 ms with torque-limited numerical tracking control.

The ideal fixture is deliberately conspicuous: it can apply arbitrary load to keep the pelvis on its prescribed path. This package therefore validates model integration, positive mass/inertia, declared foot/floor contact topology, bounded numerical tracking and explicit failure metrics. It does **not** validate free balance, a physical tether, continuous actuator capacity, electrical current, thermal behavior, firmware, stopping, recovery, safety or walking.
"""
    (OUT / "README.md").write_text(readme, encoding="utf-8", newline="\n")
    render_page(summary_rows, status)
    write_manifest()
    if REL.exists():
        shutil.rmtree(REL)
    shutil.copytree(OUT, REL)
    start, end = "<!-- HR30-MUJOCO-DYNAMICS-P01-START -->", "<!-- HR30-MUJOCO-DYNAMICS-P01-END -->"
    body_readme = (BODY / "README.md").read_text(encoding="utf-8")
    block = f"""{start}
## Executed MuJoCo dynamics checkpoint

The [MuJoCo dynamics guide](mujoco-dynamics-validation-p0.1/index.html) records two complete ideal-fixture simulations of the bilateral 40 mm sequences. The corrected 9.990 kg model now compiles with positive inertia on every moving body and explicit foot/floor contacts. The fixture is numerical test equipment, not evidence of free balance, a physical fall restraint or walking authority.
{end}"""
    if start in body_readme and end in body_readme:
        body_readme = body_readme[:body_readme.index(start)] + block + body_readme[body_readme.index(end) + len(end):]
    else:
        body_readme = body_readme.rstrip() + "\n\n" + block + "\n"
    (BODY / "README.md").write_text(body_readme, encoding="utf-8", newline="\n")
    page_path = BODY / "index.html"
    page = page_path.read_text(encoding="utf-8")
    web = f'''{start}<section id="mujoco-dynamics"><h2>The whole body now executes in MuJoCo</h2><div class="grid"><article class="card pass"><div class="metric">25</div><p>torque/force-controlled axes in an executed physics model.</p></article><article class="card pass"><div class="metric">35</div><p>named nested-interface contact exclusions.</p></article><article class="card hold"><h3>Ideal fixture</h3><p>The six-axis numerical gantry hides free-balance and restraint requirements.</p></article></div><p><a href="mujoco-dynamics-validation-p0.1/index.html">Open the interactive dynamics evidence guide</a>. No physical motion or walking authority follows.</p></section>{end}'''
    if start in page and end in page:
        page = page[:page.index(start)] + web + page[page.index(end) + len(end):]
    else:
        page = page.replace("</main>", web + "</main>")
    page_path.write_text(page, encoding="utf-8", newline="\n")
    package_status_path = BODY / "package-status.json"
    package_status = json.loads(package_status_path.read_text(encoding="utf-8"))
    package_status.update({
        "mujoco_dynamics_validation_present": True, "mujoco_model_compiles": True,
        "mujoco_executed_sequence_count": len(summary_rows), "all_moving_bodies_positive_mass_inertia": True,
        "free_balance_validated": False, "walking_sequence_physically_validated": False,
    })
    package_status_path.write_text(json.dumps(package_status, indent=2) + "\n", encoding="utf-8")
    system.refresh_manifest_and_release()
    print(json.dumps(status, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
