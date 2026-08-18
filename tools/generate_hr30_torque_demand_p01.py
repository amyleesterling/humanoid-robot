"""Generate the HR-30 whole-body inverse-dynamics torque-demand package."""

from __future__ import annotations

import csv
import hashlib
import html
import json
import math
import shutil
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

import mujoco
import numpy as np

import generate_hr30_system_package_p01 as system


ROOT = Path(__file__).resolve().parents[1]
BODY = ROOT / "hr30" / "whole-body-p0.1"
KIN = BODY / "walking-sequence-p0.1"
DYN = BODY / "mujoco-dynamics-validation-p0.1"
OUT = BODY / "torque-demand-p0.1"
REL = ROOT / "release" / "hr30" / "whole-body-p0.1" / OUT.name
IDENTIFIER = "HR30-WHOLE-BODY-TORQUE-DEMAND-P0.1"
WARNING = "PRELIMINARY - INVERSE-DYNAMICS DESIGN EVIDENCE ONLY - NOT APPROVED FOR CONNECTION, POWERED TESTING, MOTION, WALKING, OR ENERGIZATION"
DT = 0.02
DESIGN_MARGIN = 1.25


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


def trajectory() -> tuple[dict[str, list[dict]], dict[str, dict[str, list[dict]]]]:
    roots: dict[str, list[dict]] = defaultdict(list)
    for row in read_csv(KIN / "trajectory-samples.csv"):
        roots[row["sequence_id"]].append(row)
    joints: dict[str, dict[str, list[dict]]] = defaultdict(lambda: defaultdict(list))
    for row in read_csv(KIN / "joint-trajectory.csv"):
        joints[row["sequence_id"]][row["joint_id"]].append(row)
    for rows in roots.values():
        rows.sort(key=lambda row: int(row["sample_index"]))
    for sequence in joints.values():
        for rows in sequence.values():
            rows.sort(key=lambda row: int(row["sample_index"]))
    return dict(roots), {key: dict(value) for key, value in joints.items()}


def root_derivatives(rows: list[dict]) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    position = np.array([[float(row[field]) for field in ("root_x_m", "root_y_m", "root_z_m")] for row in rows])
    velocity = np.gradient(position, DT, axis=0, edge_order=2)
    acceleration = np.gradient(velocity, DT, axis=0, edge_order=2)
    return position, velocity, acceleration


def set_state(
    model: mujoco.MjModel,
    data: mujoco.MjData,
    root_position: np.ndarray,
    root_velocity: np.ndarray,
    root_acceleration: np.ndarray,
    joint_rows: dict[str, list[dict]],
    axes: list[str],
    sample_index: int,
    gravity_only: bool = False,
) -> None:
    mujoco.mj_resetData(model, data)
    data.qpos[:3] = root_position
    data.qpos[3:7] = (1.0, 0.0, 0.0, 0.0)
    data.mocap_pos[0] = root_position
    data.mocap_quat[0] = (1.0, 0.0, 0.0, 0.0)
    if not gravity_only:
        data.qvel[:3] = root_velocity
        data.qacc[:3] = root_acceleration
    for axis in axes:
        joint_id = mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_JOINT, axis)
        qpos_address = int(model.jnt_qposadr[joint_id])
        dof_address = int(model.jnt_dofadr[joint_id])
        row = joint_rows[axis][sample_index]
        data.qpos[qpos_address] = float(row["position_si"])
        if not gravity_only:
            data.qvel[dof_address] = float(row["velocity_si_s"])
            data.qacc[dof_address] = float(row["acceleration_si_s2"])
    mujoco.mj_inverse(model, data)


def active_feet(model: mujoco.MjModel, data: mujoco.MjData) -> set[str]:
    result: set[str] = set()
    for index in range(data.ncon):
        contact = data.contact[index]
        pair = {
            mujoco.mj_id2name(model, mujoco.mjtObj.mjOBJ_GEOM, int(contact.geom1)),
            mujoco.mj_id2name(model, mujoco.mjtObj.mjOBJ_GEOM, int(contact.geom2)),
        }
        if pair == {"floor", "G_L_foot"}:
            result.add("L")
        elif pair == {"floor", "G_R_foot"}:
            result.add("R")
    return result


def expected_feet(mode: str) -> set[str]:
    return {"L", "R"} if mode == "DOUBLE" else {mode.split()[0]}


def percentile(values: list[float], quantile: float) -> float:
    return float(np.quantile(np.asarray(values, dtype=float), quantile, method="linear"))


def region(axis: str) -> str:
    if axis.startswith(("L_HIP", "R_HIP", "L_KNEE", "R_KNEE", "L_ANKLE", "R_ANKLE")):
        return "LEG"
    if axis.startswith(("L_", "R_")):
        return "ARM/HAND"
    return "HEAD/WAIST"


def analyze() -> tuple[list[dict], list[dict], list[dict], list[dict], dict]:
    model_path = DYN / "hr30_tether_ideal_fixture.xml"
    contact_model = mujoco.MjModel.from_xml_path(str(model_path.resolve()))
    open_model = mujoco.MjModel.from_xml_path(str(model_path.resolve()))
    open_model.opt.disableflags |= int(mujoco.mjtDisableBit.mjDSBL_CONTACT)
    gravity_model = mujoco.MjModel.from_xml_path(str(model_path.resolve()))
    gravity_model.opt.disableflags |= int(mujoco.mjtDisableBit.mjDSBL_CONTACT)
    contact_data = mujoco.MjData(contact_model)
    open_data = mujoco.MjData(open_model)
    gravity_data = mujoco.MjData(gravity_model)

    caps = {row["axis_id"]: row for row in read_csv(BODY / "current-constrained-actuation-p0.1" / "axis-current-torque-register.csv")}
    roots, joints = trajectory()
    axes = sorted(joints[next(iter(joints))])
    peak_velocity_deg_s = {
        axis: max(abs(float(row["velocity_si_s"])) for sequence in joints.values() for row in sequence[axis]) * 180.0 / math.pi
        for axis in axes if not axis.endswith("_GRIPPER")
    }
    samples: list[dict] = []
    aggregate: dict[tuple[str, str], dict[str, list[float] | int]] = {}
    sequence_contact_coverage: dict[str, int] = defaultdict(int)

    for sequence_id in sorted(roots):
        root_rows = roots[sequence_id]
        joint_rows = joints[sequence_id]
        root_position, root_velocity, root_acceleration = root_derivatives(root_rows)
        for sample_index, base_row in enumerate(root_rows):
            set_state(contact_model, contact_data, root_position[sample_index], root_velocity[sample_index], root_acceleration[sample_index], joint_rows, axes, sample_index)
            set_state(open_model, open_data, root_position[sample_index], root_velocity[sample_index], root_acceleration[sample_index], joint_rows, axes, sample_index)
            set_state(gravity_model, gravity_data, root_position[sample_index], root_velocity[sample_index], root_acceleration[sample_index], joint_rows, axes, sample_index, gravity_only=True)
            feet = active_feet(contact_model, contact_data)
            contact_ok = expected_feet(base_row["support_mode"]).issubset(feet)
            sequence_contact_coverage[sequence_id] += int(contact_ok)
            for axis in axes:
                if axis.endswith("_GRIPPER"):
                    continue
                joint_id = mujoco.mj_name2id(contact_model, mujoco.mjtObj.mjOBJ_JOINT, axis)
                dof = int(contact_model.jnt_dofadr[joint_id])
                contact_torque = float(contact_data.qfrc_inverse[dof])
                open_torque = float(open_data.qfrc_inverse[dof])
                gravity_torque = float(gravity_data.qfrc_inverse[dof])
                cap = float(caps[axis]["current_limited_linear_endpoint_nm"])
                stall_output = float(caps[axis]["published_stall_torque_nm"]) * float(caps[axis]["transmission_ratio"]) * float(caps[axis]["transmission_efficiency_assumption"])
                samples.append({
                    "sequence_id": sequence_id,
                    "sample_index": sample_index,
                    "time_s": base_row["time_s"],
                    "support_mode": base_row["support_mode"],
                    "active_floor_contacts": "+".join(sorted(feet)) or "NONE",
                    "declared_support_contact_present": str(contact_ok).upper(),
                    "axis_id": axis,
                    "region": region(axis),
                    "contact_enabled_inverse_torque_nm": f"{contact_torque:.9f}",
                    "open_chain_inverse_torque_nm": f"{open_torque:.9f}",
                    "gravity_only_torque_nm": f"{gravity_torque:.9f}",
                    "contact_contribution_nm": f"{contact_torque - open_torque:.9f}",
                    "candidate_current_endpoint_nm": f"{cap:.9f}",
                    "published_output_stall_endpoint_nm": f"{stall_output:.9f}",
                    "absolute_contact_demand_ratio": f"{abs(contact_torque) / cap:.9f}",
                    "absolute_open_chain_demand_ratio": f"{abs(open_torque) / cap:.9f}",
                    "absolute_gravity_demand_ratio": f"{abs(gravity_torque) / cap:.9f}",
                    "method_boundary": "MUJOCO CONTINUOUS INVERSE DYNAMICS AT PRESCRIBED 50 HZ STATE; SOFT CONTACT AND IDEAL PELVIS FIXTURE",
                    "warning": WARNING,
                })
                key = (sequence_id, axis)
                if key not in aggregate:
                    aggregate[key] = {"contact": [], "open": [], "gravity": [], "contact_component": [], "over": 0}
                agg = aggregate[key]
                agg["contact"].append(abs(contact_torque))
                agg["open"].append(abs(open_torque))
                agg["gravity"].append(abs(gravity_torque))
                agg["contact_component"].append(abs(contact_torque - open_torque))
                agg["over"] += int(abs(contact_torque) > cap)

    axis_summary: list[dict] = []
    for (sequence_id, axis), values in sorted(aggregate.items()):
        cap_row = caps[axis]
        cap = float(cap_row["current_limited_linear_endpoint_nm"])
        ratio = float(cap_row["transmission_ratio"])
        efficiency = float(cap_row["transmission_efficiency_assumption"])
        stall_torque = float(cap_row["published_stall_torque_nm"])
        stall_output = stall_torque * ratio * efficiency
        peak = max(values["contact"])
        peak_ratio = peak / cap
        minimum_ratio = max(ratio, DESIGN_MARGIN * peak / (cap / ratio))
        motor_no_load_speed = float(cap_row["output_no_load_speed_deg_s"]) * ratio
        output_speed_at_minimum = motor_no_load_speed / minimum_ratio
        required_current = float(cap_row["candidate_current_a"]) * peak_ratio
        state = "WITHIN CURRENT ENDPOINT"
        if peak > stall_output:
            state = "EXCEEDS PUBLISHED OUTPUT STALL ENDPOINT"
        elif peak > cap:
            state = "EXCEEDS CANDIDATE CURRENT ENDPOINT"
        axis_summary.append({
            "sequence_id": sequence_id,
            "axis_id": axis,
            "region": region(axis),
            "candidate_actuator": cap_row["actuator_model"],
            "current_transmission_ratio": f"{ratio:.3f}",
            "candidate_current_endpoint_nm": f"{cap:.6f}",
            "published_output_stall_endpoint_nm": f"{stall_output:.6f}",
            "peak_contact_inverse_torque_nm": f"{peak:.6f}",
            "p95_contact_inverse_torque_nm": f"{percentile(values['contact'], 0.95):.6f}",
            "rms_contact_inverse_torque_nm": f"{math.sqrt(sum(value * value for value in values['contact']) / len(values['contact'])):.6f}",
            "peak_open_chain_inverse_torque_nm": f"{max(values['open']):.6f}",
            "peak_gravity_only_torque_nm": f"{max(values['gravity']):.6f}",
            "peak_contact_component_nm": f"{max(values['contact_component']):.6f}",
            "peak_to_current_endpoint_ratio": f"{peak_ratio:.6f}",
            "p95_to_current_endpoint_ratio": f"{percentile(values['contact'], 0.95) / cap:.6f}",
            "fraction_over_current_endpoint": f"{values['over'] / len(values['contact']):.9f}",
            "peak_to_published_output_stall_ratio": f"{peak / stall_output:.6f}",
            "linear_current_for_peak_a": f"{required_current:.6f}",
            "minimum_ratio_for_peak_with_1_25_margin": f"{minimum_ratio:.6f}",
            "planned_peak_output_speed_deg_s": f"{peak_velocity_deg_s[axis]:.6f}",
            "no_load_output_speed_at_minimum_ratio_deg_s": f"{output_speed_at_minimum:.6f}",
            "endpoint_state": state,
            "capacity_boundary": "STALL-LINEAR CURRENT AND NO-LOAD SPEED SCREENS ARE NOT CONTINUOUS RATINGS",
            "authority": "NO PROCUREMENT, CONNECTION, POWERED TEST, MOTION OR WALKING AUTHORITY",
            "warning": WARNING,
        })

    worst_by_axis: list[dict] = []
    for axis in axes:
        if axis.endswith("_GRIPPER"):
            continue
        candidates = [row for row in axis_summary if row["axis_id"] == axis]
        worst = max(candidates, key=lambda row: float(row["peak_to_current_endpoint_ratio"]))
        worst_row = {key: value for key, value in worst.items() if key != "sequence_id"}
        worst_by_axis.append({**worst_row, "governing_sequence": worst["sequence_id"]})

    sequence_summary: list[dict] = []
    for sequence_id in sorted(roots):
        selected = [row for row in axis_summary if row["sequence_id"] == sequence_id]
        over = [row["axis_id"] for row in selected if row["endpoint_state"] != "WITHIN CURRENT ENDPOINT"]
        sequence_summary.append({
            "sequence_id": sequence_id,
            "trajectory_sample_count": len(roots[sequence_id]),
            "axis_count": len(selected),
            "declared_support_contact_coverage_fraction": f"{sequence_contact_coverage[sequence_id] / len(roots[sequence_id]):.9f}",
            "maximum_peak_to_current_endpoint_ratio": f"{max(float(row['peak_to_current_endpoint_ratio']) for row in selected):.6f}",
            "axes_exceeding_candidate_current_endpoint": "+".join(over) or "NONE",
            "axis_exceedance_count": len(over),
            "result": "CURRENT ENDPOINT GAP" if over else "WITHIN CURRENT ENDPOINT - CONTINUOUS CAPACITY STILL OPEN",
            "scope": "INVERSE-DYNAMICS DESIGN DIAGNOSTIC; NOT WALKING VALIDATION",
            "warning": WARNING,
        })

    status = {
        "identifier": IDENTIFIER,
        "warning": WARNING,
        "mujoco_version": mujoco.__version__,
        "model_mass_kg": float(contact_model.body_subtreemass[1]),
        "sequence_count": len(sequence_summary),
        "trajectory_sample_count": sum(len(rows) for rows in roots.values()),
        "rotary_axis_count": len(axes) - 2,
        "sample_axis_evidence_count": len(samples),
        "axis_sequence_summary_count": len(axis_summary),
        "whole_body_axis_summary_count": len(worst_by_axis),
        "all_values_finite": all(math.isfinite(float(row["contact_enabled_inverse_torque_nm"])) for row in samples),
        "declared_support_contacts_present": all(float(row["declared_support_contact_coverage_fraction"]) == 1.0 for row in sequence_summary),
        "maximum_peak_to_current_endpoint_ratio": max(float(row["peak_to_current_endpoint_ratio"]) for row in axis_summary),
        "axes_exceeding_candidate_current_endpoint": sorted({row["axis_id"] for row in axis_summary if row["endpoint_state"] != "WITHIN CURRENT ENDPOINT"}),
        "current_allocation_closes_inverse_demand": all(row["endpoint_state"] == "WITHIN CURRENT ENDPOINT" for row in axis_summary),
        "inverse_dynamics_establishes_continuous_capacity": False,
        "physical_execution_count": 0,
        "connection_authority": False,
        "powered_test_authority": False,
        "motion_authority": False,
        "walking_authority": False,
        "energization_authority": False,
    }
    return samples, axis_summary, worst_by_axis, sequence_summary, status


def render_page(worst_rows: list[dict], status: dict) -> str:
    max_ratio = max(float(row["peak_to_current_endpoint_ratio"]) for row in worst_rows)
    rows = []
    for row in sorted(worst_rows, key=lambda item: float(item["peak_to_current_endpoint_ratio"]), reverse=True):
        ratio = float(row["peak_to_current_endpoint_ratio"])
        width = 100.0 * ratio / max_ratio
        rows.append(f'''<tr data-region="{html.escape(row['region'])}"><td><strong>{html.escape(row['axis_id'])}</strong><br><small>{html.escape(row['governing_sequence'])}</small></td><td>{float(row['peak_contact_inverse_torque_nm']):.2f} N·m</td><td>{float(row['candidate_current_endpoint_nm']):.2f} N·m</td><td><div class="bar"><span style="width:{width:.2f}%"></span></div>{ratio:.2f}×</td><td>{float(row['minimum_ratio_for_peak_with_1_25_margin']):.2f}:1</td><td>{html.escape(row['endpoint_state'])}</td></tr>''')
    result = "GAP FOUND" if not status["current_allocation_closes_inverse_demand"] else "WITHIN ENDPOINT"
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>HR-30 whole-body torque demand</title><style>:root{{--deep:#071d36;--blue:#0b4f91;--sky:#84d8ff;--gold:#f2b91d;--paper:#eef8fe;--ink:#142a40;--line:#96cce7;--red:#b3261e}}*{{box-sizing:border-box}}body{{margin:0;background:var(--paper);color:var(--ink);font:17px/1.5 system-ui,Segoe UI,sans-serif}}header,main{{padding:28px 20px}}header{{background:var(--deep);color:white}}header>div,main{{max-width:1240px;margin:auto}}h1{{font-size:clamp(38px,6vw,68px);line-height:1.05}}h2{{font-size:clamp(27px,4vw,42px)}}.warning{{background:var(--gold);color:#15243a;border:3px solid #805600;padding:15px 18px;font-weight:900}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));gap:16px}}.card,.panel{{background:white;border:2px solid var(--line);border-radius:15px;padding:18px;margin:18px 0}}.metric{{font-size:clamp(31px,5vw,48px);font-weight:900;color:var(--blue)}}.fail{{color:var(--red)}}label,select{{font:inherit}}select{{padding:10px;border:2px solid var(--blue);border-radius:8px}}.table-wrap{{overflow-x:auto}}table{{border-collapse:collapse;width:100%;min-width:930px}}th,td{{text-align:left;padding:12px;border-bottom:1px solid var(--line);vertical-align:top;font-size:16px}}th{{background:#d9f2ff}}small{{font-size:14px}}.bar{{height:14px;min-width:130px;background:#d8e7ef;border-radius:9px;overflow:hidden}}.bar span{{display:block;height:100%;background:var(--red)}}a{{color:#075b9b;font-weight:800}}@media(max-width:700px){{body{{font-size:16px}}header,main{{padding-inline:13px}}}}</style></head><body><header><div><div class="warning">{WARNING}</div><h1>How much torque does the complete gait actually ask for?</h1><p>MuJoCo inverse dynamics evaluates every prescribed whole-body state with the current soft foot contacts and ideal pelvis fixture, then repeats it without ground contact to separate the contact-driven load from open-chain motion.</p></div></header><main><section class="grid"><article class="card"><div class="metric fail">{result}</div><p>Candidate current endpoints do not yet close the prescribed gait.</p></article><article class="card"><div class="metric">{status['maximum_peak_to_current_endpoint_ratio']:.2f}×</div><p>Worst peak demand divided by the current-limited linear endpoint.</p></article><article class="card"><div class="metric">{len(status['axes_exceeding_candidate_current_endpoint'])}</div><p>Unique rotary axes above a candidate endpoint in at least one sequence.</p></article></section><section class="panel"><h2>Whole-body axis envelope</h2><p><label for="region"><strong>Show:</strong></label> <select id="region"><option value="ALL">All regions</option><option value="LEG">Legs</option><option value="ARM/HAND">Arms and hands</option><option value="HEAD/WAIST">Head and waist</option></select></p><div class="table-wrap"><table><thead><tr><th>Axis</th><th>Peak inverse demand</th><th>Current endpoint</th><th>Demand ratio</th><th>1.25× sizing ratio</th><th>Finding</th></tr></thead><tbody>{''.join(rows)}</tbody></table></div></section><section class="panel"><h2>What this changes</h2><p>The derived ratio is a sizing direction, not a released transmission. It must be reconciled with packaging, belt capacity, backlash, reflected inertia, output speed, motor torque-speed behavior, efficiency, electrical current and heat. The contact-enabled inverse is also specific to MuJoCo's soft-contact and ideal-fixture assumptions.</p></section><section class="panel"><h2>Evidence downloads</h2><p><a href="whole-body-axis-demand.csv">23-axis envelope</a> · <a href="axis-demand-summary.csv">both sequence results</a> · <a href="inverse-dynamics-samples.csv">all 24,702 rotary-axis samples</a> · <a href="sequence-demand-summary.csv">sequence summary</a> · <a href="runtime-provenance.json">method provenance</a> · <a href="open-holds.csv">open holds</a></p></section></main><script>const select=document.getElementById('region');select.addEventListener('change',()=>{{document.querySelectorAll('tbody tr').forEach(row=>{{row.hidden=select.value!=='ALL'&&row.dataset.region!==select.value}})}});</script></body></html>'''


def write_manifest() -> None:
    rows = []
    for path in sorted(OUT.iterdir(), key=lambda item: item.name):
        if path.is_file() and path.name != "file-manifest.csv":
            rows.append({"file": path.name, "sha256": sha(path), "bytes": path.stat().st_size, "warning": WARNING})
    write_csv(OUT / "file-manifest.csv", rows)


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    samples, axis_summary, worst_rows, sequence_summary, status = analyze()
    write_csv(OUT / "inverse-dynamics-samples.csv", samples)
    write_csv(OUT / "axis-demand-summary.csv", axis_summary)
    write_csv(OUT / "whole-body-axis-demand.csv", worst_rows)
    write_csv(OUT / "sequence-demand-summary.csv", sequence_summary)
    sources = []
    for role, path in (
        ("ideal-fixture MJCF", DYN / "hr30_tether_ideal_fixture.xml"),
        ("trajectory samples", KIN / "trajectory-samples.csv"),
        ("joint trajectory", KIN / "joint-trajectory.csv"),
        ("current endpoint register", BODY / "current-constrained-actuation-p0.1" / "axis-current-torque-register.csv"),
        ("mass reconciliation", BODY / "mass-reconciliation-summary.json"),
        ("generator", Path(__file__)),
    ):
        sources.append({"role": role, "path": path.relative_to(ROOT).as_posix(), "sha256": sha(path), "state": "BOUND", "warning": WARNING})
    write_csv(OUT / "source-binding.csv", sources)
    holds = [
        ("TD-H01", "inverse demand depends on the ideal pelvis fixture and the current MuJoCo soft-contact parameterization"),
        ("TD-H02", "the linear current/stall interpolation is not a continuous torque or thermal rating"),
        ("TD-H03", "the 1.25 sizing ratio is a development screen, not a selected pulley or released transmission"),
        ("TD-H04", "motor torque-speed curves, voltage sag, regeneration, driver limits and winding/case temperature remain unvalidated"),
        ("TD-H05", "belt tooth load, bearing reactions, shaft deflection, backlash, reflected inertia and packaging require exact redesign"),
        ("TD-H06", "sole friction/compliance and measured mass/inertia have not been correlated to hardware"),
        ("TD-H07", "free balance, disturbance recovery, fall restraint and stopping behavior remain unvalidated"),
        ("TD-H08", "qualified dynamics review and guarded physical correlation remain unexecuted"),
    ]
    write_csv(OUT / "open-holds.csv", [{"hold_id": key, "unresolved": value, "state": "OPEN", "authority": "BLOCKS HARDWARE MOTION AND WALKING", "warning": WARNING} for key, value in holds])
    provenance = {
        "identifier": IDENTIFIER,
        "warning": WARNING,
        "executed_utc": datetime.now(timezone.utc).isoformat(),
        "mujoco_version": mujoco.__version__,
        "numpy_version": np.__version__,
        "trajectory_interval_s": DT,
        "root_derivative_method": "numpy.gradient, second-order edge stencil, applied twice to 50 Hz root positions",
        "inverse_inputs": "qpos, qvel, qacc, mocap_pos and mocap_quat at each prescribed trajectory sample",
        "contact_case": "current soft foot/floor contact plus ideal pelvis weld fixture",
        "open_chain_case": "same state and fixture with mjDSBL_CONTACT",
        "gravity_case": "same pose with zero qvel/qacc and mjDSBL_CONTACT",
        "design_margin": DESIGN_MARGIN,
        "official_method_source": "https://mujoco.readthedocs.io/en/stable/programming/simulation.html#inverse-dynamics",
        "official_method_source_accessed": "2026-08-17",
    }
    (OUT / "runtime-provenance.json").write_text(json.dumps(provenance, indent=2) + "\n", encoding="utf-8")
    (OUT / "torque-demand-status.json").write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8")
    readme = f"""# HR-30 whole-body torque demand P0.1

**{WARNING}**

This package converts the two complete 50 Hz walking references into an inverse-dynamics torque-demand envelope for all 23 rotary axes. It reports the contact-enabled, open-chain and gravity-only cases separately and compares them with the existing candidate current endpoint and published stall-output screens.

The result is a design input, not motion approval. MuJoCo's inverse result is model-specific, the pelvis is held by an ideal numerical fixture, contacts are soft, and neither current endpoint nor published stall torque is a continuous-duty rating.
"""
    (OUT / "README.md").write_text(readme, encoding="utf-8", newline="\n")
    (OUT / "index.html").write_text(render_page(worst_rows, status), encoding="utf-8", newline="\n")
    shutil.copy2(__file__, OUT / "torque-demand-source.py")
    write_manifest()
    if REL.exists():
        shutil.rmtree(REL)
    shutil.copytree(OUT, REL)

    start, end = "<!-- HR30-TORQUE-DEMAND-P01-START -->", "<!-- HR30-TORQUE-DEMAND-P01-END -->"
    body_readme_path = BODY / "README.md"
    body_readme = body_readme_path.read_text(encoding="utf-8")
    block = f"""{start}
## Whole-body inverse-dynamics demand

The [interactive torque-demand guide](torque-demand-p0.1/index.html) evaluates all 23 rotary axes over both bilateral 50 Hz sequences with contact-enabled, open-chain and gravity-only inverse dynamics. It records the actual endpoint gap and produces sizing directions without releasing a transmission or claiming continuous capacity.
{end}"""
    if start in body_readme and end in body_readme:
        body_readme = body_readme[:body_readme.index(start)] + block + body_readme[body_readme.index(end) + len(end):]
    else:
        body_readme = body_readme.rstrip() + "\n\n" + block + "\n"
    body_readme_path.write_text(body_readme, encoding="utf-8", newline="\n")

    page_path = BODY / "index.html"
    page = page_path.read_text(encoding="utf-8")
    section = f'''{start}<section id="torque-demand"><h2>The gait now has a whole-body torque-demand envelope</h2><div class="grid"><article class="card hold"><div class="metric">{status['maximum_peak_to_current_endpoint_ratio']:.2f}×</div><p>Worst inverse-dynamics demand relative to the current-limited linear endpoint.</p></article><article class="card hold"><div class="metric">{len(status['axes_exceeding_candidate_current_endpoint'])}</div><p>Rotary axes with a candidate endpoint gap.</p></article><article class="card"><h3>Three demand cases</h3><p>Contact-enabled, open-chain and gravity-only loads are kept separate.</p></article></div><p><a href="torque-demand-p0.1/index.html">Open the interactive whole-body torque-demand guide</a>. These are design diagnostics, not continuous ratings or walking authority.</p></section>{end}'''
    if start in page and end in page:
        page = page[:page.index(start)] + section + page[page.index(end) + len(end):]
    else:
        page = page.replace("</main>", section + "</main>")
    page_path.write_text(page, encoding="utf-8", newline="\n")

    package_status_path = BODY / "package-status.json"
    package_status = json.loads(package_status_path.read_text(encoding="utf-8"))
    package_status.update({
        "whole_body_torque_demand_present": True,
        "inverse_dynamics_sequence_count": status["sequence_count"],
        "inverse_dynamics_axis_sample_count": status["sample_axis_evidence_count"],
        "current_allocation_closes_inverse_demand": status["current_allocation_closes_inverse_demand"],
        "continuous_actuator_capacity_validated": False,
        "walking_sequence_physically_validated": False,
    })
    package_status_path.write_text(json.dumps(package_status, indent=2) + "\n", encoding="utf-8")
    system.refresh_manifest_and_release()
    print(json.dumps(status, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
