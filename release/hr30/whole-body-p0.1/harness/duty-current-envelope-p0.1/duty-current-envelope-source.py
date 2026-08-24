"""Generate bounded HR-30 harness current-duty evidence from whole-body control traces.

The result is a torque-producing current-equivalent screen.  It intentionally
excludes actuator electronics/idle current, driver loss, active object grip,
regeneration, supply transients and physical thermal behavior, so it cannot be
used as a conductor, connector, fuse or source rating.
"""

from __future__ import annotations

import csv
import hashlib
import html
import json
import math
import shutil
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

import mujoco
import numpy as np


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import generate_hr30_control_successor_p01 as control_successor  # noqa: E402
import generate_hr30_dynamics_successor_p01 as dynamics_successor  # noqa: E402


BODY = ROOT / "hr30" / "whole-body-p0.1"
HARNESS = BODY / "harness"
OUT = HARNESS / "duty-current-envelope-p0.1"
REL = ROOT / "release" / "hr30" / "whole-body-p0.1" / "harness" / OUT.name
IDENTIFIER = "HR30-HARNESS-DUTY-CURRENT-ENVELOPE-P0.1"
WARNING = (
    "PRELIMINARY - BOUNDED TORQUE-PRODUCING CURRENT-EQUIVALENT EVIDENCE ONLY - "
    "NOT A WIRE, CONNECTOR, PROTECTION OR SOURCE RATING - NOT APPROVED FOR "
    "PROCUREMENT, CONNECTION, POWERED TESTING, MOTION, WALKING OR ENERGIZATION"
)
LOG_PERIOD_S = 0.02
GRIPPER_PINION_RADIUS_M = 0.005
GRIPPER_GAP_TO_PINION_FACTOR = 2.0


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        raise RuntimeError(f"refusing to write empty evidence table: {path}")
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def replace_marker(path: Path, start: str, end: str, content: str) -> None:
    text = path.read_text(encoding="utf-8")
    block = f"{start}\n{content}\n{end}"
    if start in text and end in text:
        before, tail = text.split(start, 1)
        _, after = tail.split(end, 1)
        text = before.rstrip() + after
    if path.suffix.lower() == ".html":
        if "</main>" not in text:
            raise RuntimeError(f"cannot insert generated section before </main>: {path}")
        before, after = text.rsplit("</main>", 1)
        text = before.rstrip() + "\n\n" + block + "\n</main>" + after
    else:
        text = text.rstrip() + "\n\n" + block + "\n"
    path.write_text(text, encoding="utf-8", newline="\n")


def stats(values: list[float]) -> tuple[float, float, float, float]:
    vector = np.asarray(values, dtype=float)
    return (
        float(np.max(vector)),
        float(np.percentile(vector, 95)),
        float(np.sqrt(np.mean(np.square(vector)))),
        float(np.mean(vector)),
    )


def build_trace() -> tuple[list[dict], list[dict], list[dict], dict[str, float], dict[str, float], float]:
    current_rows = read_csv(BODY / "current-constrained-actuation-p0.1" / "axis-current-torque-register.csv")
    baseline_caps = {row["axis_id"]: float(row["current_limited_linear_endpoint_nm"]) for row in current_rows}
    successor_caps = dict(baseline_caps)
    for axis in dynamics_successor.HIP_AXES:
        row = next(item for item in current_rows if item["axis_id"] == axis)
        successor_caps[axis] *= dynamics_successor.SUCCESSOR_RATIO / float(row["transmission_ratio"])

    source_model = BODY / "mujoco-dynamics-validation-p0.1" / "hr30_tether_ideal_fixture.xml"
    model = mujoco.MjModel.from_xml_path(str(source_model.resolve()))
    control_successor.install_controller()
    installed_control = dynamics_successor.control
    command_calls: list[dict[str, float]] = []

    def recording_control(*args, **kwargs):
        commands, saturated, raw = installed_control(*args, **kwargs)
        command_calls.append(dict(commands))
        return commands, saturated, raw

    dynamics_successor.control = recording_control
    try:
        _samples, axis_results, summaries, simulation_status = dynamics_successor.simulate(
            model, baseline_caps, successor_caps
        )
    finally:
        dynamics_successor.control = installed_control

    settle_calls_per_sequence = round(dynamics_successor.SETTLE_S / dynamics_successor.DT)
    expected_calls = sum(int(row["integration_step_count"]) for row in summaries) + len(summaries) * settle_calls_per_sequence
    if len(command_calls) != expected_calls:
        raise RuntimeError(f"control-call mismatch: {len(command_calls)} != {expected_calls}")
    return command_calls, axis_results, summaries, baseline_caps, successor_caps, float(np.sum(model.body_mass))


def render_page(axis_rows: list[dict], bus_rows: list[dict], whole_rows: list[dict]) -> str:
    aggregate = [row for row in bus_rows if row["sequence_id"] == "ALL-BOUND-TRACES"]
    worst_peak = max(aggregate, key=lambda row: float(row["peak_current_equivalent_a"]))
    worst_rms = max(aggregate, key=lambda row: float(row["rms_current_equivalent_a"]))
    bus_table = "".join(
        f"<tr><td><strong>{html.escape(row['bus_id'])}</strong></td>"
        f"<td>{float(row['peak_current_equivalent_a']):.3f} A</td>"
        f"<td>{float(row['p95_current_equivalent_a']):.3f} A</td>"
        f"<td>{float(row['rms_current_equivalent_a']):.3f} A</td>"
        f"<td>{float(row['candidate_internal_cap_sum_a']):.3f} A</td></tr>"
        for row in aggregate
    )
    gripper_rows = [row for row in axis_rows if row["axis_id"].endswith("_GRIPPER")]
    return f"""<!doctype html><html lang='en'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'><title>HR-30 harness duty-current envelope</title><style>:root{{--deep:#071d36;--blue:#0b4f91;--sky:#dff4ff;--gold:#f2b91d;--paper:#eef8fe;--ink:#142a40;--line:#96cce7;--green:#146c43}}*{{box-sizing:border-box}}html,body{{max-width:100%;overflow-x:clip}}body{{margin:0;background:var(--paper);color:var(--ink);font:17px/1.5 system-ui,Segoe UI,sans-serif}}header,main{{padding:28px 20px}}header{{background:var(--deep);color:white}}header>div,main{{max-width:1180px;margin:auto}}h1{{font-size:clamp(38px,6vw,68px);line-height:1.05}}h2{{font-size:clamp(28px,4vw,43px)}}.warning{{background:var(--gold);color:#15243a;border:3px solid #805600;padding:15px 18px;font-weight:900}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:16px}}.card,.panel{{background:white;border:2px solid var(--line);border-radius:16px;padding:18px;margin:18px 0}}.metric{{font-size:clamp(32px,5vw,48px);font-weight:900;color:var(--blue)}}.table-wrap{{overflow-x:auto}}table{{border-collapse:collapse;width:100%;min-width:760px}}th,td{{text-align:left;padding:12px;border-bottom:1px solid var(--line);font-size:16px;vertical-align:top}}th{{background:#d9f2ff}}a{{color:#075b9b;font-weight:800}}@media(max-width:700px){{body{{font-size:16px}}header,main{{padding-inline:13px}}}}</style></head><body><header><div class='warning'>{html.escape(WARNING)}</div><h1>The whole-body traces now supply a bounded harness duty envelope.</h1><p>All 25 commanded axes are mapped at 50 Hz into torque-producing current equivalents. This closes a missing calculation input; it does not select a wire, connector, fuse, eFuse, source or thermal rating.</p></header><main><section class='grid'><article class='card'><div class='metric'>{html.escape(worst_peak['bus_id'])}</div><p>largest bounded bus peak: {float(worst_peak['peak_current_equivalent_a']):.3f} A.</p></article><article class='card'><div class='metric'>{html.escape(worst_rms['bus_id'])}</div><p>largest bounded bus RMS: {float(worst_rms['rms_current_equivalent_a']):.3f} A.</p></article><article class='card'><div class='metric'>{float(whole_rows[-1]['rms_current_equivalent_a']):.3f} A</div><p>pooled whole-body torque-producing RMS across both prescribed sequences.</p></article><article class='card'><div class='metric'>{len(gripper_rows)}</div><p>gripper sequence envelopes use an explicit virtual-work map; active object gripping remains excluded.</p></article></section><section class='panel'><h2>Eight bus envelopes</h2><div class='table-wrap'><table><thead><tr><th>Bus</th><th>Peak</th><th>P95</th><th>RMS</th><th>Internal-cap sum</th></tr></thead><tbody>{bus_table}</tbody></table></div></section><section class='panel'><h2>Deliberate boundary</h2><p>These values include commanded torque or generalized gripper-hold force only. Actuator logic/idle current, driver loss, bus transients, inrush, active grip force, regeneration, stalled/fault states, free-balance corrections, environmental variation and as-built efficiency are absent. Therefore this package cannot release conductors or protection. It supplies a reproducible bounded duty case for later thermal and fault tests.</p></section><section class='panel'><h2>Evidence</h2><p><a href='axis-current-duty-envelope.csv'>axis envelopes</a> &middot; <a href='bus-current-duty-envelope.csv'>bus envelopes</a> &middot; <a href='whole-body-current-duty-envelope.csv'>whole-body envelope</a> &middot; <a href='current-equivalent-samples.csv'>50 Hz axis samples</a> &middot; <a href='open-holds.csv'>open holds</a></p></section></main></body></html>"""


def main() -> int:
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)

    bus_bindings = read_csv(BODY / "actuator-bus-axis-binding.csv")
    current_rows = read_csv(BODY / "current-constrained-actuation-p0.1" / "axis-current-torque-register.csv")
    current_by_axis = {row["axis_id"]: row for row in current_rows}
    bus_by_axis = {row["axis_id"]: row["bus_id"] for row in bus_bindings}
    bus_budget = {row["bus_id"]: row for row in read_csv(BODY / "current-constrained-actuation-p0.1" / "bus-current-budget.csv")}
    axes = sorted(bus_by_axis)
    if len(axes) != 25 or set(axes) != set(current_by_axis):
        raise RuntimeError("the 25-axis bus/current allocation is not one-to-one")

    command_calls, axis_results, summaries, _baseline_caps, successor_caps, model_mass_kg = build_trace()
    sample_rows: list[dict] = []
    bus_samples: dict[tuple[str, str], list[float]] = defaultdict(list)
    whole_samples: dict[str, list[float]] = defaultdict(list)
    axis_samples: dict[tuple[str, str], list[float]] = defaultdict(list)
    cursor = 0
    stride = round(LOG_PERIOD_S / dynamics_successor.DT)
    for summary in summaries:
        sequence = summary["sequence_id"]
        count = int(summary["integration_step_count"])
        duration = float(summary["duration_s"])
        cursor += round(dynamics_successor.SETTLE_S / dynamics_successor.DT)
        sequence_calls = command_calls[cursor:cursor + count]
        cursor += count
        for step, commands in enumerate(sequence_calls):
            if step % stride != 0 and step != count - 1:
                continue
            time_s = min(step * dynamics_successor.DT, duration)
            instant_bus: dict[str, float] = defaultdict(float)
            for axis in axes:
                command = float(commands[axis])
                current = current_by_axis[axis]
                candidate_current = float(current["candidate_current_a"])
                if axis.endswith("_GRIPPER"):
                    equivalent_output = abs(command) * GRIPPER_GAP_TO_PINION_FACTOR * GRIPPER_PINION_RADIUS_M
                    endpoint = float(current["current_limited_linear_endpoint_nm"])
                    mapping = "TOTAL-GAP GENERALIZED FORCE * 2 * 5 MM PINION RADIUS / CANDIDATE LINEAR TORQUE ENDPOINT"
                    calibration = "ACTIVE OBJECT GRIP AND PHYSICAL FORCE/CURRENT CALIBRATION EXCLUDED"
                    command_unit = "N generalized total-gap force"
                else:
                    equivalent_output = abs(command)
                    endpoint = successor_caps[axis]
                    mapping = "ABS OUTPUT TORQUE / CANDIDATE LINEAR CURRENT ENDPOINT * CANDIDATE CURRENT"
                    calibration = "TORQUE-PRODUCING CURRENT EQUIVALENT ONLY; IDLE/LOSS/TRANSIENT/REGEN EXCLUDED"
                    command_unit = "Nm output torque"
                current_equivalent = equivalent_output / endpoint * candidate_current
                axis_samples[(sequence, axis)].append(current_equivalent)
                instant_bus[bus_by_axis[axis]] += current_equivalent
                sample_rows.append({
                    "sequence_id": sequence,
                    "time_s": f"{time_s:.3f}",
                    "axis_id": axis,
                    "bus_id": bus_by_axis[axis],
                    "absolute_command": f"{abs(command):.9f}",
                    "command_unit": command_unit,
                    "equivalent_output_torque_nm": f"{equivalent_output:.9f}",
                    "torque_producing_current_equivalent_a": f"{current_equivalent:.9f}",
                    "mapping": mapping,
                    "calibration_boundary": calibration,
                    "warning": WARNING,
                })
            whole = 0.0
            for bus in sorted(bus_budget):
                value = instant_bus[bus]
                bus_samples[(sequence, bus)].append(value)
                whole += value
            whole_samples[sequence].append(whole)

    if cursor != len(command_calls):
        raise RuntimeError("not every captured control call was assigned")

    axis_rows: list[dict] = []
    for sequence in sorted(row["sequence_id"] for row in summaries):
        for axis in axes:
            peak, p95, rms, mean = stats(axis_samples[(sequence, axis)])
            mapping_state = "VIRTUAL-WORK GRIPPER HOLD ONLY; ACTIVE GRIP OPEN" if axis.endswith("_GRIPPER") else "ROTARY TORQUE-EQUIVALENT TRACE"
            axis_rows.append({
                "sequence_id": sequence,
                "axis_id": axis,
                "bus_id": bus_by_axis[axis],
                "actuator_model": current_by_axis[axis]["actuator_model"],
                "sample_count": len(axis_samples[(sequence, axis)]),
                "peak_current_equivalent_a": f"{peak:.9f}",
                "p95_current_equivalent_a": f"{p95:.9f}",
                "rms_current_equivalent_a": f"{rms:.9f}",
                "mean_current_equivalent_a": f"{mean:.9f}",
                "candidate_internal_cap_a": current_by_axis[axis]["candidate_current_a"],
                "mapping_state": mapping_state,
                "thermal_rating_credit": "NONE",
                "authority": "NO PROCUREMENT, CONNECTION, POWERED TEST, MOTION OR ENERGIZATION AUTHORITY",
                "warning": WARNING,
            })

    bus_rows: list[dict] = []
    sequences = sorted(row["sequence_id"] for row in summaries)
    for bus in sorted(bus_budget):
        bus_axes = sorted(axis for axis in axes if bus_by_axis[axis] == bus)
        for sequence in sequences + ["ALL-BOUND-TRACES"]:
            values = (
                bus_samples[(sequence, bus)]
                if sequence != "ALL-BOUND-TRACES"
                else [value for item in sequences for value in bus_samples[(item, bus)]]
            )
            peak, p95, rms, mean = stats(values)
            bus_rows.append({
                "sequence_id": sequence,
                "bus_id": bus,
                "axis_count": len(bus_axes),
                "axes": "; ".join(bus_axes),
                "sample_count": len(values),
                "peak_current_equivalent_a": f"{peak:.9f}",
                "p95_current_equivalent_a": f"{p95:.9f}",
                "rms_current_equivalent_a": f"{rms:.9f}",
                "mean_current_equivalent_a": f"{mean:.9f}",
                "candidate_internal_cap_sum_a": bus_budget[bus]["simultaneous_candidate_cap_a"],
                "active_grip_included": "NO" if any(axis.endswith("_GRIPPER") for axis in bus_axes) else "NOT APPLICABLE",
                "released_normal_demand": "NO",
                "thermal_rating_credit": "NONE",
                "warning": WARNING,
            })

    whole_rows: list[dict] = []
    for sequence in sequences + ["ALL-BOUND-TRACES"]:
        values = (
            whole_samples[sequence]
            if sequence != "ALL-BOUND-TRACES"
            else [value for item in sequences for value in whole_samples[item]]
        )
        peak, p95, rms, mean = stats(values)
        whole_rows.append({
            "sequence_id": sequence,
            "sample_count": len(values),
            "peak_current_equivalent_a": f"{peak:.9f}",
            "p95_current_equivalent_a": f"{p95:.9f}",
            "rms_current_equivalent_a": f"{rms:.9f}",
            "mean_current_equivalent_a": f"{mean:.9f}",
            "candidate_internal_cap_sum_a": f"{sum(float(row['candidate_current_a']) for row in current_rows):.9f}",
            "released_supply_demand": "NO",
            "thermal_rating_credit": "NONE",
            "warning": WARNING,
        })

    write_csv(OUT / "current-equivalent-samples.csv", sample_rows)
    write_csv(OUT / "axis-current-duty-envelope.csv", axis_rows)
    write_csv(OUT / "bus-current-duty-envelope.csv", bus_rows)
    write_csv(OUT / "whole-body-current-duty-envelope.csv", whole_rows)

    holds = [
        ("DCE-H01", "actuator electronics/idle current and driver losses are absent"),
        ("DCE-H02", "active object gripping and gripper physical force/current calibration are absent"),
        ("DCE-H03", "free-balance correction, contact/state/latency variation and gait robustness are absent"),
        ("DCE-H04", "regeneration, braking, inrush, communication, fault and stalled-axis cases are absent"),
        ("DCE-H05", "as-built transmission efficiency, backlash, compliance and thermal behavior are absent"),
        ("DCE-H06", "ambient, bundling, connector/contact temperature, voltage drop and route-length tests are unexecuted"),
        ("DCE-H07", "fault current and protection-clearing coordination remain unselected"),
        ("DCE-H08", "received hardware correlation and qualified electrical review are unexecuted"),
    ]
    write_csv(OUT / "open-holds.csv", [{
        "hold_id": key,
        "unresolved": value,
        "state": "OPEN",
        "authority": "BLOCKS CONDUCTOR/CONNECTOR/PROTECTION/SOURCE RELEASE AND ALL POWERED WORK",
        "warning": WARNING,
    } for key, value in holds])

    sources = [
        ("generator", Path(__file__)),
        ("control successor generator", ROOT / "tools" / "generate_hr30_control_successor_p01.py"),
        ("simulation implementation", ROOT / "tools" / "generate_hr30_dynamics_successor_p01.py"),
        ("active tether-first ideal-fixture control model", BODY / "mujoco-dynamics-validation-p0.1" / "hr30_tether_ideal_fixture.xml"),
        ("control successor status", BODY / "control-successor-p0.1" / "control-successor-status.json"),
        ("axis current endpoints", BODY / "current-constrained-actuation-p0.1" / "axis-current-torque-register.csv"),
        ("bus current budgets", BODY / "current-constrained-actuation-p0.1" / "bus-current-budget.csv"),
        ("bus axis binding", BODY / "actuator-bus-axis-binding.csv"),
        ("gripper force geometry", BODY / "grippers-p0.1" / "gripper-force-screen.csv"),
        ("gripper mesh geometry", BODY / "grippers-p0.1" / "gripper-mesh-state-register.csv"),
    ]
    write_csv(OUT / "source-binding.csv", [{
        "role": role,
        "path": path.relative_to(ROOT).as_posix(),
        "sha256": sha(path),
        "state": "BOUND",
        "warning": WARNING,
    } for role, path in sources])

    aggregate_bus = [row for row in bus_rows if row["sequence_id"] == "ALL-BOUND-TRACES"]
    status = {
        "identifier": IDENTIFIER,
        "warning": WARNING,
        "mujoco_version": mujoco.__version__,
        "numpy_version": np.__version__,
        "control_model_mass_kg": round(model_mass_kg, 9),
        "sequence_count": len(sequences),
        "axis_count": len(axes),
        "rotary_axis_count": sum(not axis.endswith("_GRIPPER") for axis in axes),
        "gripper_axis_count": sum(axis.endswith("_GRIPPER") for axis in axes),
        "bus_count": len(bus_budget),
        "sample_period_s": LOG_PERIOD_S,
        "axis_sample_count": len(sample_rows),
        "axis_sequence_envelope_count": len(axis_rows),
        "bus_sequence_envelope_count": len(bus_rows),
        "all_control_sequences_passed_source_screen": all(row["result"].startswith("PASS") for row in summaries),
        "maximum_bounded_bus_peak_current_equivalent_a": max(float(row["peak_current_equivalent_a"]) for row in aggregate_bus),
        "maximum_bounded_bus_rms_current_equivalent_a": max(float(row["rms_current_equivalent_a"]) for row in aggregate_bus),
        "whole_body_bounded_peak_current_equivalent_a": float(whole_rows[-1]["peak_current_equivalent_a"]),
        "whole_body_bounded_rms_current_equivalent_a": float(whole_rows[-1]["rms_current_equivalent_a"]),
        "bounded_sequence_rms_computed": True,
        "active_object_grip_included": False,
        "electronics_idle_and_loss_current_included": False,
        "regeneration_included": False,
        "normal_rms_demand_released": False,
        "wire_construction_selected": False,
        "branch_protection_selected": False,
        "thermal_validated": False,
        "procurement_authority": False,
        "connection_authority": False,
        "powered_test_authority": False,
        "motion_authority": False,
        "walking_authority": False,
        "energization_authority": False,
    }
    (OUT / "duty-current-status.json").write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8", newline="\n")
    (OUT / "runtime-provenance.json").write_text(json.dumps({
        "identifier": IDENTIFIER,
        "warning": WARNING,
        "executed_utc": datetime.now(timezone.utc).isoformat(),
        "integration_timestep_s": dynamics_successor.DT,
        "logged_period_s": LOG_PERIOD_S,
        "controller": "frozen 8.0/0.8 endpoint-scaled control successor",
        "control_model_mass_kg": model_mass_kg,
        "current_mapping": "absolute command divided by candidate linear endpoint times candidate current",
        "gripper_virtual_work": "T = F_q * 2 * 0.005 m because q is total 26 mm gap and each rack travels q/2",
        "scope": "bounded torque-producing current-equivalent calculation only",
    }, indent=2) + "\n", encoding="utf-8", newline="\n")
    (OUT / "README.md").write_text(f"""# HR-30 harness duty-current envelope P0.1

**{WARNING}**

This package reruns the frozen 25-axis whole-body control successor and records every 50 Hz command as a torque-producing current equivalent. It provides per-axis, per-bus and whole-body peak, P95, RMS and mean envelopes for both prescribed sequences.

The result closes a missing numerical duty input; it does not release a normal operating demand. Active object gripping, idle electronics, losses, regeneration, transients, fault cases, robustness, physical thermal correlation and qualified review remain open.
""", encoding="utf-8", newline="\n")
    (OUT / "index.html").write_text(render_page(axis_rows, bus_rows, whole_rows), encoding="utf-8", newline="\n")
    shutil.copy2(__file__, OUT / "duty-current-envelope-source.py")

    manifest_rows = []
    for path in sorted(OUT.iterdir(), key=lambda item: item.name):
        if path.is_file() and path.name != "file-manifest.csv":
            manifest_rows.append({"file": path.name, "bytes": path.stat().st_size, "sha256": sha(path), "warning": WARNING})
    write_csv(OUT / "file-manifest.csv", manifest_rows)
    if REL.exists():
        shutil.rmtree(REL)
    shutil.copytree(OUT, REL)

    harness_readme = """## Bounded current-duty envelope

The [interactive duty-current envelope](duty-current-envelope-p0.1/index.html) converts the frozen 25-axis whole-body control commands into 50 Hz torque-producing current equivalents and per-axis/per-bus peak, P95, RMS and mean evidence. Active gripping, idle current, losses, transients, regeneration, faults, robustness and thermal correlation remain open, so the result does not release wires, connectors, protection or a source."""
    replace_marker(HARNESS / "README.md", "<!-- HR30-DUTY-CURRENT-P01-START -->", "<!-- HR30-DUTY-CURRENT-P01-END -->", harness_readme)
    harness_index = """<section id='duty-current'><h2>Bounded whole-body current duty</h2><div class='grid'><article class='card'><div class='metric'>25 axes</div><p>50 Hz torque-producing current-equivalent traces.</p></article><article class='card'><div class='metric'>8 buses</div><p>Peak, P95, RMS and mean bounded envelopes.</p></article><article class='card'><h3>No ampacity release</h3><p>Idle current, losses, gripping, transients, faults and thermal tests remain open.</p></article></div><p><a href='duty-current-envelope-p0.1/index.html'>Open the duty-current evidence.</a></p></section>"""
    replace_marker(HARNESS / "index.html", "<!-- HR30-DUTY-CURRENT-P01-START -->", "<!-- HR30-DUTY-CURRENT-P01-END -->", harness_index)
    body_readme = """## Harness duty-current evidence

The [whole-body harness duty-current guide](harness/duty-current-envelope-p0.1/index.html) supplies the previously missing bounded per-axis and per-bus torque-producing current envelopes from the executed control successor. It is calculation evidence only; final normal demand, wire construction, protection, thermal validation and every powered-work authority remain open."""
    replace_marker(BODY / "README.md", "<!-- HR30-DUTY-CURRENT-P01-START -->", "<!-- HR30-DUTY-CURRENT-P01-END -->", body_readme)
    body_index = """<section id='harness-duty-current'><h2>The harness now has a bounded current-duty input</h2><div class='grid'><article class='card pass'><div class='metric'>25</div><p>axis command channels mapped</p></article><article class='card pass'><div class='metric'>8</div><p>bus envelopes calculated</p></article><article class='card hold'><h3>Thermal release remains open</h3><p>Active gripping, idle/loss current, transients, faults and physical tests are not included.</p></article></div><p><a href='harness/duty-current-envelope-p0.1/index.html'>Open the whole-body current-duty evidence.</a></p></section>"""
    replace_marker(BODY / "index.html", "<!-- HR30-DUTY-CURRENT-P01-START -->", "<!-- HR30-DUTY-CURRENT-P01-END -->", body_index)

    print(json.dumps(status, indent=2))
    return 0 if status["all_control_sequences_passed_source_screen"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
