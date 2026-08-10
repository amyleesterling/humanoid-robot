"""Generate HR-V0 X430 duty-fixture interface P0.2 review evidence.

This package replaces the P0.1 bridge concept with dimensioned fixed and active
adapter candidates.  It is an RFI/RFQ-review package only: it is not a released
fabrication drawing, assembly instruction, powered-test plan, or energization
authorization.
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
import generate_hr_v0_arm_architecture as arm_base  # noqa: E402
import generate_hr_v0_x430_elbow_architecture as x430_arch  # noqa: E402


IDENTIFIER = "HR-V0-X430-FIXTURE-IF-P0.2"
WARNING = (
    "PRELIMINARY - RFI/RFQ REVIEW CANDIDATE ONLY - NOT APPROVED FOR "
    "PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TEST, MOTION, "
    "OR ENERGIZATION"
)
OUT = ROOT / "test-fixtures" / "hr-v0" / "x430-duty-fixture-p0.2"
WEB = ROOT / "release" / "hr-v0" / "x430-duty-fixture-p0.2"
VENDOR = ROOT / "cad" / "vendor" / "robotis" / "x430-fr12-r91"

JZ = 180.0
TFF_FIXED_X = -90.0
TFF_ACTIVE_X = -39.2
TFF_LENGTH = 50.8
TFF_OD = 50.2
TFF_ID = 16.8
TFF_BCD = 31.75
TFF_PILOT_MAX = 19.0754
FIXED_T = 13.0
ACTIVE_T = 13.0
PLATE_YZ = 100.0
PILOT_D = 18.98
PILOT_L = 2.50
TFF_CLEAR_D = 4.50
SHELF_X0 = -26.2
SHELF_X = 52.4
SHELF_Y = 50.0
SHELF_Z0 = 220.5
SHELF_T = 12.7
S102_HOLE_X = 12.0
S102_HOLE_Y = 6.0
S102_TAP_DRILL_D = 2.05
S102_SCREW_D = 2.50
S102_HEAD_D = 4.50
S102_HEAD_H = 1.85
S102_INNER_FACE_Z = 219.0
X430_TOP_Z = 215.25


def write_csv(path: Path, records: list[dict[str, object]]) -> None:
    if not records:
        raise ValueError(f"refusing to write empty CSV: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(records[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(records)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def cylinder_x(radius: float, length: float, x0: float, y: float, z: float) -> cq.Shape:
    return cq.Solid.makeCylinder(radius, length, cq.Vector(x0, y, z), cq.Vector(1, 0, 0))


def tff_envelope() -> cq.Shape:
    return cylinder_x(TFF_OD / 2, TFF_LENGTH, TFF_FIXED_X, 0, JZ).cut(
        cylinder_x(TFF_ID / 2, TFF_LENGTH, TFF_FIXED_X, 0, JZ)
    )


def tff_axes() -> list[tuple[float, float]]:
    r = TFF_BCD / 2
    return [(r, 0), (-r, 0), (0, r), (0, -r)]


def cut_tff_pattern(shape: cq.Shape, x0: float, length: float) -> cq.Shape:
    for y, z in tff_axes():
        shape = shape.cut(cylinder_x(TFF_CLEAR_D / 2, length, x0, y, JZ + z))
    return shape


def fixed_adapter() -> cq.Shape:
    part = cq.Solid.makeBox(FIXED_T, PLATE_YZ, PLATE_YZ, cq.Vector(TFF_FIXED_X - FIXED_T, -50, JZ - 50))
    part = part.fuse(cylinder_x(PILOT_D / 2, PILOT_L, TFF_FIXED_X, 0, JZ))
    part = part.cut(cylinder_x(TFF_ID / 2, FIXED_T + PILOT_L, TFF_FIXED_X - FIXED_T, 0, JZ))
    return cut_tff_pattern(part, TFF_FIXED_X - FIXED_T, FIXED_T + PILOT_L)


def active_adapter() -> cq.Shape:
    flange = cq.Solid.makeBox(ACTIVE_T, PLATE_YZ, PLATE_YZ, cq.Vector(TFF_ACTIVE_X, -50, JZ - 50))
    flange = flange.fuse(cylinder_x(PILOT_D / 2, PILOT_L, TFF_ACTIVE_X - PILOT_L, 0, JZ))
    flange = flange.cut(cylinder_x(TFF_ID / 2, ACTIVE_T + PILOT_L, TFF_ACTIVE_X - PILOT_L, 0, JZ))
    flange = cut_tff_pattern(flange, TFF_ACTIVE_X - PILOT_L, ACTIVE_T + PILOT_L)
    shelf = cq.Solid.makeBox(SHELF_X, SHELF_Y, SHELF_T, cq.Vector(SHELF_X0, -SHELF_Y / 2, SHELF_Z0))
    part = flange.fuse(shelf)
    for x in (-S102_HOLE_X, S102_HOLE_X):
        for y in (-S102_HOLE_Y, S102_HOLE_Y):
            part = part.cut(cq.Solid.makeCylinder(S102_TAP_DRILL_D / 2, SHELF_T, cq.Vector(x, y, SHELF_Z0), cq.Vector(0, 0, 1)))
    return part


def screw_envelopes() -> dict[str, cq.Shape]:
    result: dict[str, cq.Shape] = {}
    index = 1
    for x in (-S102_HOLE_X, S102_HOLE_X):
        for y in (-S102_HOLE_Y, S102_HOLE_Y):
            head = cq.Solid.makeCylinder(S102_HEAD_D / 2, S102_HEAD_H, cq.Vector(x, y, S102_INNER_FACE_Z - S102_HEAD_H), cq.Vector(0, 0, 1))
            shank = cq.Solid.makeCylinder(S102_SCREW_D / 2, 12.0, cq.Vector(x, y, S102_INNER_FACE_Z), cq.Vector(0, 0, 1))
            result[f"M2P5_LOW_HEAD_ENVELOPE_{index}_NOT_SELECTED"] = head.fuse(shank)
            index += 1
    return result


def drawing_svg(path: Path) -> None:
    path.write_text(f'''<svg xmlns="http://www.w3.org/2000/svg" width="1600" height="1200" viewBox="0 0 1600 1200" style="max-width:100%;height:auto">
<style>text{{font-family:Arial,sans-serif;fill:#102a43;font-size:20px}}.h{{font-size:36px;font-weight:700;fill:#082b55}}.w{{font-size:19px;font-weight:700;fill:#8b1e1e}}.p{{stroke:#082b55;stroke-width:3;fill:#e4f6ff}}.g{{stroke:#8a5b00;stroke-width:3;fill:#f4b942}}.x{{stroke:#9b1c1c;stroke-width:2;stroke-dasharray:9 7}}.d{{stroke:#102a43;stroke-width:2;fill:none}}.s{{font-size:17px}}</style>
<rect width="1600" height="1100" fill="#f7fbff"/><text x="50" y="58" class="h">{IDENTIFIER} · adapter-interface drawing</text>
<text x="50" y="96" class="w">PRELIMINARY - RFI/RFQ REVIEW CANDIDATE ONLY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY,</text>
<text x="50" y="126" class="w">CONNECTION, POWERED TEST, MOTION, OR ENERGIZATION</text>
<text x="55" y="180" class="h">Side section · X430 joint axis horizontal</text>
<rect x="145" y="310" width="52" height="390" class="p"/><rect x="197" y="400" width="205" height="210" rx="100" class="g"/>
<rect x="402" y="300" width="53" height="410" class="p"/><rect x="455" y="298" width="235" height="52" class="p"/>
<rect x="550" y="350" width="120" height="220" rx="25" fill="#7dd3fc" stroke="#0b63a3" stroke-width="3"/>
<line x1="70" y1="505" x2="760" y2="505" class="x"/><line x1="610" y1="240" x2="610" y2="760" class="x"/>
<text x="132" y="735">fixed adapter 13.0</text><text x="376" y="735">active flange 13.0</text><text x="486" y="285">12.7 shelf to S102 center face</text>
<text x="80" y="900" class="s">Gold: drawing-derived TFF400 envelope. Pale blue: custom CNC adapter candidates. Sky blue: exact ROBOTIS solids.</text>
<text x="80" y="935" class="w">The fixed-adapter support pattern, connector orientation, fillets, tooling access, material allowables and proof remain OPEN.</text>
<text x="850" y="180" class="h">Controlled candidate features</text>
<text x="880" y="230">TFF flange: 100 × 100 × 13.0 mm</text><text x="880" y="270">Pilot: Ø18.98 ±0.02 × 2.50 ±0.05 mm</text>
<text x="880" y="310">TFF clearance: 4 × Ø4.50 ±0.05 on BCD31.75 basic</text><text x="880" y="350">Pattern position: Ø0.10 to pilot datum axis</text>
<text x="880" y="390">Mating-face flatness: 0.05 / 50 mm candidate</text><text x="880" y="430">Candidate finish: Ra 1.6 µm; deburr 0.2–0.5 mm</text>
<text x="880" y="490">Active shelf: 52.4 × 50.0 × 12.7 mm</text><text x="880" y="530">S102 axes: X=±12, Y=±6 mm; 4 × M2.5×0.45</text>
<text x="880" y="570">Candidate screws: M2.5×12 low head; NOT SELECTED</text><text x="880" y="610">Nominal screw-head/X430 gap: 1.900 mm</text>
<text x="880" y="670" class="w">Required before quote/fabrication:</text><text x="900" y="710">manufacturer CAD and application confirmation</text>
<text x="900" y="750">GD&amp;T/threads/fillets/access reviewed by qualified engineer</text><text x="900" y="790">FEA, fatigue, fastener, deflection and proof definition</text>
<text x="900" y="830">received-part CMM/fit evidence and controlled first article</text>
<rect x="70" y="985" width="1460" height="160" fill="#fff" stroke="#8b1e1e" stroke-width="3"/>
<text x="95" y="1035" class="w">DO NOT FABRICATE FROM THIS DRAWING.</text><text x="95" y="1080">Dimensions define a review candidate and vendor questions; they are not production authority.</text>
<text x="95" y="1120">All tolerances are provisional until the sensor manufacturer, machinist and qualified mechanical reviewer accept the stack.</text></svg>''', encoding="utf-8", newline="\n")


def html_guide(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{IDENTIFIER}</title><script type="module" src="https://ajax.googleapis.com/ajax/libs/model-viewer/4.1.0/model-viewer.min.js"></script><style>
:root{{--deep:#041a35;--navy:#082b55;--sky:#7dd3fc;--pale:#e4f6ff;--gold:#f4b942;--ink:#102a43;--red:#8b1e1e;--line:#afd5e9}}*{{box-sizing:border-box}}body{{margin:0;background:#f7fbff;color:var(--ink);font:17px/1.55 system-ui,"Segoe UI",sans-serif}}header{{padding:clamp(32px,6vw,72px) 20px;background:linear-gradient(135deg,var(--deep),var(--navy));color:#fff}}header>div,main{{max-width:1180px;margin:auto}}h1{{font-size:clamp(34px,6vw,64px);line-height:1.05;margin:.4rem 0 1rem}}h2{{font-size:clamp(27px,3vw,39px);line-height:1.2;color:var(--navy)}}.eyebrow,.tag{{font-size:13px;font-weight:850;letter-spacing:.055em;text-transform:uppercase}}.eyebrow{{color:var(--sky)}}.warning{{background:var(--gold);color:#17243a;border:3px solid #8a5b00;padding:15px 18px;font-weight:850}}main{{padding:30px 20px 80px}}.decision,.card{{background:#fff;border:2px solid var(--line);border-radius:16px;padding:20px}}.decision{{border-left:9px solid var(--gold)}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(245px,1fr));gap:18px}}.card strong{{display:block;font-size:clamp(24px,4vw,39px);color:var(--navy)}}.viewer{{background:#dff3ff;border:3px solid var(--navy);border-radius:18px;overflow:hidden}}model-viewer{{width:100%;height:clamp(470px,70vh,760px)}}.viewer p{{background:#fff;margin:0;padding:14px 18px;max-width:none}}.table-wrap{{overflow:auto;border:2px solid var(--line);border-radius:12px;background:#fff}}table{{border-collapse:collapse;width:100%;min-width:850px}}th,td{{padding:13px;text-align:left;vertical-align:top;border-bottom:1px solid var(--line);font-size:16px}}th{{background:var(--navy);color:#fff}}.hold{{color:var(--red);font-weight:850}}a{{color:#075b9b;font-weight:750}}footer{{padding:30px 20px;background:var(--deep);color:#fff}}footer p{{max-width:1180px;margin:auto}}@media(max-width:720px){{body{{font-size:16px}}main{{padding-inline:14px}}model-viewer{{height:470px}}}}
</style></head><body><header><div><div class="eyebrow">{IDENTIFIER} · R100</div><h1>The bridge is gone. The interface is now inspectable.</h1><div class="warning">{WARNING}</div></div></header><main>
<section class="decision"><h2>What changed</h2><p>P0.1 reused S102 side-ear axes that belong to the factory frame/actuator attachment. P0.2 replaces that route with a monolithic flange-and-shelf candidate attached at the exact S102 center-face pattern. Exact ROBOTIS solids show zero nominal adapter/X430 collision and a 1.900 mm nominal screw-head/X430 gap. Neither result includes manufacturing variation or received-part evidence.</p></section>
<section><h2>Inspect the candidate</h2><div class="viewer"><model-viewer src="../../../test-fixtures/hr-v0/x430-duty-fixture-p0.2/HR-V0_X430_fixture_interface_P0.2_review.glb" alt="Interactive preliminary X430 reaction torque fixture adapter model" camera-controls camera-orbit="38deg 66deg 90%" min-camera-orbit="auto auto 28%" max-camera-orbit="auto auto 320%" field-of-view="28deg" shadow-intensity="0.8"></model-viewer><p>Drag to orbit; scroll or pinch to zoom. Gold is the drawing-derived sensor envelope, pale blue is custom candidate geometry, sky blue is exact ROBOTIS geometry, and red fasteners are envelopes only.</p></div></section>
<section><h2>Nominal evidence—not acceptance</h2><div class="grid"><article class="card"><span class="tag">Exact-solid collision</span><strong>0.000 mm³</strong><p>Adapter versus X430 and S102 forbidden regions at nominal CAD coordinates.</p></article><article class="card"><span class="tag">Head clearance</span><strong>1.900 mm</strong><p>Nominal only; tolerance allocation and received inspection are open.</p></article><article class="card"><span class="tag">#8 engagement</span><strong>4.688–5.650 mm</strong><p>Candidate arithmetic only; FUTEK acceptance and joint proof are required.</p></article></div></section>
<section><h2>Why it still cannot be fabricated</h2><div class="table-wrap"><table><thead><tr><th>Hold</th><th>Missing evidence</th><th>Closure authority</th></tr></thead><tbody><tr><td>Sensor interface</td><td>Controlled FSH04015 CAD, connector orientation, pilot fit and bidirectional calibration</td><td>FUTEK written application response</td></tr><tr><td>Custom adapters</td><td>Final material/temper, GD&amp;T, fillets, tool access, thread specification and coating</td><td>Qualified mechanical review plus machinist DFM</td></tr><tr><td>Load path</td><td>FEA, fatigue, fastener preload/slip, deflection, extraneous loads and proof load</td><td>Qualified calculation and accepted proof procedure</td></tr><tr><td>Physical configuration</td><td>Received dimensions, first article, CMM/fit, guard/catch/base/anchor and cable route</td><td>Signed physical evidence</td></tr></tbody></table></div></section>
<section><h2>Critical fatigue screen</h2><p>The FUTEK EL1065 coefficient arithmetic gives approximately 14,506 psi at the 11 N·m catalog capacity if the intended axis maps to Mz. That is close to the document's 15,000 psi fully reversing reference. This is an interpretation requiring manufacturer confirmation—not a released operating point. The 16.5 N·m safe-overload arithmetic is an accidental-event screen, never a cyclic test target.</p></section>
<section><h2>Evidence files</h2><p><a href="../../../docs/hr-v0-x430-duty-fixture-interface-p0.2.md">Design record</a> · <a href="../../../test-fixtures/hr-v0/x430-duty-fixture-p0.2/adapter-interface-drawing.svg">Readable drawing</a> · <a href="../../../test-fixtures/hr-v0/x430-duty-fixture-p0.2/vendor-rfi.csv">Vendor RFI</a> · <a href="../../../test-fixtures/hr-v0/x430-duty-fixture-p0.2/tolerance-stack.csv">Tolerance stack</a> · <a href="../../../test-fixtures/hr-v0/x430-duty-fixture-p0.2/open-hold-register.csv">Open holds</a></p></section>
</main><footer><p>{WARNING}. Repository checks establish only internal consistency and fail-closed status; all release flags remain false.</p></footer></body></html>''', encoding="utf-8", newline="\n")


def main() -> int:
    if OUT.exists():
        shutil.rmtree(OUT)
    if WEB.exists():
        shutil.rmtree(WEB)
    (OUT / "parts").mkdir(parents=True)
    WEB.mkdir(parents=True)

    x_raw = cq.importers.importStep(str(VENDOR / "x-430_idle.stp")).val()
    s_raw = cq.importers.importStep(str(VENDOR / "fr12_s102.stp")).val()
    h_raw = cq.importers.importStep(str(VENDOR / "fr12_h101.stp")).val()
    x430 = x430_arch.x430_to_joint_frame(x_raw).translate((0, 0, JZ))
    s102 = s_raw.translate((0, 0, x430_arch.S102_LOCAL_Z_SHIFT + JZ))
    h101 = h_raw.translate((0, 0, JZ))
    fixed = fixed_adapter()
    active = active_adapter()
    sensor = tff_envelope()
    screws = screw_envelopes()

    collision = {
        "active_adapter_x430_mm3": active.intersect(x430).Volume(),
        "active_adapter_s102_mm3": active.intersect(s102).Volume(),
        "fixed_adapter_x430_mm3": fixed.intersect(x430).Volume(),
        "screw_head_x430_mm3": sum(shape.intersect(x430).Volume() for shape in screws.values()),
        "nominal_screw_head_x430_gap_mm": S102_INNER_FACE_Z - S102_HEAD_H - X430_TOP_Z,
    }
    if any(abs(collision[key]) > 1e-7 for key in collision if key.endswith("mm3")):
        raise ValueError(f"nominal forbidden collision: {collision}")

    components = {
        "TFF400_FSH04015_DRAWING_DERIVED_ENVELOPE": sensor,
        "FX100_C01_FIXED_ADAPTER_RFI_CANDIDATE": fixed,
        "FX100_C02_ACTIVE_L_ADAPTER_RFI_CANDIDATE": active,
        "X430_EXACT_VENDOR_GEOMETRY": x430,
        "FR12_S102_EXACT_VENDOR_GEOMETRY": s102,
        "FR12_H101_EXACT_VENDOR_GEOMETRY": h101,
        **screws,
    }
    assembly = cq.Assembly(name="HR_V0_X430_FIXTURE_INTERFACE_P02_REVIEW_ONLY")
    for name, shape in components.items():
        if "TFF400" in name:
            color = cq.Color(0.96, 0.70, 0.12)
        elif "ADAPTER" in name:
            color = cq.Color(0.66, 0.87, 0.98)
        elif "SCREW" in name:
            color = cq.Color(0.65, 0.10, 0.10)
        else:
            color = cq.Color(0.12, 0.45, 0.75)
        assembly.add(shape, name=name, color=color)
    step = OUT / "HR-V0_X430_fixture_interface_P0.2_review.step"
    cq.exporters.export(cq.Compound.makeCompound(list(components.values())), str(step))
    arm_base.canonicalize_step(step)
    assembly.save(str(OUT / "HR-V0_X430_fixture_interface_P0.2_review.glb"))
    for filename, shape in (("FX100-C01_fixed_adapter_review.step", fixed), ("FX100-C02_active_adapter_review.step", active)):
        target = OUT / "parts" / filename
        cq.exporters.export(shape, str(target))
        arm_base.canonicalize_step(target)

    drawing_svg(OUT / "adapter-interface-drawing.svg")
    html_guide(WEB / "index.html")

    write_csv(OUT / "adapter-interface-stack.csv", [
        {"interface_id":"IF2-001","from":"fixture support","to":"FX100-C01 fixed adapter","controlled_candidate":"outer support face only","status":"OPEN - SUPPORT PATTERN/JOIN/ANCHOR SELECTION REQUIRED"},
        {"interface_id":"IF2-002","from":"FX100-C01","to":"FSH04015 fixed flange","controlled_candidate":"pilot Ø18.98; 4×Ø4.50 on BCD31.75; 13.0 plate","status":"OPEN - FUTEK FIT/FASTENER APPLICATION CONFIRMATION REQUIRED"},
        {"interface_id":"IF2-003","from":"FSH04015 active flange","to":"FX100-C02","controlled_candidate":"pilot Ø18.98; 4×Ø4.50 on BCD31.75; 13.0 flange","status":"OPEN - FUTEK FIT/FASTENER APPLICATION CONFIRMATION REQUIRED"},
        {"interface_id":"IF2-004","from":"FX100-C02 shelf","to":"FR12-S102 center face","controlled_candidate":"4×M2.5×0.45 at X=±12,Y=±6; 12.7 shelf","status":"OPEN - THREAD/FASTENER/TORQUE/ACCESS/FAI REQUIRED"},
        {"interface_id":"IF2-005","from":"FR12-S102","to":"X430","controlled_candidate":"factory FR12-S102K set interface retained","status":"OPEN - RECEIVED KIT/ASSEMBLY EVIDENCE REQUIRED"},
    ])
    write_csv(OUT / "fastener-stack.csv", [
        {"stack_id":"FAST-001","interface":"TFF flange each end","candidate":"Accu SSC-8-32-3/4-A2-BL plus HRDW-M4-A2 reduced washer","published_or_candidate_dimensions_mm":"screw 18.288..19.050; adapter 12.95..13.05; washer 0.45..0.55","calculated_engagement_mm":"4.688..5.650","status":"NOT SELECTED - FUTEK/JOIN PROOF/INSTALLATION-TORQUE CONFIRMATION REQUIRED"},
        {"stack_id":"FAST-002","interface":"S102 center face to active shelf","candidate":"Accu SHCL-M2.5-12-A2 low-head Torx","published_or_candidate_dimensions_mm":"M2.5×0.45; L12; head Ø≤4.5; H≤1.85; S102 sheet 1.5 nominal","calculated_engagement_mm":"10.5 nominal through-tap geometry","status":"NOT SELECTED - THREAD CLASS/TORQUE/LOCKING/ACCESS/PROOF REQUIRED"},
    ])
    write_csv(OUT / "tolerance-stack.csv", [
        {"stack_id":"TOL-001","quantity":"TFF male pilot","nominal_mm":"18.98","variation_mm":"±0.02","result_or_margin_mm":"against published pilot 19.05..19.0754: diametral clearance 0.050..0.1154","authority":"CANDIDATE - FUTEK MUST ACCEPT FIT"},
        {"stack_id":"TOL-002","quantity":"#8 screw engagement","nominal_mm":"5.05","variation_mm":"4.688..5.650","result_or_margin_mm":"published minimum tapped depth interpreted as 6.096; minimum remaining depth margin 0.446","authority":"ARITHMETIC ONLY - VENDOR CONFIRMATION REQUIRED"},
        {"stack_id":"TOL-003","quantity":"low-head to X430 gap","nominal_mm":"1.900","variation_mm":"UNALLOCATED","result_or_margin_mm":"received/cumulative adverse variation unknown","authority":"OPEN - NO FIT CREDIT"},
        {"stack_id":"TOL-004","quantity":"TFF pattern true position","nominal_mm":"BCD31.75 basic","variation_mm":"Ø0.10 candidate","result_or_margin_mm":"not allocated against sensor thread/pilot","authority":"OPEN - GD&T REVIEW REQUIRED"},
        {"stack_id":"TOL-005","quantity":"mating face flatness","nominal_mm":"0.05 per 50","variation_mm":"candidate","result_or_margin_mm":"not linked to torque uncertainty/overload","authority":"OPEN - FEA/VENDOR/MACHINIST REVIEW REQUIRED"},
    ])
    write_csv(OUT / "collision-clearance.csv", [
        {"check_id":"CLR-001","pair":"active adapter / exact X430","method":"exact B-Rep nominal intersection","result":f"{collision['active_adapter_x430_mm3']:.9f} mm3","state":"NOMINAL PASS ONLY - TOLERANCE/RECEIVED CHECK OPEN"},
        {"check_id":"CLR-002","pair":"active adapter / exact S102 nonmating solid","method":"exact B-Rep nominal intersection","result":f"{collision['active_adapter_s102_mm3']:.9f} mm3","state":"NOMINAL PASS ONLY - MATING CONTACT EXCLUDED"},
        {"check_id":"CLR-003","pair":"candidate low heads / exact X430","method":"exact B-Rep nominal intersection","result":f"{collision['screw_head_x430_mm3']:.9f} mm3; gap {collision['nominal_screw_head_x430_gap_mm']:.6f} mm","state":"NOMINAL PASS ONLY - 1.900 MM GAP HAS NO ALLOCATED TOLERANCE"},
        {"check_id":"CLR-004","pair":"TFF connector/cable / active adapter","method":"not modeled; manufacturer says connector position may vary","result":"NO RESULT","state":"OPEN - CONTROLLED CAD/ORIENTATION/KEEP-OUT REQUIRED"},
        {"check_id":"CLR-005","pair":"tools / all fasteners / X430 cable","method":"not modeled","result":"NO RESULT","state":"OPEN - ASSEMBLY/TOOL/CABLE ACCESS REQUIRED"},
    ])
    torque_values = [("incomplete P1.1 reference",1.087329823),("X430 12 V stall endpoint",4.1),("TFF catalog capacity",11.0),("TFF safe-overload arithmetic",16.5)]
    load_rows = []
    for label, nm in torque_values:
        inlb = nm * 8.85074579
        load_rows.append({"case":label,"torque_nm":f"{nm:.9f}","torque_in_lbf":f"{inlb:.6f}","tff_mz_stress_screen_psi":f"{149*inlb:.3f}","four_tff_screw_tangential_demand_n":f"{nm/(4*(TFF_BCD/2000)):.3f}","authority":"DEMAND/COEFFICIENT ARITHMETIC ONLY; AXIS MAP/ALLOWABLE/FATIGUE/VENDOR CONFIRMATION OPEN"})
    write_csv(OUT / "load-screen.csv", load_rows)
    write_csv(OUT / "vendor-rfi.csv", [
        {"rfi_id":"RFI-001","recipient":"FUTEK applications engineering","question":"Provide current controlled 3D CAD and drawing revision for FSH04015; confirm all interface dimensions and connector angular position.","evidence_needed":"controlled CAD/drawing response tied to item and revision","state":"NOT SENT"},
        {"rfi_id":"RFI-002","recipient":"FUTEK applications engineering","question":"Accept or correct Ø18.98±0.02 male pilot, Ø4.50 clearance holes, 13.0 mm 6061-T651 flange and face flatness/finish candidates.","evidence_needed":"written application disposition and required GD&T","state":"NOT SENT"},
        {"rfi_id":"RFI-003","recipient":"FUTEK applications engineering","question":"Confirm screw grade, washer, minimum/max engagement and 25–30 lbf-in installation torque for both FSH04015 flanges.","evidence_needed":"written fastener/joint instruction for this item/application","state":"NOT SENT"},
        {"rfi_id":"RFI-004","recipient":"FUTEK applications engineering","question":"Confirm torque-axis mapping and use of EL1065 coefficients for 1.087, 4.1 and 11 N·m cyclic profiles plus 16.5 N·m accidental overload.","evidence_needed":"accepted load cases, fatigue/overload limits and extraneous-load method","state":"NOT SENT"},
        {"rfi_id":"RFI-005","recipient":"FUTEK applications engineering","question":"Quote CW+CCW system calibration, calibration uncertainty, exact cable/right-angle option and compatible conditioner for dynamic use.","evidence_needed":"formal quote/configuration and calibration scope","state":"NOT SENT"},
        {"rfi_id":"RFI-006","recipient":"ROBOTIS support","question":"Confirm whether the four S102 center-face M2.5 locations may support the external reaction bracket and provide installation torque/allowable loads.","evidence_needed":"written application response tied to FR12-S102K/X430","state":"NOT SENT"},
        {"rfi_id":"RFI-007","recipient":"candidate CNC supplier","question":"Review monolithic 6061-T651 geometry for tool access, fillets, distortion, inspection and first-article capability; do not quote until engineering release.","evidence_needed":"DFM response only; no production authorization","state":"NOT SENT"},
        {"rfi_id":"RFI-008","recipient":"qualified mechanical reviewer","question":"Independently review load path, FEA plan, fatigue, fasteners, stiffness, tolerance stack, proof and guard/catch interfaces.","evidence_needed":"signed findings/disposition","state":"NOT SENT"},
    ])
    holds = [
        ("IF-HOLD-01","controlled FSH04015 CAD/drawing/connector orientation"),("IF-HOLD-02","FUTEK application and bidirectional calibration acceptance"),("IF-HOLD-03","ROBOTIS S102 external-load acceptance"),("IF-HOLD-04","final material/temper/coating and manufacturing process"),("IF-HOLD-05","qualified FEA/fatigue/deflection/extraneous-load model"),("IF-HOLD-06","fastener grade/preload/torque/locking/engagement proof"),("IF-HOLD-07","final GD&T, fillets, surface finish and inspection plan"),("IF-HOLD-08","tool, cable and connector access/keep-out proof"),("IF-HOLD-09","received X430/FR12/TFF measurements and CMM correlation"),("IF-HOLD-10","controlled first article and fit inspection"),("IF-HOLD-11","base/upright/support/anchor structural release"),("IF-HOLD-12","independent catch, guard and load-device release"),("IF-HOLD-13","instrument chain/uncertainty/synchronization release"),("IF-HOLD-14","qualified powered-work review and authorization"),
    ]
    write_csv(OUT / "open-hold-register.csv", [{"hold_id":i,"missing_evidence":e,"state":"OPEN","authority_effect":"BLOCKS PROCUREMENT/FABRICATION/ASSEMBLY/POWERED TEST/MOTION/ENERGIZATION"} for i,e in holds])
    write_csv(OUT / "source-register.csv", [
        {"source_id":"IFS-001","organization":"FUTEK","record":"TFF400 drawing FI1251-F","revision_date":"revision F; accessed 2026-08-08","locator":"https://media.futek.com/content/futek/files/pdf/productdrawings/fsh02588.pdf","use":"envelope, pilot, pattern, tapped depth, electrical/catalog fields"},
        {"source_id":"IFS-002","organization":"FUTEK","record":"TFF Series Manual EM1040","revision_date":"current PDF accessed 2026-08-08","locator":"https://media.futek.com/content/futek/files/pdf/Manuals_and_Technical_Documents/TFFSeriesManual.pdf","use":"flat/inline mounting, installation torque, cable, connector, overload and calibration guidance"},
        {"source_id":"IFS-003","organization":"FUTEK","record":"TFF400 extraneous load factors EL1065","revision_date":"current PDF accessed 2026-08-08","locator":"https://media.futek.com/content/futek/files/pdf/extraneous_load_factors/fsh03993.pdf","use":"coefficient arithmetic and fatigue-reference screen"},
        {"source_id":"IFS-004","organization":"FUTEK","record":"hinge fatigue testing application 314","revision_date":"live page accessed 2026-08-08","locator":"https://www.futek.com/applications/hinge-fatigue-testing","use":"reaction-torque dynamic precedent and less-than-360-degree cable note"},
        {"source_id":"IFS-005","organization":"ROBOTIS","record":"FR12-S102K Set 903-0242-000","revision_date":"live record accessed 2026-08-08","locator":"https://www.robotis.us/fr12-s102k-set/","use":"exact set identity and factory fastener contents"},
        {"source_id":"IFS-006","organization":"ROBOTIS","record":"controlled X430/FR12 STEP and reference drawings","revision_date":"local controlled sources dated 2026-01-07","locator":"cad/vendor/robotis/x430-fr12-r91/","use":"exact nominal geometry and axes"},
        {"source_id":"IFS-007","organization":"Accu","record":"SSC-8-32-3/4-A2-BL and HRDW-M4-A2","revision_date":"live records accessed 2026-08-08","locator":"https://www.accu.co.uk/imperial-cap-head-screws/165205-SSC-8-32-3-4-A2-BL","use":"candidate dimensions only"},
        {"source_id":"IFS-008","organization":"Accu","record":"SHCL-M2.5-12-A2","revision_date":"live record accessed 2026-08-08","locator":"https://www.accu.co.uk/torx-low-cap-head-screws/14450-SHCL-M2-5-12-A2","use":"candidate low-head envelope only"},
    ])
    status = {
        "identifier": IDENTIFIER,
        "parent": "HR-V0-X430-FIXTURE-P0.1",
        "candidate_parts": ["FX100-C01", "FX100-C02"],
        "nominal_collision_check": collision,
        "open_hold_count": len(holds),
        "rfi_state": "NOT SENT",
        "release_flags": {key: False for key in ("procurement","quotation","fabrication","assembly","connection","powered_test","motion","energization","safety_credit","build_release")},
        "source_sha256": {name: sha256(VENDOR / name) for name in ("x-430_idle.stp","fr12_s102.stp","fr12_h101.stp")},
        "warning": WARNING,
    }
    (OUT / "package-status.json").write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8")
    print(f"generated {IDENTIFIER}: 2 adapter candidates, {len(holds)} open holds, all release flags false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
