"""Generate the HR-V0 X430 duty-fixture P0.1 review candidate.

The package is a dimensioned topology and evidence-route candidate.  It is
deliberately not a fabrication drawing, fixture release, powered-test release,
or energization authorization.  Vendor sensor geometry is a drawing-derived
envelope, not a manufacturer CAD model.
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


IDENTIFIER = "HR-V0-X430-FIXTURE-P0.1"
WARNING = (
    "PRELIMINARY - DIMENSIONED REVIEW CANDIDATE ONLY - NOT APPROVED FOR "
    "QUOTATION, PROCUREMENT, FABRICATION, ASSEMBLY, POWERED TEST, MOTION, "
    "CONNECTION, OR ENERGIZATION"
)
OUT = ROOT / "test-fixtures" / "hr-v0" / "x430-duty-fixture-p0.1"
WEB = ROOT / "release" / "hr-v0" / "x430-duty-fixture-p0.1"
VENDOR = ROOT / "cad" / "vendor" / "robotis" / "x430-fr12-r91"

# Millimetres.  These are topology controls, not released part dimensions.
BASE_X = 400.0
BASE_Y = 600.0
BASE_T = 12.7
UPRIGHT_X = 12.7
UPRIGHT_Y = 300.0
UPRIGHT_Z = 300.0
UPRIGHT_ACTIVE_FACE_X = -90.0
JOINT_Z = 180.0
TFF_LENGTH = 50.8
TFF_OD = 50.2
TFF_ID = 16.8
TFF_BCD = 31.75
TFF_FIXED_X = UPRIGHT_ACTIVE_FACE_X
TFF_ACTIVE_X = TFF_FIXED_X + TFF_LENGTH
ADAPTER_FLANGE_T = 9.2
S102_LEFT_FACE_X = -18.5
LOAD_ARM_Y0 = 28.0
LOAD_ARM_LENGTH = 160.0
LOAD_ARM_SECTION = 20.0
STATIC_FORCE_ARM = 100.0
TFF_CAPACITY_NM = 11.0
TFF_SAFE_OVERLOAD_MULTIPLIER = 1.5
X430_STALL_ENDPOINT_NM = 4.1
X430_STALL_ENDPOINT_A = 2.3
P11_INCOMPLETE_SCREEN_NM = 1.087329823
LSB205_CAPACITY_N = 111.0


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        raise ValueError(f"refusing to write empty CSV: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def cylinder_x(radius: float, length: float, x0: float, y: float, z: float) -> cq.Shape:
    return cq.Solid.makeCylinder(radius, length, cq.Vector(x0, y, z), cq.Vector(1, 0, 0))


def tff400_envelope() -> cq.Shape:
    body = cylinder_x(TFF_OD / 2.0, TFF_LENGTH, TFF_FIXED_X, 0, JOINT_Z)
    bore = cylinder_x(TFF_ID / 2.0, TFF_LENGTH, TFF_FIXED_X, 0, JOINT_Z)
    return body.cut(bore)


def active_adapter_envelope() -> cq.Shape:
    """Review envelope with a flange and two upper bridges.

    No hole diameter, thread, counterbore, tolerance, material or fastener is
    represented.  Small axis cylinders are separate nonphysical datum markers.
    """

    x0 = TFF_ACTIVE_X
    flange = cq.Solid.makeBox(
        ADAPTER_FLANGE_T, 70.0, 70.0, cq.Vector(x0, -35.0, JOINT_Z - 35.0)
    )
    bridge_x0 = x0 + ADAPTER_FLANGE_T
    bridge_l = -24.0 - bridge_x0
    bridge_a = cq.Solid.makeBox(
        bridge_l, 10.0, 32.0, cq.Vector(bridge_x0, -16.0, JOINT_Z + 10.0)
    )
    bridge_b = cq.Solid.makeBox(
        bridge_l, 10.0, 32.0, cq.Vector(bridge_x0, 6.0, JOINT_Z + 10.0)
    )
    boss_l = S102_LEFT_FACE_X - (-24.0)
    boss_a = cylinder_x(5.0, boss_l, -24.0, -11.0, JOINT_Z + 32.0)
    boss_b = cylinder_x(5.0, boss_l, -24.0, 11.0, JOINT_Z + 32.0)
    return flange.fuse(bridge_a).fuse(bridge_b).fuse(boss_a).fuse(boss_b)


def axis_markers() -> dict[str, cq.Shape]:
    markers: dict[str, cq.Shape] = {}
    radius = TFF_BCD / 2.0
    for index, (y, z) in enumerate(((radius, 0), (-radius, 0), (0, radius), (0, -radius)), 1):
        markers[f"DATUM_TFF_AXIS_{index}_NO_HOLE_SIZE"] = cylinder_x(
            0.65, 2.0, TFF_FIXED_X - 1.0, y, JOINT_Z + z
        )
    for index, y in enumerate((-11.0, 11.0), 1):
        markers[f"DATUM_S102_AXIS_{index}_NO_HOLE_SIZE"] = cylinder_x(
            0.65, 3.0, S102_LEFT_FACE_X - 1.5, y, JOINT_Z + 32.0
        )
    return markers


def drawing_svg(path: Path) -> None:
    path.write_text(
        f'''<svg xmlns="http://www.w3.org/2000/svg" width="1600" height="1050" viewBox="0 0 1600 1050" style="max-width:100%;height:auto">
<style>
text{{font-family:Arial,sans-serif;fill:#102a43;font-size:22px}}.h{{font-size:38px;font-weight:700;fill:#082b55}}.s{{font-size:18px}}.w{{font-size:20px;font-weight:700;fill:#8b1e1e}}.p{{stroke:#082b55;stroke-width:3;fill:#e4f6ff}}.v{{stroke:#0b63a3;stroke-width:3;fill:#7dd3fc}}.c{{stroke:#8a5b00;stroke-width:3;fill:#f4b942}}.d{{stroke:#102a43;stroke-width:2;fill:none;marker-start:url(#a);marker-end:url(#a)}}.x{{stroke:#9b1c1c;stroke-width:3;stroke-dasharray:10 8;fill:none}}
</style><defs><marker id="a" markerWidth="8" markerHeight="8" refX="4" refY="4" orient="auto"><path d="M0,4 L8,0 L8,8 Z" fill="#102a43"/></marker></defs>
<rect width="1600" height="1050" fill="#f7fbff"/><text x="55" y="62" class="h">{IDENTIFIER} · dimensioned topology review</text>
<text x="55" y="100" class="w">PRELIMINARY - DIMENSIONED REVIEW CANDIDATE ONLY - NOT APPROVED FOR QUOTATION, PROCUREMENT, FABRICATION,</text>
<text x="55" y="130" class="w">ASSEMBLY, POWERED TEST, MOTION, CONNECTION, OR ENERGIZATION</text>
<text x="70" y="180" class="h">Side view · joint axis projects out of page</text>
<rect x="95" y="790" width="900" height="32" class="p"/><rect x="250" y="280" width="30" height="510" class="p"/>
<rect x="280" y="440" width="142" height="140" rx="68" class="c"/><rect x="422" y="420" width="58" height="180" class="c"/>
<rect x="480" y="470" width="100" height="100" class="v"/><circle cx="580" cy="520" r="55" class="v"/>
<rect x="580" y="500" width="360" height="40" class="p"/><rect x="920" y="470" width="70" height="100" class="c"/>
<line x1="580" y1="250" x2="580" y2="830" class="x"/><line x1="60" y1="520" x2="1020" y2="520" class="x"/>
<line x1="95" y1="875" x2="995" y2="875" class="d"/><text x="430" y="912">600 mm base depth</text>
<line x1="208" y1="280" x2="208" y2="790" class="d"/><text x="70" y="550" transform="rotate(-90 70 550)">300 mm upright above base</text>
<line x1="1040" y1="520" x2="1040" y2="790" class="d"/><text x="1060" y="665">167.3 mm axis above base top</text>
<line x1="280" y1="385" x2="422" y2="385" class="d"/><text x="305" y="365">50.8 mm TFF400 envelope</text>
<text x="70" y="965" class="s">Blue: exact ROBOTIS source geometry / fixture arm envelope. Gold: drawing-derived sensor and unresolved custom interfaces.</text>
<text x="70" y="1000" class="w">No fastener holes, tolerances, anchor pattern, catch, guard access closure, load device or cable path is released.</text>
<text x="1080" y="180" style="font-size:32px;font-weight:700;fill:#082b55">Controlled review dimensions</text>
<text x="1110" y="220">Base: 400 × 600 × 12.7 mm</text><text x="1110" y="260">Upright: 12.7 × 300 × 300 mm</text>
<text x="1110" y="300">Joint axis: Z = 180 mm</text><text x="1110" y="340">TFF400: Ø50.2 × 50.8 mm</text>
<text x="1110" y="380">TFF bore: Ø16.8 mm</text><text x="1110" y="420">TFF axes: 4 × BCD 31.75 mm</text>
<text x="1110" y="460">Load arm: 160 mm × 20 mm square</text><text x="1110" y="500">Static cross-check arm: 100 mm</text>
<text x="1110" y="555" class="w">All are candidate topology controls.</text><text x="1110" y="590" class="w">Fabrication dimensions: SELECTION REQUIRED.</text>
</svg>''',
        encoding="utf-8",
        newline="\n",
    )


def html_guide(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>HR-V0 X430 duty fixture</title><script type="module" src="https://ajax.googleapis.com/ajax/libs/model-viewer/4.1.0/model-viewer.min.js"></script><style>
:root{{--deep:#041a35;--navy:#082b55;--sky:#7dd3fc;--pale:#e4f6ff;--gold:#f4b942;--ink:#102a43;--paper:#f7fbff;--line:#afd5e9;--red:#8b1e1e}}*{{box-sizing:border-box}}body{{margin:0;background:var(--paper);color:var(--ink);font:17px/1.55 system-ui,-apple-system,"Segoe UI",sans-serif}}header{{background:linear-gradient(135deg,var(--deep),var(--navy));color:#fff;padding:clamp(30px,6vw,76px) 20px}}header>div,main{{max-width:1180px;margin:auto}}h1{{font-size:clamp(34px,6vw,66px);line-height:1.05;margin:.3rem 0 1rem}}h2{{font-size:clamp(26px,3vw,38px);line-height:1.2;color:var(--navy);margin-top:2rem}}p,li{{max-width:78ch}}.eyebrow,.tag{{font-size:13px;font-weight:850;letter-spacing:.055em;text-transform:uppercase}}.eyebrow{{color:var(--sky)}}.warning{{background:var(--gold);color:#17243a;border:3px solid #8a5b00;padding:15px 18px;font-weight:850}}main{{padding:28px 20px 80px}}.decision{{background:#fff;border-left:9px solid var(--gold);padding:22px;box-shadow:0 6px 22px #082b5514}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(245px,1fr));gap:18px}}.card{{background:#fff;border:2px solid var(--line);border-radius:16px;padding:20px}}.card strong{{display:block;font-size:clamp(25px,4vw,40px);line-height:1.1;color:var(--navy)}}.tag{{display:inline-block;padding:5px 9px;border-radius:999px;background:var(--pale);color:var(--navy)}}.viewer{{background:#dff3ff;border:3px solid var(--navy);border-radius:18px;overflow:hidden}}model-viewer{{width:100%;height:clamp(460px,70vh,760px);background:radial-gradient(circle at 50% 42%,#fff 0,#dff3ff 62%,#a8d7ef 100%)}}.viewer-note{{padding:14px 18px;background:#fff;margin:0;max-width:none}}.table-wrap{{overflow:auto;border:2px solid var(--line);border-radius:12px;background:#fff}}table{{border-collapse:collapse;width:100%;min-width:820px}}th,td{{text-align:left;vertical-align:top;padding:13px;border-bottom:1px solid var(--line);font-size:16px}}th{{background:var(--navy);color:#fff}}.hold{{color:var(--red);font-weight:850}}.links a{{display:inline-block;margin:5px 14px 5px 0;color:#075b9b;font-weight:750}}footer{{background:var(--deep);color:#fff;padding:30px 20px}}footer p{{max-width:1180px;margin:auto}}@media(max-width:720px){{body{{font-size:16px}}main{{padding-inline:14px}}.card{{padding:16px}}model-viewer{{height:470px}}}}
</style></head><body><header><div><div class="eyebrow">{IDENTIFIER} · R99</div><h1>A real fixture topology—still not a fixture release.</h1><div class="warning">{WARNING}</div></div></header><main>
<section class="decision"><h2>Decision</h2><p>A stationary reaction-torque sensor is the preferred evidence route because it can observe torque throughout a motion profile without promoting motor current into torque evidence. FUTEK TFF400 item FSH04015 is an exact <em>evaluation candidate</em>, not selected hardware. The custom fixed/active adapters, structural joins, guard, catch, anchor, load device and every powered limit remain unresolved.</p></section>
<section><h2>Inspect the nominal topology</h2><div class="viewer"><model-viewer src="../../../test-fixtures/hr-v0/x430-duty-fixture-p0.1/HR-V0_X430_duty_fixture_P0.1_review.glb" alt="Interactive 3D model of the preliminary X430 reaction-torque test fixture topology" camera-controls camera-orbit="38deg 66deg 90%" min-camera-orbit="auto auto 28%" max-camera-orbit="auto auto 320%" field-of-view="28deg" touch-action="pan-y" shadow-intensity="0.8" exposure="1.05"></model-viewer><p class="viewer-note">Drag to orbit; scroll or pinch to zoom. Gold parts are drawing-derived or custom-interface envelopes. Datum markers are not holes. The model is not an assembly instruction.</p></div></section>
<section><h2>Why this sensor range</h2><div class="grid"><article class="card"><span class="tag">Candidate range</span><strong>11 N·m</strong><p>FSH04015 catalog capacity. It is not a project allowable.</p></article><article class="card"><span class="tag">Stall endpoint</span><strong>4.1 N·m</strong><p>ROBOTIS 12 V stall endpoint, not continuous torque.</p></article><article class="card"><span class="tag">Capacity ratio only</span><strong>{TFF_CAPACITY_NM / X430_STALL_ENDPOINT_NM:.3f}×</strong><p>Arithmetic screen only; shock, fixture dynamics and uncertainty are unresolved.</p></article></div></section>
<section><h2>Load path</h2><div class="table-wrap"><table><thead><tr><th>Segment</th><th>Nominal interface</th><th>What remains open</th></tr></thead><tbody><tr><td>Base → upright</td><td>400 × 600 × 12.7 / 12.7 × 300 × 300 mm envelopes</td><td>Material, join, anchor, deflection, proof</td></tr><tr><td>Upright → TFF400 fixed flange</td><td>4 axes on 31.75 mm BCD</td><td>Hole finish, #8-32 stack, torque, pilot fit, access</td></tr><tr><td>TFF400 active flange → S102</td><td>Custom upper bridge to exact Y=±11, Z=32 axes</td><td>Vendor application approval, detail design, stiffness, interference, FAI</td></tr><tr><td>H101 → load arm</td><td>160 mm envelope</td><td>Adapter, load device, retention, inertia, balance, stop/catch</td></tr></tbody></table></div></section>
<section><h2>Instrumentation candidates</h2><div class="grid"><article class="card"><strong>TFF400 FSH04015</strong><p>Primary reaction-torque candidate. CW+CCW system calibration must be quoted and accepted.</p></article><article class="card"><strong>IAA100 FSH04461</strong><p>Conditioner candidate. Gain, excitation, bandwidth, power, chassis/shield and exact cable remain selection items.</p></article><article class="card"><strong>LabJack T7</strong><p>DAQ candidate. Differential pairing, range, scan list, settling and synchronization remain selection items.</p></article><article class="card"><strong>JS220-K000</strong><p>Branch current/voltage candidate only if the accepted source and transients remain inside its limits and timing is reconciled.</p></article></div></section>
<section><h2>Fourteen holds prevent build or use</h2><p class="hold">The geometry does not close DUTY-HOLD-08.</p><p>Vendor application confirmation; sensor and calibration option; fixed adapter; active adapter; material/fasteners/tolerances; structural calculation; bench/anchor; independent catch; full guard/access closure; controlled load device; cable/thermal routing; acquisition/synchronization/uncertainty; overload/abort/reverse-energy controls; and qualified review plus powered-work authorization.</p></section>
<section><h2>Controlled evidence</h2><p class="links"><a href="../../../docs/hr-v0-x430-duty-fixture-p0.1.md">Design record</a><a href="../../../test-fixtures/hr-v0/x430-duty-fixture-p0.1/dimensioned-topology-review.svg">Readable drawing</a><a href="../../../test-fixtures/hr-v0/x430-duty-fixture-p0.1/topology-trade.csv">Topology trade</a><a href="../../../test-fixtures/hr-v0/x430-duty-fixture-p0.1/interface-register.csv">Interface register</a><a href="../../../test-fixtures/hr-v0/x430-duty-fixture-p0.1/open-hold-register.csv">Open holds</a></p></section>
</main><footer><p>{WARNING}. Passing repository checks proves only internal consistency and fail-closed status.</p></footer></body></html>''',
        encoding="utf-8",
        newline="\n",
    )


def main() -> int:
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)
    if WEB.exists():
        shutil.rmtree(WEB)
    WEB.mkdir(parents=True)

    x_raw = cq.importers.importStep(str(VENDOR / "x-430_idle.stp")).val()
    s_raw = cq.importers.importStep(str(VENDOR / "fr12_s102.stp")).val()
    h_raw = cq.importers.importStep(str(VENDOR / "fr12_h101.stp")).val()
    x430 = x430_arch.x430_to_joint_frame(x_raw).translate((0, 0, JOINT_Z))
    s102 = s_raw.translate((0, 0, x430_arch.S102_LOCAL_Z_SHIFT + JOINT_Z))
    h101 = h_raw.translate((0, 0, JOINT_Z))

    base = cq.Solid.makeBox(BASE_X, BASE_Y, BASE_T, cq.Vector(-BASE_X / 2, -BASE_Y / 2, 0))
    upright = cq.Solid.makeBox(
        UPRIGHT_X, UPRIGHT_Y, UPRIGHT_Z,
        cq.Vector(UPRIGHT_ACTIVE_FACE_X - UPRIGHT_X, -UPRIGHT_Y / 2, BASE_T),
    )
    tff = tff400_envelope()
    adapter = active_adapter_envelope()
    load_arm = cq.Solid.makeBox(
        LOAD_ARM_SECTION, LOAD_ARM_LENGTH, LOAD_ARM_SECTION,
        cq.Vector(-LOAD_ARM_SECTION / 2, LOAD_ARM_Y0, JOINT_Z - LOAD_ARM_SECTION / 2),
    )
    load_block = cq.Solid.makeBox(40, 40, 60, cq.Vector(-20, LOAD_ARM_Y0 + LOAD_ARM_LENGTH, JOINT_Z - 30))
    components = {
        "BASE_ENVELOPE_NO_ANCHOR_PATTERN": base,
        "UPRIGHT_ENVELOPE_NO_JOIN_PATTERN": upright,
        "TFF400_FSH04015_DRAWING_DERIVED_ENVELOPE": tff,
        "CUSTOM_ACTIVE_ADAPTER_ENVELOPE_SELECTION_REQUIRED": adapter,
        "X430_EXACT_VENDOR_GEOMETRY": x430,
        "FR12_S102_EXACT_VENDOR_GEOMETRY": s102,
        "FR12_H101_EXACT_VENDOR_GEOMETRY": h101,
        "LOAD_ARM_ENVELOPE_SELECTION_REQUIRED": load_arm,
        "LOAD_DEVICE_ENVELOPE_SELECTION_REQUIRED": load_block,
        **axis_markers(),
    }
    assembly = cq.Assembly(name="HR_V0_X430_DUTY_FIXTURE_P01_REVIEW_ONLY")
    for name, shape in components.items():
        if name.startswith("DATUM"):
            color = cq.Color(0.72, 0.12, 0.12)
        elif "TFF400" in name or "CUSTOM" in name or "LOAD_DEVICE" in name:
            color = cq.Color(0.96, 0.70, 0.12)
        elif "EXACT_VENDOR" in name:
            color = cq.Color(0.12, 0.45, 0.75)
        else:
            color = cq.Color(0.10, 0.25, 0.43)
        assembly.add(shape, name=name, color=color)
    step_path = OUT / "HR-V0_X430_duty_fixture_P0.1_review.step"
    cq.exporters.export(cq.Compound.makeCompound(list(components.values())), str(step_path))
    arm_base.canonicalize_step(step_path)
    assembly.save(str(OUT / "HR-V0_X430_duty_fixture_P0.1_review.glb"))
    drawing_svg(OUT / "dimensioned-topology-review.svg")
    html_guide(WEB / "index.html")

    write_csv(OUT / "geometry-control.csv", [
        {"control_id": "FXG-001", "quantity": "base envelope X/Y/T", "value_mm": "400/600/12.7", "evidence": "topology allocation", "release_state": "CANDIDATE ONLY; MATERIAL/ANCHOR/JOIN/TOLERANCE SELECTION REQUIRED"},
        {"control_id": "FXG-002", "quantity": "upright envelope X/Y/Z", "value_mm": "12.7/300/300", "evidence": "topology allocation", "release_state": "CANDIDATE ONLY; MATERIAL/JOIN/TOLERANCE/DEFLECTION PROOF REQUIRED"},
        {"control_id": "FXG-003", "quantity": "joint axis above base datum", "value_mm": "180.0", "evidence": "model datum; 167.3 above base top", "release_state": "CANDIDATE ONLY"},
        {"control_id": "FXG-004", "quantity": "TFF400 envelope OD/ID/length", "value_mm": "50.2/16.8/50.8", "evidence": "FUTEK FI1251-F drawing-derived", "release_state": "ENVELOPE ONLY; RECEIVED INSPECTION REQUIRED"},
        {"control_id": "FXG-005", "quantity": "TFF400 interface axes", "value_mm": "4 axes on BCD 31.75, both ends", "evidence": "FUTEK FI1251-F", "release_state": "AXES ONLY; HOLE/THREAD/FASTENER/ENGAGEMENT SELECTION REQUIRED"},
        {"control_id": "FXG-006", "quantity": "FR12-S102 candidate axes", "value_mm": "Y=+/-11, Z=32 relative to J2", "evidence": "controlled exact ROBOTIS STEP axes", "release_state": "EXACT NOMINAL AXES; RECEIVED FIT/FASTENER/FAI OPEN"},
        {"control_id": "FXG-007", "quantity": "fixture load-arm envelope", "value_mm": "20 square x 160; start Y=28", "evidence": "topology allocation", "release_state": "NOT P1.1 HARDWARE; LOAD DEVICE/ADAPTER/INERTIA/RETENTION SELECTION REQUIRED"},
        {"control_id": "FXG-008", "quantity": "static cross-check perpendicular arm", "value_mm": "100.0", "evidence": "calculation datum only", "release_state": "AS-BUILT METROLOGY/UNCERTAINTY/ALIGNMENT REQUIRED"},
    ])

    write_csv(OUT / "topology-trade.csv", [
        {"option": "TOP-A", "topology": "TFF400 FSH04015 stationary reaction torque in fixed-case load path", "evidence_strength": "continuous external reaction-torque channel", "limitations": "custom fixed/active interfaces; reaction includes drive dynamics; output-torque interpretation and system calibration required", "disposition": "PREFERRED EVALUATION CANDIDATE - NOT SELECTED"},
        {"option": "TOP-B", "topology": "LSB205 FSH04097 tangential force at measured 100 mm arm", "evidence_strength": "independent static/cyclic force cross-check", "limitations": "line-of-action, changing tangent geometry, off-axis load, arm deflection and exact cable/conditioner unresolved", "disposition": "RETAIN AS STATIC CROSS-CHECK CANDIDATE - NOT SELECTED"},
        {"option": "TOP-C", "topology": "motor current / DYNAMIXEL telemetry only", "evidence_strength": "supplemental correlation", "limitations": "cannot establish external torque or continuous rating", "disposition": "REJECT AS PRIMARY TORQUE EVIDENCE"},
        {"option": "TOP-D", "topology": "human-held scale, strap or applied force", "evidence_strength": "none acceptable", "limitations": "person enters stored-energy and sweep hazard", "disposition": "PROHIBITED TEST METHOD"},
    ])

    write_csv(OUT / "load-path-screen.csv", [
        {"screen_id": "LPS-001", "input": "XM430 12 V stall endpoint", "input_value": "4.1 N m", "comparison": "TFF400 FSH04015 catalog capacity 11 N m", "result": f"capacity/endpoint={TFF_CAPACITY_NM / X430_STALL_ENDPOINT_NM:.6f}", "authority": "ARITHMETIC SCREEN ONLY; NEITHER CONTINUOUS RATING NOR FIXTURE ALLOWABLE"},
        {"screen_id": "LPS-002", "input": "TFF400 150% published safe overload", "input_value": "16.5 N m", "comparison": "XM430 12 V stall endpoint 4.1 N m", "result": f"safe-overload/endpoint={TFF_CAPACITY_NM * TFF_SAFE_OVERLOAD_MULTIPLIER / X430_STALL_ENDPOINT_NM:.6f}", "authority": "DO NOT USE AS OPERATING LIMIT; IMPACT/DYNAMICS/UNCERTAINTY/PROTECTION OPEN"},
        {"screen_id": "LPS-003", "input": "P1.1 incomplete 2.25x gravity screen", "input_value": f"{P11_INCOMPLETE_SCREEN_NM:.9f} N m", "comparison": "TFF400 catalog capacity 11 N m", "result": f"capacity/incomplete-screen={TFF_CAPACITY_NM / P11_INCOMPLETE_SCREEN_NM:.6f}", "authority": "INCOMPLETE LOAD MODEL; NOT A REQUIREMENT OR CAPACITY PROOF"},
        {"screen_id": "LPS-004", "input": "LSB205 FSH04097 capacity", "input_value": "111 N", "comparison": "100 mm perpendicular arm", "result": f"nominal moment={LSB205_CAPACITY_N * STATIC_FORCE_ARM / 1000:.6f} N m", "authority": "IDEAL GEOMETRY ONLY; OFF-AXIS/ARM/FASTENER/SENSOR OVERLOAD OPEN"},
        {"screen_id": "LPS-005", "input": "XM430 stall endpoint current", "input_value": "2.3 A at 12 V", "comparison": "JS220 published 3 A continuous range", "result": f"current ratio={3.0 / X430_STALL_ENDPOINT_A:.6f}", "authority": "RANGE SCREEN ONLY; SOURCE TRANSIENTS/REGEN/PULSE DUTY/PROTECTION/TIMING OPEN"},
    ])

    write_csv(OUT / "interface-register.csv", [
        {"interface_id": "FXI-001", "from": "site bench", "to": "candidate base", "controlled_datum": "base envelope only", "unresolved": "site permission, substrate, exact anchor, edge distance, installation, proof", "state": "OPEN"},
        {"interface_id": "FXI-002", "from": "candidate base", "to": "candidate upright", "controlled_datum": "orthogonal touching envelopes", "unresolved": "material, weld/bolt topology, features, tolerance, stiffness, proof", "state": "OPEN"},
        {"interface_id": "FXI-003", "from": "upright", "to": "TFF400 fixed end", "controlled_datum": "J2 axis; four axes on 31.75 mm BCD", "unresolved": "pilot, holes, #8-32 screw selection/engagement/torque/locking/access", "state": "OPEN"},
        {"interface_id": "FXI-004", "from": "TFF400 active end", "to": "custom active adapter", "controlled_datum": "J2 axis; four axes on 31.75 mm BCD", "unresolved": "FUTEK application approval, pilot, holes, fastener stack, stiffness", "state": "OPEN"},
        {"interface_id": "FXI-005", "from": "custom active adapter", "to": "FR12-S102/X430 fixed assembly", "controlled_datum": "Y=+/-11 Z=32 exact nominal axes", "unresolved": "detailed part, collision/tolerance, fastener, received fit, FAI, proof", "state": "OPEN"},
        {"interface_id": "FXI-006", "from": "FR12-H101 moving frame", "to": "fixture load arm", "controlled_datum": "straight reference at J2", "unresolved": "adapter, holes, fastener stack, balance, inertia, proof", "state": "OPEN"},
        {"interface_id": "FXI-007", "from": "load arm", "to": "controlled load device", "controlled_datum": "160 mm envelope only", "unresolved": "brake/mass/spring topology, retention, load profile, fail-safe behavior", "state": "OPEN"},
        {"interface_id": "FXI-008", "from": "TFF400", "to": "IAA100", "controlled_datum": "4-wire bridge functions only", "unresolved": "exact CC4 cable/order code, shield/chassis, calibration configuration", "state": "OPEN"},
        {"interface_id": "FXI-009", "from": "IAA100", "to": "LabJack T7", "controlled_datum": "candidate differential voltage path", "unresolved": "range, gain, span, bandwidth, common mode, pin/terminal, settling", "state": "OPEN"},
        {"interface_id": "FXI-010", "from": "actuator branch", "to": "JS220-K000", "controlled_datum": "series current/parallel voltage concept", "unresolved": "source/transient limits, connector/wire, protection, regen, burden, timing", "state": "OPEN"},
        {"interface_id": "FXI-011", "from": "actuator/connector/cable surfaces", "to": "temperature acquisition", "controlled_datum": "three retained surface channels", "unresolved": "exact sensors/order codes, placement, CJC, retention, insulation bias", "state": "OPEN"},
        {"interface_id": "FXI-012", "from": "fixture volume", "to": "guard/catch/access system", "controlled_datum": "none released", "unresolved": "full swept volume, access closure, catch, impact, retention, cable entry, proof", "state": "OPEN"},
    ])

    write_csv(OUT / "instrument-candidate-register.csv", [
        {"item": "FSH04015", "manufacturer_model": "FUTEK TFF400 100 in-lb / 11 N m reaction torque sensor", "role": "primary reaction torque", "verified_fact": "2 mV/V nominal; 10 V calibration excitation; 150% safe overload for 100-500 in-lb family; IP40", "selection_needed": "vendor application confirmation, exact CW+CCW calibration, cable, received certificate and serial", "state": "EXACT EVALUATION CANDIDATE - NOT SELECTED"},
        {"item": "FSH04461", "manufacturer_model": "FUTEK IAA100", "role": "strain-gauge conditioning", "verified_fact": "+/-5 or +/-10 V; 5/10 V excitation; 1/10/25 kHz; 12-30 VDC; 1.2 A max inrush", "selection_needed": "gain/span/excitation/bandwidth/power/shield configuration and compatibility review", "state": "EXACT EVALUATION CANDIDATE - NOT SELECTED"},
        {"item": "T7", "manufacturer_model": "LabJack T7", "role": "external analog/digital acquisition", "verified_fact": "14 AIN / 7 adjacent differential pairs; +/-10/1/0.1/0.01 V; 100 ksample/s maximum stream", "selection_needed": "exact scan/range/rate/settling/common-mode/synchronization/calibration", "state": "EVALUATION CANDIDATE - NOT SELECTED"},
        {"item": "JS220-K000", "manufacturer_model": "Joulescope JS220", "role": "actuator-branch current and voltage", "verified_fact": "+/-15 V class range; +/-3 A continuous; 10 A pulses; simultaneous 2 MS/s channels", "selection_needed": "accepted source/transient envelope, exact connection, timing correlation, calibration option", "state": "EXACT EVALUATION CANDIDATE - NOT SELECTED"},
        {"item": "FSH04097", "manufacturer_model": "FUTEK LSB205 25 lb / 111 N", "role": "static 100 mm force-arm cross-check", "verified_fact": "2 mV/V nominal; 10 V max excitation; M3x0.5; 1000% safe overload for 1-25 lb family", "selection_needed": "tension+compression/system calibration, CC18 cable, line of action, arm and off-axis review", "state": "EXACT EVALUATION CANDIDATE - NOT SELECTED"},
        {"item": "SELECTION REQUIRED", "manufacturer_model": "OMEGA SA1-K family or qualified alternative", "role": "surface temperature", "verified_fact": "M0503/0417: 19x25x0.3 mm pad; 30 AWG PFA; one-time adhesive placement", "selection_needed": "exact order code/length/termination, CJC chain, placement, retention, uncertainty", "state": "SELECTION REQUIRED"},
    ])

    write_csv(OUT / "open-hold-register.csv", [
        {"hold_id": f"FXH-{i:02d}", "closure_needed": text, "state": "OPEN"}
        for i, text in enumerate([
            "FUTEK written application confirmation for TFF400 orientation, side loads, mounting and expected dynamic profile",
            "Exact torque sensor, bidirectional system calibration, amplifier and cable configuration selected and received",
            "Dimensioned fixed-side adapter with material, fits, holes, fasteners, tolerances and tool access",
            "Dimensioned active-side adapter to exact received S102/X430 with interference, stiffness and FAI evidence",
            "Complete materials, fasteners, locking, torque, edge treatment and manufacturing process for all fixture parts",
            "Qualified structural/load-path calculation including shock, fatigue, deflection, local stress and sensor overload protection",
            "Boston site bench survey, permission, substrate, exact anchors, installation and proof evidence",
            "Independent physical catch containing link and load after branch removal and single fixture-control failure",
            "Full guard and access closure for the actual swept/pinch/ejected-part volume with impact/retention proof",
            "Non-human controlled load device, profile, retention, balance and reverse-energy behavior",
            "Cable, connector, strain relief, bend, separation and temperature-sensor routing",
            "Acquisition ranges, rates, settling, synchronization, calibration and uncertainty budget",
            "Independent branch interruption, accepted abort logic, source limits, overload and regenerated-energy controls",
            "As-built inspection, unpowered proof, qualified mechanical/electrical review and separate powered-work authorization",
        ], 1)
    ])

    write_csv(OUT / "source-register.csv", [
        {"source_id": "FXS-001", "manufacturer": "ROBOTIS", "document": "XM430-W350 e-Manual", "revision_or_date": "live page; no formal revision shown; accessed 2026-08-08", "locator": "https://emanual.robotis.com/docs/en/dxl/x/xm430-w350/", "evidence_use": "stall endpoint and continuous-output warning; not a continuous rating"},
        {"source_id": "FXS-002", "manufacturer": "FUTEK", "document": "TFF400 drawing FI1251-F and FSH04015 live product record", "revision_or_date": "drawing revision F; live record accessed 2026-08-08", "locator": "https://media.futek.com/content/futek/files/pdf/productdrawings/fsh02588.pdf", "evidence_use": "sensor envelope, interfaces and catalog characteristics"},
        {"source_id": "FXS-003", "manufacturer": "FUTEK", "document": "IAA100 drawing FI1573", "revision_or_date": "drawing number FI1573; accessed 2026-08-08", "locator": "https://media.futek.com/content/futek/files/pdf/productdrawings/iaa100.pdf", "evidence_use": "candidate conditioner characteristics"},
        {"source_id": "FXS-004", "manufacturer": "FUTEK", "document": "LSB205 drawing FI1452-C", "revision_or_date": "drawing revision C; accessed 2026-08-08", "locator": "https://media.futek.com/content/futek/files/pdf/productdrawings/fsh04100.pdf", "evidence_use": "candidate static cross-check sensor characteristics"},
        {"source_id": "FXS-005", "manufacturer": "LabJack", "document": "T7 analog inputs / T-Series datasheet", "revision_or_date": "live documentation; accessed 2026-08-08", "locator": "https://support.labjack.com/docs/14-3-0-analog-inputs-t7-t-series-datasheet", "evidence_use": "candidate DAQ channel/range/stream facts"},
        {"source_id": "FXS-006", "manufacturer": "Joulescope", "document": "JS220 User Guide", "revision_or_date": "revision 1.10; last revised 2025-01-27; accessed 2026-08-08", "locator": "https://download.joulescope.com/products/JS220/JS220-K000/users_guide/Joulescope%20JS220%20User%27s%20Guide.pdf", "evidence_use": "candidate branch current/voltage instrument limits"},
        {"source_id": "FXS-007", "manufacturer": "OMEGA", "document": "SA1 self-adhesive thermocouple instruction sheet", "revision_or_date": "M0503/0417", "locator": "https://assets.omega.com/manuals/test-and-measurement-equipment/temperature/sensors/thermocouple-probes/M0503.pdf", "evidence_use": "surface sensor construction and placement limits"},
        {"source_id": "FXS-008", "manufacturer": "ROBOTIS", "document": "controlled X430/FR12 STEP files", "revision_or_date": "repository-controlled R91 acquisition", "locator": "cad/vendor/robotis/x430-fr12-r91/", "evidence_use": "nominal actuator/frame geometry and interface axes"},
    ])

    source_hashes = {name: sha256(VENDOR / name) for name in ("x-430_idle.stp", "fr12_s102.stp", "fr12_h101.stp")}
    status = {
        "identifier": IDENTIFIER,
        "warning": WARNING,
        "state": "DIMENSIONED_TOPOLOGY_CANDIDATE_NOT_SELECTED",
        "preferred_topology": "TFF400 FSH04015 stationary reaction torque with LSB205 static cross-check",
        "open_hold_count": 14,
        "source_sha256": source_hashes,
        "screen_values": {
            "tff_capacity_to_x430_stall_endpoint_ratio": round(TFF_CAPACITY_NM / X430_STALL_ENDPOINT_NM, 9),
            "lsb205_100mm_nominal_moment_nm": round(LSB205_CAPACITY_N * STATIC_FORCE_ARM / 1000, 9),
        },
        "release_flags": {
            "sensor_selected": False,
            "fixture_buildable": False,
            "fixture_fabrication_released": False,
            "fixture_assembly_released": False,
            "fixture_guard_complete": False,
            "fixture_catch_complete": False,
            "bench_anchor_selected": False,
            "powered_test_authorized": False,
            "motion_authorized": False,
            "connection_authorized": False,
            "energization_authorized": False,
            "duty_hold_08_closed": False,
        },
    }
    (OUT / "package-status.json").write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8", newline="\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
