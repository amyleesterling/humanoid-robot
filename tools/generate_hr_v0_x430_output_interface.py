"""Generate the R103 X430 horn/output-interface review package.

The package replaces R102's anonymous output placeholder with controlled HN12
vendor geometry and a dimensioned custom-adapter *review candidate*.  It does
not release material, tolerances, fasteners, machining, assembly or powered use.
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
import generate_hr_v0_x430_load_rig as load_rig  # noqa: E402

IDENTIFIER = "HR-V0-X430-OUTPUT-IF-P0.1"
WARNING = "PRELIMINARY - OUTPUT-INTERFACE/RFI CANDIDATE ONLY - NOT APPROVED FOR QUOTATION, PROCUREMENT, MACHINING, ASSEMBLY, CONNECTION, POWERED TEST, MOTION, OR ENERGIZATION"
OUT = ROOT / "test-fixtures" / "hr-v0" / "x430-output-interface-p0.1"
WEB = ROOT / "release" / "hr-v0" / "x430-output-interface-p0.1"
HN12 = ROOT / "cad" / "vendor" / "robotis" / "hn12-n101-r103"
MAGTROL = ROOT / "cad" / "vendor" / "magtrol" / "hb-450m-r102"

AXIS_Z = 120.0
HORN_X0 = 21.75
HORN_XMAX = 25.95
FLANGE_X0 = HORN_XMAX
FLANGE_T = 8.0
FLANGE_OD = 32.0
STUB_X0 = FLANGE_X0 + FLANGE_T
STUB_D = 15.0
STUB_L = 18.0
COUPLING_X0 = 37.0
COUPLING_L = 44.5
COUPLING_OD = 33.3
COUPLING_GAP = 0.75
HUB_L = (COUPLING_L - COUPLING_GAP) / 2
BRAKE_SHAFT_INSERTION = 15.0
BRAKE_XMIN = COUPLING_X0 + COUPLING_L - BRAKE_SHAFT_INSERTION


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


def horn_shape() -> cq.Shape:
    native = cq.importers.importStep(str(HN12 / "HN12-N101-official.step")).val()
    return native.rotate((0, 0, 0), (0, 0, 1), -90).translate((HORN_X0, 0, AXIS_Z))


def adapter_shape() -> cq.Shape:
    flange = cylinder_x(FLANGE_OD / 2, FLANGE_T, FLANGE_X0)
    stub = cylinder_x(STUB_D / 2, STUB_L, STUB_X0)
    shape = flange.fuse(stub)
    for index in range(8):
        angle = 2 * math.pi * index / 8
        y = 8.0 * math.cos(angle)
        z = AXIS_Z + 8.0 * math.sin(angle)
        hole = cylinder_x(1.1, FLANGE_T + 0.4, FLANGE_X0 - 0.2, y, z)
        shape = shape.cut(hole)
    return shape


def coupling_envelope() -> cq.Shape:
    first = cylinder_x(COUPLING_OD / 2, HUB_L, COUPLING_X0).cut(
        cylinder_x(STUB_D / 2, HUB_L + 0.2, COUPLING_X0 - 0.1)
    )
    second_x = COUPLING_X0 + HUB_L + COUPLING_GAP
    second = cylinder_x(COUPLING_OD / 2, HUB_L, second_x).cut(
        cylinder_x(STUB_D / 2, HUB_L + 0.2, second_x - 0.1)
    )
    return first.fuse(second)


def brake_shape() -> cq.Shape:
    shape = cq.importers.importStep(str(MAGTROL / "HB-450M_B_EF.step")).val()
    box = shape.BoundingBox()
    return shape.translate((BRAKE_XMIN - box.xmin, -(box.ymin + box.ymax) / 2, AXIS_Z - (box.zmin + box.zmax) / 2))


def layout_svg(path: Path) -> None:
    path.write_text(f'''<svg xmlns="http://www.w3.org/2000/svg" width="1600" height="1080" viewBox="0 0 1600 1080" style="max-width:100%;height:auto"><style>
text{{font-family:Arial,sans-serif;fill:#102a43;font-size:20px}}.h{{font-size:36px;font-weight:700;fill:#082b55}}.w{{font-size:18px;font-weight:700;fill:#8b1e1e}}.b{{fill:#e4f6ff;stroke:#082b55;stroke-width:3}}.g{{fill:#f4b942;stroke:#8a5b00;stroke-width:3}}.s{{fill:#7dd3fc;stroke:#0b63a3;stroke-width:3}}.d{{stroke:#082b55;stroke-width:2;fill:none}}.x{{stroke:#9b1c1c;stroke-width:2;stroke-dasharray:9 7}}.sm{{font-size:16px}}</style><rect width="1600" height="1080" fill="#f7fbff"/>
<text x="45" y="58" class="h">{IDENTIFIER} · dimensioned review candidate</text><text x="45" y="95" class="w">PRELIMINARY - NOT APPROVED FOR QUOTATION, PROCUREMENT, MACHINING, ASSEMBLY, CONNECTION,</text><text x="45" y="124" class="w">POWERED TEST, MOTION, OR ENERGIZATION</text>
<text x="55" y="190" class="h">Side elevation · joint axis X</text><line x1="85" y1="500" x2="1110" y2="500" class="x"/><rect x="130" y="395" width="190" height="210" rx="35" class="s"/><rect x="320" y="445" width="46" height="110" class="g"/><rect x="366" y="410" width="80" height="180" class="b"/><rect x="446" y="458" width="181" height="84" class="b"/><rect x="477" y="445" width="445" height="110" rx="22" fill="none" stroke="#8a5b00" stroke-width="4"/><rect x="778" y="345" width="300" height="310" rx="30" fill="#b7c4cf" stroke="#334e68" stroke-width="3"/>
<text x="100" y="680">X430 exact vendor geometry</text><text x="100" y="720">HN12 exact vendor geometry</text><text x="100" y="760">FX103-C01 flange Ø32 × 8</text><text x="100" y="800">integral stub Ø15 × 18</text><text x="475" y="350">two clamp hubs + 92A spider</text><text x="475" y="385">catalog envelope</text><text x="805" y="285">HB-450M exact vendor geometry</text><text x="805" y="320">provisional placement</text>
<line x1="366" y1="620" x2="446" y2="620" class="d"/><line x1="366" y1="605" x2="366" y2="635" class="d"/><line x1="446" y1="605" x2="446" y2="635" class="d"/><text x="382" y="650" class="sm">8.0 mm</text><line x1="446" y1="685" x2="627" y2="685" class="d"/><line x1="446" y1="670" x2="446" y2="700" class="d"/><line x1="627" y1="670" x2="627" y2="700" class="d"/><text x="505" y="715" class="sm">18.0 mm</text>
<text x="1160" y="190" class="h">Evidence boundary</text><text x="1175" y="240" class="sm">HN12 STEP and reference drawing:</text><text x="1175" y="270" class="sm">controlled official records.</text><text x="1175" y="315" class="sm">Adapter dimensions:</text><text x="1175" y="345" class="sm">review allocation only.</text><text x="1175" y="390" class="sm">Material, GD&amp;T, fasteners,</text><text x="1175" y="420" class="sm">preload, locking and proof: OPEN.</text><text x="1175" y="465" class="sm">Coupling: catalog envelope only;</text><text x="1175" y="495" class="sm">application acceptance OPEN.</text><text x="1175" y="540" class="sm">Brake placement: provisional.</text><text x="1175" y="600" class="h">Adapter face review</text><circle cx="1320" cy="735" r="85" class="b"/><circle cx="1320" cy="735" r="42.5" fill="none" stroke="#8a5b00" stroke-width="2" stroke-dasharray="7 6"/><circle cx="1320" cy="735" r="39.8" fill="#7dd3fc" stroke="#082b55" stroke-width="2"/><circle cx="1362.5" cy="735" r="5.8" fill="#fff" stroke="#082b55" stroke-width="2"/><circle cx="1350.1" cy="704.9" r="5.8" fill="#fff" stroke="#082b55" stroke-width="2"/><circle cx="1320" cy="692.5" r="5.8" fill="#fff" stroke="#082b55" stroke-width="2"/><circle cx="1289.9" cy="704.9" r="5.8" fill="#fff" stroke="#082b55" stroke-width="2"/><circle cx="1277.5" cy="735" r="5.8" fill="#fff" stroke="#082b55" stroke-width="2"/><circle cx="1289.9" cy="765.1" r="5.8" fill="#fff" stroke="#082b55" stroke-width="2"/><circle cx="1320" cy="777.5" r="5.8" fill="#fff" stroke="#082b55" stroke-width="2"/><circle cx="1350.1" cy="765.1" r="5.8" fill="#fff" stroke="#082b55" stroke-width="2"/><text x="1420" y="700" class="sm">8 × Ø2.2</text><text x="1420" y="730" class="sm">PCD Ø16</text><text x="1420" y="760" class="sm">review axes</text><text x="1420" y="790" class="sm">only</text>
<rect x="55" y="875" width="1490" height="150" fill="#fff" stroke="#8b1e1e" stroke-width="3"/><text x="85" y="920" class="w">DO NOT MACHINE, ASSEMBLE OR POWER FROM THIS DRAWING.</text><text x="85" y="965">The eight Ø2.2 hole axes are a clearance-hole review candidate derived from the horn's eight M2 tapped holes.</text><text x="85" y="1005">No fastener, material, tolerance, fatigue, bearing-support, guard or powered-work evidence is released.</text></svg>''', encoding="utf-8", newline="\n")


def html(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{IDENTIFIER}</title><script type="module" src="https://ajax.googleapis.com/ajax/libs/model-viewer/4.1.0/model-viewer.min.js"></script><style>
:root{{--deep:#041a35;--navy:#082b55;--sky:#7dd3fc;--pale:#e4f6ff;--gold:#f4b942;--ink:#102a43;--red:#8b1e1e;--line:#afd5e9}}*{{box-sizing:border-box}}body{{margin:0;background:#f7fbff;color:var(--ink);font:17px/1.55 system-ui,"Segoe UI",sans-serif}}header{{padding:clamp(34px,6vw,72px) 20px;background:linear-gradient(135deg,var(--deep),var(--navy));color:#fff}}header>div,main{{max-width:1180px;margin:auto}}h1{{font-size:clamp(36px,6vw,64px);line-height:1.05}}h2{{font-size:clamp(27px,3vw,39px);color:var(--navy)}}.eyebrow{{font-size:14px;font-weight:850;color:var(--sky)}}.warning{{background:var(--gold);color:#17243a;border:3px solid #8a5b00;padding:15px 18px;font-weight:850}}main{{padding:30px 20px 80px}}.decision,.card{{background:#fff;border:2px solid var(--line);border-radius:16px;padding:20px}}.decision{{border-left:9px solid var(--gold)}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(245px,1fr));gap:18px}}.card strong{{display:block;font-size:clamp(25px,4vw,39px);color:var(--navy)}}model-viewer{{width:100%;height:600px;background:#dff3ff;border:3px solid var(--navy);border-radius:16px}}.table{{overflow:auto;border:2px solid var(--line);border-radius:12px}}table{{border-collapse:collapse;width:100%;min-width:850px}}th,td{{padding:13px;text-align:left;vertical-align:top;border-bottom:1px solid var(--line);font-size:16px}}th{{background:var(--navy);color:#fff}}.hold{{color:var(--red);font-weight:850}}a{{color:#075b9b;font-weight:750}}code{{font-size:16px}}footer{{padding:30px 20px;background:var(--deep);color:#fff}}footer p{{max-width:1180px;margin:auto}}@media(max-width:720px){{body{{font-size:16px}}model-viewer{{height:470px}}}}
</style></head><body><header><div><div class="eyebrow">{IDENTIFIER} · R103</div><h1>The anonymous shaft is gone. The engineering holds are not.</h1><div class="warning">{WARNING}</div></div></header><main>
<section class="decision"><h2>Decision</h2><p>Control the official HN12-N101 geometry and advance a one-piece Ø32 × 8 mm flange with an integral Ø15 × 18 mm stub as <strong>FX103-C01 review geometry</strong>. Ask Ruland to review two <code>MJC33-15-A</code> clamp hubs with one <code>JD21/33-92Y</code> spider. No component or interface is selected.</p></section>
<section><h2>Inspect the proposed interface</h2><model-viewer src="../../../test-fixtures/hr-v0/x430-output-interface-p0.1/HR-V0_X430_output_interface_P0.1_review.glb" alt="Preliminary HN12 horn, custom output adapter, coupling envelope and brake interface" camera-controls shadow-intensity="0.8"></model-viewer><p>Sky blue is exact ROBOTIS geometry. Gold is the exact HN12 vendor horn. Pale blue is the custom adapter review candidate. The coupling is a catalog envelope and the gray brake placement remains provisional.</p></section>
<section><h2>What became exact</h2><div class="grid"><article class="card"><strong>8 × M2</strong><p>HN12 drawing pattern on a 16 mm pitch circle; reference drawing, not a project load rating.</p></article><article class="card"><strong>Ø19.5 mm</strong><p>HN12 outer diameter from controlled vendor evidence.</p></article><article class="card"><strong>14.95 mm</strong><p>Proposed stub penetration into the clamp-hub envelope; manufacturer acceptance remains open.</p></article><article class="card"><strong>0 releases</strong><p>Every quotation, procurement, machining, assembly, powered-test and energization flag is false.</p></article></div></section>
<section><h2>Topology disposition</h2><div class="table"><table><thead><tr><th>Route</th><th>Disposition</th><th>Why</th></tr></thead><tbody><tr><td>One-piece HN12 flange-to-15 mm stub + two clamp hubs</td><td>Preferred inquiry, not selected</td><td>Shortest inspectable chain; requires ROBOTIS/Ruland acceptance and qualified analysis.</td></tr><tr><td>Bearing-supported intermediate shaft cartridge</td><td>Fallback inquiry</td><td>Use if the X430 output cannot satisfy Ruland's full-bearing-support condition.</td></tr><tr><td>Set-screw hub on the smooth brake shaft</td><td>Rejected from baseline</td><td>Retention, shaft damage and application acceptance are unresolved.</td></tr><tr><td>Printed/polymer torque adapter</td><td>Prohibited</td><td>Not permitted for powered characterization.</td></tr></tbody></table></div></section>
<section><h2>What remains open</h2><p class="hold">One partial geometry hold and eleven open holds still block every physical action.</p><p>The vendor drawing is marked for reference only. Material, datum scheme, GD&amp;T, runout, fillets, fastener identity, engagement, preload, locking, fatigue, bearing support, coupling acceptance, brake mounting, guarding, instrumentation, site authorization and the final configured FR12-H101 test remain unresolved.</p></section>
<section><h2>Evidence</h2><p><a href="../../../docs/hr-v0-x430-output-interface-p0.1.md">Design record</a> · <a href="../../../test-fixtures/hr-v0/x430-output-interface-p0.1/output-interface-layout.svg">Readable layout</a> · <a href="../../../test-fixtures/hr-v0/x430-output-interface-p0.1/adapter-feature-register.csv">Feature register</a> · <a href="../../../test-fixtures/hr-v0/x430-output-interface-p0.1/open-hold-register.csv">Hold register</a></p></section>
</main><footer><p>{WARNING}. No supplier was contacted and no hardware was machined, assembled, connected or energized.</p></footer></body></html>''', encoding="utf-8", newline="\n")


def main() -> int:
    if OUT.exists():
        shutil.rmtree(OUT)
    if WEB.exists():
        shutil.rmtree(WEB)
    OUT.mkdir(parents=True)
    WEB.mkdir(parents=True)

    horn = horn_shape()
    adapter = adapter_shape()
    coupling = coupling_envelope()
    robotis = load_rig.robotis_stack()
    brake = brake_shape()
    parts = dict(robotis)
    parts.update({
        "HN12_N101_EXACT_VENDOR_GEOMETRY": horn,
        "FX103_C01_DIMENSIONED_REVIEW_CANDIDATE_NOT_FABRICATION_CAD": adapter,
        "TWO_MJC33_CLAMP_HUBS_AND_92A_SPIDER_CATALOG_ENVELOPE": coupling,
        "HB450M_EXACT_VENDOR_GEOMETRY_PROVISIONAL_PLACEMENT": brake,
    })

    adapter_step = OUT / "FX103-C01_HN12_to_15mm_stub_review.step"
    cq.exporters.export(adapter, str(adapter_step))
    base.canonicalize_step(adapter_step)
    review_step = OUT / "HR-V0_X430_output_interface_P0.1_review.step"
    cq.exporters.export(cq.Compound.makeCompound(list(parts.values())), str(review_step))
    base.canonicalize_step(review_step)
    assembly = cq.Assembly(name="HR_V0_X430_OUTPUT_INTERFACE_P01_REVIEW")
    for name, shape in parts.items():
        if "HN12" in name:
            color = cq.Color(0.96, 0.70, 0.12)
        elif "FX103" in name:
            color = cq.Color(0.66, 0.87, 0.98)
        elif "HB450M" in name:
            color = cq.Color(0.55, 0.61, 0.67)
        elif "COUPLING" in name:
            color = cq.Color(0.92, 0.60, 0.08, 0.78)
        else:
            color = cq.Color(0.12, 0.45, 0.75)
        assembly.add(shape, name=name, color=color)
    assembly.save(str(OUT / "HR-V0_X430_output_interface_P0.1_review.glb"))
    layout_svg(OUT / "output-interface-layout.svg")
    html(WEB / "index.html")

    write_csv(OUT / "topology-trade.csv", [
        {"route":"OUT-A","topology":"one-piece HN12 flange-to-15 mm stub + 2 x MJC33-15-A clamp hubs + JD21/33-92Y spider","disposition":"PREFERRED INQUIRY - NOT SELECTED","boundary":"ROBOTIS/Ruland acceptance, material, GD&T, fasteners, bearing support, FAI and proof open"},
        {"route":"OUT-B","topology":"bearing-supported 15 mm intermediate-shaft cartridge","disposition":"FALLBACK INQUIRY - NOT DEFINED","boundary":"bearing, housing, shaft, fits, alignment, support and proof all selection required"},
        {"route":"OUT-C","topology":"MJS33 set-screw hub on smooth h4 brake shaft","disposition":"REJECTED FROM CURRENT BASELINE","boundary":"surface damage, retention and application acceptance unresolved"},
        {"route":"OUT-D","topology":"printed/polymer horn-to-shaft adapter","disposition":"PROHIBITED FOR POWERED CHARACTERIZATION","boundary":"no strength, creep, fatigue, temperature or containment evidence"},
    ])
    write_csv(OUT / "candidate-bom.csv", [
        {"item":"OI-001","manufacturer":"ROBOTIS","order_identity":"HN12-N101 Set; product SKU 903-0238-000","quantity":"1","state":"EXACT GEOMETRY CONTROLLED - NOT SELECTED","missing":"application acceptance, received inspection, load allowables, datum tolerances and installation controls"},
        {"item":"OI-002","manufacturer":"SELECTION REQUIRED","order_identity":"FX103-C01 custom one-piece flange/stub","quantity":"1","state":"DIMENSIONED REVIEW CANDIDATE ONLY","missing":"material, heat treatment, finish, GD&T, fillets, analysis, DFM, FAI and proof"},
        {"item":"OI-003","manufacturer":"SELECTION REQUIRED","order_identity":"eight horn-interface fasteners","quantity":"8","state":"NOT SELECTED","missing":"exact order code, class/material, head/tool envelope, engagement, preload, locking and reuse policy"},
        {"item":"OI-004","manufacturer":"Ruland","order_identity":"MJC33-15-A","quantity":"2","state":"EXACT CATALOG CANDIDATE - NOT SELECTED","missing":"written application acceptance, received fit, clamp procedure and bearing-support closure"},
        {"item":"OI-005","manufacturer":"Ruland","order_identity":"JD21/33-92Y","quantity":"1","state":"EXACT CATALOG CANDIDATE - NOT SELECTED","missing":"application acceptance, hub-gap procedure, reversal/duty acceptance and proof"},
        {"item":"OI-006","manufacturer":"Magtrol","order_identity":"HB-450M-2 standard metric-shaft candidate","quantity":"1","state":"EXACT FAMILY CANDIDATE - NOT SELECTED","missing":"smooth-shaft clamp acceptance, insertion/location, extraneous-load limits and received inspection"},
    ])
    write_csv(OUT / "adapter-feature-register.csv", [
        {"feature":"AF-01","definition":"HN12 exact vendor body; native axis rotated to project X and placed at X=21.75 mm","authority":"controlled STEP + reference drawing","state":"GEOMETRY CONTROLLED; APPLICATION OPEN"},
        {"feature":"AF-02","definition":"8 x Ø2.2 mm clearance-hole review axes on PCD Ø16 mm","authority":"candidate clearance derived from 8-M2 x 4 TAP THRU","state":"REVIEW ALLOCATION ONLY"},
        {"feature":"AF-03","definition":"flange Ø32.0 x 8.0 mm; contact plane X=25.95 mm","authority":"project review allocation","state":"NOT TOLERANCED OR RELEASED"},
        {"feature":"AF-04","definition":"integral output stub Ø15.0 x 18.0 mm","authority":"Ruland nominal bore and project review allocation","state":"NOT TOLERANCED OR RELEASED"},
        {"feature":"AF-05","definition":"candidate shaft fit +0/-0.013 mm; not encoded in STEP","authority":"Ruland catalog shaft recommendation","state":"MANUFACTURER ACCEPTANCE REQUIRED"},
        {"feature":"AF-06","definition":"contact-face flatness, perpendicularity and total runout","authority":"SELECTION REQUIRED","state":"OPEN"},
        {"feature":"AF-07","definition":"material, heat treatment, coating and corrosion control","authority":"SELECTION REQUIRED","state":"OPEN"},
        {"feature":"AF-08","definition":"fillets, chamfers, balance and inspection datums","authority":"SELECTION REQUIRED","state":"OPEN"},
    ])
    write_csv(OUT / "calculation-screen.csv", [
        {"screen":"OI-CALC-01","inputs":"3.2 N m / 8 screws / 8 mm radius","result":"50.000000 N equal tangential load per screw","authority":"IDEAL EQUAL-SHARE ARITHMETIC ONLY; NO FASTENER CREDIT"},
        {"screen":"OI-CALC-02","inputs":"4.1 N m / 8 screws / 8 mm radius","result":"64.062500 N equal tangential load per screw","authority":"STALL-ENDPOINT SCREEN ONLY; NOT AN OPERATING OR PROOF LOAD"},
        {"screen":"OI-CALC-03","inputs":"7.9 N m / 8 screws / 8 mm radius","result":"123.437500 N equal tangential load per screw","authority":"ACCIDENT SCREEN ONLY; NO FASTENER OR HORN ALLOWABLE"},
        {"screen":"OI-CALC-04","inputs":"solid Ø15 shaft; 16T/(pi*d^3); T=3.2 N m","result":f"{16*3.2e3/(math.pi*15**3):.6f} MPa nominal torsional shear","authority":"ARITHMETIC ONLY; MATERIAL/STRESS CONCENTRATION/FATIGUE OPEN"},
        {"screen":"OI-CALC-05","inputs":"solid Ø15 shaft; 16T/(pi*d^3); T=4.1 N m","result":f"{16*4.1e3/(math.pi*15**3):.6f} MPa nominal torsional shear","authority":"STALL-ENDPOINT SCREEN ONLY"},
        {"screen":"OI-CALC-06","inputs":"solid Ø15 shaft; 16T/(pi*d^3); T=7.9 N m","result":f"{16*7.9e3/(math.pi*15**3):.6f} MPa nominal torsional shear","authority":"ACCIDENT SCREEN ONLY"},
        {"screen":"OI-CALC-07","inputs":"stub X=33.95..51.95; hub envelope begins X=37.00","result":"14.950000 mm candidate penetration","authority":"CATALOG ENVELOPE LAYOUT ONLY; RULAND ACCEPTANCE REQUIRED"},
    ])
    write_csv(OUT / "interface-tolerance-register.csv", [
        {"interface":"OI-IF-01","from":"X430 output serration","to":"HN12 DC12 serration","candidate":"exact vendor geometry","missing":"received fit, backlash, allowable torque/duty, installation and retention evidence","state":"PARTIAL"},
        {"interface":"OI-IF-02","from":"HN12 8 x M2 tapped pattern","to":"FX103-C01 8 x Ø2.2 candidate holes","candidate":"PCD Ø16; nominal axes aligned","missing":"datum tolerance, screw identity, engagement, preload, locking, bearing/shear/slip analysis and proof","state":"OPEN"},
        {"interface":"OI-IF-03","from":"FX103-C01 Ø15 stub","to":"MJC33-15-A clamp hub","candidate":"14.95 mm insertion; shaft +0/-0.013 mm catalog target","missing":"runout, surface finish, clamp procedure, full bearing support and application acceptance","state":"OPEN"},
        {"interface":"OI-IF-04","from":"second MJC33-15-A clamp hub","to":"HB-450M-2 smooth h4 shaft","candidate":"15.0 mm insertion envelope","missing":"received shaft, surface/fit, clamp acceptance, axial location and proof","state":"OPEN"},
        {"interface":"OI-IF-05","from":"rotating drivetrain","to":"fixed support/guard/instrumentation","candidate":"SELECTION REQUIRED","missing":"alignment, end float, reaction path, guard, catch, sensors and validation","state":"OPEN"},
    ])
    write_csv(OUT / "collision-register.csv", [
        {"check":"COL-01","pair":"HN12 exact geometry / X430 exact geometry","nominal_intersection_mm3":"0.000000","interpretation":"nominal B-Rep noninterference only; no tolerance or received-hardware credit"},
        {"check":"COL-02","pair":"FX103-C01 / HN12 exact geometry","nominal_intersection_mm3":"0.000000","interpretation":"touching placement at X=25.95 mm; contact datum and tolerance remain open"},
        {"check":"COL-03","pair":"FX103-C01 / X430 exact geometry","nominal_intersection_mm3":"0.000000","interpretation":"nominal B-Rep noninterference only"},
        {"check":"COL-04","pair":"eight candidate hole axes / HN12 nominal pattern","nominal_intersection_mm3":"NOT A CAPACITY CHECK","interpretation":"axis/pattern review only; threads and fasteners not represented"},
    ])
    rfis = [
        ("OI-RFI-01","ROBOTIS applications","Accept or correct HN12-N101 for guarded low-speed external-brake characterization; provide allowable torque/duty/extraneous loads, datum tolerances, material/finish, installation torque and recommended M2 fastener/engagement/locking controls."),
        ("OI-RFI-02","Ruland applications","Accept or correct 2 x MJC33-15-A plus JD21/33-92Y for the proposed bidirectional spectrum; review 14.95/15 mm insertion, fits, full-bearing support, hub gap, clamp procedure, reversals and proof."),
        ("OI-RFI-03","Magtrol applications","Accept or correct clamp-hub coupling on the HB-450M-2 smooth h4 shaft; provide insertion, surface, extraneous-load, axial-location and received-inspection requirements."),
        ("OI-RFI-04","FUTEK applications","Review the complete fixed-case reaction-torque path with the HN12/adapter/coupling/brake chain and state alignment/extraneous-load/calibration requirements."),
        ("OI-RFI-05","candidate machine shop","DFM-review FX103-C01 only after manufacturer replies and qualified analysis; identify feasible material, GD&T, tool access, inspection and proof route. No quote or machining authorized."),
        ("OI-RFI-06","qualified mechanical reviewer","Review torque path, serration/horn/fasteners, one-piece adapter, stress concentrations, fatigue, coupling, bearings, fault loads and containment before any release."),
        ("OI-RFI-07","qualified metrology provider","Propose received-horn inspection, adapter FAI, coaxiality/runout/end-float and assembled alignment records with stated uncertainty."),
        ("OI-RFI-08","qualified facility/electrical reviewer","Review guard/catch, brake control, instrumentation, thermal controls, interruption, anchoring and powered-work authorization for the actual Boston site."),
    ]
    write_csv(OUT / "vendor-rfi.csv", [{"rfi":i,"recipient":r,"question":q,"state":"NOT SENT"} for i, r, q in rfis])
    holds = [
        ("controlled HN12 geometry acquired; application acceptance, allowables, datums and received inspection remain absent","PARTIAL"),
        ("FX103-C01 material/GD&T/fillet/analysis/DFM/FAI/proof","OPEN"),
        ("exact horn fasteners, engagement, preload, locking, tool access and reuse policy","OPEN"),
        ("two-clamp-hub coupling application, full bearing support, fits, gap, reversals and proof","OPEN"),
        ("HB-450M smooth-shaft clamp acceptance and extraneous-load/axial-location limits","OPEN"),
        ("brake mount, common bed, hardware, alignment, anchoring and structural proof","OPEN"),
        ("assembled coaxiality, runout, end float and metrology uncertainty","OPEN"),
        ("complete rotating guard, independent catch, access prevention and containment proof","OPEN"),
        ("dedicated brake control, flyback, interruption, thermal limits and fault injection","OPEN"),
        ("FUTEK application, calibration, instrumentation and uncertainty closure","OPEN"),
        ("Boston site/facility permission, qualified reviews and powered-work authorization","OPEN"),
        ("final configured FR12-H101 gravity/bearing/cable/moving-mass test","OPEN"),
    ]
    write_csv(OUT / "open-hold-register.csv", [{"hold_id":f"OI-HOLD-{i:02d}","missing_evidence":h,"state":s,"effect":"BLOCKS QUOTATION/PROCUREMENT/MACHINING/ASSEMBLY/CONNECTION/POWERED TEST/MOTION/ENERGIZATION"} for i, (h, s) in enumerate(holds, 1)])
    write_csv(OUT / "received-inspection-template.csv", [
        {"record":"RI-01","item":"HN12-N101 received identity and package contents","method":"photo + order/lot trace","acceptance":"SELECTION REQUIRED","result":"NOT EXECUTED","reviewer":"UNASSIGNED"},
        {"record":"RI-02","item":"HN12 OD/thickness/pattern/serration/contact faces","method":"qualified dimensional inspection","acceptance":"SELECTION REQUIRED","result":"NOT EXECUTED","reviewer":"UNASSIGNED"},
        {"record":"RI-03","item":"FX103-C01 material certificate and heat/finish trace","method":"certificate review + positive material identification if required","acceptance":"SELECTION REQUIRED","result":"NOT EXECUTED","reviewer":"UNASSIGNED"},
        {"record":"RI-04","item":"FX103-C01 full FAI and surface finish","method":"qualified metrology","acceptance":"released drawing required","result":"NOT EXECUTED","reviewer":"UNASSIGNED"},
        {"record":"RI-05","item":"coupling hubs/spider/brake shaft fits and condition","method":"identity + dimensional + visual inspection","acceptance":"manufacturer-approved plan required","result":"NOT EXECUTED","reviewer":"UNASSIGNED"},
        {"record":"RI-06","item":"assembled coaxiality/runout/end float","method":"qualified alignment record with uncertainty","acceptance":"SELECTION REQUIRED","result":"NOT EXECUTED","reviewer":"UNASSIGNED"},
    ])
    write_csv(OUT / "source-register.csv", [
        {"source":"OI-SRC-001","organization":"ROBOTIS","record":"HN12-N101 STEP; download-center record 1748","revision_date":"publisher revision not exposed; accessed 2026-08-08","locator":"cad/vendor/robotis/hn12-n101-r103/HN12-N101-official.step","local_sha256":sha256(HN12 / "HN12-N101-official.step"),"use":"exact vendor geometry"},
        {"source":"OI-SRC-002","organization":"ROBOTIS","record":"HN12-N101 reference drawing; record 1735","revision_date":"drawing 2019-05-22; accessed 2026-08-08","locator":"cad/vendor/robotis/hn12-n101-r103/HN12-N101-official.pdf","local_sha256":sha256(HN12 / "HN12-N101-official.pdf"),"use":"reference dimensions/pattern; marked FOR REFERENCE ONLY"},
        {"source":"OI-SRC-003","organization":"ROBOTIS","record":"HN12-N101 Set product page","revision_date":"live page accessed 2026-08-08","locator":"https://www.robotis.us/hn12-n101-set/","local_sha256":"NOT DOWNLOADED","use":"product SKU, compatibility and package contents"},
        {"source":"OI-SRC-004","organization":"Ruland","record":"MJC33-15-A / JD21/33-92Y / MJS33-15-A product data","revision_date":"live page accessed 2026-08-08","locator":"https://www.ruland.com/mjc33-15-a-jd21-33-92y-mjs33-15-a.html","local_sha256":"NOT DOWNLOADED","use":"hub/spider envelope, shaft fit, seating torque and bearing-support boundary"},
        {"source":"OI-SRC-005","organization":"Magtrol","record":"HB-450M Rev A drawing + controlled STEP","revision_date":"drawing Rev A 2004-01-29; STEP publisher revision not exposed","locator":"cad/vendor/magtrol/hb-450m-r102/","local_sha256":sha256(MAGTROL / "HB-450M_B_EF.step"),"use":"brake shaft/body geometry and provisional placement"},
    ])

    horn_box = horn.BoundingBox()
    adapter_box = adapter.BoundingBox()
    geometry = {
        "identifier": IDENTIFIER,
        "axis": "project X",
        "hn12_bbox_mm": {"xmin":horn_box.xmin,"xmax":horn_box.xmax,"ymin":horn_box.ymin,"ymax":horn_box.ymax,"zmin":horn_box.zmin,"zmax":horn_box.zmax},
        "adapter_bbox_mm": {"xmin":adapter_box.xmin,"xmax":adapter_box.xmax,"ymin":adapter_box.ymin,"ymax":adapter_box.ymax,"zmin":adapter_box.zmin,"zmax":adapter_box.zmax},
        "candidate_hole_count": 8,
        "candidate_hole_diameter_mm": 2.2,
        "candidate_pcd_mm": 16.0,
        "stub_penetration_mm": 14.95,
        "nominal_intersections_mm3": {
            "hn12_x430": horn.intersect(robotis["X430_EXACT_VENDOR_GEOMETRY"]).Volume(),
            "adapter_hn12": adapter.intersect(horn).Volume(),
            "adapter_x430": adapter.intersect(robotis["X430_EXACT_VENDOR_GEOMETRY"]).Volume(),
        },
        "tolerance_credit": False,
        "capacity_credit": False,
    }
    (OUT / "geometry-check.json").write_text(json.dumps(geometry, indent=2) + "\n", encoding="utf-8")
    status = {
        "identifier": IDENTIFIER,
        "parent": "HR-V0-X430-LOAD-RIG-P0.1",
        "preferred_route": "OUT-A",
        "exact_hn12_geometry_present": True,
        "adapter_review_geometry_present": True,
        "adapter_fabrication_release_present": False,
        "fastener_selection_complete": False,
        "material_selection_complete": False,
        "manufacturer_application_acceptance": False,
        "open_hold_count": 11,
        "partial_hold_count": 1,
        "rfi_count": len(rfis),
        "rfi_state": "NOT SENT",
        "configured_h101_test_still_required": True,
        "release_flags": {k:False for k in ("quotation","procurement","machining","assembly","connection","powered_test","motion","energization","safety_credit","build_release")},
        "warning": WARNING,
    }
    (OUT / "package-status.json").write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8")
    print(f"generated {IDENTIFIER}: exact HN12 evidence, 4 routes, {len(rfis)} unsent RFIs, 1 partial + 11 open holds, all release flags false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
