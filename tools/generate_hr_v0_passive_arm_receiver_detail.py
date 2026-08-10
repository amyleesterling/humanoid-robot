"""Generate the R129 detailed passive arm-receiver candidate.

This advances the R127/R128 receiver from generic guide/contact envelopes to
dimensioned, exact-candidate interfaces.  It does not convert catalog data into
impact approval, release any fabricated part, or authorize motion/energization.
"""

from __future__ import annotations

import csv
import json
import shutil
from pathlib import Path

import cadquery as cq

import generate_hr_v0_collapse_envelope as collapse
import generate_hr_v0_guard_receiver as guard
import generate_hr_v0_passive_arm_receiver as r127


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "cad" / "hr-v0" / "generated" / "passive-arm-receiver-detail-p0.2"
GUIDE = ROOT / "release" / "hr-v0" / "passive-arm-receiver-detail-p0.2" / "index.html"
IDENTIFIER = "HR-V0-PASSIVE-ARM-RECEIVER-DETAIL-P0.2"
WARNING = "PRELIMINARY - NOT APPROVED FOR FABRICATION, MOTION OR ENERGIZATION"

GUARD_X_MIN = -200.0
GUARD_X_MAX = 200.0
GUARD_Y_MIN = -450.0
GUARD_Y_MAX = 450.0
PLATEN_X = 180.0
PLATEN_Y = 800.0
PLATEN_T = 6.35
PAD_T = 9.525
RECEIVER_TOP_Z = 320.0
PLATEN_TOP_Z = RECEIVER_TOP_Z - PAD_T
PLATEN_BOTTOM_Z = PLATEN_TOP_Z - PLATEN_T
SHOCK_STROKE = 8.128
BACKUP_STOP_TOP_Z = 294.5
BACKUP_GAP = PLATEN_BOTTOM_Z - BACKUP_STOP_TOP_Z
POST_X = (-60.0, 60.0)
POST_Y = (-420.0, 420.0)
GUIDE_X = (-110.0, 110.0)
GUIDE_Y = (-350.0, 350.0)
SHOCK_Y = (-300.0, 0.0, 300.0)


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def normalize_step(path: Path) -> None:
    path.write_text("\n".join(line.rstrip() for line in path.read_text(encoding="utf-8").splitlines()) + "\n", encoding="utf-8", newline="\n")


def box(dx: float, dy: float, dz: float, x0: float, y0: float, z0: float) -> cq.Shape:
    return cq.Solid.makeBox(dx, dy, dz, cq.Vector(x0, y0, z0))


def detailed_shapes() -> dict[str, cq.Shape]:
    shapes: dict[str, cq.Shape] = {}
    for level, z0 in (("BOTTOM", 20.0), ("TOP", 220.0)):
        for index, x in enumerate(POST_X, 1):
            shapes[f"20-2040-{level}-RAIL-{index}"] = box(20.0, 840.0, 40.0, x - 10.0, -420.0, z0)
    for xi, x in enumerate(POST_X, 1):
        for yi, y in enumerate(POST_Y, 1):
            shapes[f"20-2020-POST-{xi}-{yi}"] = box(20.0, 20.0, 160.0, x - 10.0, y - 10.0, 60.0)
    for index, y in enumerate((-410.0, 410.0), 1):
        shapes[f"20-2020-LOWER-TIE-{index}"] = box(140.0, 20.0, 20.0, -70.0, y - 10.0, 20.0)
    for index, y in enumerate(SHOCK_Y, 1):
        shapes[f"FAB-REC-002-SHOCK-PLATE-{index}"] = box(160.0, 40.0, 6.35, -80.0, y - 20.0, 260.0)
        shapes[f"ACE-MA30M-ENVELOPE-{index}"] = cq.Solid.makeCylinder(4.0, PLATEN_BOTTOM_Z - 266.35, cq.Vector(0.0, y, 266.35), cq.Vector(0, 0, 1))
    for xi, x in enumerate(GUIDE_X, 1):
        for yi, y in enumerate(GUIDE_Y, 1):
            tag = f"{xi}-{yi}"
            shapes[f"IGUS-TS-01-20-120-ENVELOPE-{tag}"] = box(12.3, 20.0, 120.0, x - 6.15, y - 10.0, PLATEN_BOTTOM_Z - 120.0)
            shapes[f"IGUS-TWA-01-20-ENVELOPE-{tag}"] = box(30.0, 63.0, 81.0, x - 15.0, y - 31.5, PLATEN_BOTTOM_Z - 81.0)
            inner_x = 90.0 if x > 0 else -110.0
            shapes[f"FAB-REC-003-GUIDE-TAB-{tag}"] = box(20.0, 50.0, 6.35, inner_x, y - 25.0, PLATEN_BOTTOM_Z - 6.35)
            shapes[f"BACKUP-STOP-ALLOCATION-{tag}"] = box(20.0, 20.0, 20.0, (75.0 if x > 0 else -95.0), y - 10.0, BACKUP_STOP_TOP_Z - 20.0)
    shapes["FAB-REC-001-MOVING-PLATEN"] = box(PLATEN_X, PLATEN_Y, PLATEN_T, -PLATEN_X / 2.0, -PLATEN_Y / 2.0, PLATEN_BOTTOM_Z)
    pad_lengths = (266.7, 266.6, 266.7)
    y0 = -400.0
    for index, length in enumerate(pad_lengths, 1):
        shapes[f"SORbothane-0212037-50-10-CUT-{index}"] = box(PLATEN_X, length, PAD_T, -PLATEN_X / 2.0, y0, PLATEN_TOP_Z)
        y0 += length
    return shapes


def make_platen() -> cq.Workplane:
    return cq.Workplane("XY").rect(PLATEN_X, PLATEN_Y).extrude(PLATEN_T)


def make_shock_plate() -> cq.Workplane:
    return cq.Workplane("XY").rect(160.0, 40.0).extrude(6.35)


def make_guide_tab() -> cq.Workplane:
    return cq.Workplane("XY").rect(20.0, 50.0).extrude(6.35)


def write_svg_drawings() -> None:
    drawing_style = "text{font-family:Arial,sans-serif;fill:#102a43;font-size:16px}.t{font-size:30px;font-weight:700}.w{font-size:14px;font-weight:700;fill:#8b2d1b}.p{fill:#dff3ff;stroke:#082b55;stroke-width:3}.d{stroke:#075b9b;stroke-width:2;fill:none}.x{stroke:#a83220;stroke-width:2;stroke-dasharray:7 5}.g{fill:#f4b942;stroke:#8a5b00;stroke-width:2}"
    platen_svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="760" viewBox="0 0 1200 760"><style>{drawing_style}</style><rect width="1200" height="760" fill="#fff"/><text x="45" y="50" class="t">FAB-REC-001 platen blank - review candidate</text><text x="45" y="82" class="w">{WARNING} - GUIDE, SHOCK AND STOP HOLES REMAIN SELECTION REQUIRED</text><rect x="260" y="130" width="360" height="500" class="p"/><line x1="235" y1="130" x2="235" y2="630" class="d"/><line x1="225" y1="130" x2="245" y2="130" class="d"/><line x1="225" y1="630" x2="245" y2="630" class="d"/><text x="135" y="385">800.0 mm</text><line x1="260" y1="665" x2="620" y2="665" class="d"/><line x1="260" y1="655" x2="260" y2="675" class="d"/><line x1="620" y1="655" x2="620" y2="675" class="d"/><text x="405" y="700">180.0 mm</text><text x="690" y="180">Material: 6061-T651 candidate</text><text x="690" y="215">Thickness: 6.35 mm nominal</text><text x="690" y="250">Flatness, thickness tolerance, edge radius:</text><text x="690" y="278" class="w">SELECTION REQUIRED</text><text x="690" y="325">The blank-only STEP is deliberate.</text><text x="690" y="353">Do not drill until received igus/ACE CAD,</text><text x="690" y="381">manufacturer application review, and the</text><text x="690" y="409">controlled interface drawing are accepted.</text><text x="45" y="735">Datum A: bottom face. Datum B: long edge. Datum C: short edge. All dimensions millimetres.</text></svg>'''
    (OUT / "FAB-REC-001-platen-blank-drawing.svg").write_text(platen_svg, encoding="utf-8", newline="\n")

    section_svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="760" viewBox="0 0 1200 760"><style>{drawing_style}</style><rect width="1200" height="760" fill="#fff"/><text x="45" y="50" class="t">Receiver vertical stack and backup-stop allocation</text><text x="45" y="82" class="w">{WARNING} - NOMINAL GEOMETRY ONLY</text><rect x="210" y="145" width="650" height="90" class="g"/><rect x="210" y="235" width="650" height="60" class="p"/><rect x="295" y="390" width="60" height="120" class="p"/><rect x="715" y="390" width="60" height="120" class="p"/><rect x="390" y="360" width="42" height="150" class="g"/><rect x="640" y="360" width="42" height="150" class="g"/><line x1="185" y1="145" x2="185" y2="295" class="d"/><text x="55" y="225">pad 9.525 + plate 6.35</text><line x1="890" y1="295" x2="890" y2="390" class="x"/><text x="915" y="340">backup gap {BACKUP_GAP:.3f} mm</text><line x1="890" y1="310" x2="890" y2="390" class="d"/><text x="915" y="385">shock stroke {SHOCK_STROKE:.3f} mm</text><text x="210" y="560">Receiver top Z = 320.000; platen bottom Z = {PLATEN_BOTTOM_Z:.3f}; backup stop top Z = {BACKUP_STOP_TOP_Z:.3f}</text><text x="210" y="595">Nominal residual after full shock stroke = {BACKUP_GAP-SHOCK_STROKE:.3f} mm. Tolerance stack is not closed.</text><text x="210" y="630" class="w">ACE integrated stop remains primary; four independent catch allocations require exact hardware, load proof and qualified review.</text></svg>'''
    (OUT / "receiver-section-drawing.svg").write_text(section_svg, encoding="utf-8", newline="\n")


def main() -> int:
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)
    shapes = detailed_shapes()

    exact_bom = [
        {"item":"REC-BOM-001","quantity":1,"manufacturer":"FABRICATED","part_or_drawing":"FAB-REC-001","description":"180 x 800 x 6.35 mm moving platen blank; 6061-T651 candidate","selection_state":"DRAWING CANDIDATE - MATERIAL CERTIFICATE, TOLERANCES AND HOLES NOT RELEASED"},
        {"item":"REC-BOM-002","quantity":3,"manufacturer":"FABRICATED","part_or_drawing":"FAB-REC-002","description":"160 x 40 x 6.35 mm shock mount plate blank","selection_state":"BLANK CANDIDATE - M8x1 INTERFACE AND RETENTION NOT RELEASED"},
        {"item":"REC-BOM-003","quantity":4,"manufacturer":"FABRICATED","part_or_drawing":"FAB-REC-003","description":"20 x 50 x 6.35 mm guide interface tab blank","selection_state":"BLANK CANDIDATE - RECEIVED IGUS CAD AND HOLES REQUIRED"},
        {"item":"REC-BOM-004","quantity":4,"manufacturer":"SELECTION REQUIRED","part_or_drawing":"SELECTION REQUIRED","description":"independent backup stop and retained contact element","selection_state":"SELECTION REQUIRED - 9.625 MM NOMINAL GAP ONLY"},
        {"item":"REC-BOM-005","quantity":4,"manufacturer":"80/20 Inc.","part_or_drawing":"20-2040","description":"20 x 40 mm T-slot profile; 840 mm candidate cut length","selection_state":"EXACT PROFILE; CONFIGURED CUT ORDER CODE AND CUT TOLERANCE SELECTION REQUIRED"},
        {"item":"REC-BOM-006","quantity":4,"manufacturer":"80/20 Inc.","part_or_drawing":"20-2020","description":"20 x 20 mm T-slot profile; 160 mm candidate post length","selection_state":"EXACT PROFILE; CONFIGURED CUT ORDER CODE AND CUT TOLERANCE SELECTION REQUIRED"},
        {"item":"REC-BOM-007","quantity":2,"manufacturer":"80/20 Inc.","part_or_drawing":"20-2020","description":"20 x 20 mm T-slot profile; 140 mm lower tie length","selection_state":"EXACT PROFILE; CONFIGURED CUT ORDER CODE AND CUT TOLERANCE SELECTION REQUIRED"},
        {"item":"REC-BOM-008","quantity":8,"manufacturer":"80/20 Inc.","part_or_drawing":"20-4113","description":"20 Series four-hole wide inside corner bracket","selection_state":"EXACT CANDIDATE - JOINT STRENGTH AND PROOF OPEN"},
        {"item":"REC-BOM-009","quantity":32,"manufacturer":"80/20 Inc.","part_or_drawing":"11-5308","description":"M5 x 8 mm BHSCS suggested for 20-4113","selection_state":"EXACT CANDIDATE - TORQUE, ENGAGEMENT AND REUSE POLICY OPEN"},
        {"item":"REC-BOM-010","quantity":32,"manufacturer":"80/20 Inc.","part_or_drawing":"14122","description":"M5 slide-in economy T-nut block suggested for 20-4113","selection_state":"EXACT CANDIDATE - JOINT PROOF OPEN"},
        {"item":"REC-BOM-011","quantity":4,"manufacturer":"igus","part_or_drawing":"TWA-01-20","description":"drylin T automatic-clearance carriage","selection_state":"EXACT CANDIDATE - RECEIVED CAD, LOAD ORIENTATION, LIFE AND APPLICATION REVIEW OPEN"},
        {"item":"REC-BOM-012","quantity":4,"manufacturer":"igus","part_or_drawing":"TS-01-20","description":"drylin T 20 mm guide rail; 120 mm candidate configured length","selection_state":"EXACT FAMILY - CONFIGURED LENGTH/HOLE ORDER CODE SELECTION REQUIRED"},
        {"item":"REC-BOM-013","quantity":3,"manufacturer":"ACE Controls Inc.","part_or_drawing":"MA30M","description":"adjustable miniature shock absorber","selection_state":"EXACT EVALUATION CANDIDATE - ACE APPLICATION ACCEPTANCE REQUIRED"},
        {"item":"REC-BOM-014","quantity":3,"manufacturer":"Sorbothane Inc.","part_or_drawing":"0212037-50-10","description":"12 x 12 x 0.375 in, 50-durometer sheet without PSA","selection_state":"EXACT MATERIAL CANDIDATE - CUT, RETENTION, DYNAMIC DEFLECTION AND SUITABILITY OPEN"},
        {"item":"REC-BOM-015","quantity":1,"manufacturer":"SELECTION REQUIRED","part_or_drawing":"SELECTION REQUIRED","description":"contact-layer adhesive or mechanical retention system","selection_state":"SELECTION REQUIRED"},
        {"item":"REC-BOM-016","quantity":1,"manufacturer":"SELECTION REQUIRED","part_or_drawing":"SELECTION REQUIRED","description":"receiver-to-guard/base attachment and anchor set","selection_state":"SELECTION REQUIRED - SITE AND GUARD LOAD PATH OPEN"},
    ]
    write_csv(OUT / "exact-candidate-bom.csv", exact_bom)

    write_csv(OUT / "contact-layer-cut-plan.csv", [
        {"cut_id":f"PAD-{i}","source_part":"0212037-50-10","source_size_in":"12 x 12 x 0.375","finished_x_mm":"180.0","finished_y_mm":f"{length:.1f}","finished_t_mm_nominal":f"{PAD_T:.3f}","source_tolerance":"+/-0.025 in (+/-0.635 mm)","retention":"SELECTION REQUIRED","state":"CUT CANDIDATE - NOT RELEASED"}
        for i, length in enumerate((266.7, 266.6, 266.7), 1)
    ])

    interfaces = [
        {"interface_id":"REC-IF-001","from":"platen","to":"four guide tabs","controlled_geometry":"tab envelope 20 x 50 x 6.35 at X +/-90..110, Y +/-350","hardware":"SELECTION REQUIRED","status":"OPEN - RECEIVED IGUS CAD AND HOLE PATTERN REQUIRED"},
        {"interface_id":"REC-IF-002","from":"guide tabs","to":"TWA-01-20 carriages","controlled_geometry":"carriage envelope 30 x 63 x 81; K2 M6 published","hardware":"SELECTION REQUIRED","status":"OPEN - DO NOT INFER THREAD PATTERN"},
        {"interface_id":"REC-IF-003","from":"TS-01-20 rails","to":"fixed guide supports","controlled_geometry":"four 120 mm vertical rail envelopes at X +/-110, Y +/-350","hardware":"SELECTION REQUIRED","status":"OPEN - CONFIGURED RAIL HOLES AND SUPPORTS REQUIRED"},
        {"interface_id":"REC-IF-004","from":"platen","to":"three MA30M units","controlled_geometry":"Y -300/0/+300; axial Z; M8x1 published","hardware":"SELECTION REQUIRED","status":"OPEN - ACE APPLICATION AND RETENTION REQUIRED"},
        {"interface_id":"REC-IF-005","from":"platen","to":"four backup catches","controlled_geometry":f"nominal gap {BACKUP_GAP:.3f} mm; {BACKUP_GAP-SHOCK_STROKE:.3f} mm after catalog stroke","hardware":"SELECTION REQUIRED","status":"OPEN - TOLERANCE, PEAK LOAD AND FAILURE CONTAINMENT REQUIRED"},
        {"interface_id":"REC-IF-006","from":"20-2020 posts","to":"20-2040 rails","controlled_geometry":"eight 90 degree joints","hardware":"20-4113 + four 11-5308 + four 14122 per joint","status":"PARTIAL - EXACT CANDIDATES; NO PUBLISHED JOINT ALLOWABLE OR PROOF"},
        {"interface_id":"REC-IF-007","from":"receiver subframe","to":"guard/base/site","controlled_geometry":"SELECTION REQUIRED","hardware":"SELECTION REQUIRED","status":"OPEN - NO ANCHOR OR GUARD LOAD CREDIT"},
    ]
    write_csv(OUT / "interface-register.csv", interfaces)

    load_rows = [
        {"load_id":"REC-LD-001","case":"provisional platen input","value":"2000","unit":"N","method":"retained R127 screen","disposition":"NOT AN ACCEPTANCE OR PEAK LOAD"},
        {"load_id":"REC-LD-002","case":"three-shock ideal share","value":"666.667","unit":"N/unit","method":"2000/3","disposition":"UNEQUAL SHARING AND DYNAMIC REACTION OPEN"},
        {"load_id":"REC-LD-003","case":"one shock unavailable; two-unit ideal share","value":"1000.000","unit":"N/unit","method":"2000/2","disposition":"FAILURE CASE ONLY; NO ACE APPROVAL"},
        {"load_id":"REC-LD-004","case":"four-catch ideal share","value":"500.000","unit":"N/catch","method":"2000/4","disposition":"CONTACT/SHARING/PEAK/PROOF OPEN"},
        {"load_id":"REC-LD-005","case":"single-catch conservative screen","value":"2000.000","unit":"N/catch","method":"no sharing credit","disposition":"CANDIDATE INPUT; STOP HARDWARE UNSELECTED"},
        {"load_id":"REC-LD-006","case":"TWA/TS 01-20 published static C0Z","value":"3700","unit":"N/system datum","method":"igus current technical table","disposition":"DIRECTION/MOMENT/DYNAMIC SHOCK/APPLICATION CHECK OPEN"},
        {"load_id":"REC-LD-007","case":"TW-01-20 single gliding-element maximum","value":"830","unit":"N","method":"igus horizontal system-design page; TWA equivalence not assumed","disposition":"REFERENCE ONLY - DO NOT APPLY TO TWA WITHOUT IGUS REVIEW"},
        {"load_id":"REC-LD-008","case":"20-4113 joint allowable","value":"SELECTION REQUIRED","unit":"N","method":"manufacturer page supplies geometry and suggested hardware, not joint capacity","disposition":"BLOCKS STRUCTURAL RELEASE"},
    ]
    write_csv(OUT / "load-path-register.csv", load_rows)

    tolerances = [
        {"stack_id":"REC-TOL-001","quantity":"receiver top Z","nominal_mm":"320.000","plus_mm":"SELECTION REQUIRED","minus_mm":"SELECTION REQUIRED","source":"assembly datum","status":"OPEN"},
        {"stack_id":"REC-TOL-002","quantity":"Sorbothane thickness","nominal_mm":f"{PAD_T:.3f}","plus_mm":"0.635","minus_mm":"0.635","source":"0212037-50-10 product page +/-0.025 in","status":"CONTROLLED SOURCE TOLERANCE"},
        {"stack_id":"REC-TOL-003","quantity":"platen thickness","nominal_mm":f"{PLATEN_T:.3f}","plus_mm":"SELECTION REQUIRED","minus_mm":"SELECTION REQUIRED","source":"supplier/material certificate required","status":"OPEN"},
        {"stack_id":"REC-TOL-004","quantity":"backup catch gap","nominal_mm":f"{BACKUP_GAP:.3f}","plus_mm":"SELECTION REQUIRED","minus_mm":"SELECTION REQUIRED","source":"plate, shock, mount and stop stack","status":"OPEN"},
        {"stack_id":"REC-TOL-005","quantity":"catalog stroke residual before catch","nominal_mm":f"{BACKUP_GAP-SHOCK_STROKE:.3f}","plus_mm":"SELECTION REQUIRED","minus_mm":"SELECTION REQUIRED","source":"nominal gap minus 8.128 mm catalog stroke","status":"OPEN - MUST REMAIN POSITIVE AFTER ACCEPTED STACK"},
        {"stack_id":"REC-TOL-006","quantity":"known commanded clearance","nominal_mm":"63.106478","plus_mm":"0","minus_mm":"SELECTION REQUIRED","source":"R127 retained lower bound minus receiver top","status":"OPEN - COMPLETE MOVING GEOMETRY AND AS-BUILT STACK REQUIRED"},
    ]
    write_csv(OUT / "tolerance-stack.csv", tolerances)

    holds = [
        ("REC2-HOLD-001","complete gripper/object/cable geometry","OPEN"),
        ("REC2-HOLD-002","measured mass, inertia, contact speed and drive persistence","OPEN"),
        ("REC2-HOLD-003","ACE written application acceptance and exact mounting","OPEN"),
        ("REC2-HOLD-004","received igus CAD, configured rail code, load/life review and guide proof","PARTIAL"),
        ("REC2-HOLD-005","Sorbothane cut/retention, dynamic deflection, rebound, wear and flammability","PARTIAL"),
        ("REC2-HOLD-006","platen material/tolerance, final holes, local strength, fatigue and inspection","PARTIAL"),
        ("REC2-HOLD-007","joint, post, brace, base, guard and anchor allowables/proof","PARTIAL"),
        ("REC2-HOLD-008","all four joint-boundary stops","OPEN"),
        ("REC2-HOLD-009","guard access, pinch, rebound and final-rest proof","OPEN"),
        ("REC2-HOLD-010","continued-drive, regeneration, elastic and detached-part cases","OPEN"),
        ("REC2-HOLD-011","FAI, metrology, drop/backdrive/fault tests and uncertainty","OPEN"),
        ("REC2-HOLD-012","qualified mechanical/functional-safety disposition and work authorization","OPEN"),
    ]
    write_csv(OUT / "closure-holds.csv", [{"hold_id":i,"evidence_required":e,"status":s,"release_effect":"BLOCKS FABRICATION MOTION AND ENERGIZATION"} for i,e,s in holds])

    sources = [
        {"source_id":"REC2-SRC-001","manufacturer":"ACE Controls Inc.","title":"MA30M product page","revision_or_date":"live page; no formal revision exposed","accessed":"2026-08-09","url":"https://www.acecontrols.com/us/products/automation-control/miniature-shock-absorbers/ma30-to-ma900/ma30m.html","use":"M8x1, 0.32 in stroke, energy/effective-weight/velocity endpoints, integrated positive stop","boundary":"application acceptance required"},
        {"source_id":"REC2-SRC-002","manufacturer":"ACE Stossdaempfer GmbH","title":"MA30-MA900 operating and mounting instructions","revision_or_date":"21_22_0019; Stand 03.2021; Issue 05.2022","accessed":"2026-08-09","url":"https://www.acecontrols.com/media/msimages/pdf/ACE_MA30-MA900_Operating-Mounting_EN_21_22_0019.pdf","use":"axial load, parallel-unit and additional-safety-element boundaries","boundary":"manufacturer instructions are not project approval"},
        {"source_id":"REC2-SRC-003","manufacturer":"igus","title":"drylin T standard rail product page","revision_or_date":"live page; no formal revision exposed","accessed":"2026-08-09","url":"https://www.igus.com/product/drylin_TS_01","use":"TS-01 family, hard-anodized aluminum, length and hole options","boundary":"configured 120 mm code not inferred"},
        {"source_id":"REC2-SRC-004","manufacturer":"igus","title":"drylin T automatic-clearance carriage product page","revision_or_date":"live page; copyright 2026; no formal revision exposed","accessed":"2026-08-09","url":"https://www.igus.com/product/drylin_TWA_01","use":"TWA-01 family, automatic clearance and installation sequence","boundary":"received size-20 CAD and application review required"},
        {"source_id":"REC2-SRC-005","manufacturer":"igus","title":"drylin T technical data","revision_or_date":"live page; no formal revision exposed","accessed":"2026-08-09","url":"https://www.igus.com/linear-bearings/linear-guides-technical-data-drylin-t","use":"01-20 static capacity table","boundary":"shock, acceleration and system moments require application calculation"},
        {"source_id":"REC2-SRC-006","manufacturer":"80/20 Inc.","title":"20-2020 product page","revision_or_date":"live page; copyright 2026; no formal revision exposed","accessed":"2026-08-09","url":"https://8020.net/20-2020.html","use":"exact profile identity and published section data","boundary":"configured cuts and joint proof open"},
        {"source_id":"REC2-SRC-007","manufacturer":"80/20 Inc.","title":"20-2040 product page","revision_or_date":"live page; no formal revision exposed","accessed":"2026-08-09","url":"https://8020.net/20-2040.html","use":"exact profile identity and published section data","boundary":"configured cuts and joint proof open"},
        {"source_id":"REC2-SRC-008","manufacturer":"80/20 Inc.","title":"20-4113 product page","revision_or_date":"live page; copyright 2026; no formal revision exposed","accessed":"2026-08-09","url":"https://8020.net/20-4113.html","use":"bracket dimensions and suggested 11-5308/14122 hardware","boundary":"no joint allowable published on page"},
        {"source_id":"REC2-SRC-009","manufacturer":"Sorbothane Inc.","title":"12 x 12 in sheet-stock product page","revision_or_date":"live page; copyright 2026; no formal revision exposed","accessed":"2026-08-09","url":"https://www.sorbothane.com/sorbothane-products/standard-industrial-products/product/sheet-stock-12-x-12/","use":"0212037-50-10 identity, size, durometer and thickness tolerance","boundary":"typical material/application claims are not acceptance limits"},
        {"source_id":"REC2-SRC-010","manufacturer":"ASTM International","title":"B209/B209M aluminum sheet and plate standard listing","revision_or_date":"B209/B209M-21a listed active at access","accessed":"2026-08-09","url":"https://store.astm.org/products-services/standards-and-publications/standards/nonferrous-metal-standards-and-nonferrous-alloy-standards.html","use":"candidate material procurement standard identity","boundary":"purchase-order edition and supplier certificate remain required"},
    ]
    write_csv(OUT / "source-register.csv", sources)

    bounds = cq.Compound.makeCompound(list(shapes.values())).BoundingBox()
    fit = {
        "x_min_mm": bounds.xmin, "x_max_mm": bounds.xmax, "y_min_mm": bounds.ymin, "y_max_mm": bounds.ymax,
        "z_min_mm": bounds.zmin, "z_max_mm": bounds.zmax,
        "guard_x_margin_left_mm": bounds.xmin - GUARD_X_MIN,
        "guard_x_margin_right_mm": GUARD_X_MAX - bounds.xmax,
        "guard_y_margin_front_mm": bounds.ymin - GUARD_Y_MIN,
        "guard_y_margin_rear_mm": GUARD_Y_MAX - bounds.ymax,
    }
    summary = {
        "identifier": IDENTIFIER,
        "warning": WARNING,
        "parent_identifiers": [r127.IDENTIFIER, "HR-V0-PASSIVE-ARM-RECEIVER-VERIFY-P0.1"],
        "receiver_top_z_mm": RECEIVER_TOP_Z,
        "platen_bottom_z_mm": PLATEN_BOTTOM_Z,
        "backup_stop_top_z_mm": BACKUP_STOP_TOP_Z,
        "backup_gap_mm": BACKUP_GAP,
        "catalog_stroke_mm": SHOCK_STROKE,
        "nominal_residual_after_catalog_stroke_mm": BACKUP_GAP - SHOCK_STROKE,
        "known_commanded_clearance_mm": 63.10647837214253,
        "assembly_bounds_and_guard_margins": fit,
        "bom_rows": len(exact_bom),
        "interface_rows": len(interfaces),
        "hold_rows": len(holds),
        "gate_state": "EG-008 AND EG-009 REMAIN PARTIAL",
    }
    (OUT / "receiver-detail-summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")

    write_svg_drawings()
    assembly = cq.Assembly(name="HR_V0_RECEIVER_DETAIL_REVIEW_ONLY")
    guard.add_frame(assembly)
    for name, shape in shapes.items():
        if name.startswith("SOR"):
            color = cq.Color(0.96, 0.72, 0.20)
        elif name.startswith("ACE"):
            color = cq.Color(0.78, 0.18, 0.12)
        elif name.startswith("IGUS"):
            color = cq.Color(0.25, 0.31, 0.38)
        elif name.startswith("BACKUP"):
            color = cq.Color(0.90, 0.35, 0.10)
        elif name.startswith("FAB"):
            color = cq.Color(0.45, 0.78, 0.94)
        else:
            color = cq.Color(0.18, 0.35, 0.55)
        assembly.add(shape, name=name, color=color)
    assembly.save(str(OUT / "HR-V0_passive-arm-receiver-detail-review.glb"))
    step_path = OUT / "HR-V0_passive-arm-receiver-detail-candidate.step"
    cq.exporters.export(cq.Compound.makeCompound(list(shapes.values())), str(step_path))
    normalize_step(step_path)
    for name, solid in (("FAB-REC-001-platen-blank.step", make_platen()), ("FAB-REC-002-shock-plate-blank.step", make_shock_plate()), ("FAB-REC-003-guide-tab-blank.step", make_guide_tab())):
        part_path = OUT / name
        cq.exporters.export(solid, str(part_path))
        normalize_step(part_path)
        cq.exporters.export(solid.faces("<Z"), str(part_path.with_suffix(".dxf")))

    GUIDE.parent.mkdir(parents=True, exist_ok=True)
    GUIDE.write_text(f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>HR-V0 receiver detail P0.2</title><style>:root{{--deep:#041a35;--navy:#082b55;--sky:#7dd3fc;--pale:#e4f6ff;--gold:#f4b942;--ink:#102a43;--line:#9ccfe8;--red:#a83220}}*{{box-sizing:border-box}}body{{margin:0;background:var(--pale);color:var(--ink);font:17px/1.55 system-ui,"Segoe UI",sans-serif}}header{{background:linear-gradient(135deg,var(--deep),var(--navy));color:#fff;padding:clamp(34px,6vw,72px) 20px}}header>div,main{{max-width:1120px;margin:auto}}h1{{font-size:clamp(36px,6vw,64px);line-height:1.05;margin:.2em 0}}h2{{font-size:clamp(27px,3.5vw,39px);line-height:1.15;color:var(--navy)}}.eyebrow{{font-size:14px;font-weight:850;color:var(--sky)}}.warning{{background:var(--gold);color:#17243a;border:3px solid #8a5b00;padding:15px 18px;font-weight:850}}main{{padding:30px 20px 80px}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(245px,1fr));gap:18px}}.card,.panel{{background:#fff;border:2px solid var(--line);border-radius:16px;padding:20px;box-shadow:0 3px 0 #bddbea}}.metric{{font-size:clamp(34px,6vw,55px);font-weight:900;color:#075b9b}}.hold{{border-left:9px solid var(--gold)}}model-viewer{{width:100%;height:520px;background:#dff3ff;border:2px solid var(--line);border-radius:16px}}table{{width:100%;border-collapse:collapse;background:#fff}}th,td{{padding:13px;border:1px solid #8aa8ba;text-align:left;vertical-align:top;font-size:16px}}th{{background:#d5effc}}footer{{background:var(--deep);color:#fff;padding:30px 20px}}footer p{{max-width:1120px;margin:auto}}@media(max-width:760px){{body{{font-size:16px}}model-viewer{{height:430px}}.table{{overflow:auto}}}}</style><script type="module" src="../../vendor/model-viewer/4.1.0/model-viewer.min.js"></script></head><body><header><div><p class="warning">{WARNING}</p><p class="eyebrow">{IDENTIFIER}</p><h1>The receiver now has exact candidate guides, contact stock, and frame joints.</h1><p>R129 replaces four anonymous guide envelopes and an anonymous pad with traceable manufacturer candidates, dimensioned blanks, a cut plan, an interface register, and an independent backup-stop allocation.</p></div></header><main><section><h2>What became concrete</h2><div class="grid"><article class="card"><div class="metric">16</div><p>BOM rows: exact candidates or explicit selection-required boundaries.</p></article><article class="card"><div class="metric">9.625 mm</div><p>Nominal independent catch gap below the platen.</p></article><article class="card"><div class="metric">1.497 mm</div><p>Nominal residual after the MA30M catalog stroke. Tolerances remain open.</p></article></div></section><section><h2>Candidate stack</h2><div class="table"><table><thead><tr><th>Function</th><th>Controlled candidate</th><th>Release boundary</th></tr></thead><tbody><tr><td>Linear guidance</td><td>4 x igus TWA-01-20 on TS-01-20, 120 mm configured-length candidate</td><td>Configured rail order code, received CAD, load orientation, life, alignment and proof remain open.</td></tr><tr><td>Contact layer</td><td>3 x Sorbothane 0212037-50-10 cut to 180 x 266.7/266.6/266.7 mm</td><td>Retention, dynamic deflection, rebound, wear, flammability and manufacturer suitability remain open.</td></tr><tr><td>Subframe joints</td><td>8 x 20-4113 with 32 x 11-5308 and 32 x 14122</td><td>The product page supplies geometry and suggested hardware, not a joint allowable.</td></tr><tr><td>Moving platen</td><td>FAB-REC-001 blank: 180 x 800 x 6.35 mm, 6061-T651 candidate</td><td>Material certificate, thickness/flatness, edges, final holes, analysis, FAI and proof remain open.</td></tr></tbody></table></div></section><section><h2>Review the detailed candidate</h2><model-viewer src="../../../cad/hr-v0/generated/passive-arm-receiver-detail-p0.2/HR-V0_passive-arm-receiver-detail-review.glb" camera-controls interaction-prompt="none" shadow-intensity="0.5" alt="Detailed receiver candidate inside the fixed guard"></model-viewer></section><section><h2>Why the backup stops are still allocations</h2><div class="panel"><p>The platen bottom is nominally Z {PLATEN_BOTTOM_Z:.3f} mm. Four independent catch surfaces are allocated at Z {BACKUP_STOP_TOP_Z:.3f} mm, leaving {BACKUP_GAP:.3f} mm before contact. The MA30M catalog stroke is {SHOCK_STROKE:.3f} mm, so the nominal separation is only {BACKUP_GAP-SHOCK_STROKE:.3f} mm. No tolerance, deformation, rebound, peak-force, single-catch, or failure-containment credit is released.</p></div></section><section><h2>Still fail-closed</h2><div class="grid"><article class="card hold"><strong>Impact application</strong><p>ACE must accept the actual mass, velocity, propelling force, parallel sharing, temperature and cycles.</p></article><article class="card hold"><strong>Guide application</strong><p>igus must confirm the selected arrangement and loads after received CAD and measured dynamics exist.</p></article><article class="card hold"><strong>Structural path</strong><p>Joints, posts, braces, guard/base transfer and anchors need accepted peak loads and proof.</p></article><article class="card hold"><strong>Physical evidence</strong><p>FAI, metrology, protected drops, fault injection and qualified review are unexecuted. EG-008 and EG-009 remain partial.</p></article></div></section></main><footer><p>Project Button · {IDENTIFIER} · zero fabrication, motion, energization or functional-safety approval</p></footer></body></html>''', encoding="utf-8", newline="\n")

    collapse.write_generated_source_manifest()
    print(f"Generated {IDENTIFIER}: {len(exact_bom)} BOM rows, {len(interfaces)} interfaces, {len(holds)} holds")
    print(f"Nominal backup gap {BACKUP_GAP:.3f} mm; residual after catalog stroke {BACKUP_GAP-SHOCK_STROKE:.3f} mm")
    print(WARNING)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
