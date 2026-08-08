"""Generate the R101 X430 fixture support-route review candidate."""

from __future__ import annotations

import csv
import json
import math
import shutil
import sys
from pathlib import Path

import cadquery as cq

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import generate_hr_v0_arm_architecture as base  # noqa: E402
import generate_hr_v0_x430_duty_fixture_interface as interface  # noqa: E402
import generate_hr_v0_x430_elbow_architecture as x430_arch  # noqa: E402

IDENTIFIER = "HR-V0-X430-FIXTURE-SUP-P0.1"
WARNING = "PRELIMINARY - SUPPORT/RFI CANDIDATE ONLY - NOT APPROVED FOR QUOTATION, PROCUREMENT, MACHINING, FLOOR WORK, ASSEMBLY, POWERED TEST, MOTION, OR ENERGIZATION"
OUT = ROOT / "test-fixtures" / "hr-v0" / "x430-fixture-support-p0.1"
WEB = ROOT / "release" / "hr-v0" / "x430-fixture-support-p0.1"
VENDOR = ROOT / "cad" / "vendor" / "robotis" / "x430-fr12-r91"

PLATE = 203.2
PLATE_T = 19.05
PEDESTAL_H = 300.0
POCKET_D = 52.0
POCKET_DEPTH = 2.50
PILOT_D = 18.98
CB_D = 9.0
CB_DEPTH = 6.70
TFF_BCD = 31.75
TFF_CLEAR_D = 4.50
CATALOG_TORQUE_NM = 2040.0
OVERLOAD_SCREEN_NM = 16.5


def write_csv(path: Path, records: list[dict[str, object]]) -> None:
    if not records:
        raise ValueError(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(records[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(records)


def rotate_to_vertical(shape: cq.Shape) -> cq.Shape:
    return shape.rotate((0, 0, 0), (0, 1, 0), -90).translate((180, 0, 406.55))


def modified_plate_envelope() -> cq.Shape:
    plate = cq.Solid.makeBox(PLATE, PLATE, PLATE_T, cq.Vector(-PLATE / 2, -PLATE / 2, PEDESTAL_H))
    # The product's existing mounting holes are intentionally not modeled: controlled CAD is required.
    pocket_bottom = PEDESTAL_H + PLATE_T - POCKET_DEPTH
    annulus = cq.Solid.makeCylinder(POCKET_D / 2, POCKET_DEPTH, cq.Vector(0, 0, pocket_bottom), cq.Vector(0, 0, 1))
    boss = cq.Solid.makeCylinder(PILOT_D / 2, POCKET_DEPTH, cq.Vector(0, 0, pocket_bottom), cq.Vector(0, 0, 1))
    plate = plate.cut(annulus).fuse(boss)
    r = TFF_BCD / 2
    for x, y in ((r, 0), (-r, 0), (0, r), (0, -r)):
        plate = plate.cut(cq.Solid.makeCylinder(TFF_CLEAR_D / 2, PLATE_T, cq.Vector(x, y, PEDESTAL_H), cq.Vector(0, 0, 1)))
        plate = plate.cut(cq.Solid.makeCylinder(CB_D / 2, CB_DEPTH, cq.Vector(x, y, PEDESTAL_H), cq.Vector(0, 0, 1)))
    return plate


def drawing_svg(path: Path) -> None:
    path.write_text(f'''<svg xmlns="http://www.w3.org/2000/svg" width="1500" height="1050" viewBox="0 0 1500 1050" style="max-width:100%;height:auto"><style>
text{{font-family:Arial,sans-serif;fill:#102a43;font-size:20px}}.h{{font-size:36px;font-weight:700;fill:#082b55}}.w{{font-size:18px;font-weight:700;fill:#8b1e1e}}.p{{fill:#e4f6ff;stroke:#082b55;stroke-width:3}}.g{{fill:#f4b942;stroke:#8a5b00;stroke-width:3}}.x{{stroke:#9b1c1c;stroke-width:2;stroke-dasharray:9 7}}.s{{font-size:17px}}
</style><rect width="1500" height="1050" fill="#f7fbff"/><text x="45" y="58" class="h">{IDENTIFIER} · vertical support route</text>
<text x="45" y="95" class="w">PRELIMINARY - SUPPORT/RFI CANDIDATE ONLY - NOT APPROVED FOR QUOTATION, PROCUREMENT, MACHINING, FLOOR WORK,</text><text x="45" y="124" class="w">ASSEMBLY, POWERED TEST, MOTION, OR ENERGIZATION</text>
<text x="55" y="175" class="h">Configuration section</text><rect x="220" y="700" width="500" height="16" class="g"/><line x1="470" y1="700" x2="470" y2="360" class="x"/>
<line x1="470" y1="700" x2="470" y2="400" stroke="#082b55" stroke-width="10"/><text x="505" y="570">40200-SP-K 300 mm height datum only</text>
<rect x="350" y="360" width="240" height="24" class="p"/><text x="620" y="380">40006-BP envelope, 203.2 square × 19.05</text>
<rect x="420" y="330" width="100" height="30" class="g"/><circle cx="470" cy="292" r="38" class="g"/><rect x="430" y="220" width="80" height="72" rx="16" fill="#7dd3fc" stroke="#0b63a3" stroke-width="3"/>
<text x="55" y="770" class="w">The centerline is not pedestal body CAD. Footprint, base plate, anchors and installed interface are not modeled.</text>
<text x="820" y="175" class="h">Controlled candidate machining</text><text x="850" y="225">Top pocket: Ø52.0 × 2.50 mm deep</text><text x="850" y="265">Retained pilot: Ø18.98 ±0.02 mm</text>
<text x="850" y="305">TFF axes: 4 × Ø4.50 on BCD31.75</text><text x="850" y="345">Underside counterbores: 4 × Ø9.0 × 6.70 deep</text><text x="850" y="385">Fastener candidate: 8-32 × 5/8 in; NOT SELECTED</text>
<text x="820" y="455" class="h">Evidence boundary</text><text x="850" y="505">2040 N·m is an 80/20 catalog figure only</text><text x="850" y="545">and applies when the pedestal is floor-mounted.</text><text x="850" y="585">Vertical orientation removes representative gravity torque.</text>
<text x="850" y="625">Horizontal configuration remains a later required test.</text><text x="850" y="665">Every anchor, floor and modified-plate interface is OPEN.</text>
<rect x="55" y="830" width="1390" height="150" fill="#fff" stroke="#8b1e1e" stroke-width="3"/><text x="85" y="875" class="w">DO NOT MACHINE OR ANCHOR FROM THIS DRAWING.</text><text x="85" y="920">Obtain controlled manufacturer CAD, configuration, anchor loads and written application acceptance first.</text><text x="85" y="960">A facilities engineer must accept the exact Boston site, substrate, anchors, edge distances and installation evidence.</text></svg>''', encoding="utf-8", newline="\n")


def html(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{IDENTIFIER}</title><script type="module" src="https://ajax.googleapis.com/ajax/libs/model-viewer/4.1.0/model-viewer.min.js"></script><style>
:root{{--deep:#041a35;--navy:#082b55;--sky:#7dd3fc;--pale:#e4f6ff;--gold:#f4b942;--ink:#102a43;--red:#8b1e1e;--line:#afd5e9}}*{{box-sizing:border-box}}body{{margin:0;background:#f7fbff;color:var(--ink);font:17px/1.55 system-ui,"Segoe UI",sans-serif}}header{{padding:clamp(32px,6vw,72px) 20px;background:linear-gradient(135deg,var(--deep),var(--navy));color:#fff}}header>div,main{{max-width:1180px;margin:auto}}h1{{font-size:clamp(34px,6vw,64px);line-height:1.05}}h2{{font-size:clamp(27px,3vw,39px);color:var(--navy)}}.eyebrow{{font-size:13px;font-weight:850;text-transform:uppercase;color:var(--sky)}}.warning{{background:var(--gold);color:#17243a;border:3px solid #8a5b00;padding:15px 18px;font-weight:850}}main{{padding:30px 20px 80px}}.decision,.card{{background:#fff;border:2px solid var(--line);border-radius:16px;padding:20px}}.decision{{border-left:9px solid var(--gold)}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(245px,1fr));gap:18px}}.card strong{{display:block;font-size:clamp(24px,4vw,39px);color:var(--navy)}}model-viewer{{width:100%;height:600px;background:#dff3ff;border:3px solid var(--navy);border-radius:16px}}.table{{overflow:auto;border:2px solid var(--line);border-radius:12px}}table{{border-collapse:collapse;width:100%;min-width:820px}}th,td{{padding:13px;text-align:left;vertical-align:top;border-bottom:1px solid var(--line);font-size:16px}}th{{background:var(--navy);color:white}}.hold{{color:var(--red);font-weight:850}}a{{color:#075b9b;font-weight:750}}footer{{padding:30px 20px;background:var(--deep);color:#fff}}footer p{{max-width:1180px;margin:auto}}@media(max-width:720px){{body{{font-size:16px}}model-viewer{{height:470px}}}}
</style></head><body><header><div><div class="eyebrow">{IDENTIFIER} · R101</div><h1>A rated support route—with a floor-sized condition.</h1><div class="warning">{WARNING}</div></div></header><main>
<section class="decision"><h2>Decision</h2><p>The preferred first support inquiry is an 80/20 <code>40200-SP-K</code> static pedestal configured at 300 mm with a modified <code>40006-BP</code> blank plate. The manufacturer's 2,040 N·m figure is relevant only when floor-mounted. It is not a project allowable and does not validate Boston's unknown substrate or anchors.</p></section>
<section><h2>Inspect the vertical-axis candidate</h2><model-viewer src="../../../test-fixtures/hr-v0/x430-fixture-support-p0.1/HR-V0_X430_fixture_support_P0.1_review.glb" alt="Preliminary vertical X430 fixture support route" camera-controls shadow-intensity="0.8"></model-viewer><p>The gold floor plane and thin centerline are datums, not pedestal geometry. Exact pedestal CAD is deliberately absent pending the manufacturer response.</p></section>
<section><h2>Useful arithmetic, bounded authority</h2><div class="grid"><article class="card"><strong>123.636×</strong><p>2,040 / 16.5 catalog-to-accidental-screen ratio only.</p></article><article class="card"><strong>4.613–5.675 mm</strong><p>Provisional 5/8-inch screw engagement assuming nominal plate thickness; vendor confirmation required.</p></article><article class="card"><strong>0 N·m</strong><p>Gravity torque about the vertical joint axis. This is why horizontal evidence remains mandatory.</p></article></div></section>
<section><h2>Topology disposition</h2><div class="table"><table><thead><tr><th>Route</th><th>Use</th><th>Disposition</th></tr></thead><tbody><tr><td>Floor-mounted static pedestal</td><td>Sensor chain, low-speed torque and controlled-duty development</td><td>Preferred inquiry candidate; not selected</td></tr><tr><td>Horizontal C-frame</td><td>Representative gravity/bearing/assembly duty</td><td>Required later; structural design open</td></tr><tr><td>Weighted/mobile pedestal</td><td>No floor anchors</td><td>Rejected for catalog torque credit</td></tr><tr><td>Bench clamps</td><td>Convenient temporary restraint</td><td>Prohibited as primary support</td></tr></tbody></table></div></section>
<section><h2>What still blocks even an order</h2><p class="hold">Ten holds remain open.</p><p>Controlled CAD/configuration, torque-rating applicability, exact plate holes, modified-plate DFM, fasteners, floor survey, anchor design, guard/catch/load device, qualified analysis and written work authorization.</p></section>
<section><h2>Evidence</h2><p><a href="../../../docs/hr-v0-x430-fixture-support-p0.1.md">Design record</a> · <a href="../../../test-fixtures/hr-v0/x430-fixture-support-p0.1/support-route-drawing.svg">Drawing</a> · <a href="../../../test-fixtures/hr-v0/x430-fixture-support-p0.1/support-rfi.csv">RFI register</a> · <a href="../../../test-fixtures/hr-v0/x430-fixture-support-p0.1/topology-trade.csv">Topology trade</a></p></section>
</main><footer><p>{WARNING}. All release flags remain false.</p></footer></body></html>''', encoding="utf-8", newline="\n")


def main() -> int:
    if OUT.exists(): shutil.rmtree(OUT)
    if WEB.exists(): shutil.rmtree(WEB)
    OUT.mkdir(parents=True); WEB.mkdir(parents=True)

    x430 = x430_arch.x430_to_joint_frame(cq.importers.importStep(str(VENDOR / "x-430_idle.stp")).val()).translate((0, 0, 180))
    s102 = cq.importers.importStep(str(VENDOR / "fr12_s102.stp")).val().translate((0, 0, 201))
    h101 = cq.importers.importStep(str(VENDOR / "fr12_h101.stp")).val().translate((0, 0, 180))
    parts = {
        "40006_BP_ENVELOPE_CENTRAL_MACHINING_CANDIDATE": modified_plate_envelope(),
        "TFF400_DRAWING_DERIVED_ENVELOPE": rotate_to_vertical(interface.tff_envelope()),
        "FX100_C02_ACTIVE_ADAPTER_REVIEW_CANDIDATE": rotate_to_vertical(interface.active_adapter()),
        "X430_EXACT_VENDOR_GEOMETRY": rotate_to_vertical(x430),
        "FR12_S102_EXACT_VENDOR_GEOMETRY": rotate_to_vertical(s102),
        "FR12_H101_EXACT_VENDOR_GEOMETRY": rotate_to_vertical(h101),
        "PEDESTAL_300MM_HEIGHT_DATUM_NOT_BODY_CAD": cq.Solid.makeCylinder(5, PEDESTAL_H, cq.Vector(0,0,0), cq.Vector(0,0,1)),
        "FLOOR_INTERFACE_EXTENT_DATUM_NOT_BASE": cq.Solid.makeBox(500,500,1,cq.Vector(-250,-250,-1)),
    }
    assembly = cq.Assembly(name="HR_V0_X430_FIXTURE_SUPPORT_P01_REVIEW")
    for name, shape in parts.items():
        color = cq.Color(0.96,0.70,0.12) if "DATUM" in name or "TFF" in name else (cq.Color(0.12,0.45,0.75) if "EXACT" in name else cq.Color(0.66,0.87,0.98))
        assembly.add(shape, name=name, color=color)
    step = OUT / "HR-V0_X430_fixture_support_P0.1_review.step"
    cq.exporters.export(cq.Compound.makeCompound(list(parts.values())), str(step)); base.canonicalize_step(step)
    assembly.save(str(OUT / "HR-V0_X430_fixture_support_P0.1_review.glb"))
    plate = OUT / "FX101-C01_40006-BP_central-machining-review.step"
    cq.exporters.export(parts["40006_BP_ENVELOPE_CENTRAL_MACHINING_CANDIDATE"], str(plate)); base.canonicalize_step(plate)
    drawing_svg(OUT / "support-route-drawing.svg"); html(WEB / "index.html")

    write_csv(OUT / "topology-trade.csv", [
        {"route":"SUP-A","topology":"40200-SP-K 300 mm floor-mounted static pedestal plus modified 40006-BP","evidence_role":"vertical-axis sensor chain and controlled duty development","limitation":"catalog torque applies only floor-mounted; site/anchors/CAD/application open; gravity torque absent","disposition":"PREFERRED INQUIRY CANDIDATE - NOT SELECTED"},
        {"route":"SUP-B","topology":"horizontal custom C-frame","evidence_role":"representative gravity/bearing/configured-joint duty","limitation":"complete frame/joint/anchor/guard design and proof absent","disposition":"REQUIRED LATER - DESIGN OPEN"},
        {"route":"SUP-C","topology":"weighted or mobile pedestal","evidence_role":"portable support","limitation":"40200-SP-K 2040 N m statement cannot be transferred to an unanchored base","disposition":"REJECT FOR CATALOG TORQUE CREDIT"},
        {"route":"SUP-D","topology":"bench clamps or temporary woodworking clamps","evidence_role":"temporary positioning only","limitation":"unrated slip, pry, substrate and release behavior","disposition":"PROHIBITED AS PRIMARY SUPPORT"},
    ])
    write_csv(OUT / "support-bom.csv", [
        {"item":"SUP-001","manufacturer":"80/20","order_identity":"40200-SP-K configured 300 mm height","quantity":"1","state":"EXACT FAMILY/HEIGHT CANDIDATE - QUOTE CONFIGURATION REQUIRED","missing":"controlled CAD/drawing, option identity, anchor pattern/loads, rating applicability, included hardware identity"},
        {"item":"SUP-002","manufacturer":"80/20","order_identity":"40006-BP","quantity":"1","state":"EXACT MODIFICATION BLANK CANDIDATE - NOT ORDERED","missing":"controlled CAD/drawing, existing hole pattern/tolerances, modification acceptance, MTR/FAI"},
        {"item":"SUP-003","manufacturer":"Accu","order_identity":"SSC-8-32-5/8-A2","quantity":"4","state":"DIMENSIONAL CANDIDATE - NOT SELECTED","missing":"FUTEK acceptance, washer, grade, engagement, torque, locking and proof"},
        {"item":"SUP-004","manufacturer":"Accu","order_identity":"HRDW-M4-A2","quantity":"4","state":"DIMENSIONAL CANDIDATE - NOT SELECTED","missing":"FUTEK acceptance and joint-stack proof"},
        {"item":"SUP-005","manufacturer":"80/20","order_identity":"included pedestal / suggested 40006-BP mounting hardware","quantity":"8 positions","state":"IDENTITY REQUIRED","missing":"exact screw/nut allocation, torque, reuse, witness, fit and proof"},
        {"item":"SUP-006","manufacturer":"SELECTION REQUIRED","order_identity":"site-specific floor anchors","quantity":"SELECTION REQUIRED","state":"NOT SELECTED","missing":"substrate survey, code/jurisdiction, loads, edge distances, embedment, installation and proof"},
    ])
    write_csv(OUT / "support-load-screen.csv", [
        {"screen":"SLS-001","input":"40200-SP-K published maximum torque when mounted to floor","value":"2040 N m","comparison":"16.5 N m accidental overload arithmetic","result":f"catalog ratio={CATALOG_TORQUE_NM/OVERLOAD_SCREEN_NM:.6f}","authority":"CATALOG COMPARISON ONLY - NOT PROJECT ALLOWABLE"},
        {"screen":"SLS-002","input":"vertical joint axis","value":"gravity force acts parallel to axis","comparison":"gravity moment about joint axis","result":"0 N m ideal","authority":"ORIENTATION FACT ONLY - DOES NOT REPLACE HORIZONTAL TEST"},
        {"screen":"SLS-003","input":"TFF four fasteners on BCD31.75","value":"16.5 N m equal-share assumption","comparison":"four tangential demands","result":f"{OVERLOAD_SCREEN_NM/(4*TFF_BCD/2000):.3f} N each","authority":"DEMAND ONLY - JOINT ALLOWABLE OPEN"},
        {"screen":"SLS-004","input":"5/8 in screw and nominal modified-plate stack","value":"L 15.113..15.875; grip 9.75..9.95; washer 0.45..0.55 mm","comparison":"thread engagement","result":"4.613..5.675 mm","authority":"PROVISIONAL; PLATE THICKNESS TOLERANCE AND VENDOR ACCEPTANCE OPEN"},
    ])
    write_csv(OUT / "support-rfi.csv", [
        {"rfi":"SUP-RFI-001","recipient":"80/20 robotics applications","question":"Provide controlled CAD/drawing and exact configured identity for 40200-SP-K at 300 mm plus 40006-BP.","state":"NOT SENT"},
        {"rfi":"SUP-RFI-002","recipient":"80/20 robotics applications","question":"State the exact boundary of the 2040 N m floor-mounted rating: load direction, duty/cycles, safety factors, top plate, height option, fasteners and exclusions.","state":"NOT SENT"},
        {"rfi":"SUP-RFI-003","recipient":"80/20 robotics applications","question":"Provide pedestal floor-interface pattern, anchor reactions/design loads, required substrate/anchors, edge distances, leveling/grout and installation/inspection instructions.","state":"NOT SENT"},
        {"rfi":"SUP-RFI-004","recipient":"80/20 robotics applications","question":"Confirm 40006-BP existing holes/tolerances, included/suggested mounting hardware and whether the proposed central pocket/boss/counterbore modification is permissible.","state":"NOT SENT"},
        {"rfi":"SUP-RFI-005","recipient":"FUTEK applications","question":"Accept or correct the vertical mounting orientation, Ø52 pocket, Ø18.98 pilot, four-hole stack and 5/8-inch screw engagement for FSH04015.","state":"NOT SENT"},
        {"rfi":"SUP-RFI-006","recipient":"candidate CNC supplier","question":"Review the modified 40006-BP central features for workholding, flatness, distortion, inspection and first article; no quote or machining authorized.","state":"NOT SENT"},
        {"rfi":"SUP-RFI-007","recipient":"Boston facility/facilities engineer","question":"Survey exact proposed location, slab/bench construction, embedded services, edge distances, drilling permission, jurisdiction and anchor installation/inspection capability.","state":"NOT SENT"},
        {"rfi":"SUP-RFI-008","recipient":"qualified mechanical reviewer","question":"Review the complete torque/extraneous-load/anchor/plate/fastener/fatigue/guard load path and vertical-to-horizontal evidence plan.","state":"NOT SENT"},
    ])
    holds = ["controlled pedestal/plate CAD and configuration","manufacturer torque-rating application acceptance","existing plate hole/interface definition","modified plate DFM/FAI/material evidence","TFF and pedestal fastener selections/proof","Boston site/substrate/permission survey","qualified anchor design/installation/proof","guard/catch/load-device integration","vertical-to-horizontal evidence equivalence and horizontal fixture","qualified powered-work authorization"]
    write_csv(OUT / "open-hold-register.csv", [{"hold_id":f"SUP-HOLD-{i:02d}","missing_evidence":v,"state":"OPEN","effect":"BLOCKS ORDER/MACHINING/FLOOR WORK/ASSEMBLY/POWERED TEST/MOTION/ENERGIZATION"} for i,v in enumerate(holds,1)])
    write_csv(OUT / "source-register.csv", [
        {"source":"SUP-SRC-001","organization":"80/20","record":"40200-SP-K static robotic pedestal","revision_date":"live page accessed 2026-08-08","locator":"https://8020.net/40200-sp-k.html","use":"300 mm option, 3207 N load, 2040 N m floor-mounted torque and hardware-family boundary"},
        {"source":"SUP-SRC-002","organization":"80/20","record":"40006-BP blank 8 inch mounting plate","revision_date":"live page accessed 2026-08-08","locator":"https://8020.net/40006-bp.html","use":"203.2 square x 19.05, 6061-T6, 40-series compatibility and suggested hardware"},
        {"source":"SUP-SRC-003","organization":"Accu","record":"SSC-8-32-5/8-A2","revision_date":"live page accessed 2026-08-08","locator":"https://www.accu.co.uk/imperial-cap-head-screws/29027-SSC-8-32-5-8-A2","use":"candidate screw identity/length only"},
        {"source":"SUP-SRC-004","organization":"FUTEK","record":"TFF400 FI1251-F and EM1040","revision_date":"drawing F/current manual accessed 2026-08-08","locator":"https://media.futek.com/content/futek/files/pdf/productdrawings/fsh02588.pdf","use":"sensor mounting interface and application-confirmation boundary"},
    ])
    status = {"identifier":IDENTIFIER,"preferred_route":"SUP-A","open_hold_count":len(holds),"rfi_state":"NOT SENT","pedestal_body_cad_present":False,"horizontal_test_still_required":True,"release_flags":{k:False for k in ("quotation","procurement","machining","floor_work","assembly","powered_test","motion","energization","safety_credit","build_release")},"warning":WARNING}
    (OUT / "package-status.json").write_text(json.dumps(status,indent=2)+"\n",encoding="utf-8")
    print(f"generated {IDENTIFIER}: 4 routes, 8 unsent RFIs, {len(holds)} open holds, all release flags false")
    return 0

if __name__ == "__main__": raise SystemExit(main())
