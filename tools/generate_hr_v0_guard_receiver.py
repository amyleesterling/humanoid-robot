"""Generate the HR-V0 fixed-guard and catch-receiver design candidate.

The output is a dimensioned space and fabrication-definition candidate.  It is
not a safety-distance determination, structural qualification, cutting release,
or authorization to fabricate, move, connect, or energize hardware.
"""

from __future__ import annotations

import csv
import json
import math
import shutil
from pathlib import Path

import cadquery as cq


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "cad" / "hr-v0" / "guard-receiver-p0.3"
REVISION = "HR-V0-GUARD-P0.3"
ARM_REVISION = "HR-V0-ARM-ARCH-P0.7"
WARNING = (
    "PRELIMINARY - DESIGN CANDIDATE ONLY - NOT APPROVED FOR FABRICATION, "
    "MOTION, CONNECTION, OR ENERGIZATION"
)

# Guard datum G0 is the vertical projection of J1 onto the bench.  X is guard
# depth, Y is guard width, and Z is height above the bench.
INNER_X = 400.0
INNER_Y = 900.0
INNER_Z = 950.0
FRAME = 20.0
PANEL_T = 6.0
FRAME_Z = INNER_Z + FRAME
SHOULDER_Z = 500.0
SPACE_RADIUS = 450.0
RECEIVER_X = 320.0
RECEIVER_Y = 820.0
RECEIVER_WALL = 50.0
RECEIVER_T = 6.0
FOAM_MASS_KG = 0.100
MAX_DROP_HEIGHT_M = INNER_Z / 1000.0
DROP_ENERGY_J = FOAM_MASS_KG * 9.80665 * MAX_DROP_HEIGHT_M
PROFILE_WEIGHT_LB_PER_IN = 0.0247
PROFILE_TOTAL_LENGTH_MM = 11820.0
PROFILE_MASS_KG = PROFILE_WEIGHT_LB_PER_IN * (PROFILE_TOTAL_LENGTH_MM / 25.4) * 0.45359237
SHEET_DENSITY_KG_M3 = 1200.0


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def normalize_step(path: Path) -> None:
    """Remove exporter-only trailing spaces while preserving STEP statements."""

    lines = path.read_text(encoding="utf-8").splitlines()
    path.write_text("\n".join(line.rstrip() for line in lines) + "\n", encoding="utf-8")


def box(dx: float, dy: float, dz: float, x: float, y: float, z: float) -> cq.Shape:
    return cq.Solid.makeBox(dx, dy, dz, cq.Vector(x, y, z))


def add_frame(assembly: cq.Assembly) -> None:
    blue = cq.Color(0.07, 0.24, 0.41)
    # Six full-height posts: four corners plus front/rear center posts.
    post_locations = (
        (-INNER_X / 2 - FRAME, -INNER_Y / 2 - FRAME),
        (-INNER_X / 2 - FRAME, INNER_Y / 2),
        (INNER_X / 2, -INNER_Y / 2 - FRAME),
        (INNER_X / 2, INNER_Y / 2),
        (-INNER_X / 2 - FRAME, -FRAME / 2),
        (INNER_X / 2, -FRAME / 2),
    )
    for index, (x, y) in enumerate(post_locations, 1):
        assembly.add(box(FRAME, FRAME, FRAME_Z, x, y, 0), name=f"POST-{index:02d}", color=blue)

    # Four width rails, four depth rails, and two center depth rails.
    for z, suffix in ((0.0, "BOT"), (INNER_Z, "TOP")):
        for x, face in ((-INNER_X / 2 - FRAME, "FRONT"), (INNER_X / 2, "REAR")):
            assembly.add(
                box(FRAME, INNER_Y, FRAME, x, -INNER_Y / 2, z),
                name=f"YRAIL-{face}-{suffix}",
                color=blue,
            )
        for y, side in ((-INNER_Y / 2 - FRAME, "LEFT"), (INNER_Y / 2, "RIGHT")):
            assembly.add(
                box(INNER_X, FRAME, FRAME, -INNER_X / 2, y, z),
                name=f"XRAIL-{side}-{suffix}",
                color=blue,
            )
        assembly.add(
            box(INNER_X, FRAME, FRAME, -INNER_X / 2, -FRAME / 2, z),
            name=f"XRAIL-CENTER-{suffix}",
            color=blue,
        )


def add_panels(assembly: cq.Assembly) -> None:
    clear = cq.Color(0.45, 0.78, 0.94, 0.35)
    # Front/rear halves overlap the center post by 15 mm.  Panel drilling and
    # retention are deliberately absent until the clamp/fastener selection closes.
    half_y = INNER_Y / 2 + FRAME + 15.0
    for x, face in ((-INNER_X / 2 - FRAME - PANEL_T, "FRONT"), (INNER_X / 2 + FRAME, "REAR")):
        for y0, half in ((-INNER_Y / 2 - FRAME, "LEFT"), (-15.0, "RIGHT")):
            assembly.add(
                box(PANEL_T, half_y, FRAME_Z, x, y0, 0),
                name=f"PANEL-{face}-{half}",
                color=clear,
            )
    for y, side in ((-INNER_Y / 2 - FRAME - PANEL_T, "LEFT"), (INNER_Y / 2 + FRAME, "RIGHT")):
        assembly.add(
            box(INNER_X + 2 * FRAME, PANEL_T, FRAME_Z, -INNER_X / 2 - FRAME, y, 0),
            name=f"PANEL-{side}",
            color=clear,
        )
    for y0, half in ((-INNER_Y / 2 - FRAME, "LEFT"), (-15.0, "RIGHT")):
        assembly.add(
            box(INNER_X + 2 * FRAME, half_y, PANEL_T, -INNER_X / 2 - FRAME, y0, FRAME_Z),
            name=f"PANEL-TOP-{half}",
            color=clear,
        )


def add_receiver(assembly: cq.Assembly) -> None:
    gold = cq.Color(0.96, 0.68, 0.12)
    x0 = -RECEIVER_X / 2 - RECEIVER_T
    y0 = -RECEIVER_Y / 2 - RECEIVER_T
    assembly.add(
        box(RECEIVER_X + 2 * RECEIVER_T, RECEIVER_Y + 2 * RECEIVER_T, RECEIVER_T, x0, y0, FRAME),
        name="RECEIVER-BASE",
        color=gold,
    )
    assembly.add(box(RECEIVER_T, RECEIVER_Y + 2 * RECEIVER_T, RECEIVER_WALL, x0, y0, FRAME), name="RECEIVER-WALL-X1", color=gold)
    assembly.add(box(RECEIVER_T, RECEIVER_Y + 2 * RECEIVER_T, RECEIVER_WALL, RECEIVER_X / 2, y0, FRAME), name="RECEIVER-WALL-X2", color=gold)
    assembly.add(box(RECEIVER_X, RECEIVER_T, RECEIVER_WALL, -RECEIVER_X / 2, y0, FRAME), name="RECEIVER-WALL-Y1", color=gold)
    assembly.add(box(RECEIVER_X, RECEIVER_T, RECEIVER_WALL, -RECEIVER_X / 2, RECEIVER_Y / 2, FRAME), name="RECEIVER-WALL-Y2", color=gold)


def svg() -> str:
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1600" height="1080" viewBox="0 0 1600 1080">
<style>
text {{ font-family: Arial, sans-serif; fill: #102a43; font-size: 18px; }}
.title {{ font-size: 34px; font-weight: 700; }} .head {{ font-size: 23px; font-weight: 700; }}
.warn {{ font-size: 19px; font-weight: 700; fill: #7b3f00; }}
.frame {{ fill: none; stroke: #123b68; stroke-width: 8; }} .panel {{ fill: #9dd8f5; fill-opacity: .30; stroke: #2878a8; stroke-width: 3; }}
.sweep {{ fill: #f4bd3e; fill-opacity: .20; stroke: #c38300; stroke-width: 4; stroke-dasharray: 12 8; }}
.catch {{ fill: #f4bd3e; fill-opacity: .55; stroke: #123b68; stroke-width: 3; }}
.dim {{ stroke: #526d82; stroke-width: 2; marker-start: url(#a); marker-end: url(#a); }}
</style>
<defs><marker id="a" markerWidth="8" markerHeight="8" refX="4" refY="4" orient="auto"><path d="M0,4 L8,0 L8,8 Z" fill="#526d82"/></marker></defs>
<rect width="1600" height="1080" fill="#f8fbff"/>
<text x="55" y="62" class="title">HR-V0 fixed guard and receiver candidate</text>
<text x="55" y="102" class="warn">{WARNING}</text>
<text x="55" y="140">Revision {REVISION} • arm basis {ARM_REVISION} • all dimensions millimetres</text>
<text x="110" y="205" class="head">Front elevation (Y–Z at guard datum G0)</text>
<rect x="130" y="235" width="620" height="655" class="panel"/><rect x="130" y="235" width="620" height="655" class="frame"/>
<line x1="440" y1="235" x2="440" y2="890" class="frame"/>
<circle cx="440" cy="545" r="295" class="sweep"/><circle cx="440" cy="545" r="8" fill="#123b68"/>
<rect x="170" y="820" width="540" height="40" class="catch"/>
<line x1="130" y1="925" x2="750" y2="925" class="dim"/><text x="388" y="956">900 internal</text>
<line x1="90" y1="235" x2="90" y2="890" class="dim"/><text x="25" y="565" transform="rotate(-90 25 565)">950 internal</text>
<text x="455" y="535">J1 axis, Z = 500</text><text x="455" y="570">450 reserved radial space</text>
<text x="170" y="812">820 × 320 receiver clear region, 50 wall</text>

<text x="900" y="205" class="head">Plan (X–Y at bench)</text>
<rect x="920" y="265" width="310" height="620" class="panel"/><rect x="920" y="265" width="310" height="620" class="frame"/>
<rect x="950" y="300" width="250" height="550" class="catch"/>
<line x1="920" y1="920" x2="1230" y2="920" class="dim"/><text x="1015" y="952">400 internal</text>
<line x1="1270" y1="265" x2="1270" y2="885" class="dim"/><text x="1295" y="610" transform="rotate(-90 1295 610)">900 internal</text>
<text x="920" y="995">Six posts; sixteen exact-candidate 80/20 20-2020 pieces.</text>
<text x="920" y="1028">Eight outer plus five receiver 6 mm TUFFAK GP geometry candidates.</text>

<rect x="55" y="970" width="790" height="80" rx="14" fill="#fff3d6" stroke="#c38300" stroke-width="3"/>
<text x="75" y="1002">These dimensions reserve space only. Measured stopping, full gripper/cable sweep,</text>
<text x="75" y="1035">panel grade, retention, impact, access, anchors and qualified review remain open.</text>
</svg>'''


def interactive_html() -> str:
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>HR-V0 guard candidate</title><style>
:root{{--sky:#9dd8f5;--navy:#102a43;--gold:#f4bd3e;--paper:#f8fbff}}*{{box-sizing:border-box}}body{{margin:0;font:16px/1.5 system-ui,sans-serif;color:var(--navy);background:var(--paper)}}
main{{max-width:1120px;margin:auto;padding:24px}}h1{{font-size:clamp(28px,4vw,44px);margin:.2em 0}}h2{{font-size:24px}}.warning{{padding:16px;border:3px solid #c38300;background:#fff3d6;font-weight:750}}
.controls{{display:flex;flex-wrap:wrap;gap:16px;margin:20px 0;padding:16px;background:white;border:2px solid #123b68;border-radius:12px}}label{{font-size:16px;font-weight:650}}input{{width:20px;height:20px;vertical-align:middle}}
svg{{width:100%;height:auto;background:white;border:2px solid #123b68;border-radius:12px}}.frame{{fill:none;stroke:#123b68;stroke-width:10}}.panel{{fill:var(--sky);opacity:.38;stroke:#2878a8;stroke-width:3}}.sweep{{fill:var(--gold);opacity:.25;stroke:#c38300;stroke-width:4;stroke-dasharray:12 8}}.catch{{fill:var(--gold);stroke:#123b68;stroke-width:3}}.label{{font-size:18px;fill:#102a43}}table{{width:100%;border-collapse:collapse;background:white}}th,td{{padding:12px;border:1px solid #789;text-align:left;vertical-align:top;font-size:16px}}th{{background:#dff2fb}}code{{font-size:16px}}@media(max-width:600px){{main{{padding:14px}}th,td{{display:block;width:100%}}}}
</style></head><body><main><p class="warning">{WARNING}</p><h1>Fixed guard and receiver candidate</h1><p>Guard datum <code>G0</code> is directly below J1 on the bench. X is depth, Y is width, and Z is height. Toggle layers to inspect the design boundary; this viewer does not establish a safety distance.</p>
<div class="controls"><label><input id="panels" type="checkbox" checked> Transparent panel geometry</label><label><input id="sweep" type="checkbox" checked> Reserved swept/stopping space</label><label><input id="catch" type="checkbox" checked> Catch receiver</label></div>
<svg viewBox="0 0 1000 760" role="img" aria-labelledby="t d"><title id="t">HR-V0 guard front and plan views</title><desc id="d">Dimensioned fixed enclosure with reserved reach space and catch receiver.</desc>
<g id="panelLayer"><rect x="70" y="80" width="520" height="550" class="panel"/><rect x="670" y="190" width="230" height="440" class="panel"/></g>
<g><rect x="70" y="80" width="520" height="550" class="frame"/><line x1="330" y1="80" x2="330" y2="630" class="frame"/><rect x="670" y="190" width="230" height="440" class="frame"/></g>
<g id="sweepLayer"><circle cx="330" cy="369" r="260" class="sweep"/><text x="346" y="360" class="label">J1 Z=500</text><text x="346" y="390" class="label">450 mm radius</text></g>
<g id="catchLayer"><rect x="100" y="570" width="460" height="35" class="catch"/><rect x="690" y="215" width="190" height="390" class="catch"/></g>
<text x="70" y="680" class="label">Front: 900 W × 950 H internal</text><text x="670" y="680" class="label">Plan: 400 D × 900 W internal</text><text x="70" y="720" class="label">Eight panel candidates; tool-removable only after isolation. No interlock is selected or credited.</text></svg>
<h2>Controlled dimensions and boundaries</h2><table><tr><th>Item</th><th>Candidate</th><th>Release boundary</th></tr><tr><td>Internal clear box</td><td>400 X × 900 Y × 950 Z mm</td><td>Must grow if complete swept, stopping, cable, payload, tolerance or access evidence exceeds it.</td></tr><tr><td>Frame</td><td>80/20 20-2020, 6063-T6 clear anodized; 16 custom lengths</td><td>Exact product candidate; joint strength, received dimensions, anchors and proof remain open.</td></tr><tr><td>Panels</td><td>Plaskolite TUFFAK GP clear, nominal 6 mm; 13 cut pieces</td><td>Exact grade candidate; supplier SKU, thickness tolerance, retention, impact and edge treatment remain open.</td></tr><tr><td>Receiver</td><td>320 × 820 mm clear, 50 mm wall</td><td>Support, nests and drop/rebound acceptance are SELECTION REQUIRED.</td></tr></table>
<p class="warning">No cutting, drilling, purchase, installation, motion, connection or energization is authorized by this package.</p></main>
<script>for(const id of ['panels','sweep','catch'])document.getElementById(id).addEventListener('change',e=>document.getElementById(id==='panels'?'panelLayer':id+'Layer').style.display=e.target.checked?'':'none');</script></body></html>'''


def main() -> int:
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)

    frame_rows = [
        {"item_id": "GF-POST", "profile_envelope_mm": "20 x 20", "cut_length_mm": FRAME_Z, "quantity": 6, "function": "vertical posts", "selection_state": "PROFILE MATERIAL CONNECTORS AND CUT TOLERANCE SELECTION REQUIRED"},
        {"item_id": "GF-YRAIL", "profile_envelope_mm": "20 x 20", "cut_length_mm": INNER_Y, "quantity": 4, "function": "front/rear top and bottom rails", "selection_state": "PROFILE MATERIAL CONNECTORS AND CUT TOLERANCE SELECTION REQUIRED"},
        {"item_id": "GF-XRAIL-SIDE", "profile_envelope_mm": "20 x 20", "cut_length_mm": INNER_X, "quantity": 4, "function": "side top and bottom rails", "selection_state": "PROFILE MATERIAL CONNECTORS AND CUT TOLERANCE SELECTION REQUIRED"},
        {"item_id": "GF-XRAIL-CENTER", "profile_envelope_mm": "20 x 20", "cut_length_mm": INNER_X, "quantity": 2, "function": "top/bottom center rails", "selection_state": "PROFILE MATERIAL CONNECTORS AND CUT TOLERANCE SELECTION REQUIRED"},
    ]
    half_y = INNER_Y / 2 + FRAME + 15.0
    panel_rows = [
        {"item_id": "GP-FRONT-HALF", "finished_x_mm": PANEL_T, "finished_y_mm": half_y, "finished_z_mm": FRAME_Z, "quantity": 2, "candidate_material": "transparent sheet", "selection_state": "GRADE THICKNESS RETENTION EDGE AND IMPACT SELECTION REQUIRED"},
        {"item_id": "GP-REAR-HALF", "finished_x_mm": PANEL_T, "finished_y_mm": half_y, "finished_z_mm": FRAME_Z, "quantity": 2, "candidate_material": "transparent sheet", "selection_state": "GRADE THICKNESS RETENTION EDGE AND IMPACT SELECTION REQUIRED"},
        {"item_id": "GP-SIDE", "finished_x_mm": INNER_X + 2 * FRAME, "finished_y_mm": PANEL_T, "finished_z_mm": FRAME_Z, "quantity": 2, "candidate_material": "transparent sheet", "selection_state": "GRADE THICKNESS RETENTION EDGE AND IMPACT SELECTION REQUIRED"},
        {"item_id": "GP-TOP-HALF", "finished_x_mm": INNER_X + 2 * FRAME, "finished_y_mm": half_y, "finished_z_mm": PANEL_T, "quantity": 2, "candidate_material": "transparent sheet", "selection_state": "GRADE THICKNESS RETENTION EDGE AND IMPACT SELECTION REQUIRED"},
        {"item_id": "GR-BASE", "finished_x_mm": RECEIVER_X + 2 * RECEIVER_T, "finished_y_mm": RECEIVER_Y + 2 * RECEIVER_T, "finished_z_mm": RECEIVER_T, "quantity": 1, "candidate_material": "Plaskolite TUFFAK GP clear nominal 6 mm", "selection_state": "EXACT GRADE CANDIDATE; SUPPLIER SKU RETENTION SUPPORT AND IMPACT SELECTION REQUIRED"},
        {"item_id": "GR-WALL-X", "finished_x_mm": RECEIVER_T, "finished_y_mm": RECEIVER_Y + 2 * RECEIVER_T, "finished_z_mm": RECEIVER_WALL, "quantity": 2, "candidate_material": "Plaskolite TUFFAK GP clear nominal 6 mm", "selection_state": "EXACT GRADE CANDIDATE; SUPPLIER SKU RETENTION SUPPORT AND IMPACT SELECTION REQUIRED"},
        {"item_id": "GR-WALL-Y", "finished_x_mm": RECEIVER_X, "finished_y_mm": RECEIVER_T, "finished_z_mm": RECEIVER_WALL, "quantity": 2, "candidate_material": "Plaskolite TUFFAK GP clear nominal 6 mm", "selection_state": "EXACT GRADE CANDIDATE; SUPPLIER SKU RETENTION SUPPORT AND IMPACT SELECTION REQUIRED"},
    ]
    for row in panel_rows[:4]:
        row["candidate_material"] = "Plaskolite TUFFAK GP clear nominal 6 mm"
        row["selection_state"] = "EXACT GRADE CANDIDATE; SUPPLIER SKU RETENTION EDGE AND IMPACT SELECTION REQUIRED"
    controls = [
        {"control_id": "G0", "controlled_value": "origin at vertical projection of J1 onto bench", "status": "DATUM CANDIDATE", "closure_evidence": "bench survey and accepted J1 as-built transform"},
        {"control_id": "G-X", "controlled_value": "internal X -200 to +200 mm", "status": "SPACE CANDIDATE", "closure_evidence": "complete gripper cable and stopping sweep"},
        {"control_id": "G-Y", "controlled_value": "internal Y -450 to +450 mm", "status": "SPACE CANDIDATE", "closure_evidence": "complete gripper cable and stopping sweep"},
        {"control_id": "G-Z", "controlled_value": "internal Z 0 to 950 mm", "status": "SPACE CANDIDATE", "closure_evidence": "complete gripper cable and stopping sweep"},
        {"control_id": "G-J1", "controlled_value": "J1 axis at G0 + (0 0 500) mm", "status": "ARM P0.7 BINDING", "closure_evidence": "received assembly metrology"},
        {"control_id": "G-R", "controlled_value": "450 mm radial reservation in Y-Z", "status": "NOT A SAFETY DISTANCE", "closure_evidence": "measured stopping travel tolerance access and payload union"},
        {"control_id": "G-SERVICE", "controlled_value": "all panels tool-removable only after isolation", "status": "NO INTERLOCK CREDIT", "closure_evidence": "service procedure panel hardware and access validation"},
        {"control_id": "G-CONTROL", "controlled_value": "E-stop RESET ARM outside boundary", "status": "LAYOUT REQUIRED", "closure_evidence": "accepted human-factors and panel installation record"},
    ]
    holds = [
        ("GH-001", "complete P0.7 gripper payload and cable swept/stopping envelope", "OPEN"),
        ("GH-002", "measured worst-case stopping travel and uncertainty for every permitted mode and fault", "OPEN"),
        ("GH-003", "80/20 20-2020 and 14201/75-3581 joint application strength received dimensions torque and proof", "OPEN"),
        ("GH-004", "Plaskolite TUFFAK GP clear 6 mm supplier SKU thickness tolerance suitability impact and flame disposition", "OPEN"),
        ("GH-005", "panel clamp or fastener pattern retention loads edge distances and service method", "DESIGN REQUIRED"),
        ("GH-006", "guard stability bench-anchor and frame-joint calculations plus proof", "OPEN"),
        ("GH-007", "access probe and minimum clearance rationale with physical test", "SELECTION REQUIRED"),
        ("GH-008", "receiver material support fasteners nests rebound and damage acceptance", "DESIGN REQUIRED"),
        ("GH-009", "drop and detached-part containment risk assessment and tests", "OPEN"),
        ("GH-010", "cable-entry plate gland clamp bend and service design", "SELECTION REQUIRED"),
        ("GH-011", "Boston site bench footprint egress electrical separation and service survey", "OPEN"),
        ("GH-012", "qualified mechanical electrical and functional-safety review", "OPEN"),
    ]
    source_rows = [
        {"source_id": "GS-001", "organization": "OSHA", "document": "29 CFR 1910.212 General requirements for all machines", "revision_or_date": "current electronic regulation accessed 2026-08-07", "url": "https://www.osha.gov/laws-regs/regulations/standardnumber/1910/1910.212", "use": "guard affixing and no-new-hazard design input", "verification": "PRIMARY SOURCE VERIFIED"},
        {"source_id": "GS-002", "organization": "ISO", "document": "ISO 14120:2015 Edition 2", "revision_or_date": "published 2015-11; confirmed 2021; systematic review opened 2026-01-15", "url": "https://www.iso.org/standard/59545.html", "use": "fixed and movable guard design framework", "verification": "PRIMARY SOURCE METADATA VERIFIED; LICENSED STANDARD REVIEW REQUIRED"},
        {"source_id": "GS-003", "organization": "80/20", "document": "20-2020 product page", "revision_or_date": "live page; no formal revision exposed; accessed 2026-08-07", "url": "https://8020.net/20-2020.html", "use": "20 x 20 frame profile exact catalog candidate", "verification": "PRIMARY SOURCE VERIFIED"},
        {"source_id": "GS-004", "organization": "80/20", "document": "14201 supported corner bracket product page", "revision_or_date": "live page; no formal revision exposed; accessed 2026-08-07", "url": "https://8020.net/14201.html", "use": "twenty frame-joint bracket candidates and suggested 75-3581 hardware", "verification": "PRIMARY SOURCE VERIFIED"},
        {"source_id": "GS-005", "organization": "80/20", "document": "20-2496 panel retainer product page", "revision_or_date": "live page; no formal revision exposed; accessed 2026-08-07", "url": "https://8020.net/20-2496.html", "use": "panel-retainer family candidate only; quantity and drill pattern open", "verification": "PRIMARY SOURCE VERIFIED"},
        {"source_id": "GS-006", "organization": "Plaskolite", "document": "PDS004 TUFFAK GP polycarbonate sheet", "revision_or_date": "122022; accessed 2026-08-07", "url": "https://plaskolite.com/docs/default-source/pds/pds004_tuf_gp.pdf", "use": "clear nominal 6 mm panel and receiver material candidate", "verification": "PRIMARY SOURCE VERIFIED; TYPICAL DATA NOT SPECIFICATION VALUES"},
    ]
    joint_rows = [
        {"joint_group": "GJ-Y-END", "joint_count": 8, "members": "four Y rails to four corner posts", "bracket_candidate": "80/20 14201", "hardware_per_joint": "two 75-3581 assemblies", "state": "EXACT CATALOG CANDIDATE; STRENGTH TORQUE FIT AND PROOF OPEN"},
        {"joint_group": "GJ-X-SIDE-END", "joint_count": 8, "members": "four side X rails to four corner posts", "bracket_candidate": "80/20 14201", "hardware_per_joint": "two 75-3581 assemblies", "state": "EXACT CATALOG CANDIDATE; STRENGTH TORQUE FIT AND PROOF OPEN"},
        {"joint_group": "GJ-X-CENTER-END", "joint_count": 4, "members": "two center X rails to two center posts", "bracket_candidate": "80/20 14201", "hardware_per_joint": "two 75-3581 assemblies", "state": "EXACT CATALOG CANDIDATE; STRENGTH TORQUE FIT AND PROOF OPEN"},
    ]
    catalog_rows = [
        {"candidate_id": "GCAT-001", "manufacturer": "80/20 Inc.", "order_code": "20-2020 custom length", "candidate_quantity": "16 pieces per frame cut schedule", "state": "EXACT CATALOG CANDIDATE HOLD", "open_evidence": "written configuration; received length/squareness/profile identity; structural and joint proof"},
        {"candidate_id": "GCAT-002", "manufacturer": "80/20 Inc.", "order_code": "14201", "candidate_quantity": "20", "state": "EXACT CATALOG CANDIDATE HOLD", "open_evidence": "application load; orientation/access; received fit; torque and proof"},
        {"candidate_id": "GCAT-003", "manufacturer": "80/20 Inc.", "order_code": "75-3581", "candidate_quantity": "40", "state": "EXACT CATALOG CANDIDATE HOLD", "open_evidence": "received identity; torque/locking/reuse; slip and proof"},
        {"candidate_id": "GCAT-004", "manufacturer": "Plaskolite", "order_code": "TUFFAK GP clear nominal 6 mm; supplier SKU SELECTION REQUIRED", "candidate_quantity": "13 cut pieces per panel schedule", "state": "EXACT GRADE CANDIDATE HOLD", "open_evidence": "supplier SKU/stock; thickness tolerance; suitability; retention; impact; flame and edge disposition"},
        {"candidate_id": "GCAT-005", "manufacturer": "80/20 Inc.", "order_code": "20-2496", "candidate_quantity": "SELECTION REQUIRED", "state": "FAMILY CANDIDATE ONLY", "open_evidence": "retention load and spacing calculation; drill pattern; edge distance; service method"},
        {"candidate_id": "GCAT-006", "manufacturer": "80/20 Inc.", "order_code": "75-3581", "candidate_quantity": "SELECTION REQUIRED", "state": "FAMILY CANDIDATE ONLY", "open_evidence": "retainer quantity follows accepted panel retention design"},
    ]
    outer_panel_volume_m3 = sum(
        float(row["finished_x_mm"]) * float(row["finished_y_mm"]) * float(row["finished_z_mm"]) * int(row["quantity"])
        for row in panel_rows[:4]
    ) / 1_000_000_000.0
    receiver_volume_m3 = sum(
        float(row["finished_x_mm"]) * float(row["finished_y_mm"]) * float(row["finished_z_mm"]) * int(row["quantity"])
        for row in panel_rows[4:]
    ) / 1_000_000_000.0
    mass_rows = [
        {"mass_id": "GM-001", "item": "80/20 20-2020 profile", "basis": "11820 mm x 0.0247 lb/in published weight", "mass_kg": f"{PROFILE_MASS_KG:.6f}", "credit": "CATALOG ESTIMATE ONLY"},
        {"mass_id": "GM-002", "item": "eight outer TUFFAK GP panel candidates", "basis": "generated finished volume x PDS004 specific gravity 1.2", "mass_kg": f"{outer_panel_volume_m3 * SHEET_DENSITY_KG_M3:.6f}", "credit": "CANDIDATE GEOMETRY ESTIMATE ONLY"},
        {"mass_id": "GM-003", "item": "five receiver TUFFAK GP pieces", "basis": "generated finished volume x PDS004 specific gravity 1.2", "mass_kg": f"{receiver_volume_m3 * SHEET_DENSITY_KG_M3:.6f}", "credit": "CANDIDATE GEOMETRY ESTIMATE ONLY"},
        {"mass_id": "GM-004", "item": "known frame plus sheet subtotal", "basis": "GM-001 + GM-002 + GM-003", "mass_kg": f"{PROFILE_MASS_KG + (outer_panel_volume_m3 + receiver_volume_m3) * SHEET_DENSITY_KG_M3:.6f}", "credit": "INCOMPLETE; BRACKETS HARDWARE RETAINERS ANCHORS NESTS AND CABLE ENTRY OMITTED"},
    ]
    calculations = [
        {"calculation_id": "GCAL-001", "expression": "360 + 35 + 25 + 25 + 5", "result": "450 mm", "status": "SPACE RESERVATION ONLY", "boundary": "stopping clearance and tolerance terms remain provisional"},
        {"calculation_id": "GCAL-002", "expression": "0.100 kg x 9.80665 m/s2 x 0.950 m", "result": f"{DROP_ENERGY_J:.6f} J", "status": "TEST INPUT ONLY", "boundary": "not a guard or receiver impact rating"},
        {"calculation_id": "GCAL-003", "expression": "6 posts x 970 + 4 x 900 + 6 x 400", "result": "11820 mm profile envelope", "status": "CUT-LENGTH CANDIDATE", "boundary": "saw allowance and joint method absent"},
        {"calculation_id": "GCAL-004", "expression": "11820 mm x 0.0247 lb/in x 0.45359237 kg/lb", "result": f"{PROFILE_MASS_KG:.6f} kg", "status": "CATALOG MASS ESTIMATE", "boundary": "received mass and cut losses absent"},
        {"calculation_id": "GCAL-005", "expression": f"{outer_panel_volume_m3 + receiver_volume_m3:.9f} m3 total sheet volume x 1200 kg/m3", "result": f"{(outer_panel_volume_m3 + receiver_volume_m3) * SHEET_DENSITY_KG_M3:.6f} kg", "status": "GEOMETRY MASS ESTIMATE", "boundary": "PDS004 values are typical and not specification values; received thickness/mass absent"},
    ]
    write_csv(OUT / "guard-frame-cut-schedule.csv", frame_rows)
    write_csv(OUT / "guard-panel-cut-schedule.csv", panel_rows)
    write_csv(OUT / "guard-interface-controls.csv", controls)
    write_csv(OUT / "guard-closure-holds.csv", [{"hold_id": a, "unresolved_item": b, "state": c, "release_effect": "BLOCKS FABRICATION AND GUARDED MOTION"} for a, b, c in holds])
    write_csv(OUT / "guard-source-register.csv", source_rows)
    write_csv(OUT / "guard-calculation-screen.csv", calculations)
    write_csv(OUT / "guard-joint-schedule.csv", joint_rows)
    write_csv(OUT / "guard-catalog-candidates.csv", catalog_rows)
    write_csv(OUT / "guard-mass-screen.csv", mass_rows)

    assembly = cq.Assembly(name="HR-V0-GUARD-RECEIVER-P0.2")
    add_frame(assembly)
    add_panels(assembly)
    add_receiver(assembly)
    # The arm rotates in the Y-Z plane about +X.  Use a 400 mm-deep extruded
    # disk, not a sphere: the full out-of-plane gripper/cable sweep is still a
    # closure hold and must not be implied by this space study.
    reserved_space = cq.Solid.makeCylinder(
        SPACE_RADIUS,
        INNER_X,
        cq.Vector(-INNER_X / 2, 0, SHOULDER_Z),
        cq.Vector(1, 0, 0),
    )
    assembly.add(reserved_space, name="RESERVED-YZ-SPACE-NOT-SAFETY-DISTANCE", color=cq.Color(0.96, 0.68, 0.12, 0.18))
    step_path = OUT / "HR-V0_fixed-guard-receiver-candidate.step"
    assembly.save(str(step_path))
    normalize_step(step_path)
    assembly.save(str(OUT / "HR-V0_fixed-guard-receiver-candidate.glb"))
    (OUT / "HR-V0_fixed-guard-receiver-layout.svg").write_text(svg(), encoding="utf-8")
    (OUT / "HR-V0_fixed-guard-interactive.html").write_text(interactive_html(), encoding="utf-8")
    summary = {
        "revision": REVISION,
        "arm_revision": ARM_REVISION,
        "warning": WARNING,
        "coordinate_system": {"origin": "G0 vertical projection of J1 on bench", "x": "depth", "y": "width", "z": "height above bench"},
        "internal_clear_mm": {"x": INNER_X, "y": INNER_Y, "z": INNER_Z},
        "frame_envelope_mm": FRAME,
        "panel_geometry_mm": PANEL_T,
        "reserved_space_radius_mm_not_safety_distance": SPACE_RADIUS,
        "j1_height_mm": SHOULDER_Z,
        "receiver_clear_mm": {"x": RECEIVER_X, "y": RECEIVER_Y, "wall_height": RECEIVER_WALL},
        "maximum_foam_drop_energy_j_test_input_only": round(DROP_ENERGY_J, 6),
        "frame_schedule_lines": len(frame_rows),
        "frame_physical_pieces": sum(int(row["quantity"]) for row in frame_rows),
        "panel_schedule_lines": len(panel_rows),
        "panel_physical_pieces": sum(int(row["quantity"]) for row in panel_rows),
        "frame_joint_count": sum(int(row["joint_count"]) for row in joint_rows),
        "frame_bracket_candidate_quantity": 20,
        "frame_joint_hardware_candidate_quantity": 40,
        "known_guard_mass_subtotal_kg_incomplete": round(PROFILE_MASS_KG + (outer_panel_volume_m3 + receiver_volume_m3) * SHEET_DENSITY_KG_M3, 6),
        "open_holds": len(holds),
        "release_state": "DESIGN CANDIDATE - ALL FABRICATION MOTION CONNECTION AND ENERGIZATION GATES OPEN",
    }
    (OUT / "guard-receiver-summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(f"Generated {REVISION}: 16 frame pieces, 13 sheet pieces, 20 catalog-candidate joints, {len(holds)} open holds")
    print(WARNING)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
