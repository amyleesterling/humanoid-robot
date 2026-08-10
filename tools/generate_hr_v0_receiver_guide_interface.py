"""Generate the R130 corrected passive-receiver guide interface candidate.

The package corrects R129's impossible 20 x 50 mm guide tab using current
manufacturer dimensions.  It emits catalog-coordinate evidence and a
hole-free right-angle bracket envelope; it does not release hole diameters,
fasteners, machining, motion, or energization.
"""

from __future__ import annotations

import csv
import json
import shutil
from pathlib import Path

import cadquery as cq

import generate_hr_v0_collapse_envelope as collapse


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "cad" / "hr-v0" / "generated" / "receiver-guide-interface-p0.1"
GUIDE = ROOT / "release" / "hr-v0" / "receiver-guide-interface-p0.1" / "index.html"
IDENTIFIER = "HR-V0-RECEIVER-GUIDE-IF-P0.1"
WARNING = "PRELIMINARY - NOT APPROVED FOR FABRICATION, MOTION OR ENERGIZATION"

PLATEN_X = 180.0
PLATEN_Y = 800.0
PLATEN_T = 6.35
PLATEN_BOTTOM_Z = 304.125
GUIDE_X = (-110.0, 110.0)
GUIDE_Y = (-350.0, 350.0)
RAIL_LENGTH = 120.0
RAIL_PITCH = 60.0
RAIL_END = (RAIL_LENGTH - RAIL_PITCH) / 2.0

CARRIAGE_WIDTH = 63.0
CARRIAGE_LENGTH = 81.0
CARRIAGE_BODY_HEIGHT = 25.0
SYSTEM_HEIGHT = 30.0
K2_SPACING_WIDTH = 53.0
K2_SPACING_LENGTH = 40.0
K2_THREAD = "M6"
K2_TORQUE_NM = 1.84

BRACKET_WALL = 6.35
BRACKET_FLANGE_REACH = 40.0
BRACKET_WIDTH = 73.0
BRACKET_HEIGHT = 80.0
BRACKET_BOTTOM_Z = PLATEN_BOTTOM_Z - BRACKET_HEIGHT
DENSITY_KG_MM3 = 2.70e-6


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


def bracket_envelope() -> cq.Shape:
    vertical = box(BRACKET_WALL, BRACKET_WIDTH, BRACKET_HEIGHT, 0.0, -BRACKET_WIDTH / 2.0, 0.0)
    horizontal = box(BRACKET_FLANGE_REACH, BRACKET_WIDTH, BRACKET_WALL, 0.0, -BRACKET_WIDTH / 2.0, BRACKET_HEIGHT - BRACKET_WALL)
    return vertical.fuse(horizontal)


def placed_bracket(x: float, y: float) -> cq.Shape:
    if x > 0:
        vertical = box(BRACKET_WALL, BRACKET_WIDTH, BRACKET_HEIGHT, 95.0, y - BRACKET_WIDTH / 2.0, BRACKET_BOTTOM_Z)
        horizontal = box(BRACKET_FLANGE_REACH, BRACKET_WIDTH, BRACKET_WALL, 95.0 - (BRACKET_FLANGE_REACH - BRACKET_WALL), y - BRACKET_WIDTH / 2.0, PLATEN_BOTTOM_Z - BRACKET_WALL)
    else:
        vertical = box(BRACKET_WALL, BRACKET_WIDTH, BRACKET_HEIGHT, -95.0 - BRACKET_WALL, y - BRACKET_WIDTH / 2.0, BRACKET_BOTTOM_Z)
        horizontal = box(BRACKET_FLANGE_REACH, BRACKET_WIDTH, BRACKET_WALL, -95.0 - BRACKET_WALL, y - BRACKET_WIDTH / 2.0, PLATEN_BOTTOM_Z - BRACKET_WALL)
    return vertical.fuse(horizontal)


def review_shapes() -> dict[str, cq.Shape]:
    shapes: dict[str, cq.Shape] = {
        "R129-PLATEN-BLANK": box(PLATEN_X, PLATEN_Y, PLATEN_T, -PLATEN_X / 2.0, -PLATEN_Y / 2.0, PLATEN_BOTTOM_Z),
    }
    for xi, x in enumerate(GUIDE_X, 1):
        for yi, y in enumerate(GUIDE_Y, 1):
            tag = f"{xi}-{yi}"
            if x > 0:
                carriage_x = 95.0
                rail_x = 125.0 - 12.3
            else:
                carriage_x = -125.0
                rail_x = -125.0
            shapes[f"TWA-01-20-CATALOG-ENVELOPE-{tag}"] = box(SYSTEM_HEIGHT, CARRIAGE_WIDTH, CARRIAGE_LENGTH, carriage_x, y - CARRIAGE_WIDTH / 2.0, PLATEN_BOTTOM_Z - CARRIAGE_LENGTH)
            shapes[f"TS-01-20-120-CATALOG-ENVELOPE-{tag}"] = box(12.3, 20.0, RAIL_LENGTH, rail_x, y - 10.0, PLATEN_BOTTOM_Z - RAIL_LENGTH)
            shapes[f"FAB-REC-004-GUIDE-ANGLE-ENVELOPE-{tag}"] = placed_bracket(x, y)
    return shapes


def write_drawing() -> None:
    style = "text{font-family:Arial,sans-serif;fill:#102a43;font-size:16px}.t{font-size:28px;font-weight:700}.w{font-size:14px;font-weight:700;fill:#8b2d1b}.p{fill:#dff3ff;stroke:#082b55;stroke-width:3}.d{stroke:#075b9b;stroke-width:2;fill:none}.c{stroke:#a83220;stroke-width:2}.o{fill:none;stroke:#a83220;stroke-width:3}"
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="1400" height="900" viewBox="0 0 1400 900"><style>{style}</style><rect width="1400" height="900" fill="#fff"/><text x="45" y="48" class="t">FAB-REC-004 guide-angle envelope and catalog coordinates</text><text x="45" y="78" class="w">{WARNING} - HOLE DIAMETERS, FASTENERS, MATERIAL ALLOWABLES AND MACHINING REMAIN SELECTION REQUIRED</text><rect x="110" y="150" width="365" height="400" class="p"/><text x="235" y="135">carriage face</text><circle cx="160" cy="250" r="10" class="o"/><circle cx="425" cy="250" r="10" class="o"/><circle cx="160" cy="450" r="10" class="o"/><circle cx="425" cy="450" r="10" class="o"/><line x1="160" y1="580" x2="425" y2="580" class="d"/><text x="260" y="615">53.0 mm K2 pattern</text><line x1="500" y1="250" x2="500" y2="450" class="d"/><text x="520" y="355">40.0 mm</text><text x="145" y="665">Four K2 threads: M6; catalog max torque 1.84 N m.</text><text x="145" y="695" class="w">Clearance diameter, screw length/grade, washer, locking and engagement: SELECTION REQUIRED</text><path d="M820 190 h32 v330 h170 v32 H820 z" class="p"/><text x="795" y="160">section envelope</text><line x1="820" y1="600" x2="1022" y2="600" class="d"/><text x="885" y="635">40.0 mm reach</text><line x1="780" y1="190" x2="780" y2="552" class="d"/><text x="690" y="380">80.0 mm</text><text x="810" y="695">6.35 mm wall candidate</text><text x="810" y="725">73.0 mm face width</text><text x="810" y="755">One-piece machined 6061-T651 candidate</text><text x="45" y="840">R129's 20 x 50 mm tab cannot cover a 53 x 40 mm rectangle in either orientation. This drawing controls centers only; it is not a fabrication drawing.</text></svg>'''
    (OUT / "FAB-REC-004-guide-angle-coordinate-drawing.svg").write_text(svg, encoding="utf-8", newline="\n")


def main() -> int:
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)

    part = bracket_envelope()
    part_step = OUT / "FAB-REC-004-guide-angle-hole-free-envelope.step"
    cq.exporters.export(part, str(part_step))
    normalize_step(part_step)

    volume = part.Volume()
    mass_kg = volume * DENSITY_KG_MM3
    platen_mass_kg = PLATEN_X * PLATEN_Y * PLATEN_T * DENSITY_KG_MM3

    catalog_rows = [
        {"coordinate_id":"GUIDE-CAT-001","item":"TWA-01-20","quantity":"A","value_mm":"63.0","tolerance":"not published in controlled row","source":"official TWA product/CAD view","release_boundary":"catalog dimension only"},
        {"coordinate_id":"GUIDE-CAT-002","item":"TWA-01-20","quantity":"C","value_mm":"81.0","tolerance":"not published in controlled row","source":"official TWA product/CAD view","release_boundary":"catalog dimension only"},
        {"coordinate_id":"GUIDE-CAT-003","item":"TWA-01-20","quantity":"body height","value_mm":"25.0","tolerance":"SELECTION REQUIRED","source":"official CADClick dimension view","release_boundary":"system height remains separate"},
        {"coordinate_id":"GUIDE-CAT-004","item":"TWA-01-20 on TS-01-20","quantity":"H system height","value_mm":"30.0","tolerance":"+/-0.35","source":"official drylin T table","release_boundary":"as-built stack open"},
        {"coordinate_id":"GUIDE-CAT-005","item":"TWA-01-20","quantity":"A2 K2 row spacing","value_mm":"53.0","tolerance":"not published","source":"official drawing/table","release_boundary":"received CAD/metrology required"},
        {"coordinate_id":"GUIDE-CAT-006","item":"TWA-01-20","quantity":"C2 K2 column spacing","value_mm":"40.0","tolerance":"not published","source":"official drawing/table","release_boundary":"received CAD/metrology required"},
        {"coordinate_id":"GUIDE-CAT-007","item":"TWA-01-20","quantity":"K2 thread","value_mm":"M6","tolerance":"thread depth not published","source":"official drawing/table","release_boundary":"screw length/engagement open"},
        {"coordinate_id":"GUIDE-CAT-008","item":"TWA-01-20","quantity":"K2 maximum torque","value_mm":"1.84 N m","tolerance":"maximum catalog datum","source":"official drylin T catalog","release_boundary":"not project torque release"},
        {"coordinate_id":"GUIDE-CAT-009","item":"TS-01-20","quantity":"a","value_mm":"20.0","tolerance":"-0.2","source":"official rail table","release_boundary":"configured article open"},
        {"coordinate_id":"GUIDE-CAT-010","item":"TS-01-20","quantity":"C4 pitch","value_mm":"60.0","tolerance":"not published","source":"official rail table","release_boundary":"configured article open"},
        {"coordinate_id":"GUIDE-CAT-011","item":"TS-01-20","quantity":"C5/C6 permitted end spacing","value_mm":"20.0..49.5","tolerance":"standard pattern symmetric","source":"official rail table","release_boundary":"derived 120 mm pattern only"},
        {"coordinate_id":"GUIDE-CAT-012","item":"TS-01-20 120 mm candidate","quantity":"derived C5=C6","value_mm":f"{RAIL_END:.1f}","tolerance":"SELECTION REQUIRED","source":"(120-60)/2","release_boundary":"not a configured order release"},
    ]
    write_csv(OUT / "catalog-coordinate-register.csv", catalog_rows)

    proof_rows = [
        {"proof_id":"GUIDE-PROOF-001","candidate":"R129 FAB-REC-003 orientation 20 across 53; 50 across 40","required_pattern_mm":"53 x 40","available_face_mm":"20 x 50","shortfall_mm":"33 x 0","result":"FAIL - CANNOT COVER K2 PATTERN"},
        {"proof_id":"GUIDE-PROOF-002","candidate":"R129 FAB-REC-003 rotated","required_pattern_mm":"53 x 40","available_face_mm":"50 x 20","shortfall_mm":"3 x 20","result":"FAIL - CANNOT COVER K2 PATTERN"},
        {"proof_id":"GUIDE-PROOF-003","candidate":"R130 FAB-REC-004 vertical face","required_pattern_mm":"53 x 40","available_face_mm":"73 x 80","shortfall_mm":"0 x 0","result":"NOMINAL COVERAGE ONLY - HOLES/LOAD PROOF OPEN"},
        {"proof_id":"GUIDE-PROOF-004","candidate":"TS-01-20 120 mm standard pattern derivation","required_pattern_mm":"C4=60; C5=C6; range 20..49.5","available_face_mm":"C5=C6=30","shortfall_mm":"0","result":"ARITHMETIC CONSISTENT - CONFIGURED CODE/CAD OPEN"},
    ]
    write_csv(OUT / "incompatibility-and-pattern-proof.csv", proof_rows)

    hole_rows: list[dict[str, object]] = []
    for xi, x in enumerate(GUIDE_X, 1):
        for yi, y in enumerate(GUIDE_Y, 1):
            face_x = 95.0 if x > 0 else -95.0
            carriage_center_z = PLATEN_BOTTOM_Z - CARRIAGE_LENGTH / 2.0
            for sy in (-1, 1):
                for sz in (-1, 1):
                    hole_rows.append({"hole_id":f"K2-{xi}{yi}-{sy:+d}{sz:+d}","part":"FAB-REC-004","interface":"TWA-01-20 K2","x_mm":f"{face_x:.3f}","y_mm":f"{y + sy*K2_SPACING_WIDTH/2:.3f}","z_mm":f"{carriage_center_z + sz*K2_SPACING_LENGTH/2:.3f}","diameter_or_thread":"SELECTION REQUIRED - mating thread M6 only","source":"53 x 40 catalog pattern","status":"CENTER CANDIDATE; NOT RELEASED"})
            for sy in (-1, 1):
                hole_rows.append({"hole_id":f"PLATEN-{xi}{yi}-{sy:+d}","part":"FAB-REC-001 + FAB-REC-004","interface":"platen attachment","x_mm":f"{80.0 if x>0 else -80.0:.3f}","y_mm":f"{y + sy*25.0:.3f}","z_mm":f"{PLATEN_BOTTOM_Z:.3f}","diameter_or_thread":"SELECTION REQUIRED","source":"R130 project coordinate candidate","status":"CENTER CANDIDATE; FASTENER/EDGE/LOAD PROOF OPEN"})
    write_csv(OUT / "hole-center-control.csv", hole_rows)

    interface_rows = [
        {"interface_id":"GUIDE-IF-001","from":"TWA-01-20 K2 face","to":"FAB-REC-004 vertical face","controlled_geometry":"four centers on 53 x 40 mm rectangle","hardware":"M6 mating thread known; all screw details SELECTION REQUIRED","status":"PARTIAL - CATALOG COORDINATES; RECEIVED CAD/THREAD DEPTH OPEN"},
        {"interface_id":"GUIDE-IF-002","from":"FAB-REC-004 horizontal flange","to":"FAB-REC-001 platen","controlled_geometry":"two project centers at X +/-80 and Y guide center +/-25","hardware":"SELECTION REQUIRED","status":"OPEN - DIAMETER/FASTENER/LOCAL STRENGTH/FAI"},
        {"interface_id":"GUIDE-IF-003","from":"TS-01-20 120 mm candidate","to":"fixed support","controlled_geometry":"derived two-hole standard pattern at 30 and 90 mm","hardware":"K1 for DIN 912 M5; all screw/hole details SELECTION REQUIRED","status":"PARTIAL - CONFIGURED CODE/CAD/APPLICATION OPEN"},
        {"interface_id":"GUIDE-IF-004","from":"four independent rails","to":"one moving platen","controlled_geometry":"axes X +/-110; Y +/-350; vertical stroke envelope 120 mm","hardware":"SELECTION REQUIRED","status":"OPEN - OVERCONSTRAINT/ALIGNMENT/FLOATING ARRANGEMENT/IGUS REVIEW"},
    ]
    write_csv(OUT / "interface-register.csv", interface_rows)

    load_rows = [
        {"load_id":"GUIDE-LD-001","case":"01-/02-20 catalog C0Y/C0(-Y)","value":"7400","unit":"N","status":"CATALOG DATUM ONLY - APPLICATION/DYNAMIC SHOCK OPEN"},
        {"load_id":"GUIDE-LD-002","case":"01-/02-20 catalog C0Z","value":"3700","unit":"N","status":"CATALOG DATUM ONLY - APPLICATION/DYNAMIC SHOCK OPEN"},
        {"load_id":"GUIDE-LD-003","case":"catalog M0X/M0Y/M0Z","value":"85 / 45 / 45","unit":"N m","status":"CATALOG DATUM ONLY - LOAD DISTRIBUTION OPEN"},
        {"load_id":"GUIDE-LD-004","case":"R130 bracket nominal volume","value":f"{volume:.3f}","unit":"mm3","status":"HOLE-FREE ENVELOPE"},
        {"load_id":"GUIDE-LD-005","case":"R130 bracket nominal mass at 2.70 g/cm3 typical density","value":f"{mass_kg:.6f}","unit":"kg each","status":"MATERIAL CERTIFICATE/HOLES/AS-BUILT MASS OPEN"},
        {"load_id":"GUIDE-LD-006","case":"four brackets + R129 platen known nominal subtotal","value":f"{4*mass_kg+platen_mass_kg:.6f}","unit":"kg","status":"EXCLUDES PAD/FASTENERS/SHOCK MOVING MASS; ACE INPUT OPEN"},
        {"load_id":"GUIDE-LD-007","case":"single-guide/angle peak reaction","value":"SELECTION REQUIRED","unit":"N and N m","status":"BLOCKS STRUCTURAL RELEASE"},
    ]
    write_csv(OUT / "load-and-mass-screen.csv", load_rows)

    holds = [
        ("GUIDE-HOLD-001","received manufacturer CAD and revision identity for TWA-01-20 and configured TS-01-20 rail","PARTIAL"),
        ("GUIDE-HOLD-002","configured 120 mm rail order code, end tolerance and hole/counterbore geometry","PARTIAL"),
        ("GUIDE-HOLD-003","K2 thread depth, screw length/grade/washer/locking/engagement and released torque","OPEN"),
        ("GUIDE-HOLD-004","platen-side hole diameter, hardware, edge distance, local strength and fatigue","OPEN"),
        ("GUIDE-HOLD-005","igus vertical shock application, load/life, floating arrangement and alignment acceptance","OPEN"),
        ("GUIDE-HOLD-006","FAB-REC-004 material, process, tolerances, fillet/tool radius, coating and FAI","OPEN"),
        ("GUIDE-HOLD-007","peak reaction, guide sharing, bracket/plate/rail/support/anchor allowables and proof","OPEN"),
        ("GUIDE-HOLD-008","received fit, stroke, binding, backlash, pull and fault/drop tests","OPEN"),
        ("GUIDE-HOLD-009","qualified mechanical and functional-safety review","OPEN"),
        ("GUIDE-HOLD-010","written work authorization","OPEN"),
    ]
    write_csv(OUT / "closure-holds.csv", [{"hold_id":i,"evidence_required":e,"status":s,"release_effect":"BLOCKS FABRICATION MOTION AND ENERGIZATION"} for i,e,s in holds])

    sources = [
        {"source_id":"GUIDE-SRC-001","manufacturer":"igus","title":"TWA-01-20 exact product variant","revision_or_date":"live page; copyright 2026; no formal revision exposed","accessed":"2026-08-09","url":"https://www.igus.com/product/drylin_TWA_01?artnr=TWA-01-20","use":"exact orderable carriage identity and 63 mm A value","boundary":"application acceptance and received article remain open"},
        {"source_id":"GUIDE-SRC-002","manufacturer":"igus","title":"TWA-01 official technical drawing","revision_or_date":"Widen asset 6dcadfe0-55b3-48fa-a7a5-6e20bc4ee05f; no drawing revision exposed","accessed":"2026-08-09","url":"https://igus.widen.net/content/ikczh6imai/png/Zg_drylinT_TWA-01.png","use":"A2/C2/K2/K3 coordinate interpretation","boundary":"image is not a revision-controlled received CAD payload"},
        {"source_id":"GUIDE-SRC-003","manufacturer":"igus / CADClick","title":"TWA-01-20 exact CAD viewer","revision_or_date":"CADClick ccCatalog 1.17.0 build 20260629.2; ccAPI 3.5.5.0","accessed":"2026-08-09","url":"https://www.igus-cad.com/default.aspx?cul=en-US&ArtNr=TWA-01-20&mandant=INT&parammode=","use":"exact model identity and 63 x 81 x 25 body dimensions","boundary":"interactive view inspected; no CAD file acquired or claimed"},
        {"source_id":"GUIDE-SRC-004","manufacturer":"igus","title":"DryLin T Linear Guide System catalog","revision_or_date":"live official PDF; no explicit document revision found","accessed":"2026-08-09","url":"https://www.igus.com/us/pdf/drylint.pdf","use":"TWA dimensions/torque and TS rail/order-pattern data","boundary":"catalog data is not application approval"},
        {"source_id":"GUIDE-SRC-005","manufacturer":"igus","title":"drylin T system design vertical","revision_or_date":"live page; no formal revision exposed","accessed":"2026-08-09","url":"https://www.igus.com/linear-bearings/linear-guides-drylin-t-system-design-vertical-ca","use":"vertical arrangement/application method","boundary":"project inputs and manufacturer review remain open"},
        {"source_id":"GUIDE-SRC-006","manufacturer":"igus","title":"clear-anodized no-hole TS-01 alternate product page","revision_or_date":"live page; no formal revision exposed","accessed":"2026-08-09","url":"https://www.igus.com/product/drylin_TS_01_CA","use":"documents exact TS-01-20-CA-S no-hole alternate identity","boundary":"alternate not selected; finish/application comparison open"},
    ]
    write_csv(OUT / "source-register.csv", sources)

    rfi = f"""# UNSENT igus application and CAD request\n\nStatus: **UNSENT - NO EXTERNAL CONTACT AUTHORIZED**\n\nPackage: `{IDENTIFIER}`\n\nPlease confirm for a four-rail vertical guided impact-receiver application:\n\n1. current STEP and dimensioned drawing revision for `TWA-01-20`;\n2. configured 120 mm `TS-01-20` order identity, length/end tolerance, standard hole centers and hole/counterbore geometry;\n3. K2 M6 thread depth, recommended DIN 912 screw length/property class/washer/locking method and allowed assembly torque;\n4. whether four independent fixed carriages/rails on one rigid platen will overconstrain, and the required fixed/floating arrangement and alignment tolerances;\n5. application calculations for measured peak force, moments, contact speed, cycles, temperature, shock/rebound and unequal sharing;\n6. rail-support screw specification, edge requirements and proof recommendations; and\n7. written disposition for use as a passive fault receiver.\n\nNo order, fabrication, physical test, motion or energization may follow from this draft.\n"""
    (OUT / "supplier-rfi-unsent.md").write_text(rfi, encoding="utf-8", newline="\n")

    write_drawing()
    shapes = review_shapes()
    assembly = cq.Assembly(name="HR_V0_RECEIVER_GUIDE_INTERFACE_REVIEW_ONLY")
    for name, shape in shapes.items():
        if name.startswith("FAB"):
            color = cq.Color(0.96, 0.61, 0.12)
        elif name.startswith("TWA"):
            color = cq.Color(0.23, 0.32, 0.42)
        elif name.startswith("TS"):
            color = cq.Color(0.48, 0.55, 0.62)
        else:
            color = cq.Color(0.45, 0.78, 0.94)
        assembly.add(shape, name=name, color=color)
    assembly.save(str(OUT / "HR-V0_receiver-guide-interface-review.glb"))
    assembly_step = OUT / "HR-V0_receiver-guide-interface-review.step"
    cq.exporters.export(cq.Compound.makeCompound(list(shapes.values())), str(assembly_step))
    normalize_step(assembly_step)

    bounds = cq.Compound.makeCompound(list(shapes.values())).BoundingBox()
    summary = {
        "identifier": IDENTIFIER,
        "warning": WARNING,
        "supersedes_interface_artifact": "R129 FAB-REC-003 20 x 50 mm guide tab envelope",
        "catalog_pattern_mm": {"A2": K2_SPACING_WIDTH, "C2": K2_SPACING_LENGTH, "K2": K2_THREAD, "max_torque_Nm": K2_TORQUE_NM},
        "bracket_envelope_mm": {"flange_reach": BRACKET_FLANGE_REACH, "face_width": BRACKET_WIDTH, "height": BRACKET_HEIGHT, "wall": BRACKET_WALL},
        "bracket_volume_mm3": volume,
        "bracket_nominal_mass_kg": mass_kg,
        "four_brackets_plus_platen_nominal_mass_kg": 4 * mass_kg + platen_mass_kg,
        "derived_rail_end_spacing_mm": RAIL_END,
        "review_bounds_mm": {"xmin": bounds.xmin, "xmax": bounds.xmax, "ymin": bounds.ymin, "ymax": bounds.ymax, "zmin": bounds.zmin, "zmax": bounds.zmax},
        "coordinate_rows": len(catalog_rows),
        "hole_center_rows": len(hole_rows),
        "hold_rows": len(holds),
        "gate_state": "EG-008 AND EG-009 REMAIN PARTIAL",
    }
    (OUT / "guide-interface-summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8", newline="\n")

    GUIDE.parent.mkdir(parents=True, exist_ok=True)
    GUIDE.write_text(f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>HR-V0 guide interface P0.1</title><style>:root{{--deep:#041a35;--navy:#082b55;--sky:#7dd3fc;--pale:#e4f6ff;--gold:#f4b942;--ink:#102a43;--line:#9ccfe8;--red:#a83220}}*{{box-sizing:border-box}}body{{margin:0;background:var(--pale);color:var(--ink);font:17px/1.55 system-ui,"Segoe UI",sans-serif}}header{{background:linear-gradient(135deg,var(--deep),var(--navy));color:#fff;padding:clamp(34px,6vw,72px) 20px}}header>div,main{{max-width:1120px;margin:auto}}h1{{font-size:clamp(36px,6vw,64px);line-height:1.05;margin:.2em 0}}h2{{font-size:clamp(27px,3.5vw,39px);line-height:1.15;color:var(--navy)}}.eyebrow{{font-size:14px;font-weight:850;color:var(--sky)}}.warning{{background:var(--gold);color:#17243a;border:3px solid #8a5b00;padding:15px 18px;font-weight:850}}main{{padding:30px 20px 80px}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(245px,1fr));gap:18px}}.card,.panel{{background:#fff;border:2px solid var(--line);border-radius:16px;padding:20px;box-shadow:0 3px 0 #bddbea}}.metric{{font-size:clamp(34px,6vw,55px);font-weight:900;color:#075b9b}}.bad{{border-left:9px solid var(--red)}}.hold{{border-left:9px solid var(--gold)}}model-viewer{{width:100%;height:520px;background:#dff3ff;border:2px solid var(--line);border-radius:16px}}table{{width:100%;border-collapse:collapse;background:#fff}}th,td{{padding:13px;border:1px solid #8aa8ba;text-align:left;vertical-align:top;font-size:16px}}th{{background:#d5effc}}footer{{background:var(--deep);color:#fff;padding:30px 20px}}footer p{{max-width:1120px;margin:auto}}@media(max-width:760px){{body{{font-size:16px}}model-viewer{{height:430px}}.table{{overflow:auto}}}}</style><script type="module" src="../../vendor/model-viewer/4.1.0/model-viewer.min.js"></script></head><body><header><div><p class="warning">{WARNING}</p><p class="eyebrow">{IDENTIFIER}</p><h1>The first guide tab did not fit the real carriage pattern.</h1><p>R130 replaces the impossible R129 tab envelope with a source-backed right-angle interface candidate and keeps every unreleased hole, fastener, load and application decision visible.</p></div></header><main><section><h2>The correction</h2><div class="grid"><article class="card bad"><div class="metric">20 x 50</div><p>R129 tab face. It cannot cover the TWA-01-20's 53 x 40 mm K2 pattern in either orientation.</p></article><article class="card"><div class="metric">73 x 80</div><p>R130 vertical face envelope. It provides nominal pattern coverage, not structural acceptance.</p></article><article class="card"><div class="metric">30 mm</div><p>Derived symmetric end spacing for a 120 mm TS-01-20 candidate with one 60 mm pitch.</p></article></div></section><section><h2>Catalog coordinates versus project decisions</h2><div class="table"><table><thead><tr><th>Controlled fact</th><th>Value</th><th>Boundary</th></tr></thead><tbody><tr><td>TWA K2 centers</td><td>53 x 40 mm; four M6 threads</td><td>Thread depth, screw length, grade, locking and released torque remain open.</td></tr><tr><td>TWA envelope</td><td>63 x 81 x 25 mm body; 30 mm installed system height</td><td>Received CAD, tolerance stack and metrology remain open.</td></tr><tr><td>R130 guide angle</td><td>40 x 73 x 80 mm envelope; 6.35 mm wall</td><td>Hole diameters, material/process, fillet, allowables, FAI and proof remain open.</td></tr><tr><td>Four-rail arrangement</td><td>X +/-110; Y +/-350</td><td>Binding, floating arrangement, alignment, load/life and igus acceptance remain open.</td></tr></tbody></table></div></section><section><h2>Review the corrected interface</h2><model-viewer src="../../../cad/hr-v0/generated/receiver-guide-interface-p0.1/HR-V0_receiver-guide-interface-review.glb" camera-controls interaction-prompt="none" shadow-intensity="0.5" alt="Corrected right-angle guide interface candidate"></model-viewer></section><section><h2>Still fail-closed</h2><div class="grid"><article class="card hold"><strong>No downloaded CAD payload</strong><p>The official interactive model and drawing were inspected, but no STEP file was acquired or claimed.</p></article><article class="card hold"><strong>No released holes</strong><p>Centers are controlled; diameters, threads, counterbores, fasteners and machining are not.</p></article><article class="card hold"><strong>No application credit</strong><p>Catalog loads and moments are not impact, life, sharing, alignment or proof acceptance.</p></article><article class="card hold"><strong>No work authority</strong><p>All ten holds block fabrication, motion and energization. EG-008 and EG-009 remain partial.</p></article></div></section></main><footer><p>Project Button · {IDENTIFIER} · zero fabrication, motion, energization or functional-safety approval</p></footer></body></html>''', encoding="utf-8", newline="\n")

    collapse.write_generated_source_manifest()
    print(f"Generated {IDENTIFIER}: {len(catalog_rows)} catalog rows, {len(hole_rows)} hole centers, {len(holds)} holds")
    print("R129 20 x 50 mm guide tab rejected; R130 73 x 80 mm face is nominal coverage only")
    print(WARNING)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
