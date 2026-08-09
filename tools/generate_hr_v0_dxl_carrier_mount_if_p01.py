"""Generate the R162 no-drill DXL carrier mounting-interface package."""

from __future__ import annotations

import csv
import hashlib
import json
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ENG = ROOT / "electrical" / "mechanical" / "hr-v0-dxl-carrier-mount-p0.1"
OUT = ROOT / "release" / "hr-v0" / "dxl-carrier-mount-p0.1"
PCB = ROOT / "electrical" / "kicad" / "hr-v0-dxl-protection-carrier-p0.3" / "hr-v0-dxl-protection-carrier-p0.3.kicad_pcb"
PANEL = ROOT / "electrical" / "panel" / "hr-v0-control-panel-p0.6" / "backplate-layout.csv"
WARNING = (
    "PRELIMINARY - NOT APPROVED FOR SUPPLIER UPLOAD, QUOTATION, PROCUREMENT, "
    "FABRICATION, ASSEMBLY, CONNECTION, MOTION, OR ENERGIZATION"
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        raise ValueError(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def warned(row: dict[str, object]) -> dict[str, object]:
    return row | {"warning": WARNING}


def package_rows() -> dict[str, list[dict[str, object]]]:
    sources = [
        warned({"source_id": "SRC-01", "organization": "Hammond Manufacturing", "document": "18P2721 product page", "document_revision_date": "live page; accessed 2026-08-09", "url": "https://www.hammfg.com/part/18P2721", "verified_use": "candidate panel identity and nominal 21 x 27 inch size"}),
        warned({"source_id": "SRC-02", "organization": "Hammond Manufacturing", "document": "18P2721 dimension drawing", "document_revision_date": "drawing dated 2020-02-07", "url": "https://www.hammfg.com/files/parts/pdf/18P2721.pdf", "verified_use": "533.4 x 685.8 mm panel; 2.54 mm nominal thickness; 19.05 mm formed flange"}),
        warned({"source_id": "SRC-03", "organization": "Essentra Components", "document": "TNM3-6.5-10-1 product page", "document_revision_date": "no revision printed; accessed 2026-08-09", "url": "https://www.essentracomponents.com/en-us/p/pcb-standoffs-round-metric-threaded-insulator-nylon-brass/tnm3-6-5-10-1", "verified_use": "M3 female/female candidate; 10 mm length; 6.5 mm diameter; 6 mm thread depth"}),
        warned({"source_id": "SRC-04", "organization": "Essentra Components", "document": "0120070000VR product page", "document_revision_date": "no revision printed; accessed 2026-08-09", "url": "https://www.essentracomponents.com/en-gb/p/machine-screws-pan/0120070000vr", "verified_use": "nylon M3 x 0.5 x 6 mm candidate; 5.9 mm head diameter; 1.8 mm head height"}),
        warned({"source_id": "SRC-05", "organization": "JST Mfg. Co.", "document": "VH connector series eVH", "document_revision_date": "no revision/date printed in controlled record; accessed 2026-08-09", "url": "https://www.jst-mfg.com/product/pdf/eng/eVH.pdf", "verified_use": "B2P-VH board-header and VHR-2N mating-housing identity/dimensional reference; full mated wire-sweep remains open"}),
        warned({"source_id": "SRC-06", "organization": "Project Button", "document": PCB.relative_to(ROOT).as_posix(), "document_revision_date": "HR-V0-DXL-PROT-CARRIER-P0.3; 2026-08-09 source hash", "url": "repository-local", "verified_use": "100 x 60 mm board, 1.6 mm candidate thickness and four 3.2 mm NPTH datums"}),
        warned({"source_id": "SRC-07", "organization": "Project Button", "document": PANEL.relative_to(ROOT).as_posix(), "document_revision_date": "P0.6; 2026-08-09 source hash", "url": "repository-local", "verified_use": "BP-026 reserve x=54..377.8 mm and y=533.4..675.8 mm"}),
    ]

    hardware = [
        warned({"item_id": "MNT-01", "role": "insulating female/female carrier standoff", "manufacturer": "Essentra Components", "manufacturer_part_number": "TNM3-6.5-10-1", "quantity_for_three_carriers": 12, "candidate_dimensions": "M3; L=10 mm; body dia=6.5 mm; internal thread depth=6 mm", "state": "EXACT CANDIDATE - NOT RELEASED", "remaining_evidence": "received dimensions; material/insert identity; temperature/fire/application acceptance; torque; creep; pull/shear/vibration proof"}),
        warned({"item_id": "MNT-02", "role": "PCB-side pan-head screw", "manufacturer": "Essentra Components", "manufacturer_part_number": "0120070000VR", "quantity_for_three_carriers": 12, "candidate_dimensions": "nylon M3 x 0.5; L=6 mm; head dia=5.9 mm; head height=1.8 mm", "state": "EXACT CANDIDATE - NOT RELEASED", "remaining_evidence": "received dimensions; driver/torque; board-bearing surface; creep; reuse policy; pull/shear/vibration proof"}),
        warned({"item_id": "MNT-03", "role": "panel-side pan-head screw", "manufacturer": "Essentra Components", "manufacturer_part_number": "0120070000VR", "quantity_for_three_carriers": 12, "candidate_dimensions": "nylon M3 x 0.5; L=6 mm; head dia=5.9 mm; head height=1.8 mm", "state": "EXACT CANDIDATE - NOT RELEASED", "remaining_evidence": "panel hole diameter/tolerance; coating/deburr; received engagement; driver/torque; creep; pull/shear/vibration proof"}),
        warned({"item_id": "MNT-04", "role": "backplate clearance hole", "manufacturer": "SELECTION REQUIRED", "manufacturer_part_number": "SELECTION REQUIRED", "quantity_for_three_carriers": 12, "candidate_dimensions": "center coordinates only; diameter and tolerance not released", "state": "SELECTION REQUIRED - DO NOT DRILL", "remaining_evidence": "fabricator capability; fastener clearance standard; coating allowance; burr control; edge distance; received template fit; qualified review"}),
    ]

    stack = [
        warned({"screen_id": "STK-01", "calculation": "PCB-side screw nominal thread engagement", "inputs_mm": "6.0 screw - 1.6 PCB", "result_mm": 4.4, "limit_or_comparison": "less than 6.0 mm candidate thread depth", "result": "ANALYTICAL PASS - TOLERANCES OPEN", "release_effect": "none"}),
        warned({"screen_id": "STK-02", "calculation": "PCB-side nominal bottom-out reserve", "inputs_mm": "6.0 thread depth - 4.4 engagement", "result_mm": 1.6, "limit_or_comparison": "positive nominal reserve", "result": "ANALYTICAL PASS - TOLERANCES OPEN", "release_effect": "none"}),
        warned({"screen_id": "STK-03", "calculation": "panel-side screw nominal thread engagement", "inputs_mm": "6.0 screw - 2.54 panel", "result_mm": 3.46, "limit_or_comparison": "less than 6.0 mm candidate thread depth", "result": "ANALYTICAL PASS - TOLERANCES OPEN", "release_effect": "none"}),
        warned({"screen_id": "STK-04", "calculation": "panel-side nominal bottom-out reserve", "inputs_mm": "6.0 thread depth - 3.46 engagement", "result_mm": 2.54, "limit_or_comparison": "positive nominal reserve", "result": "ANALYTICAL PASS - TOLERANCES OPEN", "release_effect": "none"}),
        warned({"screen_id": "STK-05", "calculation": "PCB top surface above panel face", "inputs_mm": "10.0 standoff + 1.6 PCB", "result_mm": 11.6, "limit_or_comparison": "connector/component/depth envelope not yet released", "result": "SCREEN ONLY", "release_effect": "none"}),
        warned({"screen_id": "STK-06", "calculation": "highest mounting-screw surface above panel face", "inputs_mm": "10.0 standoff + 1.6 PCB + 1.8 screw head", "result_mm": 13.4, "limit_or_comparison": "excludes all component, connector and cable heights", "result": "SCREEN ONLY", "release_effect": "none"}),
        warned({"screen_id": "STK-07", "calculation": "nominal rear clearance inside formed panel flange", "inputs_mm": "19.05 flange - 1.8 screw head", "result_mm": 17.25, "limit_or_comparison": "enclosure bosses/wall and installed panel offset unknown", "result": "SCREEN ONLY - RECEIVED FIT REQUIRED", "release_effect": "none"}),
        warned({"screen_id": "STK-08", "calculation": "standoff body margin to 100 x 60 board edge", "inputs_mm": "5.0 hole-center edge distance - 3.25 body radius", "result_mm": 1.75, "limit_or_comparison": "positive nominal board-edge margin", "result": "ANALYTICAL PASS - BODY/BOARD TOLERANCES OPEN", "release_effect": "none"}),
        warned({"screen_id": "STK-09", "calculation": "screw-head margin to 100 x 60 board edge", "inputs_mm": "5.0 hole-center edge distance - 2.95 head radius", "result_mm": 2.05, "limit_or_comparison": "positive nominal board-edge margin", "result": "ANALYTICAL PASS - HEAD/BOARD TOLERANCES OPEN", "release_effect": "none"}),
    ]

    placements = {"LIM1": (64.0, 539.6), "LIM2": (174.0, 539.6), "LIM3": (64.0, 609.6)}
    hole_rel = {"MH1": (5.0, 5.0), "MH2": (95.0, 5.0), "MH3": (5.0, 55.0), "MH4": (95.0, 55.0)}
    holes: list[dict[str, object]] = []
    for carrier, (x, y) in placements.items():
        for hole, (dx, dy) in hole_rel.items():
            holes.append(warned({"carrier_reference": carrier, "hole_reference": hole, "board_relative_x_mm": dx, "board_relative_y_mm": dy, "candidate_panel_center_x_mm": x + dx, "candidate_panel_center_y_mm": y + dy, "board_hole": "3.2 mm NPTH", "panel_hole": "SELECTION REQUIRED", "state": "CENTER CANDIDATE - DO NOT DRILL"}))

    clearance = [
        warned({"screen_id": "CLR-01", "objects": "LIM1 to BP-026 left", "nominal_clearance_mm": 10.0, "basis": "x 64.0 - reserve x 54.0", "result": "ANALYTICAL PASS - RECEIVED FIT OPEN"}),
        warned({"screen_id": "CLR-02", "objects": "LIM1/LIM3 to BP-026 lower/upper", "nominal_clearance_mm": 6.2, "basis": "vertical centering of two 60 mm boards plus 10 mm gap in 142.4 mm reserve", "result": "ANALYTICAL PASS - RECEIVED FIT OPEN"}),
        warned({"screen_id": "CLR-03", "objects": "LIM1 to LIM2", "nominal_clearance_mm": 10.0, "basis": "174.0 - (64.0 + 100.0)", "result": "ANALYTICAL PASS - CONNECTOR/WIRE SWEEP OPEN"}),
        warned({"screen_id": "CLR-04", "objects": "LIM1 to LIM3", "nominal_clearance_mm": 10.0, "basis": "609.6 - (539.6 + 60.0)", "result": "ANALYTICAL PASS - CONNECTOR/WIRE SWEEP OPEN"}),
        warned({"screen_id": "CLR-05", "objects": "LIM2 to BP-026 right", "nominal_clearance_mm": 103.8, "basis": "reserve x 377.8 - (174.0 + 100.0)", "result": "ANALYTICAL PASS - RECEIVED FIT OPEN"}),
        warned({"screen_id": "CLR-06", "objects": "JIN1/JOUT1 mated VH housing and wire service sweep", "nominal_clearance_mm": "SELECTION REQUIRED", "basis": "JST dimensional source does not close chosen contact, conductor, bend radius, strain relief or service-loop geometry", "result": "OPEN - FULL-SCALE RECEIVED FIT REQUIRED"}),
        warned({"screen_id": "CLR-07", "objects": "carrier components/connectors to enclosure cover", "nominal_clearance_mm": "SELECTION REQUIRED", "basis": "mounting stack closes only the screw/standoff height; tallest populated component and installed cover depth are unverified", "result": "OPEN - RECEIVED FIT REQUIRED"}),
        warned({"screen_id": "CLR-08", "objects": "panel-side screw heads to enclosure wall/bosses", "nominal_clearance_mm": "SELECTION REQUIRED", "basis": "17.25 mm nominal flange screen is not an installed enclosure measurement", "result": "OPEN - RECEIVED FIT REQUIRED"}),
    ]

    unresolved_names = [
        ("SEL-01", "received 18P2721 identity, flatness, thickness, flange and installed rear clearance"),
        ("SEL-02", "received P0.3 board outline, thickness, hole size and hole-coordinate tolerances"),
        ("SEL-03", "received TNM3-6.5-10-1 dimensions, insert construction and lot identity"),
        ("SEL-04", "received 0120070000VR dimensions, material and lot identity"),
        ("SEL-05", "backplate hole diameter, tolerance, positional tolerance, burr and coating treatment"),
        ("SEL-06", "mounting torque, tightening method, locking/reuse policy and witness-mark rule"),
        ("SEL-07", "static pull, shear, creep, vibration and transport acceptance loads"),
        ("SEL-08", "fire/temperature/creep suitability of nylon mounting parts for the installed enclosure"),
        ("SEL-09", "complete populated-board maximum height and conductive-part clearance"),
        ("SEL-10", "exact JST contact, conductor, insulation OD, crimp, bend radius and service sweep"),
        ("SEL-11", "cover depth, closure clearance, ventilation and local temperature evidence"),
        ("SEL-12", "touch/contamination protection and service-access method"),
        ("SEL-13", "qualified mechanical, electrical, enclosure-system and coating/bonding review"),
        ("SEL-14", "recomputed harness route geometry after R162 placement candidate"),
    ]
    unresolved = [warned({"selection_id": sid, "selection": text, "state": "SELECTION REQUIRED", "closure_evidence": "recorded received measurement or approved calculation/test with configuration, instrument and signoff"}) for sid, text in unresolved_names]

    metrology_items = [
        ("MET-01", "Record enclosure and panel manufacturer/part/lot/serial labels", "photo plus transcription"),
        ("MET-02", "Measure panel width, height, thickness, flange and installed rear gap", "calibrated dimensional record"),
        ("MET-03", "Record each carrier board revision/serial and measure outline, thickness, hole diameters and hole centers", "twelve-hole measurement record"),
        ("MET-04", "Measure all standoff lengths, diameters and thread depths by received lot", "lot sample record"),
        ("MET-05", "Measure screw length, head diameter and head height by received lot", "lot sample record"),
        ("MET-06", "Place a full-scale center-only overlay on the unmodified panel", "scale-bearing photo; no center punch"),
        ("MET-07", "Place nonconductive board envelopes and mounting-stack gauges", "front/rear photos; no drilling or adhesive"),
        ("MET-08", "Mate exact connectors and sweep actual conductors/service loops", "sweep photos and minimum clearances"),
        ("MET-09", "Close the empty enclosure around nonconductive envelopes and gauges", "cover and rear-clearance photos"),
        ("MET-10", "Reconcile measurements to this package and record every deviation", "signed discrepancy register"),
    ]
    metrology = [warned({"item_id": item, "unpowered_no_drill_action": action, "required_record": record, "execution_state": "NOT EXECUTED", "result": "OPEN", "operator": "", "reviewer": "", "evidence_uri": ""}) for item, action, record in metrology_items]

    acceptance_items = [
        ("ACC-01", "All three received boards fit BP-026 with positive recorded boundary margins"),
        ("ACC-02", "All twelve received board holes align to the center-only overlay within an approved positional tolerance"),
        ("ACC-03", "Every received screw has positive engagement and bottom-out reserve under the approved tolerance stack"),
        ("ACC-04", "Standoff bodies and screw heads clear board edges, parts, copper and connectors under received dimensions"),
        ("ACC-05", "Mated JST housings, conductors and service loops clear adjacent boards, duct, cover and service tools"),
        ("ACC-06", "Panel-side screw heads clear enclosure walls, bosses and wiring under the installed panel offset"),
        ("ACC-07", "Selected nylon/brass hardware is accepted for temperature, fire, creep and electrical-boundary use"),
        ("ACC-08", "Backplate hole/finish process has qualified diameter, positional tolerance, deburr and coating controls"),
        ("ACC-09", "Approved torque/locking/reuse method passes pull, shear, creep, vibration and transport tests"),
        ("ACC-10", "R162 placement is reconciled into panel layout and all affected harness routes"),
        ("ACC-11", "Qualified mechanical/electrical/enclosure reviewers sign the exact received configuration"),
        ("ACC-12", "A distinct work authorization releases only the next named operation"),
    ]
    acceptance = [warned({"acceptance_id": aid, "criterion": criterion, "execution_state": "NOT EXECUTED", "result": "OPEN", "evidence_uri": "", "approver": ""}) for aid, criterion in acceptance_items]
    return {
        "source-register.csv": sources,
        "hardware-bom.csv": hardware,
        "stack-calculation.csv": stack,
        "hole-coordinate-register.csv": holes,
        "clearance-screen.csv": clearance,
        "unresolved-selections.csv": unresolved,
        "no-drill-metrology-form.csv": metrology,
        "acceptance-matrix.csv": acceptance,
    }


def html() -> str:
    return f"""<!doctype html><html lang='en'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'><title>HR-V0 carrier mounting P0.1</title><style>
:root{{--ink:#0b2447;--blue:#0f5fa8;--sky:#dff3ff;--gold:#f6bd16;--paper:#f8fbff;--line:#87bde1;--danger:#8b1e1e}}*{{box-sizing:border-box}}body{{margin:0;background:var(--paper);color:var(--ink);font:clamp(16px,1.3vw,19px)/1.5 system-ui,sans-serif}}header{{background:var(--ink);color:white;padding:24px max(20px,5vw)}}header p{{max-width:980px}}.warn{{background:#fff2bd;color:#4a3300;border:3px solid var(--gold);padding:16px;font-weight:800}}main{{max-width:1200px;margin:auto;padding:28px 20px 60px}}h1{{font-size:clamp(32px,5vw,58px);line-height:1.05;margin:.2em 0}}h2{{font-size:clamp(25px,3vw,36px);margin-top:1.5em}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:18px}}.card{{background:white;border:2px solid var(--line);border-radius:16px;padding:20px;box-shadow:0 5px 0 #c4e5f7}}.metric{{font-size:32px;font-weight:850;color:var(--blue)}}button{{font:inherit;font-weight:750;padding:11px 16px;border:2px solid var(--ink);border-radius:10px;background:white;color:var(--ink);margin:4px}}button.active{{background:var(--gold)}}svg{{width:100%;height:auto;background:white;border:2px solid var(--line);border-radius:16px}}svg text{{font:14px system-ui,sans-serif;fill:var(--ink)}}g[data-board] rect{{fill:var(--sky);stroke:var(--blue);stroke-width:2}}g[data-board].active rect{{fill:#ffe895;stroke:#8a5b00;stroke-width:4}}g[data-board] text{{fill:var(--ink);stroke:none;font-weight:700}}.hole{{fill:white;stroke:var(--ink);stroke-width:1.5}}.small{{font-size:14px}}a{{color:#07599b}}table{{width:100%;border-collapse:collapse;background:white}}th,td{{text-align:left;vertical-align:top;padding:12px;border:1px solid var(--line)}}th{{background:var(--sky)}}.stack{{display:flex;align-items:end;gap:0;min-height:190px;padding:20px;background:white;border:2px solid var(--line);border-radius:16px;overflow-x:auto}}.layer{{min-width:130px;padding:16px 10px;text-align:center;border:2px solid var(--ink)}}.panel{{height:80px;background:#d6e0e7}}.spacer{{height:130px;background:var(--gold)}}.pcb{{height:105px;background:var(--sky)}}.screw{{height:122px;background:#f5f5f5}}@media(max-width:620px){{th,td{{display:block;border-top:0}}tr{{display:block;margin-bottom:16px;border-top:2px solid var(--line)}}svg text{{font-size:16px}}}}</style></head><body>
<header><div class='warn'>{WARNING}</div><h1>Carrier mounting, measured before metal</h1><p>R162 turns the three limiter-board placements into an exact mounting-stack candidate and an executable, unpowered fit-inspection package. It does not release holes, hardware, assembly, wiring or power.</p></header><main>
<section class='grid'><div class='card'><div class='metric'>3</div><b>100 x 60 mm carrier envelopes</b><p>Re-centered inside BP-026 with 10 mm board gaps and 6.2 mm nominal vertical edge margins.</p></div><div class='card'><div class='metric'>12 + 24</div><b>candidate standoffs + screws</b><p>Exact Essentra candidates; received dimensions, torque, creep and load proof remain open.</p></div><div class='card'><div class='metric'>0</div><b>released holes</b><p>Every coordinate is a center candidate. Diameter, tolerance, deburr, coating and work authority remain selection required.</p></div></section>
<h2>Candidate placement</h2><p>Select a board to highlight it. The reserve is the P0.6 lower-zone candidate, not a drilling template.</p><div><button class='active' data-ref='all'>All</button><button data-ref='LIM1'>LIM1 shoulder</button><button data-ref='LIM2'>LIM2 elbow</button><button data-ref='LIM3'>LIM3 gripper</button></div>
<svg viewBox='0 0 720 355' role='img' aria-label='Candidate panel layout showing three limiter boards'><rect x='35' y='35' width='648' height='285' fill='#eef8ff' stroke='#0b2447' stroke-width='3'/><text x='45' y='25'>BP-026 reserve: 323.8 x 142.4 mm (drawing scaled 2 px/mm)</text>
<g class='board' data-board='LIM1'><rect x='55' y='47.4' width='200' height='120' rx='5'/><text x='70' y='75'>LIM1 • x 64.0, y 539.6</text><circle class='hole' cx='65' cy='57.4' r='5'/><circle class='hole' cx='245' cy='57.4' r='5'/><circle class='hole' cx='65' cy='157.4' r='5'/><circle class='hole' cx='245' cy='157.4' r='5'/></g>
<g class='board' data-board='LIM2'><rect x='275' y='47.4' width='200' height='120' rx='5'/><text x='290' y='75'>LIM2 • x 174.0, y 539.6</text><circle class='hole' cx='285' cy='57.4' r='5'/><circle class='hole' cx='465' cy='57.4' r='5'/><circle class='hole' cx='285' cy='157.4' r='5'/><circle class='hole' cx='465' cy='157.4' r='5'/></g>
<g class='board' data-board='LIM3'><rect x='55' y='187.4' width='200' height='120' rx='5'/><text x='70' y='215'>LIM3 • x 64.0, y 609.6</text><circle class='hole' cx='65' cy='197.4' r='5'/><circle class='hole' cx='245' cy='197.4' r='5'/><circle class='hole' cx='65' cy='297.4' r='5'/><circle class='hole' cx='245' cy='297.4' r='5'/></g><text x='500' y='80'>10 mm left margin</text><text x='500' y='108'>10 mm board gaps</text><text x='500' y='136'>6.2 mm top/bottom</text><text x='500' y='180'>DO NOT DRILL</text><text x='500' y='208'>Coordinates require</text><text x='500' y='230'>received-part metrology</text></svg>
<h2>Nominal stack arithmetic</h2><div class='stack'><div class='layer panel'><b>2.54 mm</b><br>steel panel</div><div class='layer screw'><b>M3 x 6</b><br>panel screw<br>3.46 mm engagement</div><div class='layer spacer'><b>10 mm</b><br>standoff<br>6 mm thread depth</div><div class='layer pcb'><b>1.6 mm</b><br>candidate PCB</div><div class='layer screw'><b>M3 x 6</b><br>board screw<br>4.4 mm engagement</div></div><p class='small'>Nominal arithmetic only. Part tolerances, PCB build, panel coating, torque, creep, pull/shear, vibration, component height and cover clearance are not closed.</p>
<h2>Before any hole exists</h2><table><tr><th>Step</th><th>Required evidence</th></tr><tr><td>1. Receive and identify</td><td>Panel, enclosure, three boards, 12 standoffs and 24 screws recorded by manufacturer, part, lot and serial/revision.</td></tr><tr><td>2. Measure</td><td>Panel/flange/rear gap, board outlines/holes/thickness, standoff threads and screw geometry with controlled instruments.</td></tr><tr><td>3. Mock up without marking metal</td><td>Center-only overlay and nonconductive envelopes. No punch, drill, adhesive, wiring or power.</td></tr><tr><td>4. Sweep real connectors and wires</td><td>Exact JST contacts, 18 AWG candidates, bends, strain relief, service tools, cover and rear space.</td></tr><tr><td>5. Reconcile and review</td><td>All deviations, tolerances, route changes, load tests and qualified signoffs before a separate work authorization.</td></tr></table>
<h2>Controlled files</h2><p><a href='hardware-bom.csv'>Hardware candidates</a> · <a href='stack-calculation.csv'>Stack calculations</a> · <a href='hole-coordinate-register.csv'>Center coordinates</a> · <a href='clearance-screen.csv'>Clearance screens</a> · <a href='no-drill-metrology-form.csv'>Metrology form</a> · <a href='unresolved-selections.csv'>Open selections</a> · <a href='acceptance-matrix.csv'>Acceptance matrix</a></p>
<div class='warn'>Passing these analytical screens does not approve procurement, drilling, fabrication, assembly, connection, motion or energization.</div></main><script>const buttons=[...document.querySelectorAll('button[data-ref]')],boards=[...document.querySelectorAll('[data-board]')];buttons.forEach(b=>b.onclick=()=>{{buttons.forEach(x=>x.classList.remove('active'));b.classList.add('active');boards.forEach(x=>x.classList.toggle('active',b.dataset.ref==='all'||x.dataset.board===b.dataset.ref))}});</script></body></html>"""


def main() -> None:
    rows_by_name = package_rows()
    for directory in (ENG, OUT):
        directory.mkdir(parents=True, exist_ok=True)
        for old in directory.iterdir():
            if old.is_file():
                old.unlink()
        for name, rows in rows_by_name.items():
            write_csv(directory / name, rows)

    readme = f"""# HR-V0 DXL carrier mounting interface P0.1

> **{WARNING}**

R162 converts the three R161 carrier envelopes into an exact but unreleased M3 mounting-stack candidate and a received-part, no-drill inspection package. The placement is re-centered within P0.6 `BP-026`, so the R161 held route screens must be recomputed after physical fit.

Nominal arithmetic supports the 10 mm standoff and M3 x 6 mm screw combination, but tolerances, torque, creep, load capacity, connector/wire sweep, component height, cover/rear clearance, hole process, coating and qualified review remain open. Coordinates are center candidates only. Do not print or use them as a drill template.
"""
    for directory in (ENG, OUT):
        (directory / "README.md").write_text(readme, encoding="utf-8")

    status = {
        "identifier": "HR-V0-DXL-CARRIER-MOUNT-IF-P0.1",
        "round": "R162",
        "date": "2026-08-09",
        "carrier_count": 3,
        "mounting_hole_centers": 12,
        "exact_standoff_candidates": 12,
        "exact_screw_candidates": 24,
        "stack_calculations": 9,
        "clearance_screens": 8,
        "unresolved_selections": 14,
        "metrology_rows": 10,
        "acceptance_rows": 12,
        "source_hashes": {PCB.relative_to(ROOT).as_posix(): sha256(PCB), PANEL.relative_to(ROOT).as_posix(): sha256(PANEL)},
        "r161_route_screens_still_current": False,
        "panel_hole_diameter_selected": False,
        "mounting_released": False,
        "hardware_procurement_authorized": False,
        "physical_article_exists": False,
        "physical_test_executed": False,
        "qualified_review_complete": False,
        "supplier_upload_authorized": False,
        "quotation_authorized": False,
        "procurement_authorized": False,
        "fabrication_authorized": False,
        "assembly_authorized": False,
        "connection_authorized": False,
        "motion_authorized": False,
        "energization_authorized": False,
        "safety_credit": False,
        "warning": WARNING,
    }
    for directory in (ENG, OUT):
        (directory / "package-status.json").write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8")
    (OUT / "index.html").write_text(html(), encoding="utf-8")

    for name in rows_by_name | {"README.md": [], "package-status.json": []}:
        shutil.copy2(OUT / name, ENG / name)
    for directory in (ENG, OUT):
        files = sorted(p for p in directory.rglob("*") if p.is_file() and p.name != "file-manifest.csv")
        write_csv(directory / "file-manifest.csv", [{"path": p.relative_to(directory).as_posix(), "bytes": p.stat().st_size, "sha256": sha256(p)} for p in files])


if __name__ == "__main__":
    main()
