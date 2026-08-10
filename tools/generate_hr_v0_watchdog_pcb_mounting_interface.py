"""Generate the R131 watchdog-PCB current-source and mounting-interface package.

PRELIMINARY - NOT APPROVED FOR FABRICATION OR ENERGIZATION.
"""

from __future__ import annotations

import csv
import html
import json
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "electrical" / "panel" / "hr-v0-watchdog-pcb-mounting-p0.1"
WEB = ROOT / "release" / "hr-v0" / "watchdog-pcb-mounting-p0.1"
IDENTIFIER = "HR-V0-WD-MOUNT-IF-P0.1"
WARNING = "PRELIMINARY - NOT APPROVED FOR FABRICATION OR ENERGIZATION"


def write_csv(name: str, fieldnames: list[str], rows: list[dict[str, object]]) -> None:
    with (OUT / name).open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def table(rows: list[dict[str, object]], columns: list[tuple[str, str]]) -> str:
    head = "".join(f"<th>{html.escape(label)}</th>" for _, label in columns)
    body = "".join(
        "<tr>" + "".join(f"<td>{html.escape(str(row[key]))}</td>" for key, _ in columns) + "</tr>"
        for row in rows
    )
    return f'<div class="table"><table><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></div>'


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    WEB.mkdir(parents=True, exist_ok=True)

    old_center = 4.4
    old_pad_x = 2.0
    new_center = 4.765
    new_pad_x = 1.52
    old_gap = 2 * old_center - old_pad_x
    old_span = 2 * old_center + old_pad_x
    new_gap = 2 * new_center - new_pad_x
    new_span = 2 * new_center + new_pad_x

    reconciliation = [
        {
            "record_id": "WDM-REC-001",
            "configuration": "PCB-P0.5 immutable historical CAM source",
            "pad_centers_x_mm": "+/-4.400",
            "pad_size_mm": "2.00 x 1.60",
            "derived_inner_gap_mm": f"{old_gap:.3f}",
            "derived_overall_span_mm": f"{old_span:.3f}",
            "disposition": "SUPERSEDED - DOES NOT MEET CONTROLLED OPTION-7 GEOMETRY",
            "evidence": "release/hr-v0/watchdog-pcb-fabrication-candidate-p0.1/source/project-button-v3.kicad_pcb",
        },
        {
            "record_id": "WDM-REC-002",
            "configuration": "PCB-P0.6 current native board",
            "pad_centers_x_mm": "+/-4.765",
            "pad_size_mm": "1.52 x 1.78",
            "derived_inner_gap_mm": f"{new_gap:.3f}",
            "derived_overall_span_mm": f"{new_span:.3f}",
            "disposition": "CURRENT SOURCE GEOMETRY MATCHES CONTROLLED VISHAY OPTION-7 LAND DIMENSIONS",
            "evidence": "electrical/kicad/project-button-v3/project-button-v3.kicad_pcb",
        },
    ]
    write_csv("current-board-reconciliation.csv", list(reconciliation[0]), reconciliation)

    hole_board = [("MH1", 5.0, 5.0), ("MH2", 155.0, 5.0), ("MH3", 5.0, 95.0), ("MH4", 155.0, 95.0)]
    holes = []
    for ref, x, y in hole_board:
        holes.append({
            "reference": ref,
            "board_x_from_left_mm": f"{x:.3f}",
            "board_y_from_top_mm": f"{y:.3f}",
            "panel_x_candidate_mm": f"{54.0 + x:.3f}",
            "panel_y_candidate_mm": f"{230.0 + y:.3f}",
            "hole_diameter_mm": "3.200",
            "board_edge_distance_x_mm": f"{min(x, 160.0-x):.3f}",
            "board_edge_distance_y_mm": f"{min(y, 100.0-y):.3f}",
            "release_state": "COORDINATE CANDIDATE ONLY - NO PANEL DRILLING",
        })
    write_csv("mount-coordinate-register.csv", list(holes[0]), holes)

    candidates = [
        {"candidate_id": "WDM-ST-010", "manufacturer": "Harwin", "manufacturer_part_number": "R30-1611000", "body_length_mm": "10.000", "thread": "M3 female-female through-threaded", "across_flats_mm": "5.500", "material": "Polyamide 66; UL94V-2", "unit_mass_g": "0.226", "state": "EXACT CATALOG CANDIDATE - NOT SELECTED", "selection_evidence_needed": "received THT lead-trim envelope; underside clearance; thread engagement; torque; screw/washer selection; vibration proof", "source": "https://www.harwin.com/products/R30-1611000"},
        {"candidate_id": "WDM-ST-013", "manufacturer": "Harwin", "manufacturer_part_number": "R30-1611300", "body_length_mm": "13.000", "thread": "M3 female-female", "across_flats_mm": "5.500", "material": "Polyamide 66; UL94V-2", "unit_mass_g": "0.294", "state": "EXACT CATALOG CANDIDATE - NOT SELECTED", "selection_evidence_needed": "received THT lead-trim envelope; underside clearance; thread engagement; torque; screw/washer selection; vibration proof", "source": "https://www.harwin.com/products/R30-1611300"},
        {"candidate_id": "WDM-ST-015", "manufacturer": "Harwin", "manufacturer_part_number": "R30-1611500", "body_length_mm": "15.000", "thread": "M3 female-female; 6 mm minimum threaded both ends", "across_flats_mm": "5.500", "material": "Polyamide 66; UL94V-2", "unit_mass_g": "0.339", "state": "EXACT CATALOG CANDIDATE - NOT SELECTED", "selection_evidence_needed": "received THT lead-trim envelope; underside clearance; thread engagement; torque; screw/washer selection; vibration proof", "source": "https://www.harwin.com/products/R30-1611500"},
    ]
    write_csv("standoff-candidate-register.csv", list(candidates[0]), candidates)

    corner_radius = 5.5 / math.sqrt(3.0)
    screens = [
        {"screen_id": "WDM-SCR-001", "subject": "board outline", "input": "160 x 100 mm; 1.6 mm source thickness", "result": "controlled native-source dimensions", "status": "SOURCE CONFIRMED", "boundary": "received board thickness and tolerance remain required"},
        {"screen_id": "WDM-SCR-002", "subject": "mount pattern", "input": "MH1..MH4 at 5 mm from adjacent board edges", "result": "150 x 90 mm rectangular center pattern", "status": "SOURCE CONFIRMED", "boundary": "panel coordinates are candidates until received panel survey"},
        {"screen_id": "WDM-SCR-003", "subject": "standoff edge envelope", "input": "5.5 mm A/F regular hex; 5 mm hole-center edge distance", "result": f"{5.0-corner_radius:.6f} mm nominal material-envelope margin to each adjacent board edge", "status": "ARITHMETIC SCREEN ONLY", "boundary": "washer/screw head/enclosure acceptance remains open"},
        {"screen_id": "WDM-SCR-004", "subject": "10 mm candidate mounted plane", "input": "10.0 mm standoff plus 1.6 mm source board thickness", "result": "11.6 mm nominal board-top plane above panel before coating/flatness", "status": "ARITHMETIC SCREEN ONLY", "boundary": "underside lead trim and panel stack remain open"},
        {"screen_id": "WDM-SCR-005", "subject": "four-standoff mass", "input": "Harwin published per-unit weights", "result": "0.904 g / 1.176 g / 1.356 g for 10 / 13 / 15 mm variants", "status": "CATALOG ARITHMETIC ONLY", "boundary": "screws, washers and received mass excluded"},
        {"screen_id": "WDM-SCR-006", "subject": "ISO1 current land", "input": "centers +/-4.765 mm; copper width 1.52 mm", "result": f"{new_gap:.3f} mm inner gap; {new_span:.3f} mm overall span", "status": "CURRENT SOURCE CONFIRMED", "boundary": "mask/stencil/cleaning/system insulation acceptance remains open"},
    ]
    write_csv("interface-screen.csv", list(screens[0]), screens)

    holds = [
        {"hold_id": "WDM-HOLD-001", "subject": "standoff height", "status": "OPEN", "evidence_needed": "received board and installed THT lead-trim envelope; select one height and reject the others"},
        {"hold_id": "WDM-HOLD-002", "subject": "top fastener", "status": "OPEN", "evidence_needed": "exact screw, washer if used, head envelope, material, thread engagement, torque and locking method"},
        {"hold_id": "WDM-HOLD-003", "subject": "panel fastener", "status": "OPEN", "evidence_needed": "exact screw/washer/nut or stud system, panel-side access, thread engagement, torque and locking method"},
        {"hold_id": "WDM-HOLD-004", "subject": "received panel", "status": "OPEN", "evidence_needed": "18P2721 identity, thickness, flatness, coating, enclosure fit, inserts/keepouts and rear access survey"},
        {"hold_id": "WDM-HOLD-005", "subject": "panel drilling", "status": "OPEN", "evidence_needed": "released hole diameter/tolerance, coordinate datum, drill/deburr/coating-repair method and first-article measurement"},
        {"hold_id": "WDM-HOLD-006", "subject": "underside clearance", "status": "OPEN", "evidence_needed": "received THT protrusion and solder-fillet measurements, lead-trim limit, contamination clearance and no-contact inspection"},
        {"hold_id": "WDM-HOLD-007", "subject": "electrical isolation/bonding", "status": "OPEN", "evidence_needed": "qualified disposition for plastic hardware, PCB domains, steel panel bond and fault/EMC behavior"},
        {"hold_id": "WDM-HOLD-008", "subject": "mechanical proof", "status": "OPEN", "evidence_needed": "board mass/COM, connector insertion and conductor-torque loads, static pull, vibration and service-cycle acceptance"},
        {"hold_id": "WDM-HOLD-009", "subject": "assembly process", "status": "PARTIAL", "evidence_needed": "assembler acceptance of lands, stencil, mask, paste, reflow/manual-THT, cleaning, AOI and rework limits"},
        {"hold_id": "WDM-HOLD-010", "subject": "ISO1 insulation system", "status": "PARTIAL", "evidence_needed": "working voltage, OVC, pollution degree, material group, coating, altitude, environment, standard/jurisdiction and qualified calculation"},
        {"hold_id": "WDM-HOLD-011", "subject": "physical first article", "status": "OPEN", "evidence_needed": "received-board dimensions, holes, warp, isolation gap, polarity, solder, contamination and mounting inspection"},
        {"hold_id": "WDM-HOLD-012", "subject": "authorization", "status": "OPEN", "evidence_needed": "independent PCB/assembly review plus controlled fabrication and later energization work authorization"},
    ]
    write_csv("closure-holds.csv", list(holds[0]), holds)

    receiving = []
    for ref, *_ in hole_board:
        receiving.append({"record_id": f"WDM-RCV-{len(receiving)+1:03d}", "item": ref, "measurement": "received hole diameter and X/Y center from board datums", "instrument": "SELECTION REQUIRED", "result": "", "acceptance": "SELECTION REQUIRED", "state": "NOT EXECUTED / NOT AUTHORIZED"})
    for item, measurement in (("BP1", "received panel thickness/flatness/coating"), ("STACK", "selected hardware identity and complete installed height"), ("CLEARANCE", "minimum underside clearance after lead trim"), ("PROOF", "static/vibration/service result")):
        receiving.append({"record_id": f"WDM-RCV-{len(receiving)+1:03d}", "item": item, "measurement": measurement, "instrument": "SELECTION REQUIRED", "result": "", "acceptance": "SELECTION REQUIRED", "state": "NOT EXECUTED / NOT AUTHORIZED"})
    write_csv("receiving-template.csv", list(receiving[0]), receiving)

    sources = [
        {"source_id": "WDM-SRC-001", "organization": "Vishay", "record": "VO618A datasheet 83432", "revision_date": "Rev 2.1; 2025-01-22; rechecked 2026-08-09", "url": "https://www.vishay.com/docs/83432/vo618a.pdf", "use": "current ISO1 option-7 land reconciliation"},
        {"source_id": "WDM-SRC-002", "organization": "Harwin", "record": "R30-1611000 product record", "revision_date": "live record; rechecked 2026-08-09", "url": "https://www.harwin.com/products/R30-1611000", "use": "10 mm exact standoff candidate"},
        {"source_id": "WDM-SRC-003", "organization": "Harwin", "record": "R30-1611300 product record", "revision_date": "live record; rechecked 2026-08-09", "url": "https://www.harwin.com/products/R30-1611300", "use": "13 mm exact standoff candidate"},
        {"source_id": "WDM-SRC-004", "organization": "Harwin", "record": "R30-1611500 product record", "revision_date": "live record; rechecked 2026-08-09", "url": "https://www.harwin.com/products/R30-1611500", "use": "15 mm exact standoff candidate and minimum thread note"},
        {"source_id": "WDM-SRC-005", "organization": "Hammond Manufacturing", "record": "18P2721 product record", "revision_date": "live record; rechecked 2026-08-09", "url": "https://www.hammfg.com/part/18P2721", "use": "held steel inner-panel identity; thickness/stack not released"},
        {"source_id": "WDM-SRC-006", "organization": "Project Button", "record": "PCB-P0.6 native board and R131 native DRC", "revision_date": "KiCad 10.0.5; checked 2026-08-09", "url": "electrical/kicad/project-button-v3/project-button-v3.kicad_pcb", "use": "current geometry, hole coordinates and DRC evidence"},
    ]
    write_csv("source-register.csv", list(sources[0]), sources)

    summary = {
        "identifier": IDENTIFIER,
        "warning": WARNING,
        "current_board": "PCB-P0.6",
        "historical_board": "PCB-P0.5",
        "iso1_current_inner_gap_mm": round(new_gap, 3),
        "iso1_current_overall_span_mm": round(new_span, 3),
        "mount_pattern_mm": [150.0, 90.0],
        "mount_holes": 4,
        "standoff_candidates": len(candidates),
        "holds": len(holds),
        "hold_status": {"partial": 2, "open": 10},
        "physical_results": 0,
        "selected_standoff": "SELECTION REQUIRED",
        "selected_fasteners": "SELECTION REQUIRED",
    }
    (OUT / "mounting-interface-summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")

    hole_marks = "".join(f'<circle cx="{40 + x*4}" cy="{40 + y*4}" r="10"/><text x="{40+x*4}" y="{45+y*4}" text-anchor="middle">{html.escape(ref)}</text>' for ref, x, y in hole_board)
    html_text = f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>HR-V0 watchdog PCB mounting interface</title><style>
:root{{--ink:#082c57;--sky:#dff5ff;--blue:#07579f;--gold:#f2b72b;--paper:#fff;--line:#8fbdd8}}*{{box-sizing:border-box}}body{{margin:0;background:var(--sky);color:var(--ink);font:17px/1.55 system-ui,sans-serif}}header,main{{max-width:1160px;margin:auto;padding:28px}}header{{padding-top:36px}}h1{{font-size:clamp(2rem,5vw,4rem);line-height:1.05;margin:.3rem 0 1rem}}h2{{font-size:clamp(1.6rem,3vw,2.25rem);margin-top:2.2rem}}h3{{font-size:1.2rem}}.warning{{background:#fff4c2;border:3px solid var(--gold);padding:14px 18px;font-weight:800;font-size:16px}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));gap:18px}}.card{{background:var(--paper);border:2px solid var(--line);border-radius:16px;padding:20px}}.metric{{font-size:1.8rem;font-weight:800;color:var(--blue)}}.table{{overflow:auto;background:white;border:2px solid var(--line);border-radius:14px}}table{{border-collapse:collapse;min-width:880px;width:100%}}th,td{{padding:12px 14px;border-bottom:1px solid var(--line);text-align:left;vertical-align:top;font-size:16px}}th{{background:#cceeff}}svg{{width:100%;height:auto;background:white;border:2px solid var(--line);border-radius:14px}}svg text{{font:14px system-ui,sans-serif;fill:var(--ink)}}svg circle{{fill:var(--gold);stroke:var(--ink);stroke-width:2}}code,.meta{{font-size:14px}}footer{{margin:38px 0 10px;padding:20px;border-top:3px solid var(--gold);font-weight:700}}@media(max-width:600px){{body{{font-size:16px}}header,main{{padding:18px}}th,td{{font-size:16px}}}}
</style></head><body><header><div class="warning">{WARNING}</div><p class="meta">{IDENTIFIER} · 2026-08-09</p><h1>Current board, honest mounting boundary</h1><p>The reported ISO1 defect belongs to historical PCB-P0.5. PCB-P0.6 already contains the corrected Vishay option-7 copper geometry. The remaining work is physical: choose and prove the complete mounting and assembly stack.</p></header><main>
<section class="grid"><article class="card"><h3>ISO1 current inner gap</h3><div class="metric">{new_gap:.2f} mm</div><p>8.01 mm from the encoded P0.6 pad centers and copper width.</p></article><article class="card"><h3>Board mount pattern</h3><div class="metric">150 × 90 mm</div><p>Four 3.20 mm NPTH source holes.</p></article><article class="card"><h3>Exact standoff candidates</h3><div class="metric">3</div><p>10, 13 and 15 mm Harwin variants. None is selected.</p></article><article class="card"><h3>Closure holds</h3><div class="metric">12</div><p>Two partial, ten open, zero physical results.</p></article></section>
<h2>Board and candidate panel coordinates</h2><svg viewBox="0 0 760 480" role="img" aria-label="160 by 100 millimetre watchdog board with four mounting holes"><rect x="40" y="40" width="640" height="400" fill="#fff" stroke="#07579f" stroke-width="5"/><text x="360" y="230" text-anchor="middle" style="font-size:22px;font-weight:700">PCB-P0.6 · 160 × 100 mm</text>{hole_marks}<text x="360" y="468" text-anchor="middle">Panel-coordinate candidates derive from the P0.6 board envelope at x=54, y=230 mm. No panel drilling is released.</text></svg>
<h2>P0.5 versus current P0.6</h2>{table(reconciliation, [("configuration","Configuration"),("pad_centers_x_mm","X centers"),("pad_size_mm","Pad size"),("derived_inner_gap_mm","Inner gap"),("derived_overall_span_mm","Overall span"),("disposition","Disposition")])}
<h2>Standoff candidates</h2>{table(candidates, [("manufacturer_part_number","Part"),("body_length_mm","Length mm"),("thread","Thread"),("material","Material"),("unit_mass_g","Mass g"),("state","State"),("selection_evidence_needed","Evidence needed")])}
<h2>What remains fail-closed</h2>{table(holds, [("hold_id","ID"),("subject","Subject"),("status","Status"),("evidence_needed","Evidence needed")])}
<footer>{WARNING}. This guide does not select screws, washers, standoff height, drilling, torque, insulation classification, assembly process, fabrication, connection or energization.</footer></main></body></html>'''
    (WEB / "index.html").write_text(html_text, encoding="utf-8")

    print(f"Generated {IDENTIFIER}: 2 reconciliation rows, 4 holes, 3 standoff candidates, 12 holds")
    print(f"PCB-P0.6 ISO1: {new_gap:.3f} mm inner gap / {new_span:.3f} mm span; no hardware selected")
    print(WARNING)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
