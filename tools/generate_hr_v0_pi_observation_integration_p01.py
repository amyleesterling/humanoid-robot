#!/usr/bin/env python3
"""Generate R205 panel-placement and harness-route integration evidence."""

from __future__ import annotations

import csv
import hashlib
import html
import json
import math
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ENG = ROOT / "electrical/integration/hr-v0-pi-observation-integration-p0.1"
WEB = ROOT / "release/hr-v0/pi-observation-integration-p0.1"
DOC = ROOT / "docs/hr-v0-pi-observation-integration-p0.1.md"
IDENTIFIER = "HR-V0-PI-OBS-INTEGRATION-P0.1"
ROUND = "R205"
DATE = "2026-08-10"
WARNING = "PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION"

PANEL = ROOT / "electrical/panel/hr-v0-control-panel-p0.6"
R161 = ROOT / "electrical/integration/hr-v0-dxl-carrier-integration-p0.1"
R202 = ROOT / "electrical/kicad/hr-v0-runtime-observation-carrier-p0.2"
R204 = ROOT / "electrical/kicad/hr-v0-pi-observation-carrier-p0.1"

SOURCES = {
    "electrical/panel/hr-v0-control-panel-p0.6/backplate-layout.csv": PANEL / "backplate-layout.csv",
    "electrical/panel/hr-v0-control-panel-p0.6/thermal-space-screen.csv": PANEL / "thermal-space-screen.csv",
    "electrical/integration/hr-v0-dxl-carrier-integration-p0.1/panel-placement-screen.csv": R161 / "panel-placement-screen.csv",
    "electrical/kicad/hr-v0-runtime-observation-carrier-p0.2/connector-schedule.csv": R202 / "connector-schedule.csv",
    "electrical/kicad/hr-v0-runtime-observation-carrier-p0.2/pcb-placement.csv": R202 / "pcb-placement.csv",
    "electrical/kicad/hr-v0-runtime-observation-carrier-p0.2/hr-v0-runtime-observation-carrier-p0.2.kicad_pcb": R202 / "hr-v0-runtime-observation-carrier-p0.2.kicad_pcb",
    "electrical/kicad/hr-v0-pi-observation-carrier-p0.1/connector-schedule.csv": R204 / "connector-schedule.csv",
    "electrical/kicad/hr-v0-pi-observation-carrier-p0.1/pcb-placement.csv": R204 / "pcb-placement.csv",
    "electrical/kicad/hr-v0-pi-observation-carrier-p0.1/harness-interface.csv": R204 / "harness-interface.csv",
}

# Panel coordinates are millimetres from the P0.6 backplate top-left planning datum.
BP = (0.0, 0.0, 533.4, 685.8)
WD2 = (383.8, 10.0, 40.0, 665.8)
CCASE1 = (433.0, 55.0, 90.5, 87.0)
GTM3 = (440.0, 250.0, 63.5, 25.4)
PROTECTION_RESERVE = (250.0, 375.0, 127.8, 140.0)
OBS = (433.0, 300.0, 90.0, 120.0)  # R202 board rotated 90 degrees counterclockwise.

# R204 carrier is shown centred inside CCASE1 only as a reference transform.
PI_CARRIER = (445.75, 70.25, 65.0, 56.5)


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def ccw(x: float, y: float, width: float = 120.0) -> tuple[float, float]:
    """Rotate a source-board point 90 degrees counterclockwise into its bbox."""
    return y, width - x


def global_obs(x: float, y: float) -> tuple[float, float]:
    dx, dy = ccw(x, y)
    return OBS[0] + dx, OBS[1] + dy


def manhattan(points: list[tuple[float, float]]) -> float:
    return sum(abs(b[0] - a[0]) + abs(b[1] - a[1]) for a, b in zip(points, points[1:]))


def point(value: tuple[float, float]) -> str:
    return f"({value[0]:.2f}, {value[1]:.2f})"


def manifest(directory: Path) -> None:
    target = directory / "SOURCE-MANIFEST.csv"
    rows = []
    for path in sorted(directory.rglob("*")):
        if path.is_file() and path != target:
            rows.append({"file": path.relative_to(directory).as_posix(), "sha256": sha256(path).upper()})
    write_csv(target, rows)


def main() -> int:
    for source in SOURCES.values():
        if not source.is_file():
            raise FileNotFoundError(source)
    ENG.mkdir(parents=True, exist_ok=True)
    WEB.mkdir(parents=True, exist_ok=True)

    jobs = (PI_CARRIER[0] + 32.5, PI_CARRIER[1] + 49.0)
    jlogic = global_obs(114.0, 45.0)
    jfield = global_obs(6.0, 45.0)
    xt1_surrogate = (274.0, 342.0)
    duct_x = WD2[0] + WD2[2] / 2.0
    compute_route = [jobs, (duct_x, jobs[1]), (duct_x, jlogic[1]), jlogic]
    field_route = [jfield, (duct_x, jfield[1]), (duct_x, xt1_surrogate[1]), xt1_surrogate]
    compute_length = manhattan(compute_route)
    field_length = manhattan(field_route)

    placements = [
        {
            "placement_id": "PIOI-PLC-001", "reference": "OBS1 / R202 carrier", "role": "four-channel diagnostic receiver",
            "x_mm": "433.0", "y_mm": "300.0", "width_mm": "90.0", "height_mm": "120.0", "rotation": "90 deg counterclockwise",
            "basis": "R202 120 x 90 mm source outline; rotated transform x'=y, y'=120-x",
            "state": "ANALYTICAL PLACEMENT CANDIDATE - NO DRILLING", "required_evidence": "received PCB and backplate dimensions; standoffs; connector sweep; depth; airflow; service access; qualified review", "warning": WARNING,
        },
        {
            "placement_id": "PIOI-PLC-002", "reference": "PIOBS1 / R204 carrier", "role": "Pi-side passive observation carrier",
            "x_mm": "445.75", "y_mm": "70.25", "width_mm": "65.0", "height_mm": "56.5", "rotation": "0 deg reference only",
            "basis": "centred inside CCASE1 90.5 x 87 mm plan envelope solely to derive a nominal route screen",
            "state": "REFERENCE TRANSFORM ONLY - RECEIVED OFFSET UNKNOWN", "required_evidence": "received Pi/case/bracket/stack transform; connector overhang; cooler clearance; case access; service and retention", "warning": WARNING,
        },
    ]
    write_csv(ENG / "panel-placement.csv", placements)

    collision_rows = [
        ("PIOI-CLR-001", "OBS1", "backplate right edge", "10.4", "mm planar", "ANALYTICAL PASS", "received edge keepout and connector sweep"),
        ("PIOI-CLR-002", "OBS1", "WD2 right edge", "9.2", "mm planar", "ANALYTICAL PASS", "received duct cover and board/connector sweep"),
        ("PIOI-CLR-003", "OBS1", "GTM3 lower edge", "24.6", "mm planar", "ANALYTICAL PASS", "received cable bend and retention sweep"),
        ("PIOI-CLR-004", "OBS1", "protection reserve right edge", "55.2", "mm planar", "ANALYTICAL PASS", "selected protection parts and service sweep"),
        ("PIOI-CLR-005", "OBS1", "nearest R161 DXL carrier top edge", "118.0", "mm planar", "ANALYTICAL PASS", "R161 placements remain unreleased; received combined-layout review"),
        ("PIOI-CLR-006", "OBS1", "backplate lower edge", "265.8", "mm planar", "ANALYTICAL PASS", "received enclosure and backplate fit"),
        ("PIOI-CLR-007", "PIOBS1", "CCASE1 left/right plan edges", "12.75", "mm nominal each side", "REFERENCE ONLY", "received Pi/case/bracket/stack transform"),
        ("PIOI-CLR-008", "PIOBS1", "CCASE1 top/bottom plan edges", "15.25", "mm nominal each side", "REFERENCE ONLY", "received Pi/case/bracket/stack transform"),
        ("PIOI-CLR-009", "compute harness", "GTM1/GTM2/GTM3 bodies", "no planar intersection", "WD2 centreline route", "ANALYTICAL PASS", "duct entry/exit, cover, fill, separation and retention"),
        ("PIOI-CLR-010", "compute vs field harness", "WD2 occupied spans", "36.0", "mm nominal vertical gap", "ANALYTICAL PASS", "bundle diameters, bends, partitioning and installed inspection"),
    ]
    write_csv(ENG / "collision-clearance-register.csv", [
        {"clearance_id": a, "subject": b, "other": c, "screened_clearance": d, "basis": e, "result": f, "required_evidence": g, "warning": WARNING}
        for a, b, c, d, e, f, g in collision_rows
    ])

    holes = []
    for ref, x, y in (("MH1", 4.5, 4.5), ("MH2", 115.5, 4.5), ("MH3", 4.5, 85.5), ("MH4", 115.5, 85.5)):
        gx, gy = global_obs(x, y)
        holes.append({"hole": ref, "source_x_mm": f"{x:.1f}", "source_y_mm": f"{y:.1f}", "candidate_panel_x_mm": f"{gx:.1f}", "candidate_panel_y_mm": f"{gy:.1f}", "source_hole": "3.2 mm M3 NPTH candidate", "panel_hole": "SELECTION REQUIRED - DO NOT DRILL", "required_evidence": "received hole metrology; selected standoff/fastener; edge and coating review; drill process; load and service proof", "warning": WARNING})
    write_csv(ENG / "mounting-hole-screen.csv", holes)

    route_rows = []
    for route_id, route_role, conductor_count, path, start_basis, end_basis in (
        ("PIOI-ROUTE-COMPUTE", "R204 JOBS1 to R202 JLOGIC1", 6, compute_route, "R204 carrier centred-reference JOBS1", "R202 rotated-source JLOGIC1"),
        ("PIOI-ROUTE-FIELD", "R202 JFIELD1 to XT1 field status group", 5, field_route, "R202 rotated-source JFIELD1", "P0.6 XT1 envelope-centre surrogate"),
    ):
        for index, coord in enumerate(path):
            route_rows.append({"route_id": route_id, "route_role": route_role, "conductor_count": conductor_count, "node": index, "x_mm": f"{coord[0]:.2f}", "y_mm": f"{coord[1]:.2f}", "node_basis": start_basis if index == 0 else end_basis if index == len(path) - 1 else "WD2 nominal centreline", "state": "ROUTE SCREEN ONLY - DO NOT CUT OR INSTALL", "warning": WARNING})
    write_csv(ENG / "harness-route.csv", route_rows)

    length_rows = [
        {"route_id": "PIOI-ROUTE-COMPUTE", "nominal_centerline_mm": f"{compute_length:.1f}", "equation": "|478.25-403.8| + |306.0-119.25| + |478.0-403.8|", "cut_length_mm": "SELECTION REQUIRED", "unknown_addends": "received Pi/case offset; connector exit; bend correction; service loop; termination allowance; strain relief; tolerance", "state": "GEOMETRIC SCREEN ONLY", "warning": WARNING},
        {"route_id": "PIOI-ROUTE-FIELD", "nominal_centerline_mm": f"{field_length:.1f}", "equation": "|478.0-403.8| + |414.0-342.0| + |403.8-274.0|", "cut_length_mm": "SELECTION REQUIRED", "unknown_addends": "exact XT1 terminal coordinates; connector exit; bend correction; service loop; termination allowance; strain relief; tolerance", "state": "GEOMETRIC SCREEN ONLY", "warning": WARNING},
    ]
    write_csv(ENG / "harness-length-calculation.csv", length_rows)

    field_map = [
        ("1", "SR1_STATUS", "XT1-03", "JFIELD1.1"), ("2", "SRA1_STATUS", "XT1-04", "JFIELD1.2"),
        ("3", "K1_STATUS", "XT1-05", "JFIELD1.3"), ("4", "K2_STATUS", "XT1-06", "JFIELD1.4"),
        ("5", "SAFETY_0V", "XT1-02", "JFIELD1.5"),
    ]
    logic_map = [
        ("1", "PI_3V3_CANDIDATE", "JLOGIC1.1", "JOBS1.1"), ("2", "COMPUTE_0V", "JLOGIC1.2", "JOBS1.2"),
        ("3", "OBS_SR1_PI", "JLOGIC1.3", "JOBS1.3"), ("4", "OBS_SRA1_PI", "JLOGIC1.4", "JOBS1.4"),
        ("5", "OBS_K1_PI", "JLOGIC1.5", "JOBS1.5"), ("6", "OBS_K2_PI", "JLOGIC1.6", "JOBS1.6"),
    ]
    interface_rows = []
    for domain, rows in (("FIELD", field_map), ("COMPUTE", logic_map)):
        for pin, net, start, end in rows:
            interface_rows.append({"domain": domain, "conductor": pin, "net": net, "from": start, "to": end, "parity_result": "SOURCE-PARITY PASS", "physical_state": "NOT BUILT / NOT CONNECTED", "warning": WARNING})
    write_csv(ENG / "interface-parity.csv", interface_rows)

    source_rows = [
        ("PIOI-SRC-001", "Control panel P0.6", "backplate-layout.csv and thermal-space-screen.csv", "nominal backplate, WD2, CCASE1, GTM3, XT1 and reserve envelopes", "received fit, depth, duct fill, holes or installed separation"),
        ("PIOI-SRC-002", "R161 DXL integration", "panel-placement-screen.csv", "three provisional lower-zone carrier rectangles", "combined physical layout or mounting release"),
        ("PIOI-SRC-003", "R202 runtime observation carrier", "native PCB, connector schedule and placement", "120 x 90 mm source outline plus JFIELD1/JLOGIC1 and hole coordinates", "fabrication, assembly, received article or electrical performance"),
        ("PIOI-SRC-004", "R204 Pi observation carrier", "native connector schedule, placement and harness interface", "65 x 56.5 mm reference outline, JOBS1 coordinate and six exact net mappings", "received stack transform, case fit, harness or powered behavior"),
    ]
    write_csv(ENG / "source-register.csv", [{"source_id": a, "source": b, "controlled_artifact": c, "controlled_fact": d, "not_proved": e, "warning": WARNING} for a, b, c, d, e in source_rows])

    hold_topics = [
        "received P0.6 backplate and enclosure datums, usable edge keepouts and closed-cover depth",
        "received R202 PCB dimensions, connector overhang and four-hole metrology",
        "exact observation-carrier standoffs, fasteners, locking, coating treatment and load proof",
        "received Pi 5, PI5-CASE-D, rail bracket, cooler, R204 socket and carrier stack transform",
        "fabricator and assembler acceptance of R202 and R204 native candidates",
        "exact WD2 entry/exit geometry, fill, cover fit, bend radii, partitions and domain separation",
        "exact XT1 terminal coordinates and accepted five-wire field harness stock/termination schedule",
        "six-wire Pi harness measured route, exact cut lengths, labels, retention and service loop",
        "five-wire field harness measured route, exact cut lengths, labels, retention and service loop",
        "direct-strip preparation, torque, exposed-strand, pull, retorque and inspection process",
        "3.3 V loading, startup/shutdown, brownout, back-power and cable-fault acceptance",
        "continuity, polarity, isolation, EMC, thermal, fault-injection and HIL evidence",
        "qualified electrical, panel-layout and functional-safety review plus separate written work authority",
    ]
    write_csv(ENG / "selection-holds.csv", [{"hold_id": f"PIOI-HOLD-{i:03d}", "topic": topic, "state": "OPEN - SELECTION/EVIDENCE REQUIRED", "evidence_uri": "", "warning": WARNING} for i, topic in enumerate(hold_topics, 1)])

    acceptance_topics = [
        "source hash and interface parity", "nominal panel boundary/no-overlap", "received backplate/enclosure fit", "received R202/R204 geometry",
        "mounting hardware and hole process", "case/cooler/stack fit", "WD2 fill and separation", "compute harness measured route and cut schedule",
        "field harness measured route and cut schedule", "termination-process qualification", "continuity/polarity/isolation", "power sequencing and back-power",
        "thermal and EMC", "fault injection and HIL", "qualified review", "separate written work authorization",
    ]
    write_csv(ENG / "acceptance-matrix.csv", [{"acceptance_id": f"PIOI-ACC-{i:03d}", "subject": topic, "execution_state": "NOT EXECUTED", "result": "OPEN", "evidence_uri": "", "approver": "", "approval_date": "", "warning": WARNING} for i, topic in enumerate(acceptance_topics, 1)])

    status = {
        "identifier": IDENTIFIER, "round": ROUND, "date": DATE,
        "panel_baseline": "HR-V0-CP-P0.6", "observation_carrier": "HR-V0-RUNTIME-OBS-CARRIER-P0.2", "pi_carrier": "HR-V0-PI-OBS-CARRIER-P0.1",
        "placement_rows": len(placements), "clearance_rows": len(collision_rows), "mounting_hole_rows": len(holes), "route_node_rows": len(route_rows),
        "interface_rows": len(interface_rows), "selection_holds": len(hold_topics), "acceptance_rows": len(acceptance_topics),
        "compute_nominal_centerline_mm": round(compute_length, 1), "field_nominal_centerline_mm": round(field_length, 1),
        "source_hashes": {key: sha256(path) for key, path in SOURCES.items()},
        "nominal_boundary_screen_passed": True, "nominal_overlap_screen_passed": True, "source_interface_parity_passed": True,
        "cut_lengths_selected": False, "panel_layout_superseded": False, "mounting_released": False, "harness_released": False,
        "physical_article_exists": False, "physical_test_executed": False, "qualified_review_complete": False,
        "procurement_authorized": False, "fabrication_authorized": False, "assembly_authorized": False, "connection_authorized": False,
        "powered_testing_authorized": False, "motion_authorized": False, "energization_authorized": False, "safety_credit": False,
        "warning": WARNING,
    }
    write_text(ENG / "package-status.json", json.dumps(status, indent=2) + "\n")

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 760 760" role="img" aria-labelledby="title desc">
<title id="title">R205 observation electronics panel integration screen</title><desc id="desc">Nominal P0.6 backplate with compute carrier, observation receiver, DXL carrier candidates and two unreleased harness route screens.</desc>
<style>.label{{font:700 16px system-ui,sans-serif;fill:#082b55}}.note{{font:14px system-ui,sans-serif;fill:#082b55}}.small{{font:13px system-ui,sans-serif;fill:#082b55}}.bp{{fill:#f6fbff;stroke:#082b55;stroke-width:3}}.duct{{fill:#d9e4ec;stroke:#37566d;stroke-width:2}}.compute{{fill:#dff3ff;stroke:#0b4f8a;stroke-width:2}}.obs{{fill:#ffe28a;stroke:#9b6700;stroke-width:3}}.dxl{{fill:#e8eef3;stroke:#527086;stroke-width:2;stroke-dasharray:7 5}}.routec{{fill:none;stroke:#0b4f8a;stroke-width:5}}.routef{{fill:none;stroke:#c17a00;stroke-width:5}}.hold{{fill:#fff8db;stroke:#9b6700;stroke-width:2;stroke-dasharray:8 5}}</style>
<rect x="25" y="25" width="533.4" height="685.8" class="bp"/><text x="35" y="50" class="label">P0.6 nominal backplate - no hole release</text>
<rect x="408.8" y="35" width="40" height="665.8" class="duct"/><text x="416" y="690" class="small">WD2</text>
<text x="462" y="72" class="label">CCASE1 / Pi stack area</text><rect x="458" y="80" width="90.5" height="87" class="compute"/><rect x="470.75" y="95.25" width="65" height="56.5" class="compute"/><text x="478" y="128" class="small">R204 ref.</text>
<rect x="465" y="185" width="63.5" height="25.4" class="compute"/><text x="471" y="202" class="small">GTM1</text><rect x="465" y="230" width="63.5" height="25.4" class="compute"/><text x="471" y="247" class="small">GTM2</text><rect x="465" y="275" width="63.5" height="25.4" class="compute"/><text x="471" y="292" class="small">GTM3</text>
<rect x="458" y="325" width="90" height="120" class="obs"/><text x="466" y="350" class="label">OBS1</text><text x="466" y="372" class="note">R202 receiver</text><text x="466" y="394" class="note">90 deg CCW</text><text x="466" y="416" class="note">90 x 120 mm</text>
<rect x="79" y="558" width="100" height="60" class="dxl"/><rect x="189" y="558" width="100" height="60" class="dxl"/><rect x="79" y="628" width="100" height="60" class="dxl"/><text x="84" y="582" class="note">R161 DXL</text><text x="194" y="582" class="note">R161 DXL</text><text x="84" y="652" class="note">R161 DXL</text>
<rect x="275" y="400" width="127.8" height="140" class="hold"/><text x="283" y="425" class="note">Protection reserve</text><rect x="249" y="343" width="100" height="48" class="hold"/><text x="260" y="359" class="label">XT1 surrogate</text>
<polyline points="503.25,144.25 428.8,144.25 428.8,331 503,331" class="routec"/><polyline points="503,439 428.8,439 428.8,367 299,367" class="routef"/>
<text x="575" y="145" class="label">Compute route</text><text x="575" y="168" class="note">335.4 mm nominal</text><text x="575" y="190" class="note">cut: SELECTION REQUIRED</text><text x="575" y="440" class="label">Field route</text><text x="575" y="463" class="note">276.0 mm nominal</text><text x="575" y="485" class="note">cut: SELECTION REQUIRED</text>
<desc>{html.escape(WARNING)}</desc><text x="25" y="731" class="small"><tspan x="25">PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION,</tspan><tspan x="25" dy="17">POWERED TESTING, MOTION, OR ENERGIZATION</tspan></text></svg>'''
    write_text(ENG / "panel-integration.svg", svg)

    common_files = ["README.md", "panel-placement.csv", "collision-clearance-register.csv", "mounting-hole-screen.csv", "harness-route.csv", "harness-length-calculation.csv", "interface-parity.csv", "source-register.csv", "selection-holds.csv", "acceptance-matrix.csv", "package-status.json", "panel-integration.svg"]
    readme = f'''# {IDENTIFIER}\n\n> **{WARNING}**\n\nR205 integrates the R202 observation receiver and R204 Pi-side carrier into the current P0.6 planning geometry without changing or superseding P0.6. The rotated receiver candidate fits nominally in the compute column without overlapping the three R161 lower-zone DXL placements. Two route screens are explicit: {compute_length:.1f} mm compute-side and {field_length:.1f} mm field-side. Neither value is a cut length. Thirteen evidence holds and sixteen unexecuted acceptance rows remain open.\n'''
    write_text(ENG / "README.md", readme)
    for name in common_files:
        shutil.copy2(ENG / name, WEB / name)

    placement_html = "".join(f"<tr><td>{html.escape(r['reference'])}</td><td>{r['x_mm']}, {r['y_mm']}</td><td>{r['width_mm']} x {r['height_mm']}</td><td>{html.escape(r['rotation'])}</td><td>{html.escape(r['state'])}</td></tr>" for r in placements)
    length_html = "".join(f"<tr><td>{html.escape(r['route_id'])}</td><td>{r['nominal_centerline_mm']} mm</td><td><code>{html.escape(r['equation'])}</code></td><td>{r['cut_length_mm']}</td><td>{html.escape(r['unknown_addends'])}</td></tr>" for r in length_rows)
    holds_html = "".join(f"<tr><td>PIOI-HOLD-{i:03d}</td><td>{html.escape(topic)}</td><td>OPEN</td></tr>" for i, topic in enumerate(hold_topics, 1))
    page = f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{IDENTIFIER}</title><style>
:root{{--ink:#082b55;--blue:#0b4f8a;--sky:#dff3ff;--gold:#f5bd24;--paper:#f8fbff}}*{{box-sizing:border-box}}body{{margin:0;background:var(--paper);color:var(--ink);font:16px/1.55 system-ui,sans-serif}}header{{padding:clamp(1.5rem,4vw,3.5rem);background:linear-gradient(135deg,var(--sky),white);border-bottom:7px solid var(--gold)}}main{{max-width:1280px;margin:auto;padding:1rem}}h1{{font-size:clamp(2rem,5vw,4.2rem);line-height:1.05}}h2{{font-size:clamp(1.55rem,3vw,2.4rem)}}.warning{{background:var(--gold);border:3px solid #211700;padding:1rem;font-weight:850}}.metrics{{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:1rem;margin:1.5rem 0}}.metric{{background:white;border:2px solid var(--blue);border-radius:12px;padding:1rem}}.metric strong{{display:block;font-size:1.8rem}}.figure,.table{{overflow:auto;background:white;border:2px solid var(--blue);border-radius:10px;margin:1rem 0}}.figure img{{display:block;min-width:820px;width:100%;height:auto}}table{{border-collapse:collapse;min-width:1000px;width:100%}}th,td{{padding:.8rem;text-align:left;vertical-align:top;border-bottom:1px solid #adc9df}}th{{background:var(--ink);color:white}}code,small{{font-size:14px}}footer{{background:var(--ink);color:white;padding:1rem;margin-top:2rem}}a{{color:#075a96}}</style></head><body><header><div class="warning">{WARNING}</div><p>{IDENTIFIER} - {ROUND} - {DATE}</p><h1>The boards fit on paper. The wires still need measuring.</h1><p>A source-bound integration screen for the diagnostic receiver, Pi carrier and both harness domains. It changes no panel baseline and grants no work authority.</p></header><main><section class="metrics"><div class="metric"><strong>90 x 120 mm</strong>rotated receiver envelope</div><div class="metric"><strong>{compute_length:.1f} mm</strong>nominal compute route</div><div class="metric"><strong>{field_length:.1f} mm</strong>nominal field route</div><div class="metric"><strong>0</strong>released cut lengths</div><div class="metric"><strong>{len(hold_topics)}</strong>open holds</div></section><h2>Combined panel screen</h2><div class="figure"><img src="panel-integration.svg" alt="Nominal panel integration diagram with observation boards and two held harness routes"></div><p>The blue and gold paths use separate nominal WD2 spans. Clearances are planar arithmetic only; they do not prove depth, bend, fill, partitioning, temperature, or installed access.</p><h2>Candidate transforms</h2><div class="table"><table><thead><tr><th>Reference</th><th>Origin (mm)</th><th>Envelope</th><th>Rotation</th><th>State</th></tr></thead><tbody>{placement_html}</tbody></table></div><h2>Length arithmetic, not a cut schedule</h2><div class="table"><table><thead><tr><th>Route</th><th>Nominal centreline</th><th>Equation</th><th>Cut length</th><th>Missing terms</th></tr></thead><tbody>{length_html}</tbody></table></div><h2>Thirteen holds remain</h2><div class="table"><table><thead><tr><th>ID</th><th>Evidence needed</th><th>State</th></tr></thead><tbody>{holds_html}</tbody></table></div><p><a href="panel-placement.csv">placement schedule</a> - <a href="collision-clearance-register.csv">clearance register</a> - <a href="harness-route.csv">route nodes</a> - <a href="harness-length-calculation.csv">length calculations</a> - <a href="interface-parity.csv">interface parity</a> - <a href="acceptance-matrix.csv">acceptance matrix</a></p></main><footer>{WARNING}. Diagnostic-only integration candidate; zero functional-safety credit.</footer></body></html>'''
    write_text(WEB / "index.html", page)

    doc = f'''# HR-V0 Pi observation panel integration P0.1\n\n**{WARNING}**\n\n`{IDENTIFIER}` is a configuration-controlled analytical overlay, not a modification or release of control-panel P0.6. It resolves a source-level placement conflict: R161 already occupies the lower reserve with three DXL carrier candidates, so R202 is instead rotated 90 degrees counterclockwise at nominal panel origin `(433.0, 300.0)` in the compute column.\n\nThe source transform places `JLOGIC1` at `{point(jlogic)}` and `JFIELD1` at `{point(jfield)}`. A reference-only centred R204 transform places `JOBS1` at `{point(jobs)}`; its real position remains unknown until received stack metrology. The resulting WD2 route screens are {compute_length:.1f} mm on the six-wire compute side and {field_length:.1f} mm on the five-wire field side. Both final cut lengths remain `SELECTION REQUIRED`.\n\nThe overlay records ten planar clearance screens, four transformed mounting-hole coordinates, eleven interface-parity rows, thirteen open evidence holds and sixteen unexecuted acceptance rows. It proves no depth, mounting, duct fill, separation, cut length, termination, physical fit, electrical performance, functional safety or work authority.\n'''
    write_text(DOC, doc)
    write_text(ROOT / "docs/reviews/2026-08-10-r205-independent-review-request.md", f'''# R205 independent review request\n\n**{WARNING}**\n\nReview `{IDENTIFIER}` as a source-bound analytical panel/harness integration candidate only. Independently reproduce the R202 90-degree counterclockwise transform, all four hole coordinates, ten planar clearance screens, 335.4 mm compute-route and 276.0 mm field-route arithmetic, and all eleven source interface mappings. Check that R161 lower-zone carrier placements are not double-booked; that compute and field route segments remain physically separated in the nominal drawing; and that neither geometric number is represented as a cut length.\n\nChallenge the WD2 routing, case/stack reference assumption, XT1 surrogate, connector sweeps, depth, duct fill, domain separation, termination, grounding, power sequencing, back-power, EMC, thermal and fault evidence boundaries. Confirm all thirteen holds and sixteen acceptance rows remain open and that no procurement, fabrication, assembly, connection, powered test, motion, energization or safety credit is granted.\n''')
    write_text(ROOT / "docs/reviews/2026-08-10-r205-validation-record.md", f'''# R205 validation record\n\n**{WARNING}**\n\nR205 issues `{IDENTIFIER}` without changing P0.6, R161, R202 or R204 source. The R202 120 x 90 mm board is rotated into a 90 x 120 mm compute-column candidate at `(433.0, 300.0)`. Ten nominal planar screens show no encoded rectangle overlap, including 9.2 mm to WD2, 24.6 mm to GTM3, 55.2 mm to the protection reserve and 118.0 mm to the nearest R161 carrier.\n\nSource-coordinate transformation places `JLOGIC1` at `{point(jlogic)}` and `JFIELD1` at `{point(jfield)}`. The centred R204 reference transform places `JOBS1` at `{point(jobs)}` but is explicitly not a received transform. The two Manhattan route screens reproduce {compute_length:.1f} mm and {field_length:.1f} mm. Every cut length remains `SELECTION REQUIRED`; all thirteen holds and sixteen acceptance rows remain open.\n\nPassing repository checks prove deterministic source parity and arithmetic only. No physical article, Sol R12 finding, requirement, gate, qualified review, safety credit or work authority closes.\n''')
    write_text(ROOT / "docs/reviews/2026-08-10-sol-r12-post-r205-status.md", f'''# Sol R12 status after R205\n\n**{WARNING}**\n\nR205 responds narrowly to the missing panel/harness integration evidence behind Sol's buildability finding. It avoids double-booking the R161 lower reserve, places the R202 candidate in the compute column, source-transforms its connectors and holes, and exposes two explicit but unreleased route calculations.\n\nNo Sol finding closes. The placement is analytical; the Pi transform is reference-only; XT1 is a surrogate; cut lengths, mounting, enclosure depth, duct fill, domain separation, terminations, received fit, power sequencing, back-power, EMC, thermal, fault injection, HIL and qualified review remain absent. R205 does not provide a complete buildable machine, functional-safety allocation, stopping validation, common-cause analysis, accepted fabrication data, mass/inertia closure, continuous leg torque evidence or physical test evidence.\n\nSol R12 remains controlling independent-review input. R205 supplies no procurement, fabrication, assembly, connection, powered-test, motion or energization authority.\n''')

    manifest(ENG)
    manifest(WEB)
    print(f"{IDENTIFIER}: {compute_length:.1f} mm compute / {field_length:.1f} mm field route screens")
    print(f"{len(hold_topics)} holds and {len(acceptance_topics)} acceptance rows remain open; zero work authority")
    print(WARNING)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
