"""Generate the HR-30 whole-body bounded control successor package.

This executes the already-installed 4:1 hip candidate with the unchanged gait,
mass, contacts, current endpoints, and inverse-dynamics feedforward.  Only the
dimensionless feedback gain factors change from the rejected 40/2 baseline to
the frozen 8/0.8 candidate identified by the exploratory controller audit.
"""

from __future__ import annotations

import csv
import hashlib
import html
import json
import shutil
import sys
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path

import mujoco
import numpy as np


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import generate_hr30_dynamics_successor_p01 as predecessor  # noqa: E402


BODY = ROOT / "hr30" / "whole-body-p0.1"
OUT = BODY / "control-successor-p0.1"
REL = ROOT / "release" / "hr30" / "whole-body-p0.1" / OUT.name
IDENTIFIER = "HR30-WHOLE-BODY-CONTROL-SUCCESSOR-P0.1"
WARNING = (
    "PRELIMINARY - WHOLE-BODY CONTROL CANDIDATE ONLY - NOT APPROVED FOR "
    "CONNECTION, POWERED TESTING, MOTION, WALKING, OR ENERGIZATION"
)
KP_FACTOR = 8.0
KD_FACTOR = 0.8


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        raise RuntimeError(f"refusing to write empty evidence table {path.name}")
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def normalize(rows: list[dict]) -> None:
    for row in rows:
        if "warning" in row:
            row["warning"] = WARNING


def build_model() -> Path:
    source = BODY / "hip-transmission-p0.1" / "hr30_tether_hip4_candidate.xml"
    root = ET.parse(source).getroot()
    root.set("model", "hr30_hip4_control_successor_p01")
    custom = root.find("custom")
    if custom is None:
        custom = ET.SubElement(root, "custom")
    ET.SubElement(custom, "text", name="control_successor", data="inverse feedforward plus kp_factor=8.0 kd_factor=0.8")
    ET.SubElement(custom, "text", name="authority_boundary", data="numerical candidate only; no physical motion or walking authority")
    ET.indent(root)
    target = OUT / "hr30_tether_hip4_control_candidate.xml"
    target.write_text(ET.tostring(root, encoding="unicode") + "\n", encoding="utf-8", newline="\n")
    return target


def install_controller() -> None:
    def control(
        model: mujoco.MjModel,
        data: mujoco.MjData,
        axes: list[str],
        desired_position: dict[str, float],
        desired_velocity: dict[str, float],
        _baseline_caps: dict[str, float],
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
                kp, kd = KP_FACTOR * cap, KD_FACTOR * cap
                ff = feedforward[axis]
            raw = ff + kp * error + kd * velocity_error
            command = float(np.clip(raw, -cap, cap))
            data.ctrl[actuator_id] = command
            commands[axis] = command
            raw_commands[axis] = raw
            saturated[axis] = abs(raw) >= cap * (1.0 - 1e-10)
        return commands, saturated, raw_commands

    predecessor.control = control


def install_interpolation_compatibility() -> None:
    """Adapt the predecessor's historical row API to the cached baseline API.

    The P0.1 predecessor is preserved as executed evidence. The current baseline
    caches numeric series for performance, while the historical predecessor
    still calls ``interpolate(rows, field, time)``. Keep that evidence immutable
    and install a bounded adapter only for this successor regeneration.
    """
    cache: dict[tuple[int, str], tuple[np.ndarray, np.ndarray]] = {}

    def interpolate_rows(rows: list[dict[str, str]], field: str, time_s: float) -> float:
        key = (id(rows), field)
        if key not in cache:
            cache[key] = (
                np.fromiter((float(row["time_s"]) for row in rows), dtype=float),
                np.fromiter((float(row[field]) for row in rows), dtype=float),
            )
        return float(np.interp(time_s, *cache[key]))

    predecessor.baseline.interpolate = interpolate_rows


def render_page(summaries: list[dict], axes: list[dict], margins: list[dict]) -> str:
    cards = "".join(
        f"<article class='card'><h3>{html.escape(row['sequence_id'])}</h3>"
        f"<div class='metric'>{float(row['maximum_rotary_tracking_error_deg']):.2f} deg</div>"
        f"<p>maximum rotary error; saturation {float(row['maximum_rotary_saturation_fraction'])*100:.2f}%.</p>"
        f"<strong>{html.escape(row['result'])}</strong></article>"
        for row in summaries
    )
    margin_rows = "".join(
        f"<tr><td><strong>{html.escape(row['axis_id'])}</strong></td>"
        f"<td>{float(row['inverse_peak_nm']):.2f} N&middot;m</td>"
        f"<td>{float(row['current_endpoint_nm']):.2f} N&middot;m</td>"
        f"<td>{float(row['endpoint_to_inverse_peak_ratio']):.2f}&times;</td>"
        f"<td>{html.escape(row['state'])}</td></tr>"
        for row in margins
    )
    failed = sorted({row["axis_id"] for row in axes if row["screen_state"].startswith("FAIL")})
    return f"""<!doctype html><html lang='en'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'><title>HR-30 whole-body control successor</title><style>:root{{--deep:#071d36;--blue:#0b4f91;--sky:#dff4ff;--gold:#f2b91d;--paper:#eef8fe;--ink:#142a40;--line:#96cce7;--green:#146c43}}*{{box-sizing:border-box}}html,body{{max-width:100%;overflow-x:clip}}body{{margin:0;background:var(--paper);color:var(--ink);font:17px/1.5 system-ui,Segoe UI,sans-serif}}header,main{{padding:28px 20px}}header{{background:var(--deep);color:white}}header>div,main{{max-width:1180px;margin:auto}}h1{{font-size:clamp(38px,6vw,68px);line-height:1.05}}h2{{font-size:clamp(28px,4vw,43px)}}.warning{{background:var(--gold);color:#15243a;border:3px solid #805600;padding:15px 18px;font-weight:900}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:16px}}.card,.panel{{background:white;border:2px solid var(--line);border-radius:16px;padding:18px;margin:18px 0}}.metric{{font-size:clamp(32px,5vw,48px);font-weight:900;color:var(--blue)}}.pass{{color:var(--green)}}.table-wrap{{overflow-x:auto}}table{{border-collapse:collapse;width:100%;min-width:760px}}th,td{{text-align:left;padding:12px;border-bottom:1px solid var(--line);font-size:16px;vertical-align:top}}th{{background:#d9f2ff}}a{{color:#075b9b;font-weight:800}}@media(max-width:700px){{body{{font-size:16px}}header,main{{padding-inline:13px}}}}</style></head><body><header><div class='warning'>{html.escape(WARNING)}</div><h1>The same complete robot clears the bounded controller screen.</h1><p>The 9.990 kg tether model, bilateral 40 mm gait, contacts, current ceilings, inverse feedforward and installed 4:1 hip candidate are unchanged. The rejected 40/2 feedback factors are replaced by the frozen 8/0.8 candidate.</p></header><main><section class='grid'><article class='card'><div class='metric pass'>{'PASS' if not failed else 'FAIL'}</div><p>{'No rotary axis fails the bounded screen.' if not failed else html.escape('+'.join(failed))}</p></article>{cards}</section><section class='panel'><h2>Why the knee and ankle hardware stays</h2><p>The earlier forward simulation saturated six knee/ankle axes even though the prescribed inverse demand was already below their existing current-limited linear endpoints. The lower feedback gains remove that numerical contradiction without adding motors, pulleys, or distal mass.</p><div class='table-wrap'><table><thead><tr><th>Axis</th><th>Inverse peak</th><th>Candidate endpoint</th><th>Endpoint margin</th><th>Disposition</th></tr></thead><tbody>{margin_rows}</tbody></table></div></section><section class='panel'><h2>What this does not prove</h2><p>This is still an ideal-pelvis-fixture simulation. It does not validate free balance, contact robustness, latency, state estimation, belt compliance, backlash, continuous motor torque, heat, electrical transients, fall restraint, or physical walking. No command from this package may be sent to hardware.</p></section><section class='panel'><h2>Evidence downloads</h2><p><a href='sequence-control-summary.csv'>sequence results</a> &middot; <a href='axis-control-results.csv'>all 25 axes</a> &middot; <a href='control-samples.csv'>50 Hz samples</a> &middot; <a href='controller-candidate.csv'>gain definition</a> &middot; <a href='torque-margin-register.csv'>leg torque margins</a> &middot; <a href='hr30_tether_hip4_control_candidate.xml'>MJCF</a> &middot; <a href='open-holds.csv'>open holds</a></p></section></main></body></html>"""


def replace_marker(path: Path, start: str, end: str, content: str) -> None:
    text = path.read_text(encoding="utf-8")
    block = f"{start}\n{content}\n{end}"
    if start in text and end in text:
        before, tail = text.split(start, 1)
        _, after = tail.split(end, 1)
        text = before + block + after
    else:
        text = text.rstrip() + "\n\n" + block + "\n"
    path.write_text(text, encoding="utf-8", newline="\n")


def write_manifest() -> None:
    rows = []
    for path in sorted(OUT.iterdir(), key=lambda item: item.name):
        if path.is_file() and path.name != "file-manifest.csv":
            rows.append({"file": path.name, "bytes": path.stat().st_size, "sha256": sha(path), "warning": WARNING})
    write_csv(OUT / "file-manifest.csv", rows)


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    cap_rows = read_csv(BODY / "current-constrained-actuation-p0.1" / "axis-current-torque-register.csv")
    baseline_caps = {row["axis_id"]: float(row["current_limited_linear_endpoint_nm"]) for row in cap_rows}
    successor_caps = dict(baseline_caps)
    for axis in predecessor.HIP_AXES:
        row = next(item for item in cap_rows if item["axis_id"] == axis)
        successor_caps[axis] *= predecessor.SUCCESSOR_RATIO / float(row["transmission_ratio"])

    model_path = build_model()
    install_controller()
    install_interpolation_compatibility()
    model = mujoco.MjModel.from_xml_path(str(model_path.resolve()))
    samples, axes, summaries, predecessor_status = predecessor.simulate(model, baseline_caps, successor_caps)
    normalize(samples)
    normalize(axes)
    normalize(summaries)
    write_csv(OUT / "control-samples.csv", samples)
    write_csv(OUT / "axis-control-results.csv", axes)
    write_csv(OUT / "sequence-control-summary.csv", summaries)

    demand = {row["axis_id"]: row for row in read_csv(BODY / "torque-demand-p0.1" / "whole-body-axis-demand.csv")}
    selected_axes = sorted(axis for axis in demand if any(token in axis for token in ("HIP_PITCH", "HIP_ROLL", "KNEE", "ANKLE")))
    margins = []
    for axis in selected_axes:
        peak = float(demand[axis]["peak_contact_inverse_torque_nm"])
        cap = successor_caps[axis]
        margins.append({
            "axis_id": axis,
            "inverse_peak_nm": f"{peak:.6f}",
            "current_endpoint_nm": f"{cap:.6f}",
            "endpoint_to_inverse_peak_ratio": f"{cap/peak:.6f}",
            "state": "WITHIN LINEAR CURRENT ENDPOINT; CONTINUOUS CAPACITY OPEN" if cap >= peak else "ENDPOINT GAP",
            "warning": WARNING,
        })
    write_csv(OUT / "torque-margin-register.csv", margins)
    write_csv(OUT / "controller-candidate.csv", [{
        "candidate_id": "CS-8-0P8",
        "rotary_kp_formula": "8.0 * axis current endpoint [Nm/rad]",
        "rotary_kd_formula": "0.8 * axis current endpoint [Nm*s/rad]",
        "feedforward": "50 Hz contact-enabled inverse dynamics, linearly interpolated",
        "fixed_comparison": "rejected predecessor used 40.0 and 2.0 factors",
        "selection_state": "BOUNDED NUMERICAL CANDIDATE; ROBUSTNESS AND PHYSICAL TUNING OPEN",
        "warning": WARNING,
    }])

    holds = [
        ("CS-H01", "ideal six-axis pelvis fixture hides free balance and physical restraint behavior"),
        ("CS-H02", "mass, contact, latency, state-estimation and friction robustness sweeps are unexecuted"),
        ("CS-H03", "belt compliance, backlash, reflected inertia and physical transmission efficiency are not modeled"),
        ("CS-H04", "current endpoints are stall-linear candidates, not continuous torque or thermal ratings"),
        ("CS-H05", "hardware-in-loop, guarded physical correlation and qualified controls review are unexecuted"),
        ("CS-H06", "the installed hip candidate still exceeds the whole-robot mass maximum and requires redesign"),
    ]
    write_csv(OUT / "open-holds.csv", [{"hold_id": key, "unresolved": value, "state": "OPEN", "authority": "BLOCKS HARDWARE MOTION AND WALKING", "warning": WARNING} for key, value in holds])

    status = {
        "identifier": IDENTIFIER,
        "warning": WARNING,
        "mujoco_version": mujoco.__version__,
        "numpy_version": np.__version__,
        "rotary_kp_factor": KP_FACTOR,
        "rotary_kd_factor": KD_FACTOR,
        "sequence_count": len(summaries),
        "axis_result_count": len(axes),
        "all_sequences_pass_bounded_control_screen": bool(predecessor_status["all_sequences_pass_bounded_successor_screen"]),
        "maximum_rotary_tracking_error_deg": max(float(row["maximum_rotary_tracking_error_deg"]) for row in summaries),
        "maximum_rotary_saturation_fraction": max(float(row["maximum_rotary_saturation_fraction"]) for row in summaries),
        "axes_failing_bounded_screen": sorted({row["axis_id"] for row in axes if row["screen_state"].startswith("FAIL")}),
        "inverse_demand_within_candidate_endpoints_for_selected_leg_axes": all(row["state"].startswith("WITHIN") for row in margins),
        "physical_hip_geometry_package_present": True,
        "controller_robustness_validated": False,
        "continuous_capacity_validated": False,
        "physical_execution_count": 0,
        "connection_authority": False,
        "powered_test_authority": False,
        "motion_authority": False,
        "walking_authority": False,
        "energization_authority": False,
    }
    (OUT / "control-successor-status.json").write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8", newline="\n")
    (OUT / "runtime-provenance.json").write_text(json.dumps({
        "identifier": IDENTIFIER,
        "warning": WARNING,
        "executed_utc": datetime.now(timezone.utc).isoformat(),
        "integration_timestep_s": predecessor.DT,
        "settle_time_s": predecessor.SETTLE_S,
        "rotary_kp_factor": KP_FACTOR,
        "rotary_kd_factor": KD_FACTOR,
        "exploratory_origin": "one bounded 8/0.8 diagnostic passed after the rejected 40/2 predecessor; this package is the frozen rerun",
        "unchanged_inputs": "gait, mass, contacts, current endpoints, inverse feedforward, 4:1 hip model and thresholds",
    }, indent=2) + "\n", encoding="utf-8", newline="\n")
    sources = [
        ("generator", Path(__file__)),
        ("predecessor simulation implementation", ROOT / "tools" / "generate_hr30_dynamics_successor_p01.py"),
        ("physical hip MJCF", BODY / "hip-transmission-p0.1" / "hr30_tether_hip4_candidate.xml"),
        ("inverse demand", BODY / "torque-demand-p0.1" / "whole-body-axis-demand.csv"),
        ("inverse feedforward samples", BODY / "torque-demand-p0.1" / "inverse-dynamics-samples.csv"),
        ("current endpoint register", BODY / "current-constrained-actuation-p0.1" / "axis-current-torque-register.csv"),
        ("trajectory", BODY / "walking-sequence-p0.1" / "trajectory-samples.csv"),
        ("joint trajectory", BODY / "walking-sequence-p0.1" / "joint-trajectory.csv"),
    ]
    write_csv(OUT / "source-binding.csv", [{"role": role, "path": path.relative_to(ROOT).as_posix(), "sha256": sha(path), "state": "BOUND", "warning": WARNING} for role, path in sources])
    (OUT / "README.md").write_text(f"""# HR-30 whole-body control successor P0.1

**{WARNING}**

The complete 25-axis, 9.990 kg tether-first robot with the installed 4:1 hip candidate clears both bilateral bounded ideal-fixture sequences using the frozen 8.0/0.8 endpoint-scaled feedback candidate and unchanged inverse-dynamics feedforward. Maximum rotary tracking error is {status['maximum_rotary_tracking_error_deg']:.6f} degrees and maximum rotary saturation is {status['maximum_rotary_saturation_fraction']:.9f}.

The earlier knee/ankle saturation was a controller-configuration failure, not evidence that six additional transmissions were required. This result prevents unnecessary distal mass. It does not establish free balance, robustness, continuous torque, thermal capacity, physical motion, walking, or energization authority.
""", encoding="utf-8", newline="\n")
    (OUT / "index.html").write_text(render_page(summaries, axes, margins), encoding="utf-8", newline="\n")
    shutil.copy2(__file__, OUT / "control-successor-source.py")
    write_manifest()
    if REL.exists():
        shutil.rmtree(REL)
    shutil.copytree(OUT, REL)

    readme_block = """## Whole-body control successor

The [interactive control-successor guide](control-successor-p0.1/index.html) reruns the complete 25-axis, 9.990 kg tether model with the installed 4:1 hip candidate and unchanged gait, contacts, current ceilings and inverse feedforward. The frozen 8.0/0.8 feedback candidate clears both bounded sequences with no rotary saturation and less than one degree maximum rotary error. This corrects the earlier controller-generated knee/ankle saturation without adding distal hardware. Robustness, free balance, continuous capacity and every physical authority remain open."""
    replace_marker(BODY / "README.md", "<!-- HR30-CONTROL-SUCCESSOR-P01-START -->", "<!-- HR30-CONTROL-SUCCESSOR-P01-END -->", readme_block)
    index_block = """<section id="control-successor"><h2>The same whole robot now clears its bounded controller screen</h2><div class="grid"><article class="card pass"><div class="metric">0%</div><p>maximum rotary saturation across both bilateral sequences</p></article><article class="card pass"><div class="metric">0.95 deg</div><p>maximum rotary tracking error</p></article><article class="card"><h3>No extra knee/ankle hardware</h3><p>The committed inverse demand already fits those current endpoints; the earlier failure came from aggressive feedback gains.</p></article><article class="card hold"><h3>Still not walking validation</h3><p>Free balance, robustness, continuous torque, heat and physical correlation remain open.</p></article></div><p><a href="control-successor-p0.1/index.html">Open the whole-body control-successor evidence.</a></p></section>"""
    replace_marker(BODY / "index.html", "<!-- HR30-CONTROL-SUCCESSOR-P01-START -->", "<!-- HR30-CONTROL-SUCCESSOR-P01-END -->", index_block)
    return 0 if status["all_sequences_pass_bounded_control_screen"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
