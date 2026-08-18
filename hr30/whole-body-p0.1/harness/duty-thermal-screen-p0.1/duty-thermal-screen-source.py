"""Generate route-specific HR-30 harness duty/thermal planning evidence.

This is a calculation successor to the bounded torque-producing current traces.
It does not invent the unverified CF130 conductor resistance, total actuator
current, hot ampacity, contact derating, fault current, or a thermal release.
"""

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


ROOT = Path(__file__).resolve().parents[1]
BODY = ROOT / "hr30" / "whole-body-p0.1"
HARNESS = BODY / "harness"
PHYSICAL = HARNESS / "physical-p0.1"
DUTY = HARNESS / "duty-current-envelope-p0.1"
CABLE = HARNESS / "actuator-cable-kit-p0.1"
OUT = HARNESS / "duty-thermal-screen-p0.1"
REL = ROOT / "release" / "hr30" / "whole-body-p0.1" / "harness" / OUT.name
IDENTIFIER = "HR30-HARNESS-DUTY-THERMAL-SCREEN-P0.1"
WARNING = (
    "PRELIMINARY - ROUTE-SPECIFIC DUTY/VOLTAGE-DROP/LOSS PLANNING SCREEN ONLY - "
    "NOT A WIRE, CONNECTOR, PROTECTION OR THERMAL RATING - NOT APPROVED FOR "
    "PROCUREMENT, FABRICATION, CONNECTION, POWERED TESTING, MOTION OR ENERGIZATION"
)
ALPHA_3051_DCR_OHM_PER_1000FT = 16.2
ALPHA_3051_DCR_OHM_PER_KM = ALPHA_3051_DCR_OHM_PER_1000FT / 0.3048
COMPARISON_DCR_20C_OHM_PER_KM = 79.0
COPPER_ALPHA_PER_C = 0.00393
JST_EH_HEADLINE_A = 3.0


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def normalized_text_sha(path: Path) -> str:
    """Bind semantic text independently of a Windows checkout's line endings."""
    text = path.read_text(encoding="utf-8").replace("\r\n", "\n").replace("\r", "\n")
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        raise RuntimeError(f"refusing to write empty table: {path}")
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
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


def pooled_stats(values: list[float]) -> tuple[float, float, float, float]:
    if not values:
        raise RuntimeError("empty sample set")
    ordered = sorted(values)
    rank = 0.95 * (len(ordered) - 1)
    low = math.floor(rank)
    high = math.ceil(rank)
    p95 = ordered[low] if low == high else ordered[low] + (rank - low) * (ordered[high] - ordered[low])
    return max(values), p95, math.sqrt(sum(value * value for value in values) / len(values)), sum(values) / len(values)


def fmt(value: float) -> str:
    return f"{value:.9f}"


def render_page(axis_rows: list[dict], bus_rows: list[dict], corridor_rows: list[dict], contact_rows: list[dict]) -> str:
    worst_drop = max(axis_rows, key=lambda row: float(row["bounded_peak_drop_80c_comparison_v"]))
    worst_loss = max(axis_rows, key=lambda row: float(row["bounded_rms_loss_80c_comparison_w"]))
    worst_contact = max(contact_rows, key=lambda row: float(row["bounded_peak_to_3a_headline_ratio"]))
    table = "".join(
        f"<tr><td><strong>{html.escape(row['bus_id'])}</strong></td><td>{row['axis_count']}</td>"
        f"<td>{float(row['bounded_peak_current_equivalent_a']):.3f} A</td>"
        f"<td>{float(row['bounded_rms_current_equivalent_a']):.3f} A</td>"
        f"<td>{float(row['sum_axis_bounded_rms_loss_80c_comparison_w']):.3f} W</td></tr>"
        for row in bus_rows
    )
    corridors = "".join(
        f"<tr><td><strong>{html.escape(row['power_corridor'])}</strong></td><td>{row['axis_count']} pairs</td>"
        f"<td>{row['insulated_conductor_count']}</td><td>{float(row['sum_bounded_rms_loss_80c_comparison_w']):.3f} W</td>"
        f"<td>{html.escape(row['thermal_state'])}</td></tr>" for row in corridor_rows
    )
    return f"""<!doctype html><html lang='en'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'><title>HR-30 harness duty and thermal planning screen</title><style>:root{{--deep:#071d36;--blue:#0b4f91;--sky:#dff4ff;--gold:#f2b91d;--paper:#eef8fe;--ink:#142a40;--line:#96cce7;--red:#8b2432}}*{{box-sizing:border-box}}html,body{{max-width:100%;overflow-x:clip}}body{{margin:0;background:var(--paper);color:var(--ink);font:17px/1.5 system-ui,Segoe UI,sans-serif}}header,main{{padding:28px 20px}}header{{background:var(--deep);color:white}}header>div,main{{max-width:1180px;margin:auto}}h1{{font-size:clamp(38px,6vw,68px);line-height:1.05}}h2{{font-size:clamp(28px,4vw,43px)}}.warning{{background:var(--gold);color:#15243a;border:3px solid #805600;padding:15px 18px;font-weight:900}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));gap:16px}}.card,.panel{{background:white;border:2px solid var(--line);border-radius:16px;padding:18px;margin:18px 0}}.metric{{font-size:clamp(32px,5vw,48px);font-weight:900;color:var(--blue)}}.hold{{border-color:#d59a23}}.table-wrap{{overflow-x:auto}}table{{border-collapse:collapse;width:100%;min-width:820px}}th,td{{text-align:left;padding:12px;border-bottom:1px solid var(--line);font-size:16px;vertical-align:top}}th{{background:#d9f2ff}}a{{color:#075b9b;font-weight:800}}code{{font-size:16px}}@media(max-width:700px){{body{{font-size:16px}}header,main{{padding-inline:13px}}}}</style></head><body><header><div class='warning'>{html.escape(WARNING)}</div><h1>Every actuator route now has a bounded loss case.</h1><p>The existing whole-body walking traces, 25 physical route lengths, eight buses and power-corridor ownership are calculated together. This is the missing test-planning input—not a hot ampacity or connector release.</p></header><main><section class='grid'><article class='card'><div class='metric'>{html.escape(worst_drop['axis_id'])}</div><p>largest bounded peak comparison drop: {float(worst_drop['bounded_peak_drop_80c_comparison_v']):.3f} V.</p></article><article class='card'><div class='metric'>{float(worst_loss['bounded_rms_loss_80c_comparison_w']):.3f} W</div><p>largest per-branch bounded RMS comparison loss: {html.escape(worst_loss['axis_id'])}.</p></article><article class='card'><div class='metric'>{float(worst_contact['bounded_peak_to_3a_headline_ratio'])*100:.1f}%</div><p>largest bounded axis peak divided by the JST EH 3 A headline—not a derated contact result.</p></article><article class='card hold'><div class='metric'>0</div><p>thermal tests, released conductors, protection values or powered-work approvals.</p></article></section><section class='panel'><h2>Eight electrical domains</h2><div class='table-wrap'><table><thead><tr><th>Bus</th><th>Axes</th><th>Bounded peak</th><th>Bounded RMS</th><th>Summed branch I²R comparison</th></tr></thead><tbody>{table}</tbody></table></div></section><section class='panel'><h2>Physical corridor bundle obligations</h2><div class='table-wrap'><table><thead><tr><th>Power corridor</th><th>Pairs</th><th>Conductors</th><th>Bounded RMS comparison loss</th><th>State</th></tr></thead><tbody>{corridors}</tbody></table></div></section><section class='panel'><h2>What the numbers mean</h2><p>The duty values are pooled from both frozen 50 Hz whole-body sequence traces. The 80 °C comparison applies the copper temperature coefficient to the existing 79 Ω/km rejected-predecessor value over each complete route. It is intentionally conservative-looking but is <strong>not</strong> the resistance of CF130.03.02.UL. Alpha 3051's official 16.2 Ω/1000 ft nominal DCR is reported separately as an all-route reference even though Alpha is only the fixed pigtail candidate. Actual moving/fixed length splits, received resistance, idle/loss current, active grip, regeneration, faults, bundling temperature rise and connector derating remain open.</p></section><section class='panel'><h2>Engineering tables</h2><p><a href='axis-duty-voltage-drop-screen.csv'>25 axis screens</a> &middot; <a href='bus-duty-loss-screen.csv'>eight bus screens</a> &middot; <a href='corridor-bundle-duty-screen.csv'>corridor bundles</a> &middot; <a href='contact-utilization-screen.csv'>contact comparisons</a> &middot; <a href='current-derating-successor-binding.csv'>derating successor</a> &middot; <a href='thermal-test-prescription.csv'>physical test prescription</a> &middot; <a href='open-holds.csv'>open holds</a></p></section></main></body></html>"""


def main() -> int:
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)

    samples = read_csv(DUTY / "current-equivalent-samples.csv")
    cable_rows = read_csv(CABLE / "axis-power-cable-candidate.csv")
    binding_rows = read_csv(PHYSICAL / "axis-harness-binding.csv")
    derating_rows = read_csv(PHYSICAL / "current-derating-register.csv")
    bus_envelopes = read_csv(DUTY / "bus-current-duty-envelope.csv")
    cable_by_axis = {row["axis_id"]: row for row in cable_rows}
    binding_by_axis = {row["axis_id"]: row for row in binding_rows}
    derating_by_axis = {row["circuit"].removeprefix("PWR-"): row for row in derating_rows}
    values_by_axis: dict[str, list[float]] = defaultdict(list)
    for row in samples:
        values_by_axis[row["axis_id"]].append(float(row["torque_producing_current_equivalent_a"]))
    axes = sorted(values_by_axis)
    if len(axes) != 25 or set(axes) != set(cable_by_axis) or set(axes) != set(binding_by_axis) or set(axes) != set(derating_by_axis):
        raise RuntimeError("25-axis duty/cable/physical/derating bindings do not match")

    axis_rows: list[dict] = []
    contact_rows: list[dict] = []
    for axis in axes:
        cable = cable_by_axis[axis]
        physical = binding_by_axis[axis]
        derating = derating_by_axis[axis]
        length_mm = float(cable["one_way_planning_length_mm"])
        if not math.isclose(length_mm, float(derating["length_mm"]), abs_tol=0.001):
            raise RuntimeError(f"route length drift for {axis}")
        round_trip_km = 2.0 * length_mm / 1_000_000.0
        peak, p95, rms, mean = pooled_stats(values_by_axis[axis])
        cap = float(cable["candidate_internal_limit_a"])
        stall = float(cable["published_stall_endpoint_a"])
        alpha_r20 = round_trip_km * ALPHA_3051_DCR_OHM_PER_KM
        compare_r20 = round_trip_km * COMPARISON_DCR_20C_OHM_PER_KM
        compare_r60 = compare_r20 * (1.0 + COPPER_ALPHA_PER_C * 40.0)
        compare_r80 = compare_r20 * (1.0 + COPPER_ALPHA_PER_C * 60.0)
        row = {
            "axis_id": axis,
            "bus_id": cable["bus_id"],
            "actuator_model": cable["actuator_model"],
            "power_corridor": physical["power_trunk"],
            "one_way_planning_length_mm": f"{length_mm:.3f}",
            "round_trip_planning_length_mm": f"{2*length_mm:.3f}",
            "sample_count": len(values_by_axis[axis]),
            "bounded_peak_current_equivalent_a": fmt(peak),
            "bounded_p95_current_equivalent_a": fmt(p95),
            "bounded_rms_current_equivalent_a": fmt(rms),
            "bounded_mean_current_equivalent_a": fmt(mean),
            "candidate_internal_cap_a": fmt(cap),
            "published_stall_endpoint_a": fmt(stall),
            "alpha_3051_nominal_dcr_20c_ohm_per_km": fmt(ALPHA_3051_DCR_OHM_PER_KM),
            "all_route_alpha_3051_reference_loop_r20_ohm": fmt(alpha_r20),
            "rejected_predecessor_comparison_dcr_20c_ohm_per_km": fmt(COMPARISON_DCR_20C_OHM_PER_KM),
            "comparison_loop_r20_ohm": fmt(compare_r20),
            "comparison_loop_r60_ohm": fmt(compare_r60),
            "comparison_loop_r80_ohm": fmt(compare_r80),
            "bounded_rms_drop_80c_comparison_v": fmt(rms * compare_r80),
            "bounded_peak_drop_80c_comparison_v": fmt(peak * compare_r80),
            "bounded_rms_loss_80c_comparison_w": fmt(rms * rms * compare_r80),
            "bounded_peak_instantaneous_loss_80c_comparison_w": fmt(peak * peak * compare_r80),
            "candidate_cap_drop_80c_comparison_v": fmt(cap * compare_r80),
            "candidate_cap_loss_80c_comparison_w": fmt(cap * cap * compare_r80),
            "normal_rms_current_state": "PARTIAL - BOUNDED TORQUE-PRODUCING COMPONENT COMPUTED; TOTAL NORMAL RMS NOT RELEASED",
            "resistance_state": "COMPARISON ONLY - CF130 DCR AND MOVING/FIXED LENGTH SPLIT UNVERIFIED",
            "thermal_rating_credit": "NONE",
            "authority": "NO PROCUREMENT, FABRICATION, CONNECTION, POWERED TEST, MOTION OR ENERGIZATION AUTHORITY",
            "warning": WARNING,
        }
        axis_rows.append(row)
        contact_rows.append({
            "axis_id": axis,
            "bus_id": cable["bus_id"],
            "connector_family": "JST EH ACTUATOR INTERFACE",
            "published_headline_current_a": fmt(JST_EH_HEADLINE_A),
            "published_condition": "3 A AT AWG22 SERIES HEADLINE; APPLICATION DERATING AND TEMPERATURE RISE OPEN",
            "bounded_peak_current_equivalent_a": fmt(peak),
            "bounded_peak_to_3a_headline_ratio": fmt(peak / JST_EH_HEADLINE_A),
            "candidate_internal_cap_a": fmt(cap),
            "candidate_cap_to_3a_headline_ratio": fmt(cap / JST_EH_HEADLINE_A),
            "published_stall_endpoint_a": fmt(stall),
            "stall_to_3a_headline_ratio": fmt(stall / JST_EH_HEADLINE_A),
            "contact_disposition": "COMPARISON ONLY - NO HOT CONTACT OR DERATING CREDIT",
            "authority": "NO CONNECTOR RELEASE OR POWERED-WORK AUTHORITY",
            "warning": WARNING,
        })

    axis_by_id = {row["axis_id"]: row for row in axis_rows}
    aggregate_bus = {row["bus_id"]: row for row in bus_envelopes if row["sequence_id"] == "ALL-BOUND-TRACES"}
    bus_axes: dict[str, list[str]] = defaultdict(list)
    corridor_axes: dict[str, list[str]] = defaultdict(list)
    for row in axis_rows:
        bus_axes[row["bus_id"]].append(row["axis_id"])
        corridor_axes[row["power_corridor"]].append(row["axis_id"])
    if len(bus_axes) != 8:
        raise RuntimeError("expected eight bus domains")
    bus_rows: list[dict] = []
    for bus in sorted(bus_axes):
        env = aggregate_bus[bus]
        members = sorted(bus_axes[bus])
        bus_rows.append({
            "bus_id": bus,
            "axis_count": len(members),
            "axes": "; ".join(members),
            "bounded_peak_current_equivalent_a": env["peak_current_equivalent_a"],
            "bounded_p95_current_equivalent_a": env["p95_current_equivalent_a"],
            "bounded_rms_current_equivalent_a": env["rms_current_equivalent_a"],
            "candidate_internal_cap_sum_a": env["candidate_internal_cap_sum_a"],
            "sum_axis_bounded_rms_loss_80c_comparison_w": fmt(sum(float(axis_by_id[a]["bounded_rms_loss_80c_comparison_w"]) for a in members)),
            "sum_axis_candidate_cap_loss_80c_comparison_w": fmt(sum(float(axis_by_id[a]["candidate_cap_loss_80c_comparison_w"]) for a in members)),
            "aggregation_boundary": "INDEPENDENT BRANCH I^2R SUM; NOT SHARED-FEED OR SOURCE LOSS",
            "thermal_rating_credit": "NONE",
            "warning": WARNING,
        })

    corridor_rows: list[dict] = []
    for corridor in sorted(corridor_axes):
        members = sorted(corridor_axes[corridor])
        corridor_rows.append({
            "power_corridor": corridor,
            "axis_count": len(members),
            "axes": "; ".join(members),
            "insulated_conductor_count": 2 * len(members),
            "sum_bounded_rms_loss_80c_comparison_w": fmt(sum(float(axis_by_id[a]["bounded_rms_loss_80c_comparison_w"]) for a in members)),
            "sum_candidate_cap_loss_80c_comparison_w": fmt(sum(float(axis_by_id[a]["candidate_cap_loss_80c_comparison_w"]) for a in members)),
            "ambient_c": "SELECTION REQUIRED",
            "installed_fill_and_spacing": "SELECTION REQUIRED",
            "thermal_state": "TEST REQUIRED - NO BUNDLE DERATING OR TEMPERATURE CREDIT",
            "warning": WARNING,
        })

    derating_successor: list[dict] = []
    for original in derating_rows:
        axis = original["circuit"].removeprefix("PWR-")
        calculated = axis_by_id[axis]
        derating_successor.append({
            "circuit": original["circuit"],
            "axis_id": axis,
            "bus_branch": original["bus_branch"],
            "endpoint_current_a": original["endpoint_current_a"],
            "bounded_torque_component_rms_a": calculated["bounded_rms_current_equivalent_a"],
            "bounded_torque_component_peak_a": calculated["bounded_peak_current_equivalent_a"],
            "total_normal_rms_current_a": "SELECTION REQUIRED - IDLE/LOSS/GRIP/ROBUSTNESS/MEASUREMENT ABSENT",
            "fault_current_a": original["fault_current_a"],
            "length_mm": original["length_mm"],
            "power_corridor": calculated["power_corridor"],
            "corridor_pair_count": len(corridor_axes[calculated["power_corridor"]]),
            "ambient_c": original["ambient_c"],
            "duty_cycle": "TWO 50 HZ BOUNDED SEQUENCES COMPUTED; PHYSICAL DUTY CYCLE SELECTION REQUIRED",
            "inrush": original["inrush"],
            "calculation_state": "ADVANCED - BOUNDED RMS/PEAK AND CORRIDOR BUNDLE PRESENT; TOTAL NORMAL/FAULT/AMBIENT/INRUSH/HOT TEST OPEN",
            "thermal_rating_credit": "NONE",
            "warning": WARNING,
        })

    tests = [
        ("DTS-T01", "each of 25 completed power branches", "four-wire resistance at received ambient; measure moving cable and fixed pigtail separately", "DCR, length split, crimp/contact resistance"),
        ("DTS-T02", "each actuator/contact family coupon", "replay bounded RMS/peak waveform with actuator replaced by qualified load where appropriate", "conductor and connector temperature rise"),
        ("DTS-T03", "each of 6 populated power corridors", "simultaneous branch replay at bounded sequence phasing in as-built bundle", "hotspot temperature and voltage drop"),
        ("DTS-T04", "each of 8 bus domains", "measure complete normal current including electronics, communication and conversion losses", "measured bus RMS/peak and correlation factor"),
        ("DTS-T05", "both hand/gripper branches", "execute defined grasp/hold/release duty with force-limited fixture", "active-grip RMS/peak and contact temperature"),
        ("DTS-T06", "all regenerative axes and each bus-domain sink", "capture voltage/current during commanded deceleration and power removal", "bidirectional energy and overvoltage boundary"),
        ("DTS-T07", "each protection/contact/conductor chain", "qualified current-limited fault and clearing coordination procedure", "prospective/limited fault current, clearing time, damage"),
        ("DTS-T08", "whole routed robot in restraint", "repeat prescribed duty at declared ambient after assembly and inspection gates", "final harness temperature map and supply margin"),
    ]
    write_csv(OUT / "thermal-test-prescription.csv", [{
        "test_id": test_id, "article": article, "method_boundary": method, "required_measurements": measurements,
        "ambient_duration_limits": "SELECTION REQUIRED BY QUALIFIED PROCEDURE", "execution_state": "NOT EXECUTED",
        "pass_criteria": "SELECTION REQUIRED BEFORE TEST", "authority": "NO CONNECTION OR POWERED-TEST AUTHORITY", "warning": WARNING,
    } for test_id, article, method, measurements in tests])
    write_csv(OUT / "axis-duty-voltage-drop-screen.csv", axis_rows)
    write_csv(OUT / "bus-duty-loss-screen.csv", bus_rows)
    write_csv(OUT / "corridor-bundle-duty-screen.csv", corridor_rows)
    write_csv(OUT / "contact-utilization-screen.csv", contact_rows)
    write_csv(OUT / "current-derating-successor-binding.csv", derating_successor)

    holds = [
        ("DTS-H01", "CF130.03.02.UL conductor resistance and received moving-cable resistance are unverified"),
        ("DTS-H02", "moving/fixed length split, final cut length, service slack and crimp/contact resistance are unmeasured"),
        ("DTS-H03", "total normal current excludes electronics idle, driver/conversion loss, communication and active grip"),
        ("DTS-H04", "regeneration, inrush, fault current and protection clearing remain unresolved"),
        ("DTS-H05", "ambient, bundle fill/spacing, material limits and hot connector/contact derating are unresolved"),
        ("DTS-H06", "JST EH and Micro-Fit application temperature-rise evidence is unexecuted"),
        ("DTS-H07", "all eight prescribed physical thermal/fault tests are unexecuted and pass criteria require qualified approval"),
        ("DTS-H08", "wire, connector, protection, source, procurement and every powered-work authority remain withheld"),
    ]
    write_csv(OUT / "open-holds.csv", [{"hold_id": key, "unresolved": text, "state": "OPEN", "warning": WARNING} for key, text in holds])

    local_sources = [
        ("generator", Path(__file__)),
        ("duty samples", DUTY / "current-equivalent-samples.csv"),
        ("axis duty envelopes", DUTY / "axis-current-duty-envelope.csv"),
        ("bus duty envelopes", DUTY / "bus-current-duty-envelope.csv"),
        ("duty status", DUTY / "duty-current-status.json"),
        ("axis cable candidates", CABLE / "axis-power-cable-candidate.csv"),
        ("cable primary sources", CABLE / "primary-source-register.csv"),
        ("axis physical binding", PHYSICAL / "axis-harness-binding.csv"),
        ("physical derating baseline", PHYSICAL / "current-derating-register.csv"),
        ("physical route segments", PHYSICAL / "route-segment-register.csv"),
    ]
    write_csv(OUT / "source-binding.csv", [{
        "role": role, "path": path.relative_to(ROOT).as_posix(), "normalized_lf_sha256": normalized_text_sha(path),
        "hash_boundary": "UTF-8 TEXT NORMALIZED TO LF", "state": "BOUND", "warning": WARNING,
    } for role, path in local_sources])
    write_csv(OUT / "calculation-basis.csv", [
        {"basis_id": "DTS-B01", "parameter": "Alpha Wire 3051 nominal conductor DCR at 20 C", "value": "16.2 ohm/1000 ft = 53.149606299 ohm/km", "source": "Alpha Wire 3051 live official product specification", "revision_or_access": "live official page; accessed 2026-08-18", "url": "https://www.alphawire.com/products/wire/hook-up-wire/premium/3051", "use_boundary": "ALL-ROUTE REFERENCE ONLY; ACTUAL ALPHA PIGTAIL LENGTH OPEN", "warning": WARNING},
        {"basis_id": "DTS-B02", "parameter": "CF130.03.02.UL construction", "value": "2 x 22 AWG / 0.34 mm2", "source": "igus CF130-UL live official product page", "revision_or_access": "live official page; accessed 2026-08-18", "url": "https://www.igus.com/product/CF130_UL", "use_boundary": "MOVING-CABLE CANDIDATE IDENTITY ONLY; DCR/AMPACITY NOT RELEASED", "warning": WARNING},
        {"basis_id": "DTS-B03", "parameter": "JST EH series headline", "value": "3 A at AWG22", "source": "JST EH official product page/data sheet", "revision_or_access": "live official page; accessed 2026-08-18", "url": "https://www.jst-mfg.com/product/index.php?lang=2&series=58", "use_boundary": "RATIO COMPARISON ONLY; APPLICATION DERATING AND TEMPERATURE RISE OPEN", "warning": WARNING},
        {"basis_id": "DTS-B04", "parameter": "rejected predecessor comparison DCR", "value": "79 ohm/km at 20 C", "source": "existing ACK-S10 primary-source record", "revision_or_access": "accessed 2026-08-16", "url": "https://www.igus.cn/zh-CN/product/CF9_UL?artNr=CF9.UL.02.02&category=control-cable", "use_boundary": "SENSITIVITY ONLY; NOT CF130 OR SELECTED CONDUCTOR DATA", "warning": WARNING},
        {"basis_id": "DTS-B05", "parameter": "copper resistance temperature coefficient", "value": "0.00393 per degree C from 20 C", "source": "engineering planning coefficient", "revision_or_access": "P0.1 method assumption", "url": "N/A", "use_boundary": "COMPARISON TEMPERATURE SENSITIVITY ONLY; RECEIVED-CABLE MEASUREMENT CONTROLS", "warning": WARNING},
    ])

    max_drop = max(float(row["bounded_peak_drop_80c_comparison_v"]) for row in axis_rows)
    max_loss = max(float(row["bounded_rms_loss_80c_comparison_w"]) for row in axis_rows)
    status = {
        "identifier": IDENTIFIER, "warning": WARNING, "generated_utc": datetime.now(timezone.utc).isoformat(),
        "axis_count": 25, "bus_count": 8, "power_corridor_count": len(corridor_rows), "sample_count": len(samples),
        "maximum_bounded_peak_drop_80c_comparison_v": max_drop,
        "maximum_axis_bounded_rms_loss_80c_comparison_w": max_loss,
        "bounded_torque_component_computed": True, "route_lengths_bound": True, "corridor_bundle_counts_computed": True,
        "total_normal_rms_released": False, "cf130_resistance_verified": False, "wire_selected": False,
        "contact_derating_validated": False, "branch_protection_selected": False, "thermal_validated": False,
        "procurement_authority": False, "fabrication_authority": False, "connection_authority": False,
        "powered_test_authority": False, "motion_authority": False, "energization_authority": False,
    }
    (OUT / "duty-thermal-status.json").write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8", newline="\n")
    (OUT / "README.md").write_text(f"""# HR-30 harness duty and thermal planning screen P0.1

**{WARNING}**

This package binds both frozen whole-body sequence traces to every physical actuator power route, electrical bus and reserved power corridor. It computes pooled bounded torque-producing peak/P95/RMS/mean current, route-specific comparison voltage drop and I²R loss, contact headline ratios, bundle obligations and eight physical test families.

The complete normal current is not known. The 79 ohm/km comparison is the already rejected predecessor sensitivity—not CF130 data. Alpha Wire 3051's official nominal DCR is a separate all-route reference even though only a short fixed pigtail is proposed. Final cable splits, hot resistance, connector temperature, faults, protection, regeneration and all physical tests remain open.
""", encoding="utf-8", newline="\n")
    (OUT / "index.html").write_text(render_page(axis_rows, bus_rows, corridor_rows, contact_rows), encoding="utf-8", newline="\n")
    shutil.copy2(__file__, OUT / "duty-thermal-screen-source.py")
    manifest = [{"file": path.name, "bytes": path.stat().st_size, "sha256": sha(path), "warning": WARNING}
                for path in sorted(OUT.iterdir()) if path.is_file() and path.name != "file-manifest.csv"]
    write_csv(OUT / "file-manifest.csv", manifest)
    if REL.exists():
        shutil.rmtree(REL)
    shutil.copytree(OUT, REL)

    readme = """## Route-specific duty and thermal planning

The [interactive duty/thermal screen](duty-thermal-screen-p0.1/index.html) binds the two frozen whole-body sequence traces to all 25 routed actuator power pairs, eight electrical buses and every reserved power corridor. It supplies bounded torque-current drop/loss and bundle test cases, while keeping total normal current, CF130 resistance, hot ampacity, faults, protection and all powered work open."""
    index = """<section id='duty-thermal'><h2>Every actuator route now has a bounded loss case</h2><div class='grid'><article class='card pass'><div class='metric'>25 / 25</div><p>physical power routes bound to pooled whole-body duty.</p></article><article class='card pass'><div class='metric'>8</div><p>bus-domain loss and peak/RMS screens.</p></article><article class='card'><div class='metric'>6</div><p>power-corridor bundle obligations.</p></article><article class='card hold'><div class='metric'>0</div><p>released hot ratings or executed thermal tests.</p></article></div><p><a href='duty-thermal-screen-p0.1/index.html'>Open the route-specific duty and thermal planning guide.</a></p></section>"""
    body_readme = """## Whole-body harness duty/thermal screen

The [route-specific harness duty/thermal guide](harness/duty-thermal-screen-p0.1/index.html) connects both frozen walking traces to all 25 physical power-pair lengths, eight buses and six reserved power corridors. The derived loss cases define physical test obligations; they do not release conductors, contacts, protection or energization."""
    body_index = """<section id='harness-duty-thermal'><h2>The whole-body duty now reaches the physical harness</h2><div class='grid'><article class='card pass'><div class='metric'>25</div><p>axis route-specific loss cases</p></article><article class='card pass'><div class='metric'>6</div><p>bundle test obligations</p></article><article class='card hold'><div class='metric'>0</div><p>thermal or powered-work approvals</p></article></div><p><a href='harness/duty-thermal-screen-p0.1/index.html'>Open the harness duty/thermal guide.</a></p></section>"""
    physical_readme = """## Duty/thermal successor

The [route-specific duty/thermal successor](../duty-thermal-screen-p0.1/index.html) now fills the bounded torque-producing RMS and peak component for every entry in this package's derating register and groups the 25 pairs by physical power corridor. Total normal RMS, fault current, ambient, hot derating and physical tests remain open."""
    physical_index = """<section id='physical-duty-thermal'><h2>The routed harness now has bounded electrical loss cases</h2><div class='grid'><article class='card pass'><div class='metric'>25</div><p>power pairs with bounded peak/RMS inputs.</p></article><article class='card'><div class='metric'>6</div><p>corridor bundle groups.</p></article><article class='card hold'><h3>No hot rating</h3><p>CF130 DCR, ambient, faults and physical temperature-rise tests remain open.</p></article></div><p><a href='../duty-thermal-screen-p0.1/index.html'>Open the duty/thermal successor.</a></p></section>"""
    replace_marker(HARNESS / "README.md", "<!-- HR30-DUTY-THERMAL-P01-START -->", "<!-- HR30-DUTY-THERMAL-P01-END -->", readme)
    replace_marker(HARNESS / "index.html", "<!-- HR30-DUTY-THERMAL-P01-START -->", "<!-- HR30-DUTY-THERMAL-P01-END -->", index)
    replace_marker(BODY / "README.md", "<!-- HR30-DUTY-THERMAL-P01-START -->", "<!-- HR30-DUTY-THERMAL-P01-END -->", body_readme)
    replace_marker(BODY / "index.html", "<!-- HR30-DUTY-THERMAL-P01-START -->", "<!-- HR30-DUTY-THERMAL-P01-END -->", body_index)
    replace_marker(PHYSICAL / "README.md", "<!-- HR30-DUTY-THERMAL-P01-START -->", "<!-- HR30-DUTY-THERMAL-P01-END -->", physical_readme)
    replace_marker(PHYSICAL / "index.html", "<!-- HR30-DUTY-THERMAL-P01-START -->", "<!-- HR30-DUTY-THERMAL-P01-END -->", physical_index)
    print(json.dumps(status, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
