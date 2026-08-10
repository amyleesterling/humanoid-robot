"""Generate the R102 horizontal X430/brake load-rig review package.

The package is deliberately fail-closed.  It combines controlled vendor geometry
and catalog envelopes to make the test topology reviewable, but it contains no
released custom output adapter, brake bracket, base attachment, guard or powered
test limit.
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
import generate_hr_v0_x430_duty_fixture_interface as fixture  # noqa: E402
import generate_hr_v0_x430_elbow_architecture as x430_arch  # noqa: E402

IDENTIFIER = "HR-V0-X430-LOAD-RIG-P0.1"
WARNING = "PRELIMINARY - LOAD-RIG/RFI CANDIDATE ONLY - NOT APPROVED FOR QUOTATION, PROCUREMENT, MACHINING, ASSEMBLY, CONNECTION, POWERED TEST, MOTION, OR ENERGIZATION"
OUT = ROOT / "test-fixtures" / "hr-v0" / "x430-load-rig-p0.1"
WEB = ROOT / "release" / "hr-v0" / "x430-load-rig-p0.1"
MAGTROL = ROOT / "cad" / "vendor" / "magtrol" / "hb-450m-r102"
PT_SOURCE = ROOT / "cad" / "vendor" / "magtrol" / "pt-series-r104"
ROBOTIS = ROOT / "cad" / "vendor" / "robotis" / "x430-fr12-r91"

AXIS_Z = 120.0
BASE_X0 = -200.0
BASE_L = 600.0
BASE_W = 375.0
BASE_T = 20.0
COUPLING_X0 = 52.0
COUPLING_L = 44.5
COUPLING_OD = 33.3
BRAKE_XMIN = COUPLING_X0 + COUPLING_L


def write_csv(path: Path, records: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(records[0]), lineterminator="\n")
        writer.writeheader(); writer.writerows(records)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def cylinder_x(radius: float, length: float, x0: float) -> cq.Shape:
    return cq.Solid.makeCylinder(radius, length, cq.Vector(x0, 0, AXIS_Z), cq.Vector(1, 0, 0))


def robotis_stack() -> dict[str, cq.Shape]:
    dz = AXIS_Z - fixture.JZ
    x430 = x430_arch.x430_to_joint_frame(cq.importers.importStep(str(ROBOTIS / "x-430_idle.stp")).val()).translate((0, 0, fixture.JZ + dz))
    s102 = cq.importers.importStep(str(ROBOTIS / "fr12_s102.stp")).val().translate((0, 0, x430_arch.S102_LOCAL_Z_SHIFT + fixture.JZ + dz))
    h101 = cq.importers.importStep(str(ROBOTIS / "fr12_h101.stp")).val().translate((0, 0, fixture.JZ + dz))
    return {
        "TFF400_DRAWING_DERIVED_ENVELOPE": fixture.tff_envelope().translate((0, 0, dz)),
        "FX100_C01_FIXED_ADAPTER_REVIEW_CANDIDATE": fixture.fixed_adapter().translate((0, 0, dz)),
        "FX100_C02_ACTIVE_ADAPTER_REVIEW_CANDIDATE": fixture.active_adapter().translate((0, 0, dz)),
        "X430_EXACT_VENDOR_GEOMETRY": x430,
        "FR12_S102_EXACT_VENDOR_GEOMETRY": s102,
        "FR12_H101_EXACT_VENDOR_GEOMETRY": h101,
    }


def magtrol_shape() -> cq.Shape:
    shape = cq.importers.importStep(str(MAGTROL / "HB-450M_B_EF.step")).val()
    box = shape.BoundingBox()
    return shape.translate((BRAKE_XMIN - box.xmin, -(box.ymin + box.ymax) / 2, AXIS_Z - (box.zmin + box.zmax) / 2))


def layout_svg(path: Path) -> None:
    path.write_text(f'''<svg xmlns="http://www.w3.org/2000/svg" width="1600" height="1050" viewBox="0 0 1600 1050" style="max-width:100%;height:auto"><style>
text{{font-family:Arial,sans-serif;fill:#102a43;font-size:20px}}.h{{font-size:36px;font-weight:700;fill:#082b55}}.w{{font-size:18px;font-weight:700;fill:#8b1e1e}}.b{{fill:#e4f6ff;stroke:#082b55;stroke-width:3}}.g{{fill:#f4b942;stroke:#8a5b00;stroke-width:3}}.s{{fill:#7dd3fc;stroke:#0b63a3;stroke-width:3}}.x{{stroke:#9b1c1c;stroke-width:2;stroke-dasharray:9 7}}.sm{{font-size:16px}}</style><rect width="1600" height="1050" fill="#f7fbff"/>
<text x="45" y="58" class="h">{IDENTIFIER} · horizontal characterization topology</text><text x="45" y="95" class="w">PRELIMINARY - LOAD-RIG/RFI CANDIDATE ONLY - NOT APPROVED FOR QUOTATION, PROCUREMENT, MACHINING,</text><text x="45" y="124" class="w">ASSEMBLY, CONNECTION, POWERED TEST, MOTION, OR ENERGIZATION</text>
<text x="55" y="185" class="h">Common-bed side elevation</text><rect x="100" y="710" width="980" height="24" class="g"/><line x1="120" y1="500" x2="1170" y2="500" class="x"/>
<rect x="150" y="405" width="75" height="190" class="b"/><rect x="225" y="435" width="150" height="130" rx="60" class="g"/><rect x="375" y="405" width="75" height="190" class="b"/><rect x="450" y="430" width="130" height="140" rx="20" class="s"/>
<rect x="580" y="460" width="90" height="80" class="b"/><rect x="670" y="474" width="145" height="52" class="g"/><rect x="815" y="360" width="250" height="280" rx="30" fill="#b7c4cf" stroke="#334e68" stroke-width="3"/>
<text x="130" y="650">TFF400 / X430 fixed-case stack</text><text x="575" y="420">output-adapter placeholder</text><text x="670" y="455">MJC33 15×15 envelope</text><text x="820" y="330">exact HB-450M STEP</text><text x="100" y="775">PT-600 600×375×20 mm corrected envelope only — slots, hardware and anchoring intentionally absent</text>
<text x="1140" y="185" class="h">Evidence boundary</text><text x="1160" y="235" class="sm">Brake, X430 and FR12 geometry:</text><text x="1160" y="265" class="sm">controlled vendor files.</text><text x="1160" y="310" class="sm">Base and coupling:</text><text x="1160" y="340" class="sm">catalog envelopes only.</text><text x="1160" y="385" class="sm">Output adapter and brake riser:</text><text x="1160" y="415" class="sm">placeholders, not fabrication CAD.</text><text x="1160" y="460" class="sm">Guard, wiring, anchors, thermal</text><text x="1160" y="490" class="sm">controls and limits: OPEN.</text>
<rect x="55" y="840" width="1490" height="150" fill="#fff" stroke="#8b1e1e" stroke-width="3"/><text x="85" y="885" class="w">DO NOT BUILD OR POWER FROM THIS LAYOUT.</text><text x="85" y="930">This route characterizes an actuator against a brake; it does not reproduce the final FR12-H101 configured joint.</text><text x="85" y="970">Manufacturer application acceptance, qualified design, full guarding and a separate powered-work authorization are mandatory.</text></svg>''', encoding="utf-8", newline="\n")


def html(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{IDENTIFIER}</title><script type="module" src="https://ajax.googleapis.com/ajax/libs/model-viewer/4.1.0/model-viewer.min.js"></script><style>
:root{{--deep:#041a35;--navy:#082b55;--sky:#7dd3fc;--pale:#e4f6ff;--gold:#f4b942;--ink:#102a43;--red:#8b1e1e;--line:#afd5e9}}*{{box-sizing:border-box}}body{{margin:0;background:#f7fbff;color:var(--ink);font:17px/1.55 system-ui,"Segoe UI",sans-serif}}header{{padding:clamp(34px,6vw,72px) 20px;background:linear-gradient(135deg,var(--deep),var(--navy));color:#fff}}header>div,main{{max-width:1180px;margin:auto}}h1{{font-size:clamp(36px,6vw,64px);line-height:1.05}}h2{{font-size:clamp(27px,3vw,39px);color:var(--navy)}}.eyebrow{{font-size:14px;font-weight:850;color:var(--sky)}}.warning{{background:var(--gold);color:#17243a;border:3px solid #8a5b00;padding:15px 18px;font-weight:850}}main{{padding:30px 20px 80px}}.decision,.card{{background:#fff;border:2px solid var(--line);border-radius:16px;padding:20px}}.decision{{border-left:9px solid var(--gold)}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(245px,1fr));gap:18px}}.card strong{{display:block;font-size:clamp(25px,4vw,39px);color:var(--navy)}}model-viewer{{width:100%;height:600px;background:#dff3ff;border:3px solid var(--navy);border-radius:16px}}.table{{overflow:auto;border:2px solid var(--line);border-radius:12px}}table{{border-collapse:collapse;width:100%;min-width:850px}}th,td{{padding:13px;text-align:left;vertical-align:top;border-bottom:1px solid var(--line);font-size:16px}}th{{background:var(--navy);color:#fff}}.hold{{color:var(--red);font-weight:850}}a{{color:#075b9b;font-weight:750}}footer{{padding:30px 20px;background:var(--deep);color:#fff}}footer p{{max-width:1180px;margin:auto}}@media(max-width:720px){{body{{font-size:16px}}model-viewer{{height:470px}}}}
</style></head><body><header><div><div class="eyebrow">{IDENTIFIER} · R102</div><h1>A controllable load device—still behind hard holds.</h1><div class="warning">{WARNING}</div></div></header><main>
<section class="decision"><h2>Decision</h2><p>The preferred inquiry topology is a common Magtrol <code>PT-600</code> bed, a standard metric <code>HB-450M-2</code> hysteresis brake, a Ruland 15×15 mm jaw coupling and the existing stationary FUTEK/X430 reaction-torque stack. It is a topology candidate, not a supplier selection or build release.</p></section>
<section><h2>Inspect the horizontal route</h2><model-viewer src="../../../test-fixtures/hr-v0/x430-load-rig-p0.1/HR-V0_X430_load_rig_P0.1_review.glb" alt="Preliminary horizontal X430 brake-load characterization rig" camera-controls shadow-intensity="0.8"></model-viewer><p>Gold indicates a catalog envelope or drawing-derived sensor. Sky blue is exact ROBOTIS geometry; gray is exact Magtrol geometry. Pale custom interfaces are placeholders and intentionally omit fabrication features.</p></section>
<section><h2>Bounded catalog arithmetic</h2><div class="grid"><article class="card"><strong>3.2 N·m</strong><p>HB-450M-2 minimum torque at rated current—not a selected test point.</p></article><article class="card"><strong>1.2375×</strong><p>Coupling rated torque divided by brake rated torque; application acceptance remains open.</p></article><article class="card"><strong>10.053 W</strong><p>Ideal brake dissipation at 3.2 N·m and 30 rpm, not a thermal release.</p></article><article class="card"><strong>9.042 kg</strong><p>PT-600 catalog mass screen from 15.07 kg/m × 0.600 m.</p></article></div></section>
<section><h2>Topology disposition</h2><div class="table"><table><thead><tr><th>Route</th><th>Role</th><th>Disposition</th></tr></thead><tbody><tr><td>PT-600 + standard HB-450M-2 + reviewed riser</td><td>Actuator/brake characterization</td><td>Preferred inquiry; not selected</td></tr><tr><td>Magtrol metric base-mount special</td><td>Reduce custom brake support</td><td>Ask manufacturer; exact identity required</td></tr><tr><td>80/20 cantilever</td><td>Reuse R101 pedestal</td><td>Rejected for this 5.85 kg coaxial drivetrain</td></tr><tr><td>Human-held/friction/weights</td><td>Informal load</td><td>Prohibited for powered characterization</td></tr></tbody></table></div></section>
<section><h2>What remains open</h2><p class="hold">Fourteen blocking holds remain open and every release flag is false.</p><p>The exact output interface, brake mounting, coupling application, coaxial alignment, common-bed attachment, anchoring, electrical brake control, flyback protection, instrumentation, thermal limits, complete guard/catch and qualified powered-work authorization remain unresolved. The final configured FR12-H101 gravity test remains mandatory.</p></section>
<section><h2>Evidence</h2><p><a href="../../../docs/hr-v0-x430-load-rig-p0.1.md">Design record</a> · <a href="../../../test-fixtures/hr-v0/x430-load-rig-p0.1/load-rig-layout.svg">Readable layout</a> · <a href="../../../test-fixtures/hr-v0/x430-load-rig-p0.1/vendor-rfi.csv">RFI register</a> · <a href="../../../test-fixtures/hr-v0/x430-load-rig-p0.1/open-hold-register.csv">Hold register</a></p></section>
</main><footer><p>{WARNING}. No hardware was connected or energized.</p></footer></body></html>''', encoding="utf-8", newline="\n")


def main() -> int:
    if OUT.exists(): shutil.rmtree(OUT)
    if WEB.exists(): shutil.rmtree(WEB)
    OUT.mkdir(parents=True); WEB.mkdir(parents=True)

    parts = robotis_stack()
    parts.update({
        "PT600_CATALOG_ENVELOPE_NOT_BODY_CAD": cq.Solid.makeBox(BASE_L, BASE_W, BASE_T, cq.Vector(BASE_X0, -BASE_W/2, 0)),
        "OUTPUT_ADAPTER_PLACEHOLDER_NO_ATTACHMENT_FEATURES": cylinder_x(22.5, 30.0, 22.0).fuse(cylinder_x(7.5, 20.0, 32.0)),
        "MJC33_15X15_CATALOG_ENVELOPE_NOT_BODY_CAD": cylinder_x(COUPLING_OD/2, COUPLING_L, COUPLING_X0),
        "HB450M_EXACT_VENDOR_GEOMETRY_PROVISIONAL_PLACEMENT": magtrol_shape(),
        "BRAKE_RISER_PLACEHOLDER_NOT_FABRICATION_GEOMETRY": cq.Solid.makeBox(145, 125, 35, cq.Vector(BRAKE_XMIN+5, -62.5, BASE_T)),
        "ROTATING_GUARD_REQUIRED_VOLUME_DATUM": cylinder_x(70, 100, 15.0),
    })
    assembly = cq.Assembly(name="HR_V0_X430_LOAD_RIG_P01_REVIEW")
    for name, shape in parts.items():
        if "HB450M" in name: color = cq.Color(0.55,0.61,0.67)
        elif "EXACT_VENDOR" in name: color = cq.Color(0.12,0.45,0.75)
        elif "PLACEHOLDER" in name: color = cq.Color(0.66,0.87,0.98)
        elif "GUARD_REQUIRED" in name: color = cq.Color(0.75,0.12,0.12,0.25)
        else: color = cq.Color(0.96,0.70,0.12)
        assembly.add(shape, name=name, color=color)
    step = OUT / "HR-V0_X430_load_rig_P0.1_review.step"
    cq.exporters.export(cq.Compound.makeCompound(list(parts.values())), str(step)); base.canonicalize_step(step)
    assembly.save(str(OUT / "HR-V0_X430_load_rig_P0.1_review.glb"))
    layout_svg(OUT / "load-rig-layout.svg"); html(WEB / "index.html")

    write_csv(OUT / "topology-trade.csv", [
        {"route":"LOAD-A","topology":"PT-600 common bed + standard HB-450M-2 + reviewed riser","role":"regulated actuator/brake characterization","limitation":"base CAD, riser, attachment, control and application acceptance open","disposition":"PREFERRED INQUIRY - NOT SELECTED"},
        {"route":"LOAD-B","topology":"Magtrol metric base-mount special derived from HB-450M-2","role":"remove custom brake riser","limitation":"HB-451 statement applies to imperial family; metric identity/shaft/performance not established","disposition":"MANUFACTURER RFI REQUIRED"},
        {"route":"LOAD-C","topology":"R101 80/20 pedestal cantilever","role":"reuse support concept","limitation":"5.85 kg brake, coaxial alignment and drivetrain load path not accepted","disposition":"REJECT FOR CURRENT LOAD RIG"},
        {"route":"LOAD-D","topology":"friction belt, loose weights or human-held load","role":"informal resistance","limitation":"uncontrolled stored energy, alignment and repeatability","disposition":"PROHIBITED FOR POWERED CHARACTERIZATION"},
    ])
    write_csv(OUT / "load-device-bom.csv", [
        {"item":"LR-001","manufacturer":"Magtrol","order_identity":"HB-450M-2, standard metric shaft candidate","quantity":"1","state":"EXACT FAMILY CANDIDATE - NOT SELECTED","missing":"written application acceptance, coil/order identity, received certificate, control and thermal limits"},
        {"item":"LR-002","manufacturer":"Magtrol","order_identity":"PT-600","quantity":"1","state":"CATALOG ENVELOPE CANDIDATE - NOT SELECTED","missing":"controlled CAD/drawing, T-slot hardware, attachment/anchor design and application acceptance"},
        {"item":"LR-003","manufacturer":"Ruland","order_identity":"MJC33-15-A & JD21/33-92Y & MJS33-15-A","quantity":"1 set","state":"EXACT CATALOG CANDIDATE - NOT SELECTED","missing":"application acceptance, shaft fits, clamp/key strategy, bearing support and proof"},
        {"item":"LR-004","manufacturer":"ROBOTIS","order_identity":"HN12-N101 Set SKU 903-0238-000","quantity":"1","state":"CANDIDATE - NOT SELECTED","missing":"controlled CAD, exact adapter attachment pattern and application acceptance"},
        {"item":"LR-005","manufacturer":"SELECTION REQUIRED","order_identity":"custom HN12-to-15 mm adapter","quantity":"1","state":"NOT DEFINED","missing":"material, geometry, GD&T, fasteners, analysis, FAI and proof"},
        {"item":"LR-006","manufacturer":"SELECTION REQUIRED","order_identity":"HB-450M-2 riser/bracket and PT attachment","quantity":"1 set","state":"NOT DEFINED","missing":"controlled geometry, load path, alignment, analysis, fasteners and proof"},
        {"item":"LR-007","manufacturer":"SELECTION REQUIRED","order_identity":"dedicated current-regulated brake supply/controller","quantity":"1","state":"NOT SELECTED","missing":"range, current limit, isolation, protection, flyback, interlock, fault and thermal behavior"},
        {"item":"LR-008","manufacturer":"SELECTION REQUIRED","order_identity":"complete rotating guard/catch/access interlock","quantity":"1 system","state":"NOT DEFINED","missing":"hazard analysis, geometry, material, retention, access, impact and validation"},
    ])
    write_csv(OUT / "load-capacity-screen.csv", [
        {"screen":"LCS-001","inputs":"HB-450M-2 rated-current minimum torque / X430 12 V stall endpoint","calculation":"3.2 / 4.1","result":"0.780488","authority":"CATALOG COMPARISON ONLY; TEST CURRENT/TORQUE LIMIT SELECTION REQUIRED"},
        {"screen":"LCS-002","inputs":"MJC33 92A rated torque / HB-450M-2 minimum torque","calculation":"3.96 / 3.2","result":"1.237500","authority":"CATALOG COMPARISON ONLY; RULAND APPLICATION ACCEPTANCE REQUIRED"},
        {"screen":"LCS-003","inputs":"MJC33 peak torque / X430 stall endpoint","calculation":"7.9 / 4.1","result":"1.926829","authority":"ACCIDENT SCREEN ONLY; NOT AN OPERATING OR PROOF LIMIT"},
        {"screen":"LCS-004","inputs":"ideal brake power at 3.2 N m and 30 rpm","calculation":"3.2 * 2*pi*30/60","result":f"{3.2*2*math.pi*30/60:.6f} W","authority":"IDEAL DISSIPATION ONLY; DUTY/TEMPERATURE/MOUNTING LIMITS OPEN"},
        {"screen":"LCS-005","inputs":"MJC33 nominal torsional stiffness 2.52 N m/degree at 3.2 N m","calculation":"3.2 / 2.52","result":"1.269841 degree","authority":"CATALOG GUIDANCE ONLY; ANGLE/UNCERTAINTY ALLOCATION OPEN"},
        {"screen":"LCS-006","inputs":"PT series mass 15.07 kg/m at 600 mm","calculation":"15.07 * 0.600","result":"9.042000 kg","authority":"CATALOG MASS SCREEN ONLY; RECEIVED MASS/ANCHOR LOAD OPEN"},
    ])
    write_csv(OUT / "interface-register.csv", [
        {"interface":"LR-IF-01","from":"X430 output / HN12-N101","to":"custom 15 mm shaft adapter","state":"OPEN","missing":"controlled horn CAD, attachment subset, fasteners, fit, torque, retention and proof"},
        {"interface":"LR-IF-02","from":"custom 15 mm shaft adapter","to":"MJC33 input hub","state":"OPEN","missing":"shaft tolerance, clamp/key strategy, axial retention, runout and application acceptance"},
        {"interface":"LR-IF-03","from":"MJC33 output hub","to":"HB-450M-2 15 mm shaft","state":"OPEN","missing":"received shaft dimensions, clamp/key strategy, axial position and proof"},
        {"interface":"LR-IF-04","from":"HB-450M-2 front flange/body","to":"brake riser/PT-600","state":"OPEN","missing":"base-mount identity or designed riser, M5 interface, fasteners, alignment and load proof"},
        {"interface":"LR-IF-05","from":"FUTEK/X430 fixed-side stack","to":"PT-600","state":"OPEN","missing":"horizontal support geometry, T-slot hardware, alignment, reaction load path and proof"},
        {"interface":"LR-IF-06","from":"PT-600","to":"qualified bench/foundation","state":"OPEN","missing":"site survey, support/anchor design, permission, installation and proof"},
    ])
    write_csv(OUT / "alignment-tolerance-register.csv", [
        {"control":"ALI-01","quantity":"X430-to-brake coaxiality","candidate_limit":"SELECTION REQUIRED","evidence":"manufacturer limits, tolerance stack, received metrology and runout test"},
        {"control":"ALI-02","quantity":"coupling shaft fits","candidate_limit":"shaft +0/-0.013 mm; hub bore +0.03/0 mm catalog values","evidence":"Ruland acceptance and received inspection"},
        {"control":"ALI-03","quantity":"axial gap/end float","candidate_limit":"SELECTION REQUIRED","evidence":"brake, coupling and X430 application limits plus assembled inspection"},
        {"control":"ALI-04","quantity":"base/riser parallelism and center height","candidate_limit":"SELECTION REQUIRED","evidence":"released GD&T, FAI and installed alignment record"},
        {"control":"ALI-05","quantity":"extraneous brake/actuator loads","candidate_limit":"SELECTION REQUIRED","evidence":"Magtrol, ROBOTIS and FUTEK written acceptance plus qualified load analysis"},
    ])
    write_csv(OUT / "power-thermal-register.csv", [
        {"control":"PWR-01","subject":"dedicated brake source","state":"SELECTION REQUIRED","missing":"regulated 0..rated-current behavior, isolation, current measurement and fault energy"},
        {"control":"PWR-02","subject":"coil interruption/flyback","state":"SELECTION REQUIRED","missing":"Magtrol-required diode implementation, switching device rating and measured decay"},
        {"control":"PWR-03","subject":"interlock/abort","state":"SELECTION REQUIRED","missing":"safe-state definition, E-stop relationship, contact duty and fault injection"},
        {"control":"PWR-04","subject":"brake temperature","state":"SELECTION REQUIRED","missing":"sensor, placement, uncertainty, limit, dwell/cooldown and mounting derating"},
        {"control":"PWR-05","subject":"regenerated/mechanical energy","state":"SELECTION REQUIRED","missing":"four-quadrant behavior, actuator source absorption and shutdown transient evidence"},
        {"control":"PWR-06","subject":"robot 24 V rail separation","state":"REQUIRED","missing":"schematic proof that the brake supply is not carried by the robot 24 V control rail"},
    ])
    rfis = [
        ("LR-RFI-01","Magtrol applications","Confirm HB-450M-2 for low-speed bidirectional X430 characterization; provide coil/order identity, rated-current tolerance, thermal derating, bearing/extraneous-load limits and acceptance conditions."),
        ("LR-RFI-02","Magtrol applications","Provide controlled PT-600 CAD/drawing, slot/hardware definition and acceptable brake mounting route."),
        ("LR-RFI-03","Magtrol applications","State whether a metric base-mounted HB-450M-2 special exists and provide its exact identity, shaft, performance and CAD."),
        ("LR-RFI-04","Ruland applications","Accept or correct MJC33 15×15 92A for the proposed brake/X430 spectrum, reversals, starts/stops, fits, clamp strategy and bearing support."),
        ("LR-RFI-05","ROBOTIS applications","Provide controlled HN12-N101 CAD and accept or correct a rigid adapter for guarded low-speed external brake characterization."),
        ("LR-RFI-06","FUTEK applications","Review the horizontal common-bed reaction-torque configuration, alignment/extraneous-load limits and calibration route."),
        ("LR-RFI-07","candidate machine shop","DFM-review the output adapter and brake riser after controlled vendor interfaces arrive; no quote or machining authorized."),
        ("LR-RFI-08","qualified mechanical/electrical reviewer and facility","Review the full drivetrain, support, guard, brake control, thermal, interruption and site load path before powered-work authorization."),
    ]
    write_csv(OUT / "vendor-rfi.csv", [{"rfi":i,"recipient":r,"question":q,"state":"NOT SENT"} for i,r,q in rfis])
    holds = ["controlled HN12 output-interface CAD/application acceptance","custom output-adapter material/GD&T/fastener/analysis/FAI/proof","Magtrol brake application/coil/order identity","brake base-mount or riser exact configuration and proof","PT-600 controlled CAD/T-slot hardware/attachment","coupling application/shaft fits/retention/proof","coaxial alignment/runout/end-float closure","FUTEK interface/axis/application/calibration closure","brake current-regulated supply/flyback/protection","instrumentation/calibration/temperature/duty limits","common-bed support/anchor/Boston site survey","complete rotating guard/catch/access prevention","configured FR12-H101 horizontal gravity-equivalence test","qualified powered-work and energization authorization"]
    write_csv(OUT / "open-hold-register.csv", [{"hold_id":f"LR-HOLD-{i:02d}","missing_evidence":h,"state":"OPEN","effect":"BLOCKS PROCUREMENT/MACHINING/ASSEMBLY/CONNECTION/POWERED TEST/MOTION/ENERGIZATION"} for i,h in enumerate(holds,1)])
    write_csv(OUT / "source-register.csv", [
        {"source":"LR-SRC-001","organization":"Magtrol","record":"HB/MHB hysteresis brake datasheet","revision_date":"©2025; accessed 2026-08-08","locator":"https://www.magtrol.com/wp-content/uploads/hb-mhb.pdf","local_sha256":"NOT DOWNLOADED","use":"HB-450M-2 torque/current/power/speed/thermal/flyback boundary"},
        {"source":"LR-SRC-002","organization":"Magtrol","record":"HB-450M installation drawing Rev A","revision_date":"Rev A, 2004-01-29; accessed 2026-08-08","locator":"https://www.magtrol.com/wp-content/uploads/hb-450m.pdf","local_sha256":"B60AE3A2B5E4CB18BA8F9875AD1C44B6AD78002DC2E2E880331C67FFE1FEB77F","use":"metric shaft and mounting interface; local PDF is drawing only"},
        {"source":"LR-SRC-003","organization":"Magtrol","record":"HB-450M_B_EF STEP","revision_date":"downloaded 2026-08-08; publisher revision not exposed","locator":"https://www.magtrol.com/product/hysteresis-brakes/","local_sha256":"2EE1136C6CA3B2202A13BC11DEA1A18EEB9D261B7E7D776EE940699C7F89EDE1","use":"exact vendor review geometry; placement provisional"},
        {"source":"LR-SRC-004","organization":"Magtrol","record":"PT Series T-slot base plates PT25","revision_date":"US 02/2022; accessed 2026-08-08","locator":"https://www.magtrol.com/wp-content/uploads/pt25.pdf","local_sha256":sha256(PT_SOURCE / "PT-series-US-02-2022.pdf"),"use":"PT-600 corrected 600 x 375 x 20 mm envelope, profile, pitch, mass and product identity; countersunk holes omitted"},
        {"source":"LR-SRC-005","organization":"Ruland","record":"MJC33-15-A / JD21/33-92Y / MJS33-15-A","revision_date":"live product page accessed 2026-08-08","locator":"https://www.ruland.com/mjc33-15-a-jd21-33-92y-mjs33-15-a.html","local_sha256":"NOT DOWNLOADED","use":"coupling envelope, torque, stiffness, speed and fit boundary"},
        {"source":"LR-SRC-006","organization":"ROBOTIS","record":"HN12-N101 Set","revision_date":"live product page accessed 2026-08-08","locator":"https://www.robotis.us/hn12-n101-set/","local_sha256":"NOT DOWNLOADED","use":"candidate identity/compatibility only"},
    ])
    status = {"identifier":IDENTIFIER,"preferred_route":"LOAD-A","open_hold_count":len(holds),"rfi_count":len(rfis),"rfi_state":"NOT SENT","pt_body_cad_present":False,"output_adapter_fabrication_geometry_present":False,"configured_h101_test_still_required":True,"robot_24v_brake_supply_allowed":False,"release_flags":{k:False for k in ("quotation","procurement","machining","assembly","connection","powered_test","motion","energization","safety_credit","build_release")},"warning":WARNING}
    (OUT / "package-status.json").write_text(json.dumps(status,indent=2)+"\n",encoding="utf-8")
    print(f"generated {IDENTIFIER}: 4 routes, {len(rfis)} unsent RFIs, {len(holds)} open holds, all release flags false")
    return 0


if __name__ == "__main__": raise SystemExit(main())
