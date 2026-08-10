#!/usr/bin/env python3
"""Generate the controlled HR-V0 coordinate/sign convention review package."""

from __future__ import annotations

import csv
import hashlib
import json
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "cad" / "hr-v0" / "generated" / "coordinate-convention-p0.1"
WEB = ROOT / "release" / "hr-v0" / "coordinate-convention-p0.1"
FORM = ROOT / "tests" / "forms" / "hr-v0-coordinate-calibration-template-p0.1.csv"
IDENTIFIER = "HR-V0-FRAME-CONV-P0.1"
DATE = "2026-08-09"
WARNING = "PRELIMINARY - NOT APPROVED FOR FABRICATION, MOTION, CONNECTION, OR ENERGIZATION"

SOURCES = {
    "arm_transform_schedule": ROOT / "cad" / "hr-v0" / "generated" / "arm-architecture-p0.7" / "transform-schedule.csv",
    "arm_summary": ROOT / "cad" / "hr-v0" / "generated" / "arm-architecture-p0.7" / "architecture-summary.json",
    "mechanical_release": ROOT / "cad" / "hr-v0" / "generated" / "assembly" / "mechanical-release-summary.json",
    "mechanical_parameters": ROOT / "cad" / "hr-v0" / "mechanical-release-data.csv",
    "actuator_config": ROOT / "firmware" / "supervisor" / "actuator-config.json",
    "supervisor_config": ROOT / "firmware" / "supervisor" / "supervisor-config.json",
    "legacy_guard_summary": ROOT / "cad" / "hr-v0" / "guard-receiver-p0.2" / "guard-receiver-summary.json",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_csv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def matrix(tx: float, ty: float, tz: float, rx_deg: float = 0.0) -> list[list[float]]:
    c = round(math.cos(math.radians(rx_deg)), 12)
    s = round(math.sin(math.radians(rx_deg)), 12)
    return [
        [1.0, 0.0, 0.0, tx],
        [0.0, c, -s, ty],
        [0.0, s, c, tz],
        [0.0, 0.0, 0.0, 1.0],
    ]


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    WEB.mkdir(parents=True, exist_ok=True)
    actuator = json.loads(SOURCES["actuator_config"].read_text(encoding="utf-8"))
    supervisor = json.loads(SOURCES["supervisor_config"].read_text(encoding="utf-8"))
    arm = json.loads(SOURCES["arm_summary"].read_text(encoding="utf-8"))
    guard = json.loads(SOURCES["legacy_guard_summary"].read_text(encoding="utf-8"))

    frames = [
        {
            "frame_id": "A0_BASE_CENTER",
            "parent": "NONE",
            "origin_in_parent_mm": "0,0,0",
            "basis": "+X right; +Y front; +Z up",
            "handedness": "RIGHT_HANDED",
            "use": "authoritative HR-V0 assembly, kinematics, controls, load and metrology frame",
            "status": "CONTROLLED CANDIDATE - physical datum marking and survey open",
        },
        {
            "frame_id": "J1_LOCAL",
            "parent": "A0_BASE_CENTER",
            "origin_in_parent_mm": "-210.000,81.025,500.000",
            "basis": "+X joint axis; +Y straight upper-link direction; +Z completes right hand",
            "handedness": "RIGHT_HANDED",
            "use": "J1 engineering angle and upper-arm geometry",
            "status": "CONTROLLED NOMINAL - received axis survey open",
        },
        {
            "frame_id": "J2_ZERO",
            "parent": "J1_LOCAL",
            "origin_in_parent_mm": "0.000,202.550,0.000",
            "basis": "+X joint axis; +Y straight forearm direction at q2=0; +Z completes right hand",
            "handedness": "RIGHT_HANDED",
            "use": "J2 internal engineering angle; q2=0 is geometric reference and is outside command range",
            "status": "CONTROLLED NOMINAL - received axis survey open",
        },
        {
            "frame_id": "G1_H104_ZERO",
            "parent": "J1_LOCAL",
            "origin_in_parent_mm": "0.000,331.600,0.000",
            "basis": "H104 frame has Rx=180 deg in straight reference",
            "handedness": "RIGHT_HANDED",
            "use": "controlled H104 frame only; complete gripper/TCP transform remains open",
            "status": "PARTIAL - H104 fit and gripper registration open",
        },
        {
            "frame_id": "G0_RH",
            "parent": "A0_BASE_CENTER",
            "origin_in_parent_mm": "-210.000,81.025,0.000",
            "basis": "+X right; +Y front; +Z up, parallel to A0",
            "handedness": "RIGHT_HANDED",
            "use": "future guard/receiver measurements centered below J1",
            "status": "CONTROLLED SUCCESSOR CONVENTION - physical datum marking open",
        },
        {
            "frame_id": "G0_LEGACY_LAYOUT",
            "parent": "physical point below J1, not a rigid-transform parent",
            "origin_in_parent_mm": "A0(-210.000,81.025,0.000)",
            "basis": "+x legacy depth=A0 +Y; +y legacy width=A0 +X; +z=A0 +Z",
            "handedness": "NOT A KINEMATIC FRAME - axis swap has determinant -1",
            "use": "interpret historical guard P0.2/P0.3 dimension labels only",
            "status": "LEGACY LAYOUT ONLY - prohibited for rotations, cross products, torques, or controls",
        },
    ]
    write_csv(OUT / "frame-register.csv", frames, list(frames[0]))

    transforms = [
        {"transform_id": "TF-001", "parent": "A0_BASE_CENTER", "child": "J1_LOCAL", "tx_mm": "-210.000", "ty_mm": "81.025", "tz_mm": "500.000", "rx_deg": "0.000", "matrix_4x4_row_major": json.dumps(matrix(-210, 81.025, 500)), "state": "CONTROLLED NOMINAL"},
        {"transform_id": "TF-002", "parent": "J1_LOCAL", "child": "J2_ZERO", "tx_mm": "0.000", "ty_mm": "202.550", "tz_mm": "0.000", "rx_deg": "0.000", "matrix_4x4_row_major": json.dumps(matrix(0, 202.55, 0)), "state": "CONTROLLED NOMINAL"},
        {"transform_id": "TF-003", "parent": "J1_LOCAL", "child": "G1_H104_ZERO", "tx_mm": "0.000", "ty_mm": "331.600", "tz_mm": "0.000", "rx_deg": "180.000", "matrix_4x4_row_major": json.dumps(matrix(0, 331.6, 0, 180)), "state": "PARTIAL - COMPLETE GRIPPER/TCP OPEN"},
        {"transform_id": "TF-004", "parent": "A0_BASE_CENTER", "child": "G0_RH", "tx_mm": "-210.000", "ty_mm": "81.025", "tz_mm": "0.000", "rx_deg": "0.000", "matrix_4x4_row_major": json.dumps(matrix(-210, 81.025, 0)), "state": "CONTROLLED SUCCESSOR CONVENTION"},
    ]
    write_csv(OUT / "transform-register.csv", transforms, list(transforms[0]))

    joints = [
        {
            "axis_id": "J1",
            "engineering_quantity": "shoulder angle q1",
            "positive_axis": "J1_LOCAL +X",
            "positive_rule": "right-hand rotation; from q1=0, +q1 moves the straight upper link from +Y toward +Z",
            "zero_definition": "upper-link straight reference along J1_LOCAL +Y",
            "command_range": "-20.000..70.000 deg inclusive",
            "native_actuator_axis_fact": "manufacturer local +Z maps to project joint -X in the P0.7 package transform",
            "raw_to_engineering": "RECEIVED CALIBRATION REQUIRED - do not infer register sign",
            "state": "ENGINEERING SIGN CONTROLLED; RAW POLARITY OPEN; MOTION INHIBITED",
        },
        {
            "axis_id": "J2",
            "engineering_quantity": "elbow internal angle q2",
            "positive_axis": "J2_ZERO +X",
            "positive_rule": "right-hand relative rotation; from q2=0, +q2 moves the forearm from local +Y toward local +Z",
            "zero_definition": "straight forearm reference; geometric datum only and outside the 15 deg command minimum",
            "command_range": "15.000..115.000 deg inclusive; positive metal candidate contact 117.999985 deg",
            "native_actuator_axis_fact": "manufacturer local +Z maps to project joint -X in the P0.7 package transform",
            "raw_to_engineering": "RECEIVED CALIBRATION REQUIRED - do not infer register sign",
            "state": "ENGINEERING SIGN CONTROLLED; RAW POLARITY OPEN; MOTION INHIBITED",
        },
        {
            "axis_id": "GRIPPER",
            "engineering_quantity": "usable object opening",
            "positive_axis": "larger reported opening in mm",
            "positive_rule": "positive engineering change means increasing verified usable opening",
            "zero_definition": "no zero released; project range is 20.000..75.000 mm candidate",
            "command_range": "20.000..75.000 mm candidate",
            "native_actuator_axis_fact": "complete H104-to-mechanism registration and opening transfer remain open",
            "raw_to_engineering": "RECEIVED CALIBRATION REQUIRED - mesh distance is not jaw opening",
            "state": "INTENT CONTROLLED; GEOMETRY/POLARITY/OPENING CALIBRATION OPEN; MOTION INHIBITED",
        },
    ]
    write_csv(OUT / "joint-sign-register.csv", joints, list(joints[0]))

    mapping = [
        {"mapping_id": "MAP-001", "legacy_quantity": "G0_LEGACY_LAYOUT x_depth", "controlled_quantity": "G0_RH +Y / A0 +Y", "equation": "y_RH = x_legacy", "allowed_use": "historical dimension interpretation only", "state": "CONTROLLED MAPPING"},
        {"mapping_id": "MAP-002", "legacy_quantity": "G0_LEGACY_LAYOUT y_width", "controlled_quantity": "G0_RH +X / A0 +X", "equation": "x_RH = y_legacy", "allowed_use": "historical dimension interpretation only", "state": "CONTROLLED MAPPING"},
        {"mapping_id": "MAP-003", "legacy_quantity": "G0_LEGACY_LAYOUT z_height", "controlled_quantity": "G0_RH +Z / A0 +Z", "equation": "z_RH = z_legacy", "allowed_use": "historical dimension interpretation only", "state": "CONTROLLED MAPPING"},
        {"mapping_id": "MAP-004", "legacy_quantity": "legacy orientation/cross product/torque", "controlled_quantity": "NONE", "equation": "PROHIBITED", "allowed_use": "none", "state": "FAIL CLOSED - use A0 or G0_RH"},
    ]
    write_csv(OUT / "legacy-layout-mapping.csv", mapping, list(mapping[0]))

    mirror = [
        {"scope": "HR-V0", "rule": "single bench arm; no left/right mirrored joint exists", "configuration_action": "do not synthesize or mirror actuator direction", "state": "NOT APPLICABLE TO HR-V0"},
        {"scope": "HR-30", "rule": "left/right frame transforms, joint signs, zero poses and raw polarity require a separately released full-body convention", "configuration_action": "mirrored-joint mismatch must inhibit drive enable under CFG-002", "state": "SELECTION REQUIRED - NOT INHERITED FROM HR-V0"},
    ]
    write_csv(OUT / "mirroring-register.csv", mirror, list(mirror[0]))

    calibration_points = [
        ("CAL-J1-01", "J1", "zero-reference fixture", "0.000", "deg"),
        ("CAL-J1-02", "J1", "independent positive reference", "SELECTION REQUIRED", "deg"),
        ("CAL-J2-01", "J2", "command-minimum fixture", "15.000", "deg"),
        ("CAL-J2-02", "J2", "independent positive reference below stop", "SELECTION REQUIRED", "deg"),
        ("CAL-G1-01", "GRIPPER", "minimum verified usable opening", "20.000 candidate", "mm"),
        ("CAL-G1-02", "GRIPPER", "maximum verified usable opening", "75.000 candidate", "mm"),
    ]
    cal_rows = [
        {
            "record_id": rid,
            "axis_id": axis,
            "reference_condition": condition,
            "nominal_engineering_value": value,
            "unit": unit,
            "received_model_number": "",
            "received_firmware_version": "",
            "measured_engineering_value": "",
            "measured_raw_value": "",
            "raw_direction_result": "",
            "instrument_id": "",
            "uncertainty": "",
            "witness": "",
            "evidence_uri": "",
            "result": "NOT EXECUTED",
            "warning": WARNING,
        }
        for rid, axis, condition, value, unit in calibration_points
    ]
    write_csv(FORM, cal_rows, list(cal_rows[0]))

    sources = [
        {"source_id": key, "path": str(path.relative_to(ROOT)).replace("\\", "/"), "sha256": sha256(path), "use": "controlled input; no physical acceptance implied"}
        for key, path in SOURCES.items()
    ]
    write_csv(OUT / "source-register.csv", sources, list(sources[0]))

    holds = [
        ("FCH-001", "physically mark/survey A0 and J1/J2 axes on the accepted assembly", "OPEN"),
        ("FCH-002", "receive each actuator and record model/firmware/unique identity", "OPEN"),
        ("FCH-003", "measure two independent points per axis and solve raw sign/scale/zero with uncertainty", "OPEN"),
        ("FCH-004", "prove commanded positive engineering motion matches metrology at torque-limited guarded HIL", "OPEN - POWERED TEST NOT AUTHORIZED"),
        ("FCH-005", "freeze start-pose tolerances and accepted calibration/configuration hashes", "OPEN"),
        ("FCH-006", "complete H104-to-gripper/TCP rigid transform and usable-opening calibration", "OPEN"),
        ("FCH-007", "replace legacy guard layout axes in the next guard revision and survey G0_RH", "OPEN"),
        ("FCH-008", "release separate HR-30 world/body/left/right mirrored frame convention", "OPEN - HR-30 STAGE"),
        ("FCH-009", "qualified mechanical/controls review of signs, zeros, tolerances and collision binding", "OPEN"),
        ("FCH-010", "execute CFG-002 polarity/mirror mismatch inhibition and retained evidence", "OPEN"),
    ]
    hold_rows = [{"hold_id": hid, "required_evidence": evidence, "state": state, "warning": WARNING} for hid, evidence, state in holds]
    write_csv(OUT / "coordinate-convention-holds.csv", hold_rows, list(hold_rows[0]))

    status = {
        "identifier": IDENTIFIER,
        "date": DATE,
        "warning": WARNING,
        "frame_count": len(frames),
        "right_handed_frame_count": sum(row["handedness"] == "RIGHT_HANDED" for row in frames),
        "joint_count": len(joints),
        "transform_count": len(transforms),
        "legacy_mapping_count": len(mapping),
        "calibration_record_count": len(cal_rows),
        "open_hold_count": len(hold_rows),
        "a0_axes": {"x": "right", "y": "front", "z": "up"},
        "j1_origin_a0_mm": [-210.0, 81.025, 500.0],
        "j2_origin_j1_mm": [0.0, 202.55, 0.0],
        "g1_origin_j1_mm": [0.0, 331.6, 0.0],
        "j1_limits_deg": [supervisor["joints"]["J1"]["minimum"], supervisor["joints"]["J1"]["maximum"]],
        "j2_limits_deg": [supervisor["joints"]["J2"]["minimum"], supervisor["joints"]["J2"]["maximum"]],
        "gripper_limits_mm": [supervisor["joints"]["GRIPPER"]["minimum"], supervisor["joints"]["GRIPPER"]["maximum"]],
        "raw_calibration_closed": False,
        "physical_datum_closed": False,
        "motion_authorized": False,
        "energization_authorized": False,
        "functional_safety_credit": False,
    }
    (OUT / "coordinate-convention-summary.json").write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8")

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="1400" height="900" viewBox="0 0 1400 900">
<style>text{{font-family:Arial,sans-serif;fill:#10253d;font-size:18px}}.title{{font-size:36px;font-weight:700}}.head{{font-size:25px;font-weight:700;fill:#07579f}}.warn{{font-size:19px;font-weight:700;fill:#071c36}}.axis{{stroke-width:5}}.part{{stroke:#07579f;stroke-width:10;stroke-linecap:round}}.panel{{fill:#fff;stroke:#07579f;stroke-width:3}}.gold{{fill:#f4bd28}}</style>
<rect width="1400" height="900" fill="#f4f9ff"/><rect width="1400" height="90" class="gold"/><text x="40" y="55" class="warn">{WARNING}</text>
<text x="40" y="145" class="title">HR-V0 right-handed frame and sign convention</text>
<rect x="40" y="185" width="600" height="650" rx="18" class="panel"/><text x="75" y="235" class="head">A0 assembly frame</text>
<circle cx="220" cy="600" r="8" fill="#10253d"/><line x1="220" y1="600" x2="430" y2="600" class="axis" stroke="#07579f"/><polygon points="430,600 405,588 405,612" fill="#07579f"/><text x="440" y="607">+X right</text>
<line x1="220" y1="600" x2="220" y2="380" class="axis" stroke="#f4bd28"/><polygon points="220,380 208,405 232,405" fill="#f4bd28"/><text x="238" y="395">+Z up</text>
<circle cx="220" cy="600" r="24" fill="none" stroke="#0a8f6a" stroke-width="5"/><circle cx="220" cy="600" r="5" fill="#0a8f6a"/><text x="100" y="650">+Y front, out of page</text><text x="75" y="700">+q is right-hand rotation about +X.</text><text x="75" y="735">At zero, each link points along local +Y.</text><text x="75" y="780">Positive q moves +Y toward +Z.</text>
<rect x="680" y="185" width="680" height="650" rx="18" class="panel"/><text x="715" y="235" class="head">Straight-reference Y-Z projection</text>
<circle cx="800" cy="650" r="12" fill="#07579f"/><line x1="800" y1="650" x2="1050" y2="650" class="part"/><circle cx="1050" cy="650" r="12" fill="#07579f"/><line x1="1050" y1="650" x2="1220" y2="650" class="part"/><text x="760" y="690">J1</text><text x="1020" y="690">J2</text><text x="1190" y="690">G1</text>
<text x="760" y="745">J1-J2 202.550 mm</text><text x="1030" y="780">J2-G1 129.050 mm</text>
<line x1="800" y1="650" x2="800" y2="400" class="axis" stroke="#f4bd28"/><polygon points="800,400 788,425 812,425" fill="#f4bd28"/><text x="820" y="420">+Z</text><line x1="800" y1="650" x2="1240" y2="650" class="axis" stroke="#07579f"/><polygon points="1240,650 1215,638 1215,662" fill="#07579f"/><text x="1250" y="657">+Y</text>
<text x="715" y="300">J2 q=0 is a geometric datum, not an allowed command.</text><text x="715" y="335">J2 commands remain 15..115 degrees candidate-only.</text><text x="715" y="370">Raw encoder sign, scale and zero remain uncalibrated.</text>
<text x="40" y="875" class="warn">Legacy G0 depth/width labels are layout-only; use A0/G0_RH for kinematics, torque, rotation and controls.</text></svg>'''
    (OUT / "HR-V0_coordinate-sign-convention.svg").write_text(svg, encoding="utf-8")

    frame_json = json.dumps(frames)
    page = f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>HR-V0 frame convention P0.1</title><style>
:root{{--sky:#8ed5ff;--blue:#07579f;--dark:#082f5b;--gold:#f4bd28;--paper:#f4f9ff;--ink:#10253d}}*{{box-sizing:border-box}}body{{margin:0;font:16px/1.55 system-ui,sans-serif;color:var(--ink);background:var(--paper)}}.warning{{padding:15px 5vw;background:var(--gold);font-weight:850}}header,main,footer{{padding:28px 5vw}}header{{background:var(--sky)}}h1{{font-size:clamp(32px,5vw,58px);line-height:1.08;color:var(--dark);max-width:1000px}}h2{{font-size:clamp(25px,3vw,38px);color:var(--blue)}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:18px}}.panel{{background:#fff;border:2px solid var(--blue);border-radius:14px;padding:18px}}label,input,output{{font-size:16px}}input{{width:100%}}svg{{width:100%;height:auto;background:white;border:2px solid var(--blue);border-radius:14px}}.axis{{stroke-width:4}}.link{{stroke:var(--blue);stroke-width:12;stroke-linecap:round}}table{{border-collapse:collapse;width:100%}}th,td{{padding:10px;text-align:left;border-bottom:1px solid #b8d3e7;vertical-align:top}}th{{background:var(--dark);color:#fff}}.table-wrap{{overflow:auto;border:2px solid var(--blue);border-radius:12px}}footer{{background:var(--dark);color:white;margin-top:28px}}@media(max-width:600px){{header,main,footer{{padding:20px}}}}
</style></head><body><div class="warning">{WARNING}</div><header><p>{IDENTIFIER} · R140 · {DATE}</p><h1>One frame convention for CAD, controls, metrology and review.</h1><p>A0 is right-handed: +X right, +Y front, +Z up. Joint-positive motion follows the right-hand rule about +X. Raw DYNAMIXEL polarity is deliberately unresolved until received calibration.</p></header><main><section class="grid"><div class="panel"><h2>Pose explorer</h2><label>J1 q1: <output id="q1o">0</output>°<input id="q1" type="range" min="-20" max="70" value="0" step="1"></label><label>J2 q2: <output id="q2o">30</output>°<input id="q2" type="range" min="15" max="115" value="30" step="1"></label><p>Diagram is a sign/kinematic teaching view, not a collision, stop, or motion release.</p></div><div class="panel"><h2>Fail-closed boundary</h2><p><strong>Raw sign, raw scale, raw zero, start tolerances and received identities remain open.</strong> The supervisor must continue to refuse motion until the accepted calibration/configuration evidence hash exists.</p><p>HR-V0 has one arm and no mirrored joint. HR-30 must issue its own left/right convention; it cannot inherit a guessed mirror.</p></div></section><section><h2>Y-Z sign view</h2><svg viewBox="0 0 900 520" role="img" aria-label="Interactive HR-V0 joint sign view"><line x1="100" y1="420" x2="100" y2="100" class="axis" stroke="#f4bd28"/><text x="112" y="110" font-size="18">+Z up</text><line x1="100" y1="420" x2="820" y2="420" class="axis" stroke="#07579f"/><text x="780" y="448" font-size="18">+Y front</text><line id="upper" class="link"/><line id="fore" class="link"/><circle id="j1p" cx="170" cy="380" r="11" fill="#082f5b"/><circle id="j2p" r="11" fill="#082f5b"/><circle id="g1p" r="9" fill="#f4bd28"/><text x="145" y="415" font-size="18">J1</text><text id="poseText" x="420" y="70" font-size="18"/></svg></section><section><h2>Controlled frames</h2><div class="table-wrap"><table><thead><tr><th>Frame</th><th>Parent / origin</th><th>Basis</th><th>Use and state</th></tr></thead><tbody id="frames"></tbody></table></div></section><section><h2>Evidence</h2><p><a href="../../../cad/hr-v0/generated/coordinate-convention-p0.1/frame-register.csv">Frame register</a> · <a href="../../../cad/hr-v0/generated/coordinate-convention-p0.1/joint-sign-register.csv">Joint signs</a> · <a href="../../../cad/hr-v0/generated/coordinate-convention-p0.1/legacy-layout-mapping.csv">Legacy mapping</a> · <a href="../../../tests/forms/hr-v0-coordinate-calibration-template-p0.1.csv">Blank calibration form</a> · <a href="../../../cad/hr-v0/generated/coordinate-convention-p0.1/coordinate-convention-summary.json">Status</a></p></section></main><footer>{WARNING}. No raw actuator polarity, calibration, gripper transform, physical datum, motion, fabrication, or energization authority is released.</footer><script>
const frames={frame_json};const q1=document.querySelector('#q1'),q2=document.querySelector('#q2');function esc(v){{return String(v).replace(/[&<>"']/g,c=>({{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}}[c]))}}document.querySelector('#frames').innerHTML=frames.map(f=>`<tr><td><strong>${{esc(f.frame_id)}}</strong></td><td>${{esc(f.parent)}}<br>${{esc(f.origin_in_parent_mm)}}</td><td>${{esc(f.basis)}}<br>${{esc(f.handedness)}}</td><td>${{esc(f.use)}}<br><strong>${{esc(f.status)}}</strong></td></tr>`).join('');function draw(){{const a=Number(q1.value)*Math.PI/180,b=Number(q2.value)*Math.PI/180;const base=[170,380],scale=1.25,L1=202.55*scale,L2=129.05*scale;const j2=[base[0]+L1*Math.cos(a),base[1]-L1*Math.sin(a)],g=[j2[0]+L2*Math.cos(a+b),j2[1]-L2*Math.sin(a+b)];for(const [id,p1,p2] of [['upper',base,j2],['fore',j2,g]]){{const e=document.querySelector('#'+id);e.setAttribute('x1',p1[0]);e.setAttribute('y1',p1[1]);e.setAttribute('x2',p2[0]);e.setAttribute('y2',p2[1])}}for(const [id,p] of [['j2p',j2],['g1p',g]]){{const e=document.querySelector('#'+id);e.setAttribute('cx',p[0]);e.setAttribute('cy',p[1])}}document.querySelector('#q1o').value=q1.value;document.querySelector('#q2o').value=q2.value;document.querySelector('#poseText').textContent=`q1=${{q1.value}}°, q2=${{q2.value}}°`;}}q1.addEventListener('input',draw);q2.addEventListener('input',draw);draw();
</script></body></html>'''
    (WEB / "index.html").write_text(page, encoding="utf-8")

    print(f"{IDENTIFIER}: {len(frames)} frames / {len(joints)} axes / {len(hold_rows)} holds")
    print("A0 +X right / +Y front / +Z up; raw calibration remains open")
    print(WARNING)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
