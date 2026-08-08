"""Generate the R104 HB-450M/PT-600 brake-support review package.

R104 corrects the R102 PT-series thickness interpretation and advances a
manufacturer pillow-block route.  Drawing-derived geometry is used only to
make interfaces reviewable; it is not production CAD or capacity evidence.
"""

from __future__ import annotations

import csv
import hashlib
import json
import math
import shutil
import sys
from pathlib import Path

import cadquery as cq

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import generate_hr_v0_arm_architecture as base  # noqa: E402
import generate_hr_v0_x430_load_rig as r102  # noqa: E402
import generate_hr_v0_x430_output_interface as r103  # noqa: E402

IDENTIFIER = "HR-V0-X430-BRAKE-SUP-P0.1"
WARNING = "PRELIMINARY - BRAKE-SUPPORT/ERRATUM/RFI CANDIDATE ONLY - NOT APPROVED FOR QUOTATION, PROCUREMENT, MACHINING, ASSEMBLY, CONNECTION, POWERED TEST, MOTION, OR ENERGIZATION"
OUT = ROOT / "test-fixtures" / "hr-v0" / "x430-brake-support-p0.1"
WEB = ROOT / "release" / "hr-v0" / "x430-brake-support-p0.1"
HB = ROOT / "cad" / "vendor" / "magtrol" / "hb-450m-r102"
PT = ROOT / "cad" / "vendor" / "magtrol" / "pt-series-r104"

AXIS_Z = 120.0
PT_X0 = -200.0
PT_LENGTH = 600.0
PT_WIDTH = 375.0
PT_THICKNESS = 20.0
PT_SLOT_PITCH = 25.0
PT_SLOT_COUNT = 15
PT_SLOT_OPENING = 8.0
PT_SLOT_LOWER_WIDTH = 14.5
PT_SLOT_DEPTH = 12.0
PT_LIP_DEPTH = 5.0

PB_MODEL = "4866"
PB_O = 117.3
PB_P = 104.0
PB_Q = 12.7
PB_R = 76.0
PB_S = 120.4
PB_T = 14.2
PB_U = 60.0
PB_W = 6.6
PB_X = 6.4
PB_Y = 12.7
PB_TOP_RADIUS = PB_S - PB_R

ADAPTER_LENGTH_X = 90.0
ADAPTER_WIDTH_Y = 160.0
ADAPTER_THICKNESS = AXIS_Z - PT_THICKNESS - PB_R
HB_MOUNT_FACE_LOCAL_X = -3.0904


def write_csv(path: Path, records: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(records[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(records)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def cylinder_x(radius: float, length: float, x0: float, y: float = 0, z: float = AXIS_Z) -> cq.Shape:
    return cq.Solid.makeCylinder(radius, length, cq.Vector(x0, y, z), cq.Vector(1, 0, 0))


def pt_profile() -> cq.Shape:
    """Drawing-derived PT-600 profile; countersunk mounting holes are omitted."""
    shape = cq.Solid.makeBox(PT_LENGTH, PT_WIDTH, PT_THICKNESS, cq.Vector(PT_X0, -PT_WIDTH / 2, 0))
    centers = [(index - (PT_SLOT_COUNT - 1) / 2) * PT_SLOT_PITCH for index in range(PT_SLOT_COUNT)]
    lower_height = PT_SLOT_DEPTH - PT_LIP_DEPTH
    lower_z = PT_THICKNESS - PT_SLOT_DEPTH
    for y in centers:
        lower = cq.Solid.makeBox(
            PT_LENGTH + 0.4, PT_SLOT_LOWER_WIDTH, lower_height + 0.2,
            cq.Vector(PT_X0 - 0.2, y - PT_SLOT_LOWER_WIDTH / 2, lower_z - 0.1),
        )
        opening = cq.Solid.makeBox(
            PT_LENGTH + 0.4, PT_SLOT_OPENING, PT_LIP_DEPTH + 0.2,
            cq.Vector(PT_X0 - 0.2, y - PT_SLOT_OPENING / 2, PT_THICKNESS - PT_LIP_DEPTH - 0.1),
        )
        shape = shape.cut(lower.fuse(opening))
    return shape


def brake_geometry() -> tuple[cq.Shape, float]:
    native = cq.importers.importStep(str(HB / "HB-450M_B_EF.step")).val()
    translation_x = r103.BRAKE_XMIN - native.BoundingBox().xmin
    placed = native.translate((translation_x, -(native.BoundingBox().ymin + native.BoundingBox().ymax) / 2, AXIS_Z - (native.BoundingBox().zmin + native.BoundingBox().zmax) / 2))
    return placed, translation_x + HB_MOUNT_FACE_LOCAL_X


def pillow_block_envelope(mount_face_x: float) -> cq.Shape:
    """Simplified drawing-derived 4866 envelope, not manufacturer body CAD."""
    base_z = PT_THICKNESS + ADAPTER_THICKNESS
    foot = cq.Solid.makeBox(PB_T, PB_O, PB_Q, cq.Vector(mount_face_x - PB_T, -PB_O / 2, base_z))
    trapezoid = (
        cq.Workplane("YZ", origin=(mount_face_x - PB_Y, 0, base_z))
        .polyline([(-PB_O / 2, PB_Q), (PB_O / 2, PB_Q), (PB_TOP_RADIUS, PB_R), (-PB_TOP_RADIUS, PB_R)])
        .close().extrude(PB_Y).val()
    )
    crown = cylinder_x(PB_TOP_RADIUS, PB_Y, mount_face_x - PB_Y, z=base_z + PB_R)
    shape = foot.fuse(trapezoid).fuse(crown)
    # The center opening is not dimensioned in the accessory table.  A 50 mm
    # visual clearance removes the exact brake boss/key envelope from this
    # simplified body; it receives no fabrication or tolerance credit.
    shape = shape.cut(cylinder_x(25.0, PB_Y + 0.4, mount_face_x - PB_Y - 0.2, z=base_z + PB_R))
    hole_x = mount_face_x - PB_T + PB_X
    for y in (-PB_P / 2, PB_P / 2):
        shape = shape.cut(cq.Solid.makeCylinder(PB_W / 2, PB_Q + 0.4, cq.Vector(hole_x, y, base_z - 0.2), cq.Vector(0, 0, 1)))
    return shape


def adapter_plate(mount_face_x: float) -> cq.Shape:
    hole_x = mount_face_x - PB_T + PB_X
    x0 = hole_x - ADAPTER_LENGTH_X / 2
    shape = cq.Solid.makeBox(ADAPTER_LENGTH_X, ADAPTER_WIDTH_Y, ADAPTER_THICKNESS, cq.Vector(x0, -ADAPTER_WIDTH_Y / 2, PT_THICKNESS))
    # Two blind Ø5 review bores represent candidate M6 tapped axes only.
    for y in (-PB_P / 2, PB_P / 2):
        bore = cq.Solid.makeCylinder(2.5, 18.0, cq.Vector(hole_x, y, PT_THICKNESS + 6.0), cq.Vector(0, 0, 1))
        shape = shape.cut(bore)
    # Four Ø6.6 review holes align with PT slot centerlines y=±50 mm.
    for dx in (-30.0, 30.0):
        for y in (-50.0, 50.0):
            hole = cq.Solid.makeCylinder(3.3, ADAPTER_THICKNESS + 0.4, cq.Vector(hole_x + dx, y, PT_THICKNESS - 0.2), cq.Vector(0, 0, 1))
            shape = shape.cut(hole)
    return shape


def axis_markers(mount_face_x: float) -> cq.Shape:
    base_z = PT_THICKNESS + ADAPTER_THICKNESS
    markers: list[cq.Shape] = []
    for index in range(3):
        angle = math.pi / 2 + index * 2 * math.pi / 3
        y = (PB_U / 2) * math.cos(angle)
        z = base_z + PB_R + (PB_U / 2) * math.sin(angle)
        markers.append(cylinder_x(1.2, PB_Y + 2.0, mount_face_x - PB_Y - 1.0, y, z))
    return cq.Compound.makeCompound(markers)


def layout_svg(path: Path) -> None:
    path.write_text(f'''<svg xmlns="http://www.w3.org/2000/svg" width="1600" height="1120" viewBox="0 0 1600 1120" style="max-width:100%;height:auto"><style>
text{{font-family:Arial,sans-serif;fill:#102a43;font-size:20px}}.h{{font-size:36px;font-weight:700;fill:#082b55}}.w{{font-size:18px;font-weight:700;fill:#8b1e1e}}.b{{fill:#e4f6ff;stroke:#082b55;stroke-width:3}}.g{{fill:#f4b942;stroke:#8a5b00;stroke-width:3}}.s{{fill:#7dd3fc;stroke:#0b63a3;stroke-width:3}}.m{{fill:#83c5be;stroke:#0f5d57;stroke-width:3}}.d{{stroke:#082b55;stroke-width:2;fill:none}}.x{{stroke:#9b1c1c;stroke-width:2;stroke-dasharray:9 7}}.sm{{font-size:16px}}</style><rect width="1600" height="1120" fill="#f7fbff"/>
<text x="45" y="58" class="h">{IDENTIFIER} · corrected support route</text><text x="45" y="95" class="w">PRELIMINARY - NOT APPROVED FOR QUOTATION, PROCUREMENT, MACHINING, ASSEMBLY, CONNECTION,</text><text x="45" y="124" class="w">POWERED TEST, MOTION, OR ENERGIZATION</text>
<text x="55" y="190" class="h">Side elevation · nominal joint axis 120 mm</text><line x1="70" y1="500" x2="1010" y2="500" class="x"/><rect x="70" y="780" width="960" height="40" class="g"/><rect x="700" y="675" width="180" height="105" class="b"/><path d="M735 675 L845 675 L845 605 L825 440 A78 78 0 0 0 755 440 L735 605 Z" class="m"/><circle cx="890" cy="500" r="130" fill="#b7c4cf" stroke="#334e68" stroke-width="3"/><rect x="545" y="465" width="175" height="70" rx="20" class="g"/><rect x="455" y="450" width="90" height="100" class="b"/>
<text x="80" y="855">PT-600 profile · 600 × 375 × 20 mm</text><text x="715" y="735" class="sm">FX104-C01 · 24 mm</text><text x="600" y="300">Magtrol 4866 drawing-derived envelope</text><line x1="720" y1="315" x2="765" y2="420" class="d"/><text x="820" y="335">HB-450M exact vendor geometry</text><text x="455" y="425">R103 output chain</text>
<line x1="1060" y1="220" x2="1060" y2="880" stroke="#afd5e9" stroke-width="3"/><text x="1100" y="190" class="h">4866 front interface</text><path d="M1160 550 L1460 550 L1425 340 A115 115 0 0 0 1195 340 Z" class="m"/><circle cx="1310" cy="405" r="55" fill="#fff" stroke="#082b55" stroke-width="3"/><circle cx="1310" cy="350" r="8" fill="#fff" stroke="#082b55" stroke-width="2"/><circle cx="1262" cy="432" r="8" fill="#fff" stroke="#082b55" stroke-width="2"/><circle cx="1358" cy="432" r="8" fill="#fff" stroke="#082b55" stroke-width="2"/><circle cx="1195" cy="520" r="8" fill="#fff" stroke="#082b55" stroke-width="2"/><circle cx="1425" cy="520" r="8" fill="#fff" stroke="#082b55" stroke-width="2"/><text x="1100" y="600" class="sm">O 117.3 · P 104 · Q 12.7 · R 76 · S 120.4 mm</text><text x="1100" y="630" class="sm">3 × M5 on Ø60 brake pattern · 2 × Ø6.6 base holes</text>
<text x="1100" y="700" class="h">PT profile erratum</text><rect x="1160" y="755" width="330" height="100" class="g"/><path d="M1280 755 V805 H1240 V855 H1410 V805 H1370 V755" fill="#f7fbff" stroke="#082b55" stroke-width="3"/><text x="1100" y="895" class="sm">C = 20 thickness · D = 14.5 lower width</text><text x="1100" y="925" class="sm">E = 8 opening · F = 12 depth · G = 5 lip</text><text x="1100" y="955" class="sm">R102's former 14.5 mm thickness interpretation is superseded.</text>
<rect x="55" y="990" width="1490" height="95" fill="#fff" stroke="#8b1e1e" stroke-width="3"/><text x="85" y="1030" class="w">DO NOT ORDER, MACHINE, ASSEMBLE OR POWER FROM THIS DRAWING.</text><text x="85" y="1068">4866 CAD, materials, fasteners, PT hardware, adapter GD&amp;T, allowables, alignment, proof and work authorization remain open.</text></svg>''', encoding="utf-8", newline="\n")


def html(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{IDENTIFIER}</title><script type="module" src="https://ajax.googleapis.com/ajax/libs/model-viewer/4.1.0/model-viewer.min.js"></script><style>
:root{{--deep:#041a35;--navy:#082b55;--sky:#7dd3fc;--pale:#e4f6ff;--gold:#f4b942;--ink:#102a43;--red:#8b1e1e;--mint:#83c5be;--line:#afd5e9}}*{{box-sizing:border-box}}body{{margin:0;background:#f7fbff;color:var(--ink);font:17px/1.55 system-ui,"Segoe UI",sans-serif}}header{{padding:clamp(34px,6vw,72px) 20px;background:linear-gradient(135deg,var(--deep),var(--navy));color:#fff}}header>div,main{{max-width:1180px;margin:auto}}h1{{font-size:clamp(36px,6vw,64px);line-height:1.05}}h2{{font-size:clamp(27px,3vw,39px);color:var(--navy)}}.eyebrow{{font-size:14px;font-weight:850;color:var(--sky)}}.warning{{background:var(--gold);color:#17243a;border:3px solid #8a5b00;padding:15px 18px;font-weight:850}}main{{padding:30px 20px 80px}}.decision,.card,.erratum{{background:#fff;border:2px solid var(--line);border-radius:16px;padding:20px}}.decision{{border-left:9px solid var(--mint)}}.erratum{{border-left:9px solid var(--red)}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(245px,1fr));gap:18px}}.card strong{{display:block;font-size:clamp(25px,4vw,39px);color:var(--navy)}}model-viewer{{width:100%;height:600px;background:#dff3ff;border:3px solid var(--navy);border-radius:16px}}.table{{overflow:auto;border:2px solid var(--line);border-radius:12px}}table{{border-collapse:collapse;width:100%;min-width:850px}}th,td{{padding:13px;text-align:left;vertical-align:top;border-bottom:1px solid var(--line);font-size:16px}}th{{background:var(--navy);color:#fff}}.hold{{color:var(--red);font-weight:850}}a{{color:#075b9b;font-weight:750}}code{{font-size:16px}}footer{{padding:30px 20px;background:var(--deep);color:#fff}}footer p{{max-width:1180px;margin:auto}}@media(max-width:720px){{body{{font-size:16px}}model-viewer{{height:470px}}}}
</style></head><body><header><div><div class="eyebrow">{IDENTIFIER} · R104</div><h1>A manufacturer support route—and a caught dimension error.</h1><div class="warning">{WARNING}</div></div></header><main>
<section class="erratum"><h2>Controlled erratum</h2><p>The official PT profile makes <strong>C = 20.0 mm</strong> the plate thickness. <strong>D = 14.5 mm</strong> is the lower T-slot width. R102's former 14.5 mm thickness interpretation is superseded and its generated envelope is corrected.</p></section>
<section class="decision"><h2>Decision</h2><p>Use Magtrol metric pillow-block assembly <code>4866</code> for <code>HB/MHB-450M</code> as the preferred inquiry route. A 24 mm <code>FX104-C01</code> adapter aligns its published 76 mm axis height to the 120 mm rig axis and bridges the 104 mm pillow-block base spacing to PT slot centerlines 100 mm apart. Nothing is selected or released.</p></section>
<section><h2>Inspect the support chain</h2><model-viewer src="../../../test-fixtures/hr-v0/x430-brake-support-p0.1/HR-V0_X430_brake_support_P0.1_review.glb" alt="Preliminary PT-600 profile, adapter plate, Magtrol 4866 pillow-block envelope and HB-450M brake" camera-controls shadow-intensity="0.8"></model-viewer><p>Gold is drawing-derived PT geometry. Mint is the drawing-derived 4866 envelope. Pale blue is the custom adapter review candidate. Gray is exact HB-450M vendor geometry; the output chain remains inherited from R103.</p></section>
<section><h2>What the official records now establish</h2><div class="grid"><article class="card"><strong>20.0 mm</strong><p>Correct PT-series plate thickness.</p></article><article class="card"><strong>4866</strong><p>Published pillow-block assembly for HB/MHB-450M.</p></article><article class="card"><strong>104 mm</strong><p>4866 base-hole spacing versus a 100 mm four-pitch PT span.</p></article><article class="card"><strong>0 releases</strong><p>All physical and energization authorizations remain false.</p></article></div></section>
<section><h2>Topology disposition</h2><div class="table"><table><thead><tr><th>Route</th><th>Disposition</th><th>Boundary</th></tr></thead><tbody><tr><td>4866 + FX104-C01 + PT-600</td><td>Preferred inquiry, not selected</td><td>Accessory CAD, hardware, material, GD&amp;T, analysis and proof remain open.</td></tr><tr><td>Magtrol-approved direct/special base route</td><td>Manufacturer alternative</td><td>Exact order identity and geometry required.</td></tr><tr><td>Custom HB face-mount bracket</td><td>Fallback only</td><td>Use only if 4866 is unavailable or rejected.</td></tr><tr><td>Body clamp, shaft-bearing support or hand restraint</td><td>Prohibited</td><td>Uncontrolled loads and retention.</td></tr></tbody></table></div></section>
<section><h2>What remains open</h2><p class="hold">Two partial evidence holds and ten open holds still block every physical action.</p><p>The 4866 body CAD, material, mass, supplied hardware, allowable loads and application acceptance are unavailable. PT countersunk holes, T-nut/bolt identities and allowables are unavailable. FX104-C01 material, threads, GD&amp;T, analysis, DFM, FAI and proof remain undefined. Guarding, brake controls, instrumentation, anchoring, final configured H101 testing and qualified authorization remain mandatory.</p></section>
<section><h2>Evidence</h2><p><a href="../../../docs/hr-v0-x430-brake-support-p0.1.md">Design record</a> · <a href="../../../test-fixtures/hr-v0/x430-brake-support-p0.1/brake-support-layout.svg">Readable layout</a> · <a href="../../../test-fixtures/hr-v0/x430-brake-support-p0.1/interface-register.csv">Interface register</a> · <a href="../../../test-fixtures/hr-v0/x430-brake-support-p0.1/open-hold-register.csv">Hold register</a></p></section>
</main><footer><p>{WARNING}. No supplier was contacted and no hardware was ordered, machined, assembled, connected or energized.</p></footer></body></html>''', encoding="utf-8", newline="\n")


def main() -> int:
    if OUT.exists():
        shutil.rmtree(OUT)
    if WEB.exists():
        shutil.rmtree(WEB)
    OUT.mkdir(parents=True)
    WEB.mkdir(parents=True)

    brake, mount_face_x = brake_geometry()
    pt = pt_profile()
    pillow = pillow_block_envelope(mount_face_x)
    adapter = adapter_plate(mount_face_x)
    axes = axis_markers(mount_face_x)
    parts = r102.robotis_stack()
    parts.update({
        "HN12_N101_EXACT_VENDOR_GEOMETRY": r103.horn_shape(),
        "FX103_C01_DIMENSIONED_REVIEW_CANDIDATE": r103.adapter_shape(),
        "TWO_CLAMP_HUB_COUPLING_CATALOG_ENVELOPE": r103.coupling_envelope(),
        "HB450M_EXACT_VENDOR_GEOMETRY": brake,
        "PT600_DRAWING_DERIVED_PROFILE_COUNTERSUNK_HOLES_OMITTED": pt,
        "MAGTROL_4866_DRAWING_DERIVED_SIMPLIFIED_ENVELOPE_NOT_BODY_CAD": pillow,
        "FX104_C01_4866_TO_PT_ADAPTER_REVIEW_CANDIDATE": adapter,
        "THREE_M5_BRAKE_MOUNT_AXIS_MARKERS_NOT_FASTENERS": axes,
    })

    adapter_step = OUT / "FX104-C01_4866_to_PT_adapter_review.step"
    cq.exporters.export(adapter, str(adapter_step)); base.canonicalize_step(adapter_step)
    review_step = OUT / "HR-V0_X430_brake_support_P0.1_review.step"
    cq.exporters.export(cq.Compound.makeCompound(list(parts.values())), str(review_step)); base.canonicalize_step(review_step)
    assembly = cq.Assembly(name="HR_V0_X430_BRAKE_SUPPORT_P01_REVIEW")
    for name, shape in parts.items():
        if "PT600" in name:
            color = cq.Color(0.96, 0.70, 0.12)
        elif "4866" in name and "FX104" not in name:
            color = cq.Color(0.38, 0.70, 0.65)
        elif "FX104" in name:
            color = cq.Color(0.66, 0.87, 0.98)
        elif "HB450M" in name:
            color = cq.Color(0.55, 0.61, 0.67)
        elif "AXIS_MARKERS" in name:
            color = cq.Color(0.72, 0.10, 0.10)
        elif "HN12" in name or "COUPLING" in name:
            color = cq.Color(0.94, 0.58, 0.08)
        else:
            color = cq.Color(0.12, 0.45, 0.75)
        assembly.add(shape, name=name, color=color)
    assembly.save(str(OUT / "HR-V0_X430_brake_support_P0.1_review.glb"))
    layout_svg(OUT / "brake-support-layout.svg")
    html(WEB / "index.html")

    write_csv(OUT / "erratum-register.csv", [{
        "erratum":"ER-104-01","affected":"HR-V0-X430-LOAD-RIG-P0.1 PT-600 envelope",
        "former_interpretation":"14.5 mm plate thickness","corrected_interpretation":"20.0 mm plate thickness; 14.5 mm lower T-slot width",
        "source":"PT SERIES - US 02/2022 dimensions C and D","disposition":"R102 generator/export corrected; R104 controls current profile/support interpretation",
    }])
    write_csv(OUT / "topology-trade.csv", [
        {"route":"BS-A","topology":"Magtrol 4866 + FX104-C01 + PT-600","disposition":"PREFERRED INQUIRY - NOT SELECTED","boundary":"4866 CAD/material/mass/hardware/allowables and adapter release evidence absent"},
        {"route":"BS-B","topology":"Magtrol-approved direct or special metric base route","disposition":"MANUFACTURER ALTERNATIVE - IDENTITY REQUIRED","boundary":"no exact product identity, geometry or acceptance"},
        {"route":"BS-C","topology":"custom HB-450M face-mount bracket using 3 x M5 on PCD 60","disposition":"FALLBACK ONLY - NOT DEFINED","boundary":"use only if 4866 is unavailable/rejected; full qualified design required"},
        {"route":"BS-D","topology":"body clamp, shaft-bearing support, hand restraint or loose blocking","disposition":"PROHIBITED","boundary":"uncontrolled case/shaft loads, retention and stored energy"},
    ])
    write_csv(OUT / "brake-support-bom.csv", [
        {"item":"BS-001","manufacturer":"Magtrol","order_identity":"HB-450M-2 / stock code 004665 candidate","quantity":"1","state":"EXACT FAMILY CANDIDATE - NOT SELECTED","missing":"application acceptance, received identity, coil/order certificate and installed limits"},
        {"item":"BS-002","manufacturer":"Magtrol","order_identity":"4866 pillow block assembly for HB/MHB-450M","quantity":"1","state":"EXACT CATALOG IDENTITY - NOT SELECTED","missing":"current availability, CAD/drawing, material, mass, supplied hardware, allowables and acceptance"},
        {"item":"BS-003","manufacturer":"Magtrol","order_identity":"PT-600","quantity":"1","state":"DRAWING-DERIVED PROFILE - NOT SELECTED","missing":"body CAD, countersunk pattern, tolerances, T-slot hardware, allowables and application acceptance"},
        {"item":"BS-004","manufacturer":"SELECTION REQUIRED","order_identity":"FX104-C01 4866-to-PT adapter","quantity":"1","state":"DIMENSIONED REVIEW CANDIDATE ONLY","missing":"material, finish, threads, GD&T, analysis, DFM, FAI and proof"},
        {"item":"BS-005","manufacturer":"SELECTION REQUIRED","order_identity":"two 4866-to-adapter fasteners","quantity":"2","state":"NOT SELECTED","missing":"exact MPN, class/material, length, engagement, preload, locking, torque and reuse"},
        {"item":"BS-006","manufacturer":"SELECTION REQUIRED","order_identity":"four PT T-nut/bolt/washer sets","quantity":"4 sets","state":"NOT SELECTED","missing":"Magtrol-compatible order identity, fit, class, length, preload, locking, torque and proof"},
        {"item":"BS-007","manufacturer":"SELECTION REQUIRED","order_identity":"three HB-to-4866 M5 fasteners","quantity":"3","state":"NOT SELECTED","missing":"exact MPN, head/tool envelope, length, 10 mm minimum brake thread depth use, preload, locking and torque"},
    ])
    write_csv(OUT / "dimension-register.csv", [
        {"record":"DIM-01","subject":"PT plate width B","value_mm":"375.0","evidence":"PT US 02/2022","state":"DRAWING CONTROLLED"},
        {"record":"DIM-02","subject":"PT plate thickness C","value_mm":"20.0","evidence":"PT US 02/2022","state":"CORRECTED DRAWING CONTROLLED"},
        {"record":"DIM-03","subject":"PT slot pitch A","value_mm":"25.0","evidence":"PT US 02/2022","state":"DRAWING CONTROLLED"},
        {"record":"DIM-04","subject":"PT lower slot width D / opening E / depth F / lip G","value_mm":"14.5 / 8.0 / 12.0 / 5.0","evidence":"PT US 02/2022","state":"DRAWING CONTROLLED; TOLERANCES OPEN"},
        {"record":"DIM-05","subject":"4866 O / P / Q / R / S","value_mm":"117.3 / 104 / 12.7 / 76 / 120.4","evidence":"HB/MHB 2025 page 11","state":"DRAWING CONTROLLED; BODY CAD OPEN"},
        {"record":"DIM-06","subject":"4866 T / ØU / ØW / X / Y","value_mm":"14.2 / 60 / 6.6 / 6.4 / 12.7","evidence":"HB/MHB 2025 page 11","state":"DRAWING CONTROLLED; APPLICATION OPEN"},
        {"record":"DIM-07","subject":"FX104-C01 envelope","value_mm":"90 x 160 x 24","evidence":"project review allocation","state":"NOT TOLERANCED OR RELEASED"},
        {"record":"DIM-08","subject":"nominal axis height","value_mm":"20 + 24 + 76 = 120","evidence":"drawing/project arithmetic","state":"NOMINAL ONLY; ALIGNMENT/TOLERANCE OPEN"},
        {"record":"DIM-09","subject":"4866 model center opening","value_mm":"Ø50 visual clearance in simplified envelope","evidence":"NOT PUBLISHED; clears exact HB boss/key envelope only","state":"NOT A FABRICATION DIMENSION"},
    ])
    write_csv(OUT / "interface-register.csv", [
        {"interface":"BS-IF-01","from":"HB-450M front face","to":"4866 pillow block","state":"PARTIAL","missing":"exact accessory CAD, supplied 3 x M5 fasteners, seating datum, torque/locking, allowable loads and received fit"},
        {"interface":"BS-IF-02","from":"4866 2 x Ø6.6 base holes at 104 mm","to":"FX104-C01 candidate upper axes","state":"OPEN","missing":"thread/fastener selection, edge/engagement, preload, locking, analysis, FAI and proof"},
        {"interface":"BS-IF-03","from":"FX104-C01 four Ø6.6 review holes","to":"PT slot centerlines y=±50 mm","state":"OPEN","missing":"exact T-nuts/bolts, slot tolerance/fit, clamp load, torque, slip and proof"},
        {"interface":"BS-IF-04","from":"PT-600","to":"qualified bench/foundation","state":"OPEN","missing":"countersunk-hole pattern, anchors, substrate/site survey, permission, installation and proof"},
        {"interface":"BS-IF-05","from":"brake/support axis","to":"R103 coupling/X430 axis","state":"OPEN","missing":"coaxiality, center-height, parallelism, end-float, runout and metrology uncertainty"},
        {"interface":"BS-IF-06","from":"support hardware","to":"guard/catch/brake wiring/thermal instrumentation","state":"OPEN","missing":"complete physical integration, access, cable restraint, sensors, limits and validation"},
    ])
    brake_weight = 5.85 * 9.80665
    axial_bound = 0.1000082
    weight_moment = brake_weight * axial_bound
    adapter_volume = adapter.Volume()
    write_csv(OUT / "calculation-screen.csv", [
        {"screen":"BS-CALC-01","inputs":"PT mass 15.07 kg/m x 0.600 m","result":"9.042000 kg","authority":"CATALOG MASS SCREEN; RECEIVED MASS/ANCHOR LOAD OPEN"},
        {"screen":"BS-CALC-02","inputs":"HB-450M catalog mass 5.85 kg x 9.80665 m/s^2","result":f"{brake_weight:.6f} N","authority":"STATIC WEIGHT INPUT ONLY"},
        {"screen":"BS-CALC-03","inputs":"57.3689025 N x 100.0082 mm maximum axial envelope from mount face","result":f"{weight_moment:.6f} N m bounding weight moment","authority":"CONSERVATIVE ENVELOPE SCREEN; ACTUAL COM/ALLOWABLE OPEN"},
        {"screen":"BS-CALC-04","inputs":"3.2 N m / 104 mm 4866 base-hole span","result":f"{3.2/0.104:.6f} N ideal couple force","authority":"IDEAL TWO-POINT COUPLE ONLY; NO FASTENER/BRACKET CREDIT"},
        {"screen":"BS-CALC-05","inputs":"4.1 N m / 104 mm 4866 base-hole span","result":f"{4.1/0.104:.6f} N ideal couple force","authority":"STALL-ENDPOINT SCREEN ONLY"},
        {"screen":"BS-CALC-06","inputs":"4866 P 104 mm - four PT pitches 100 mm","result":"4.000000 mm mismatch; 2.000000 mm per side when centered","authority":"NOMINAL GEOMETRY; REQUIRES ADAPTER"},
        {"screen":"BS-CALC-07","inputs":"PT 20 mm + adapter 24 mm + 4866 R 76 mm","result":"120.000000 mm nominal axis height","authority":"NOMINAL ONLY; TOLERANCE/SHIM/ALIGNMENT OPEN"},
        {"screen":"BS-CALC-08","inputs":f"FX104-C01 CAD volume {adapter_volume:.3f} mm^3 x 2.70/7.85 g/cm^3","result":f"{adapter_volume*2.70/1000:.6f} g aluminum sensitivity; {adapter_volume*7.85/1000:.6f} g steel sensitivity","authority":"MATERIAL SENSITIVITY ONLY; MATERIAL/PROCESS NOT SELECTED"},
    ])
    rfis = [
        ("BS-RFI-01","Magtrol applications","Confirm current model 4866 identity, availability and suitability for HB-450M-2 on a PT-600 low-speed bidirectional characterization rig; provide controlled CAD/drawing, material, mass, supplied hardware, allowables and acceptance conditions."),
        ("BS-RFI-02","Magtrol applications","Provide PT-600 CAD, countersunk-hole pattern, profile/slot tolerances, compatible T-nut/bolt order identities, tightening guidance, allowable clamp/structural loads and base anchoring requirements."),
        ("BS-RFI-03","Magtrol applications","Review the 24 mm FX104-C01 adapter concept bridging 4866's 104 mm base spacing to PT slots 100 mm apart; accept or correct hole layout, fastening and alignment method."),
        ("BS-RFI-04","Ruland applications","Review the assembled support stiffness/alignment assumptions with the two-clamp-hub coupling and state allowable parallel/angular/axial misalignment and full-bearing-support conditions."),
        ("BS-RFI-05","candidate machine shop","DFM-review FX104-C01 only after manufacturer replies and qualified analysis; identify material, threads, GD&T, inspection and proof route. No quote or machining authorized."),
        ("BS-RFI-06","qualified mechanical reviewer","Review brake weight/torque/fault load paths, 4866 accessory evidence, adapter plate, fasteners, PT profile, slip, fatigue, alignment and containment before any release."),
        ("BS-RFI-07","qualified metrology provider","Propose received 4866/PT inspection, adapter FAI, installed center-height/coaxiality/runout/end-float measurement and uncertainty records."),
        ("BS-RFI-08","qualified facility/electrical reviewer","Review common-bed anchoring, guard/catch, brake cable/control/thermal integration and powered-work authorization for the actual Boston site."),
    ]
    write_csv(OUT / "vendor-rfi.csv", [{"rfi":i,"recipient":recipient,"question":question,"state":"NOT SENT"} for i, recipient, question in rfis])
    holds = [
        ("controlled 4866 catalog dimensions acquired; current availability, body CAD, material, mass, hardware, allowables and application acceptance absent","PARTIAL"),
        ("controlled PT profile acquired; body CAD, countersunk pattern, tolerances, T-slot hardware, allowables and application acceptance absent","PARTIAL"),
        ("FX104-C01 material, finish, threads, GD&T, analysis, DFM, FAI and proof","OPEN"),
        ("three HB-to-4866 and two 4866-to-adapter exact fastener stacks, preload, locking, torque and reuse controls","OPEN"),
        ("four PT T-nut/bolt/washer identities, fit, clamp load, slip resistance, torque and proof","OPEN"),
        ("assembled center height, coaxiality, parallelism, runout, end float, shimming and measurement uncertainty","OPEN"),
        ("brake/coupling extraneous-load and full-bearing-support application acceptance","OPEN"),
        ("dedicated brake source, control, flyback, interruption, current/temperature limits and fault injection","OPEN"),
        ("complete rotating guard, independent catch, access prevention, hot-surface and containment proof","OPEN"),
        ("PT common-bed support, countersunk attachments, Boston substrate/site permission, anchors and proof","OPEN"),
        ("FUTEK application, calibration, instrumentation and uncertainty closure","OPEN"),
        ("final configured FR12-H101 gravity/bearing/cable/moving-mass test and qualified powered-work authorization","OPEN"),
    ]
    write_csv(OUT / "open-hold-register.csv", [{"hold_id":f"BS-HOLD-{index:02d}","missing_evidence":missing,"state":state,"effect":"BLOCKS QUOTATION/PROCUREMENT/MACHINING/ASSEMBLY/CONNECTION/POWERED TEST/MOTION/ENERGIZATION"} for index, (missing, state) in enumerate(holds, 1)])
    write_csv(OUT / "received-inspection-template.csv", [
        {"record":"BS-RI-01","item":"4866 identity, revision, package contents and trace","acceptance":"MANUFACTURER-CONFIRMED RECORD REQUIRED","result":"NOT EXECUTED","reviewer":"UNASSIGNED"},
        {"record":"BS-RI-02","item":"4866 O/P/Q/R/S/T/U/W/X/Y dimensions and center opening","acceptance":"CONTROLLED DRAWING + INSPECTION PLAN REQUIRED","result":"NOT EXECUTED","reviewer":"UNASSIGNED"},
        {"record":"BS-RI-03","item":"PT-600 identity, length/width/thickness, slot count/profile/pitch and countersunk holes","acceptance":"CONTROLLED CAD/DRAWING + INSPECTION PLAN REQUIRED","result":"NOT EXECUTED","reviewer":"UNASSIGNED"},
        {"record":"BS-RI-04","item":"FX104-C01 material certificate and full FAI","acceptance":"RELEASED DRAWING REQUIRED","result":"NOT EXECUTED","reviewer":"UNASSIGNED"},
        {"record":"BS-RI-05","item":"all fastener/T-nut identities and received dimensions","acceptance":"RELEASED BOM/STACK REQUIRED","result":"NOT EXECUTED","reviewer":"UNASSIGNED"},
        {"record":"BS-RI-06","item":"assembled 4866/brake/adapter/PT torque and witness controls","acceptance":"RELEASED PROCEDURE REQUIRED","result":"NOT EXECUTED","reviewer":"UNASSIGNED"},
        {"record":"BS-RI-07","item":"installed axis height, coaxiality, runout and end float","acceptance":"RELEASED LIMITS + UNCERTAINTY REQUIRED","result":"NOT EXECUTED","reviewer":"UNASSIGNED"},
        {"record":"BS-RI-08","item":"support proof, slip witness, guard/catch and post-test inspection","acceptance":"QUALIFIED TEST PLAN REQUIRED","result":"NOT EXECUTED","reviewer":"UNASSIGNED"},
    ])
    write_csv(OUT / "source-register.csv", [
        {"source":"BS-SRC-001","organization":"Magtrol","record":"HB/MHB Series datasheet","revision_date":"©2025; accessed 2026-08-08","locator":"cad/vendor/magtrol/hb-450m-r102/HB-MHB-datasheet-2025.pdf","local_sha256":sha256(HB / "HB-MHB-datasheet-2025.pdf"),"use":"HB-450M ratings/mass and 4866 pillow-block identity/dimensions"},
        {"source":"BS-SRC-002","organization":"Magtrol","record":"HB-450M drawing Rev A","revision_date":"Rev A 2004-01-29","locator":"cad/vendor/magtrol/hb-450m-r102/hb-450m-rev-a.pdf","local_sha256":sha256(HB / "hb-450m-rev-a.pdf"),"use":"brake 3 x M5 x 0.8, 10 mm minimum, PCD 60 and Ø32 h3 boss"},
        {"source":"BS-SRC-003","organization":"Magtrol","record":"HB-450M official STEP","revision_date":"publisher revision not exposed; downloaded 2026-08-08","locator":"cad/vendor/magtrol/hb-450m-r102/HB-450M_B_EF.step","local_sha256":sha256(HB / "HB-450M_B_EF.step"),"use":"exact brake geometry and nominal mount-face transform"},
        {"source":"BS-SRC-004","organization":"Magtrol","record":"PT Series T-slot base plates","revision_date":"US 02/2022; accessed 2026-08-08","locator":"cad/vendor/magtrol/pt-series-r104/PT-series-US-02-2022.pdf","local_sha256":sha256(PT / "PT-series-US-02-2022.pdf"),"use":"corrected PT profile, pitch, length identity and mass"},
        {"source":"BS-SRC-005","organization":"Magtrol","record":"current HB/MHB and PT product pages","revision_date":"live pages accessed 2026-08-08","locator":"https://www.magtrol.com/product/hysteresis-brakes/ ; https://www.magtrol.com/product/pt-series-t-slot-base-plates/","local_sha256":"NOT DOWNLOADED","use":"current product/download context only"},
    ])

    hole_x = mount_face_x - PB_T + PB_X
    geometry = {
        "identifier": IDENTIFIER,
        "mount_face_x_mm": mount_face_x,
        "pt_profile": {"length_mm":PT_LENGTH,"width_mm":PT_WIDTH,"thickness_mm":PT_THICKNESS,"slot_count":PT_SLOT_COUNT,"pitch_mm":PT_SLOT_PITCH,"opening_mm":PT_SLOT_OPENING,"lower_width_mm":PT_SLOT_LOWER_WIDTH,"depth_mm":PT_SLOT_DEPTH,"lip_mm":PT_LIP_DEPTH},
        "pillow_block": {"model":PB_MODEL,"O_mm":PB_O,"P_mm":PB_P,"Q_mm":PB_Q,"R_mm":PB_R,"S_mm":PB_S,"T_mm":PB_T,"U_mm":PB_U,"W_mm":PB_W,"X_mm":PB_X,"Y_mm":PB_Y,"visual_clearance_diameter_mm":50.0,"visual_clearance_is_fabrication_dimension":False,"body_cad_present":False},
        "adapter": {"length_x_mm":ADAPTER_LENGTH_X,"width_y_mm":ADAPTER_WIDTH_Y,"thickness_mm":ADAPTER_THICKNESS,"upper_axis_y_mm":[-PB_P/2,PB_P/2],"lower_slot_y_mm":[-50.0,50.0],"hole_x_mm":hole_x,"fabrication_release":False},
        "nominal_axis_height_mm": PT_THICKNESS + ADAPTER_THICKNESS + PB_R,
        "nominal_intersections_mm3": {
            "pillow_brake": pillow.intersect(brake).Volume(),
            "pillow_coupling": pillow.intersect(r103.coupling_envelope()).Volume(),
            "adapter_pt": adapter.intersect(pt).Volume(),
            "pillow_adapter": pillow.intersect(adapter).Volume(),
        },
        "tolerance_credit": False,
        "capacity_credit": False,
    }
    (OUT / "geometry-check.json").write_text(json.dumps(geometry, indent=2) + "\n", encoding="utf-8")
    status = {
        "identifier": IDENTIFIER,
        "parents": ["HR-V0-X430-LOAD-RIG-P0.1", "HR-V0-X430-OUTPUT-IF-P0.1"],
        "preferred_route": "BS-A",
        "r102_pt_thickness_erratum_applied": True,
        "exact_brake_geometry_present": True,
        "pt_drawing_profile_present": True,
        "pillow_block_body_cad_present": False,
        "adapter_review_geometry_present": True,
        "adapter_fabrication_release_present": False,
        "manufacturer_application_acceptance": False,
        "fastener_selection_complete": False,
        "open_hold_count": 10,
        "partial_hold_count": 2,
        "rfi_count": len(rfis),
        "rfi_state": "NOT SENT",
        "configured_h101_test_still_required": True,
        "release_flags": {key:False for key in ("quotation","procurement","machining","assembly","connection","powered_test","motion","energization","safety_credit","build_release")},
        "warning": WARNING,
    }
    (OUT / "package-status.json").write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8")
    print(f"generated {IDENTIFIER}: PT erratum, 4866 route, 8 unsent RFIs, 2 partial + 10 open holds, all release flags false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
