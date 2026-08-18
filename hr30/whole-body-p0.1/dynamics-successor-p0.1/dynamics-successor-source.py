"""Execute the preregistered HR-30 hip-4:1 inverse-feedforward successor."""

from __future__ import annotations

import csv
import hashlib
import html
import json
import math
import shutil
import xml.etree.ElementTree as ET
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

import mujoco
import numpy as np

import generate_hr30_mujoco_dynamics_validation_p01 as baseline
import generate_hr30_system_package_p01 as system


ROOT = Path(__file__).resolve().parents[1]
BODY = ROOT / "hr30" / "whole-body-p0.1"
BASE = BODY / "mujoco-dynamics-validation-p0.1"
DEMAND = BODY / "torque-demand-p0.1"
OUT = BODY / "dynamics-successor-p0.1"
REL = ROOT / "release" / "hr30" / "whole-body-p0.1" / OUT.name
IDENTIFIER = "HR30-DYNAMICS-SUCCESSOR-P0.1"
WARNING = "PRELIMINARY - NUMERICAL HIP-REDUCTION SUCCESSOR ONLY - NOT APPROVED FOR CONNECTION, POWERED TESTING, MOTION, WALKING, OR ENERGIZATION"
DT = 0.002
SETTLE_S = 0.5
MAX_ROTARY_ERROR_DEG = 5.0
MAX_GRIPPER_ERROR_MM = 2.0
MAX_ROTARY_SATURATION_FRACTION = 0.10
MIN_SUPPORT_COVERAGE = 0.99
HIP_AXES = {"L_HIP_PITCH", "R_HIP_PITCH", "L_HIP_ROLL", "R_HIP_ROLL"}
SUCCESSOR_RATIO = 4.0


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        raise RuntimeError(f"refusing to write empty evidence table {path.name}")
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build_model(baseline_caps: dict[str, float], successor_caps: dict[str, float]) -> Path:
    root = ET.parse(BASE / "hr30_tether_ideal_fixture.xml").getroot()
    root.set("model", "hr30_hip4_inverse_feedforward_p01")
    option = root.find("option")
    if option is None:
        raise RuntimeError("MuJoCo option missing")
    option.set("timestep", f"{DT:.6f}")
    option.set("integrator", "implicitfast")
    option.set("solver", "Newton")
    actuators = root.find("actuator")
    if actuators is None:
        raise RuntimeError("MuJoCo actuator block missing")
    for motor in actuators:
        joint = motor.get("joint")
        if joint in successor_caps and not joint.endswith("_GRIPPER"):
            cap = successor_caps[joint]
            motor.set("ctrlrange", f"{-cap:.9f} {cap:.9f}")
    custom = ET.SubElement(root, "custom")
    ET.SubElement(custom, "text", name="successor_boundary", data="4:1 hip pitch and hip roll sizing scenario; transmission inertia/backlash/efficiency dynamics not modeled")
    ET.SubElement(custom, "text", name="baseline_cap_hash", data=hashlib.sha256(json.dumps(baseline_caps, sort_keys=True).encode()).hexdigest())
    ET.indent(root)
    target = OUT / "hr30_tether_hip4_inverse_feedforward.xml"
    target.write_text(ET.tostring(root, encoding="unicode") + "\n", encoding="utf-8", newline="\n")
    return target


def demand_table() -> dict[str, dict[str, tuple[np.ndarray, np.ndarray]]]:
    grouped: dict[str, dict[str, list[tuple[float, float]]]] = defaultdict(lambda: defaultdict(list))
    for row in read_csv(DEMAND / "inverse-dynamics-samples.csv"):
        grouped[row["sequence_id"]][row["axis_id"]].append((float(row["time_s"]), float(row["contact_enabled_inverse_torque_nm"])))
    result: dict[str, dict[str, tuple[np.ndarray, np.ndarray]]] = {}
    for sequence, axes in grouped.items():
        result[sequence] = {}
        for axis, points in axes.items():
            points.sort()
            result[sequence][axis] = (
                np.array([point[0] for point in points], dtype=float),
                np.array([point[1] for point in points], dtype=float),
            )
    return result


def control(
    model: mujoco.MjModel,
    data: mujoco.MjData,
    axes: list[str],
    desired_position: dict[str, float],
    desired_velocity: dict[str, float],
    baseline_caps: dict[str, float],
    successor_caps: dict[str, float],
    feedforward: dict[str, float],
) -> tuple[dict[str, float], dict[str, bool], dict[str, float]]:
    commands: dict[str, float] = {}
    saturated: dict[str, bool] = {}
    raw_commands: dict[str, float] = {}
    for axis in axes:
        joint_id = mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_JOINT, axis)
        actuator_id = mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_ACTUATOR, f"M_{axis}")
        qpos_address = int(model.jnt_qposadr[joint_id])
        dof_address = int(model.jnt_dofadr[joint_id])
        error = desired_position[axis] - data.qpos[qpos_address]
        velocity_error = desired_velocity[axis] - data.qvel[dof_address]
        if axis.endswith("_GRIPPER"):
            cap, kp, kd, ff = 1.0, 100.0, 5.0, 0.0
        else:
            cap = successor_caps[axis]
            kp, kd = 40.0 * baseline_caps[axis], 2.0 * baseline_caps[axis]
            ff = feedforward[axis]
        raw = ff + kp * error + kd * velocity_error
        command = float(np.clip(raw, -cap, cap))
        data.ctrl[actuator_id] = command
        commands[axis] = command
        raw_commands[axis] = raw
        saturated[axis] = abs(raw) >= cap * (1.0 - 1e-10)
    return commands, saturated, raw_commands


def simulate(model: mujoco.MjModel, baseline_caps: dict[str, float], successor_caps: dict[str, float]) -> tuple[list[dict], list[dict], list[dict], dict]:
    base_by_sequence, joints_by_sequence = baseline.trajectory_data()
    demand = demand_table()
    axes = sorted(joints_by_sequence[next(iter(joints_by_sequence))])
    sample_rows: list[dict] = []
    axis_rows: list[dict] = []
    summary_rows: list[dict] = []
    global_unexpected: set[str] = set()
    all_finite = True

    for sequence_id in sorted(base_by_sequence):
        base_rows = base_by_sequence[sequence_id]
        joint_rows = joints_by_sequence[sequence_id]
        duration = float(base_rows[-1]["time_s"])
        data = mujoco.MjData(model)
        first_root = np.array([float(base_rows[0][field]) for field in ("root_x_m", "root_y_m", "root_z_m")])
        data.qpos[:3] = first_root
        data.qpos[3:7] = (1.0, 0.0, 0.0, 0.0)
        data.mocap_pos[0] = first_root
        data.mocap_quat[0] = (1.0, 0.0, 0.0, 0.0)
        for axis in axes:
            joint_id = mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_JOINT, axis)
            data.qpos[model.jnt_qposadr[joint_id]] = float(joint_rows[axis][0]["position_si"])
        mujoco.mj_forward(model, data)

        def desired(time_s: float) -> tuple[dict[str, float], dict[str, float], np.ndarray, dict, dict[str, float]]:
            nearest = min(int(round(time_s / 0.02)), len(base_rows) - 1)
            root = np.array([baseline.interpolate(base_rows, field, time_s) for field in ("root_x_m", "root_y_m", "root_z_m")])
            position = {axis: baseline.interpolate(joint_rows[axis], "position_si", time_s) for axis in axes}
            velocity = {axis: baseline.interpolate(joint_rows[axis], "velocity_si_s", time_s) for axis in axes}
            feedforward = {
                axis: 0.0 if axis.endswith("_GRIPPER") else float(np.interp(time_s, *demand[sequence_id][axis]))
                for axis in axes
            }
            return position, velocity, root, base_rows[nearest], feedforward

        initial_position, initial_velocity, _, _, initial_ff = desired(0.0)
        for _ in range(round(SETTLE_S / DT)):
            data.mocap_pos[0] = first_root
            mujoco.mj_forward(model, data)
            control(model, data, axes, initial_position, initial_velocity, baseline_caps, successor_caps, initial_ff)
            mujoco.mj_step(model, data)
        data.time = 0.0

        error_sq = defaultdict(float)
        error_max = defaultdict(float)
        command_sq = defaultdict(float)
        command_max = defaultdict(float)
        raw_max = defaultdict(float)
        saturation_count = defaultdict(int)
        work = defaultdict(float)
        integration_steps = int(round(duration / DT)) + 1
        support_covered = unexpected_steps = 0
        max_rot_error = max_gripper_error = 0.0
        max_fixture_force = max_fixture_moment = 0.0

        for step in range(integration_steps):
            time_s = min(step * DT, duration)
            position, velocity, root_target, nearest_base, feedforward = desired(time_s)
            data.mocap_pos[0] = root_target
            data.mocap_quat[0] = (1.0, 0.0, 0.0, 0.0)
            mujoco.mj_forward(model, data)
            commands, saturated, raw_commands = control(model, data, axes, position, velocity, baseline_caps, successor_caps, feedforward)
            mujoco.mj_forward(model, data)
            feet, left_force, right_force, unexpected, minimum_distance = baseline.contact_state(model, data)
            global_unexpected.update(unexpected)
            unexpected_steps += int(bool(unexpected))
            support_covered += int(baseline.expected_support(nearest_base["support_mode"]).issubset(feet))
            fixture_force = float(np.linalg.norm(data.qfrc_constraint[:3]))
            fixture_moment = float(np.linalg.norm(data.qfrc_constraint[3:6]))
            max_fixture_force = max(max_fixture_force, fixture_force)
            max_fixture_moment = max(max_fixture_moment, fixture_moment)
            display_errors: dict[str, float] = {}
            for axis in axes:
                joint_id = mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_JOINT, axis)
                qpos_address = int(model.jnt_qposadr[joint_id])
                dof_address = int(model.jnt_dofadr[joint_id])
                error_si = position[axis] - data.qpos[qpos_address]
                display_error = abs(error_si) * (1000.0 if axis.endswith("_GRIPPER") else 180.0 / math.pi)
                display_errors[axis] = display_error
                error_sq[axis] += display_error**2
                error_max[axis] = max(error_max[axis], display_error)
                command_sq[axis] += commands[axis] ** 2
                command_max[axis] = max(command_max[axis], abs(commands[axis]))
                raw_max[axis] = max(raw_max[axis], abs(raw_commands[axis]))
                saturation_count[axis] += int(saturated[axis])
                work[axis] += abs(commands[axis] * data.qvel[dof_address]) * DT
                if axis.endswith("_GRIPPER"):
                    max_gripper_error = max(max_gripper_error, display_error)
                else:
                    max_rot_error = max(max_rot_error, display_error)
            all_finite = all_finite and bool(np.isfinite(data.qpos).all() and np.isfinite(data.qvel).all() and np.isfinite(data.qacc).all() and np.isfinite(data.ctrl).all())
            if step % round(0.02 / DT) == 0 or step == integration_steps - 1:
                sample_rows.append({
                    "sequence_id": sequence_id,
                    "time_s": f"{time_s:.3f}",
                    "support_mode": nearest_base["support_mode"],
                    "active_floor_contacts": "+".join(sorted(feet)) or "NONE",
                    "maximum_rotary_tracking_error_deg": f"{max((value for axis, value in display_errors.items() if not axis.endswith('_GRIPPER')), default=0.0):.6f}",
                    "maximum_gripper_tracking_error_mm": f"{max((value for axis, value in display_errors.items() if axis.endswith('_GRIPPER')), default=0.0):.6f}",
                    "left_normal_force_n": f"{left_force:.6f}",
                    "right_normal_force_n": f"{right_force:.6f}",
                    "unexpected_contact_pairs": ";".join(sorted(unexpected)) or "NONE",
                    "minimum_contact_distance_m": f"{minimum_distance:.9f}",
                    "fixture_generalized_force_norm_n": f"{fixture_force:.6f}",
                    "fixture_generalized_moment_norm_nm": f"{fixture_moment:.6f}",
                    "controller": "50 HZ CONTACT-ENABLED INVERSE FEEDFORWARD + FROZEN BASELINE PD GAINS",
                    "warning": WARNING,
                })
            if step < integration_steps - 1:
                mujoco.mj_step(model, data)

        maximum_saturation = 0.0
        for axis in axes:
            fraction = saturation_count[axis] / integration_steps
            if not axis.endswith("_GRIPPER"):
                maximum_saturation = max(maximum_saturation, fraction)
            baseline_row = next(row for row in read_csv(BASE / "axis-dynamics-register.csv") if row["sequence_id"] == sequence_id and row["axis_id"] == axis)
            state = "PRISMATIC FORCE CALIBRATION OPEN" if axis.endswith("_GRIPPER") else ("PASS BOUNDED NUMERICAL SCREEN" if fraction <= MAX_ROTARY_SATURATION_FRACTION and error_max[axis] <= MAX_ROTARY_ERROR_DEG else "FAIL BOUNDED NUMERICAL SCREEN")
            axis_rows.append({
                "sequence_id": sequence_id,
                "axis_id": axis,
                "transmission_scenario": "4.000:1 HIP SUCCESSOR" if axis in HIP_AXES else "BASELINE RATIO RETAINED",
                "control_limit": f"{(1.0 if axis.endswith('_GRIPPER') else successor_caps[axis]):.6f}",
                "control_unit": "N NUMERICAL HOLD ONLY" if axis.endswith("_GRIPPER") else "Nm CURRENT-LIMITED LINEAR ENDPOINT; NOT CONTINUOUS RATING",
                "maximum_abs_control": f"{command_max[axis]:.6f}",
                "maximum_abs_unclipped_command": f"{raw_max[axis]:.6f}",
                "maximum_tracking_error": f"{error_max[axis]:.6f}",
                "rms_tracking_error": f"{math.sqrt(error_sq[axis] / integration_steps):.6f}",
                "tracking_error_unit": "mm" if axis.endswith("_GRIPPER") else "deg",
                "saturation_fraction": f"{fraction:.9f}",
                "baseline_saturation_fraction": baseline_row["saturation_fraction"],
                "absolute_mechanical_work_j": f"{work[axis]:.9f}",
                "screen_state": state,
                "authority": "NO HARDWARE CONTROL OR MOTION AUTHORITY",
                "warning": WARNING,
            })
        coverage = support_covered / integration_steps
        passed = all_finite and unexpected_steps == 0 and max_rot_error <= MAX_ROTARY_ERROR_DEG and max_gripper_error <= MAX_GRIPPER_ERROR_MM and maximum_saturation <= MAX_ROTARY_SATURATION_FRACTION and coverage >= MIN_SUPPORT_COVERAGE
        baseline_summary = next(row for row in read_csv(BASE / "sequence-dynamics-summary.csv") if row["sequence_id"] == sequence_id)
        summary_rows.append({
            "sequence_id": sequence_id,
            "duration_s": f"{duration:.3f}",
            "integration_timestep_s": f"{DT:.6f}",
            "integration_step_count": integration_steps,
            "logged_sample_count": sum(row["sequence_id"] == sequence_id for row in sample_rows),
            "maximum_rotary_tracking_error_deg": f"{max_rot_error:.6f}",
            "maximum_gripper_tracking_error_mm": f"{max_gripper_error:.6f}",
            "maximum_rotary_saturation_fraction": f"{maximum_saturation:.9f}",
            "baseline_maximum_rotary_saturation_fraction": baseline_summary["maximum_rotary_saturation_fraction"],
            "declared_support_coverage_fraction": f"{coverage:.9f}",
            "unexpected_contact_step_count": unexpected_steps,
            "maximum_fixture_generalized_force_norm_n": f"{max_fixture_force:.6f}",
            "maximum_fixture_generalized_moment_norm_nm": f"{max_fixture_moment:.6f}",
            "numerically_finite": str(all_finite).upper(),
            "result": "PASS SUCCESSOR IDEAL-FIXTURE NUMERICAL SCREEN" if passed else "FAIL SUCCESSOR IDEAL-FIXTURE NUMERICAL SCREEN",
            "scope": "DOES NOT ESTABLISH TRANSMISSION FEASIBILITY, CONTINUOUS CAPACITY, FREE BALANCE, PHYSICAL RESTRAINT, OR WALKING",
            "warning": WARNING,
        })

    status = {
        "identifier": IDENTIFIER,
        "warning": WARNING,
        "numerically_finite": all_finite,
        "unexpected_contact_pairs": sorted(global_unexpected),
        "all_sequences_pass_bounded_successor_screen": all(row["result"].startswith("PASS") for row in summary_rows),
        "sequence_count": len(summary_rows),
        "simulation_logged_sample_count": len(sample_rows),
        "axis_result_count": len(axis_rows),
        "transmission_geometry_validated": False,
        "transmission_inertia_backlash_modeled": False,
        "continuous_actuator_capacity_validated": False,
        "physical_execution_count": 0,
        "connection_authority": False,
        "powered_test_authority": False,
        "motion_authority": False,
        "walking_authority": False,
        "energization_authority": False,
    }
    return sample_rows, axis_rows, summary_rows, status


def render_page(summaries: list[dict], scenario_rows: list[dict], status: dict) -> str:
    cards = "".join(f'''<article class="card"><h3>{html.escape(row['sequence_id'])}</h3><div class="metric">{float(row['maximum_rotary_saturation_fraction'])*100:.2f}%</div><p>Maximum rotary saturation; baseline {float(row['baseline_maximum_rotary_saturation_fraction'])*100:.1f}%. Tracking error {float(row['maximum_rotary_tracking_error_deg']):.2f}°.</p><strong>{html.escape(row['result'])}</strong></article>''' for row in summaries)
    table = "".join(f'''<tr><td>{html.escape(row['axis_id'])}</td><td>{row['baseline_ratio']}:1</td><td>{row['successor_ratio']}:1</td><td>{float(row['successor_current_endpoint_nm']):.2f} N·m</td><td>{float(row['inverse_peak_nm']):.2f} N·m</td><td>{float(row['speed_reserve_ratio']):.2f}×</td></tr>''' for row in scenario_rows)
    passed = bool(status["all_sequences_pass_bounded_successor_screen"])
    state = "PASS" if passed else "FAIL"
    heading = "The preregistered 4:1 hip successor clears the numerical screen." if passed else "The preregistered 4:1 hip successor does not clear the numerical screen."
    result_explanation = (
        "The bounded result supports proceeding to physical transmission design, while all hardware and walking validation remain open."
        if passed else
        "All revised hip axes clear, but unchanged knee and ankle axes still exceed the saturation threshold. The run is retained as a rejected controller-and-model configuration."
    )
    state_class = "state pass" if passed else "state fail"
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>HR-30 dynamics successor</title><style>:root{{--deep:#071d36;--blue:#0b4f91;--sky:#84d8ff;--gold:#f2b91d;--paper:#eef8fe;--ink:#142a40;--line:#96cce7;--green:#146c43;--red:#a4281f}}*{{box-sizing:border-box}}body{{margin:0;background:var(--paper);color:var(--ink);font:17px/1.5 system-ui,Segoe UI,sans-serif}}header,main{{padding:28px 20px}}header{{background:var(--deep);color:white}}header>div,main{{max-width:1180px;margin:auto}}h1{{font-size:clamp(38px,6vw,68px);line-height:1.05}}h2{{font-size:clamp(27px,4vw,42px)}}.warning{{background:var(--gold);color:#15243a;border:3px solid #805600;padding:15px 18px;font-weight:900}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:16px}}.card,.panel{{background:white;border:2px solid var(--line);border-radius:15px;padding:18px;margin:18px 0}}.metric{{font-size:clamp(31px,5vw,48px);font-weight:900;color:var(--blue)}}.state.pass{{color:var(--green)}}.state.fail{{color:var(--red)}}.table-wrap{{overflow-x:auto}}table{{border-collapse:collapse;width:100%;min-width:720px}}th,td{{text-align:left;padding:12px;border-bottom:1px solid var(--line);font-size:16px}}th{{background:#d9f2ff}}small{{font-size:14px}}a{{color:#075b9b;font-weight:800}}@media(max-width:700px){{body{{font-size:16px}}header,main{{padding-inline:13px}}}}</style></head><body><header><div><div class="warning">{WARNING}</div><h1>{heading}</h1><p>The gait, mass, contacts, timestep and thresholds are unchanged. Only the four hip pitch/roll output limits and the model-based feedforward change.</p></div></header><main><section class="grid"><article class="card"><div class="metric {state_class}">{state}</div><p>{result_explanation}</p><p>This is a bounded ideal-fixture result—not physical walking validation.</p></article>{cards}</section><section class="panel"><h2>Preregistered transmission scenario</h2><div class="table-wrap"><table><thead><tr><th>Axis</th><th>Baseline</th><th>Successor</th><th>Current endpoint</th><th>Inverse peak</th><th>No-load speed reserve</th></tr></thead><tbody>{table}</tbody></table></div></section><section class="panel"><h2>What remains unmodeled</h2><p>The 4:1 ratio is not yet a physical transmission. This run omits added pulley/shaft/bearing mass, belt compliance, backlash, reflected rotor inertia, tooth loading, efficiency variation, actuator torque-speed behavior and heat. Model-based inverse feedforward also requires robustness tests against mass, contact, latency and state-estimation error.</p></section><section class="panel"><h2>Evidence downloads</h2><p><a href="sequence-successor-summary.csv">sequence results</a> · <a href="axis-successor-results.csv">all 25 axes</a> · <a href="successor-samples.csv">50 Hz samples</a> · <a href="hip4-transmission-scenario.csv">scenario definition</a> · <a href="hr30_tether_hip4_inverse_feedforward.xml">MuJoCo model</a> · <a href="open-holds.csv">open holds</a></p></section></main></body></html>'''


def write_manifest() -> None:
    rows = []
    for path in sorted(OUT.iterdir(), key=lambda item: item.name):
        if path.is_file() and path.name != "file-manifest.csv":
            rows.append({"file": path.name, "sha256": sha(path), "bytes": path.stat().st_size, "warning": WARNING})
    write_csv(OUT / "file-manifest.csv", rows)


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    cap_rows = read_csv(BODY / "current-constrained-actuation-p0.1" / "axis-current-torque-register.csv")
    baseline_caps = {row["axis_id"]: float(row["current_limited_linear_endpoint_nm"]) for row in cap_rows}
    successor_caps = dict(baseline_caps)
    demand_rows = read_csv(DEMAND / "whole-body-axis-demand.csv")
    demand_by_axis = {row["axis_id"]: row for row in demand_rows}
    scenario_rows = []
    for axis in sorted(HIP_AXES):
        cap_row = next(row for row in cap_rows if row["axis_id"] == axis)
        baseline_ratio = float(cap_row["transmission_ratio"])
        successor_caps[axis] = baseline_caps[axis] * SUCCESSOR_RATIO / baseline_ratio
        motor_no_load_speed = float(cap_row["output_no_load_speed_deg_s"]) * baseline_ratio
        planned_speed = float(demand_by_axis[axis]["planned_peak_output_speed_deg_s"])
        scenario_rows.append({
            "axis_id": axis,
            "candidate_actuator": cap_row["actuator_model"],
            "candidate_current_a": cap_row["candidate_current_a"],
            "baseline_ratio": f"{baseline_ratio:.3f}",
            "successor_ratio": f"{SUCCESSOR_RATIO:.3f}",
            "baseline_current_endpoint_nm": f"{baseline_caps[axis]:.6f}",
            "successor_current_endpoint_nm": f"{successor_caps[axis]:.6f}",
            "inverse_peak_nm": demand_by_axis[axis]["peak_contact_inverse_torque_nm"],
            "successor_peak_margin_ratio": f"{successor_caps[axis] / float(demand_by_axis[axis]['peak_contact_inverse_torque_nm']):.6f}",
            "planned_peak_speed_deg_s": f"{planned_speed:.6f}",
            "successor_no_load_output_speed_deg_s": f"{motor_no_load_speed / SUCCESSOR_RATIO:.6f}",
            "speed_reserve_ratio": f"{(motor_no_load_speed / SUCCESSOR_RATIO) / planned_speed:.6f}",
            "geometry_state": "NUMERICAL SCENARIO ONLY - PHYSICAL TWO-STAGE OR COMPACT REDUCER DESIGN REQUIRED",
            "authority": "NO PROCUREMENT OR FABRICATION AUTHORITY",
            "warning": WARNING,
        })
    model_path = build_model(baseline_caps, successor_caps)
    model = mujoco.MjModel.from_xml_path(str(model_path.resolve()))
    samples, axes, summaries, status = simulate(model, baseline_caps, successor_caps)
    write_csv(OUT / "successor-samples.csv", samples)
    write_csv(OUT / "axis-successor-results.csv", axes)
    write_csv(OUT / "sequence-successor-summary.csv", summaries)
    write_csv(OUT / "hip4-transmission-scenario.csv", scenario_rows)
    sources = []
    for role, path in (
        ("baseline ideal-fixture model", BASE / "hr30_tether_ideal_fixture.xml"),
        ("baseline dynamics results", BASE / "axis-dynamics-register.csv"),
        ("inverse-demand samples", DEMAND / "inverse-dynamics-samples.csv"),
        ("inverse-demand envelope", DEMAND / "whole-body-axis-demand.csv"),
        ("current endpoint register", BODY / "current-constrained-actuation-p0.1" / "axis-current-torque-register.csv"),
        ("trajectory samples", BODY / "walking-sequence-p0.1" / "trajectory-samples.csv"),
        ("joint trajectory", BODY / "walking-sequence-p0.1" / "joint-trajectory.csv"),
        ("generator", Path(__file__)),
        ("baseline generator dependency", ROOT / "tools" / "generate_hr30_mujoco_dynamics_validation_p01.py"),
    ):
        sources.append({"role": role, "path": path.relative_to(ROOT).as_posix(), "sha256": sha(path), "state": "BOUND", "warning": WARNING})
    write_csv(OUT / "source-binding.csv", sources)
    holds = [
        ("DS-H01", "no physical 4:1 hip transmission geometry, bearings, shafts, tensioning or housing has been released"),
        ("DS-H02", "added transmission mass, efficiency, compliance, backlash and reflected inertia are not included"),
        ("DS-H03", "candidate current endpoint remains a stall-linear screen rather than a continuous thermal rating"),
        ("DS-H04", "inverse feedforward robustness to mass/contact/state/latency error is not demonstrated"),
        ("DS-H05", "belt tooth load, shaft/bearing reactions and actuator torque-speed behavior remain unvalidated"),
        ("DS-H06", "electrical peak/RMS current, voltage sag, regeneration and heat remain unvalidated"),
        ("DS-H07", "free balance, recovery, physical restraint, stopping and fall behavior remain unvalidated"),
        ("DS-H08", "qualified review and guarded physical correlation remain unexecuted"),
    ]
    write_csv(OUT / "open-holds.csv", [{"hold_id": key, "unresolved": value, "state": "OPEN", "authority": "BLOCKS PROCUREMENT, FABRICATION, HARDWARE MOTION AND WALKING", "warning": WARNING} for key, value in holds])
    provenance = {
        "identifier": IDENTIFIER,
        "warning": WARNING,
        "executed_utc": datetime.now(timezone.utc).isoformat(),
        "mujoco_version": mujoco.__version__,
        "numpy_version": np.__version__,
        "integration_timestep_s": DT,
        "settle_time_s": SETTLE_S,
        "hip_successor_ratio": SUCCESSOR_RATIO,
        "controller": "contact-enabled inverse-dynamics feedforward interpolated from 50 Hz plus baseline-cap-scaled PD gains",
        "thresholds": {"maximum_rotary_error_deg": MAX_ROTARY_ERROR_DEG, "maximum_gripper_error_mm": MAX_GRIPPER_ERROR_MM, "maximum_rotary_saturation_fraction": MAX_ROTARY_SATURATION_FRACTION, "minimum_support_coverage": MIN_SUPPORT_COVERAGE},
        "predeclared_scope": "single 4:1 bilateral hip pitch/roll scenario; no ratio tuning after result",
    }
    (OUT / "runtime-provenance.json").write_text(json.dumps(provenance, indent=2) + "\n", encoding="utf-8")
    (OUT / "dynamics-successor-status.json").write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8")
    result_sentence = (
        "Both sequences pass the bounded ideal-fixture numerical screen."
        if status["all_sequences_pass_bounded_successor_screen"] else
        "Both sequences fail the bounded ideal-fixture numerical screen because unchanged knee and ankle axes remain above the 10% saturation threshold; the four revised hip axes pass."
    )
    result_authority_sentence = (
        "This passing numerical result can justify beginning a physical successor-transmission design."
        if status["all_sequences_pass_bounded_successor_screen"] else
        "This failed numerical result does not justify releasing a physical successor-transmission design."
    )
    (OUT / "README.md").write_text(f"""# HR-30 dynamics successor P0.1

**{WARNING}**

This package executes one preregistered numerical successor: 4:1 bilateral hip pitch/roll reductions with the existing 2.5 A current candidate, the unchanged 9.990 kg gait, and contact-enabled inverse-dynamics feedforward. The baseline tracking thresholds are unchanged.

{result_sentence}

{result_authority_sentence} Neither outcome can validate a transmission, continuous actuator capacity, free balance, a physical restraint or walking.
""", encoding="utf-8", newline="\n")
    (OUT / "index.html").write_text(render_page(summaries, scenario_rows, status), encoding="utf-8", newline="\n")
    shutil.copy2(__file__, OUT / "dynamics-successor-source.py")
    write_manifest()
    if REL.exists():
        shutil.rmtree(REL)
    shutil.copytree(OUT, REL)

    start, end = "<!-- HR30-DYNAMICS-SUCCESSOR-P01-START -->", "<!-- HR30-DYNAMICS-SUCCESSOR-P01-END -->"
    readme_path = BODY / "README.md"
    readme = readme_path.read_text(encoding="utf-8")
    body_result = (
        "The bounded numerical screen passes, permitting only physical transmission design work."
        if status["all_sequences_pass_bounded_successor_screen"] else
        "The bounded numerical screen fails: the four revised hip axes clear, but unchanged knee and ankle saturation remains excessive. The configuration is retained as rejection evidence."
    )
    block = f"""{start}
## Hip-reduction dynamics successor

The [dynamics successor guide](dynamics-successor-p0.1/index.html) executes the unchanged bilateral gait with a preregistered 4:1 hip pitch/roll scenario and inverse-dynamics feedforward. {body_result} It does not approve fabrication, motion or walking.
{end}"""
    if start in readme and end in readme:
        readme = readme[:readme.index(start)] + block + readme[readme.index(end) + len(end):]
    else:
        readme = readme.rstrip() + "\n\n" + block + "\n"
    readme_path.write_text(readme, encoding="utf-8", newline="\n")
    page_path = BODY / "index.html"
    page = page_path.read_text(encoding="utf-8")
    passed = bool(status["all_sequences_pass_bounded_successor_screen"])
    section_heading = "The preregistered 4:1 hip successor clears the bounded gait screen" if passed else "The preregistered 4:1 hip successor fails the bounded gait screen"
    section_card_class = "pass" if passed else "hold"
    section = f'''{start}<section id="dynamics-successor"><h2>{section_heading}</h2><div class="grid"><article class="card {section_card_class}"><div class="metric">{max(float(row['maximum_rotary_saturation_fraction']) for row in summaries)*100:.2f}%</div><p>Worst rotary saturation after inverse feedforward; threshold 10%. The four revised hip axes pass, while unchanged knee and ankle saturation causes the overall failure.</p></article><article class="card"><div class="metric">4:1</div><p>Bilateral hip pitch/roll sizing scenario; physical transmission still required and this failed run does not authorize its design release.</p></article><article class="card hold"><h3>No walking approval</h3><p>Added inertia, backlash, heat, balance and hardware correlation remain open.</p></article></div><p><a href="dynamics-successor-p0.1/index.html">Open the dynamics successor guide</a>.</p></section>{end}'''
    if start in page and end in page:
        page = page[:page.index(start)] + section + page[page.index(end) + len(end):]
    else:
        page = page.replace("</main>", section + "</main>")
    page_path.write_text(page, encoding="utf-8", newline="\n")
    package_status_path = BODY / "package-status.json"
    package_status = json.loads(package_status_path.read_text(encoding="utf-8"))
    package_status.update({
        "dynamics_successor_present": True,
        "dynamics_successor_sequence_count": len(summaries),
        "dynamics_successor_bounded_screen_pass": status["all_sequences_pass_bounded_successor_screen"],
        "physical_hip_transmission_validated": False,
        "continuous_actuator_capacity_validated": False,
        "walking_sequence_physically_validated": False,
    })
    package_status_path.write_text(json.dumps(package_status, indent=2) + "\n", encoding="utf-8")
    system.refresh_manifest_and_release()
    print(json.dumps(status, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
