"""Generate the no-stop-credit HR-V0 rigid-body collapse-envelope screen.

The proof uses rotations only about the parallel J1/J2 X axes.  A bounding-box
radius is continuous under J1 rotation; the triangle inequality bounds every
forearm point under arbitrary J2 rotation.  Missing gripper, cable, tolerance,
deformation and physical evidence remain explicit holds.
"""

from __future__ import annotations

import csv
import hashlib
import json
import math
import shutil
from pathlib import Path

import cadquery as cq

import generate_hr_v0_arm_architecture as arm
import generate_hr_v0_guard_receiver as guard


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "cad" / "hr-v0" / "generated" / "power-loss-envelope-p0.1"
GENERATED_ROOT = ROOT / "cad" / "hr-v0" / "generated"
GENERATED_SOURCE_MANIFEST = GENERATED_ROOT / "SOURCE-MANIFEST.csv"
GUIDE = ROOT / "release" / "hr-v0" / "collapse-envelope-p0.1" / "index.html"
REVISION = "HR-V0-COLLAPSE-ENV-P0.1"
WARNING = "PRELIMINARY - GEOMETRIC SCREEN ONLY - NOT APPROVED FOR FABRICATION, MOTION OR ENERGIZATION"
MECHANICAL_REVISION = "HR-V0-MECH-R0.1-PRELIMINARY"
GENERATED_TEXT_SUFFIXES = {".csv", ".dxf", ".json", ".step", ".svg", ".txt"}


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def normalize_step(path: Path) -> None:
    lines = path.read_text(encoding="utf-8").splitlines()
    path.write_text("\n".join(line.rstrip() for line in lines) + "\n", encoding="utf-8", newline="\n")


def generated_sha256(path: Path) -> str:
    data = path.read_bytes()
    if path.suffix.lower() in GENERATED_TEXT_SUFFIXES:
        data = data.replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return hashlib.sha256(data).hexdigest().upper()


def write_generated_source_manifest() -> None:
    records = []
    for path in sorted(GENERATED_ROOT.rglob("*"), key=lambda item: item.as_posix().lower()):
        if path.is_file() and path != GENERATED_SOURCE_MANIFEST:
            records.append({
                "file": path.relative_to(GENERATED_ROOT).as_posix(),
                "sha256": generated_sha256(path),
                "revision": MECHANICAL_REVISION,
                "status": "PRELIMINARY - NOT RELEASED FOR FABRICATION OR ENERGIZATION",
            })
    write_csv(GENERATED_SOURCE_MANIFEST, records)


def controlled_shapes() -> tuple[dict[str, cq.Shape], dict[str, cq.Shape]]:
    xm540 = arm.import_step("XMHD-540.N101.I101.STP")
    h101 = arm.import_step("FR13-H101K.stp")
    s102 = arm.import_step("FR13-S102K.stp")
    h104 = arm.import_step("FR12-H104K.stp")
    joint_body = arm.actuator_to_joint_frame(xm540)
    fore_p_y = arm.J2_Y + 32.0
    upper = {
        "J1_H101": h101,
        "UPPER_PROX_ADAPTER": arm.adapter(32.0),
        "UPPER_20-2040": arm.beam(32.0 + arm.PLATE_T, arm.UPPER_BEAM_L),
        "J2_FIXED_CATCH_ADAPTER": arm.j2_positive_catch_adapter(32.0 + arm.PLATE_T + arm.UPPER_BEAM_L),
        "J2_XM540": arm.rotate_x(joint_body, 90.0).translate((0.0, arm.J2_Y, 0.0)),
        "J2_S102": arm.rotate_x(s102, 90.0).translate((0.0, arm.J2_Y, 0.0)),
    }
    fore = {
        "J2_H101": h101.translate((0.0, arm.J2_Y, 0.0)),
        "J2_MOVING_STRIKER_ADAPTER": arm.j2_positive_striker_adapter(fore_p_y),
        "FOREARM_20-2040": arm.beam(fore_p_y + arm.PLATE_T, arm.FOREARM_BEAM_L),
        "H104_DISTAL_ADAPTER": arm.gripper_adapter(fore_p_y + arm.PLATE_T + arm.FOREARM_BEAM_L),
        "H104_FRAME": arm.rotate_x(h104, 180.0).translate((0.0, arm.G1_Y, 0.0)),
    }
    return upper, fore


def main() -> int:
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)
    upper, fore = controlled_shapes()

    component_rows: list[dict[str, object]] = []
    known_radius = 0.0
    x_min = math.inf
    x_max = -math.inf
    for group, shapes in (("J1_MOVING", upper), ("J1_PLUS_J2_MOVING", fore)):
        for name, shape in shapes.items():
            bounds = arm.bbox_tuple(shape)
            local_radius = arm.bbox_radius_about_x(shape, arm.J2_Y if group == "J1_PLUS_J2_MOVING" else 0.0)
            shoulder_radius = local_radius if group == "J1_MOVING" else arm.J2_Y + local_radius
            known_radius = max(known_radius, shoulder_radius)
            x_min = min(x_min, bounds[0])
            x_max = max(x_max, bounds[1])
            component_rows.append({
                "component": name,
                "motion_group": group,
                "x_min_mm": f"{bounds[0]:.6f}",
                "x_max_mm": f"{bounds[1]:.6f}",
                "local_yz_radius_bound_mm": f"{local_radius:.6f}",
                "continuous_shoulder_radius_bound_mm": f"{shoulder_radius:.6f}",
                "method": "AABB CORNER RADIUS" if group == "J1_MOVING" else "J2 AXIS RADIUS + AABB CORNER RADIUS",
                "status": "CONTROLLED KNOWN BREP ONLY - PHYSICAL CLOSURE OPEN",
            })

    ledger_radius = 360.0
    controlled_known_radius = max(known_radius, ledger_radius)
    reserved_radius = guard.SPACE_RADIUS
    radial_margin = reserved_radius - controlled_known_radius
    depth_negative_margin = x_min - (-guard.INNER_X / 2.0)
    depth_positive_margin = guard.INNER_X / 2.0 - x_max
    bottom_margin = guard.SHOULDER_Z - controlled_known_radius
    top_margin = guard.INNER_Z - (guard.SHOULDER_Z + controlled_known_radius)
    object_catch_top = guard.FRAME + guard.RECEIVER_T
    object_catch_to_arm_gap = bottom_margin - object_catch_top
    known_fit = min(radial_margin, depth_negative_margin, depth_positive_margin, bottom_margin, top_margin) >= 0.0

    write_csv(OUT / "collapse-envelope-components.csv", component_rows)
    fit_rows = [
        {"fit_id":"CEF-001","boundary":"known B-Rep continuous shoulder radius","candidate_value_mm":f"{known_radius:.6f}","guard_limit_mm":f"{reserved_radius:.6f}","remaining_margin_mm":f"{reserved_radius-known_radius:.6f}","result":"PASS KNOWN BREP ONLY" if known_radius <= reserved_radius else "FAIL","exclusion":"complete gripper mechanism, object, cable, strain relief, tolerance, deflection and physical motion"},
        {"fit_id":"CEF-002","boundary":"controlled ledger radius versus guard radial reservation","candidate_value_mm":f"{ledger_radius:.6f}","guard_limit_mm":f"{reserved_radius:.6f}","remaining_margin_mm":f"{reserved_radius-ledger_radius:.6f}","result":"PASS ALLOCATION ONLY" if ledger_radius <= reserved_radius else "FAIL","exclusion":"ledger radius is a requirement ceiling, not as-built sweep proof"},
        {"fit_id":"CEF-003","boundary":"combined known geometric/allocation radius","candidate_value_mm":f"{controlled_known_radius:.6f}","guard_limit_mm":f"{reserved_radius:.6f}","remaining_margin_mm":f"{radial_margin:.6f}","result":"PASS INPUTS ONLY" if radial_margin >= 0 else "FAIL","exclusion":"unused margin is not a released cable, stopping or safety clearance"},
        {"fit_id":"CEF-004","boundary":"negative X depth","candidate_value_mm":f"{x_min:.6f}","guard_limit_mm":f"{-guard.INNER_X/2.0:.6f}","remaining_margin_mm":f"{depth_negative_margin:.6f}","result":"PASS KNOWN BREP ONLY" if depth_negative_margin >= 0 else "FAIL","exclusion":"complete gripper/cable out-of-plane envelope"},
        {"fit_id":"CEF-005","boundary":"positive X depth","candidate_value_mm":f"{x_max:.6f}","guard_limit_mm":f"{guard.INNER_X/2.0:.6f}","remaining_margin_mm":f"{depth_positive_margin:.6f}","result":"PASS KNOWN BREP ONLY" if depth_positive_margin >= 0 else "FAIL","exclusion":"complete gripper/cable out-of-plane envelope"},
        {"fit_id":"CEF-006","boundary":"bottom Z at G0","candidate_value_mm":f"{guard.SHOULDER_Z-controlled_known_radius:.6f}","guard_limit_mm":"0.000000","remaining_margin_mm":f"{bottom_margin:.6f}","result":"PASS INPUTS ONLY" if bottom_margin >= 0 else "FAIL","exclusion":"contact/rebound/receiver thickness and deformation"},
        {"fit_id":"CEF-007","boundary":"top Z at G0","candidate_value_mm":f"{guard.SHOULDER_Z+controlled_known_radius:.6f}","guard_limit_mm":f"{guard.INNER_Z:.6f}","remaining_margin_mm":f"{top_margin:.6f}","result":"PASS INPUTS ONLY" if top_margin >= 0 else "FAIL","exclusion":"contact/rebound/tolerance and deformation"},
        {"fit_id":"CEF-008","boundary":"P0.3 floor-tray top versus controlled arm-envelope bottom","candidate_value_mm":f"{object_catch_top:.6f}","guard_limit_mm":f"{bottom_margin:.6f}","remaining_margin_mm":f"{object_catch_to_arm_gap:.6f}","result":"NO ARM CONTACT EXPECTED - OBJECT CATCH ROLE ONLY" if object_catch_to_arm_gap > 0 else "CONTACT POSSIBLE - ANALYSIS REQUIRED","exclusion":"missing gripper/cable geometry cannot be used to invent arm-support credit"},
    ]
    write_csv(OUT / "guard-fit-screen.csv", fit_rows)

    role_rows = [
        {"role_id":"RCD-001","current_item":"P0.3 five-piece 320 x 820 x 50 mm floor tray","controlled_role":"OBJECT CATCH ENVELOPE ONLY","arm_support_credit":"ZERO","energy_or_load_credit":"ZERO","required_correction":"refer to it as the object catch; retain material/retention/drop/rebound holds","status":"ROLE CORRECTED - IMPLEMENTATION OPEN"},
        {"role_id":"RCD-002","current_item":"passive arm receiver","controlled_role":"support arm/gripper after power-loss collapse without control energy","arm_support_credit":"REQUIRED AFTER PHYSICAL ACCEPTANCE","energy_or_load_credit":"SELECTION REQUIRED","required_correction":"exact contact geometry, compliant element, load path, force/travel/rebound limits and proof","status":"DESIGN REQUIRED"},
        {"role_id":"RCD-003","current_item":"J1 bidirectional hard stops","controlled_role":"bound shoulder rotation before cable/guard/self-contact","arm_support_credit":"REQUIRED AFTER PHYSICAL ACCEPTANCE","energy_or_load_credit":"SELECTION REQUIRED","required_correction":"both stop parts, bumper, backing, tolerance, impact/fatigue and physical proof","status":"DESIGN REQUIRED"},
        {"role_id":"RCD-004","current_item":"J2 bidirectional hard stops","controlled_role":"bound elbow rotation before cable/guard/self-contact","arm_support_credit":"REQUIRED AFTER PHYSICAL ACCEPTANCE","energy_or_load_credit":"positive direction CAD only; all physical and negative direction open","required_correction":"J2 minimum topology plus complete positive/negative proof","status":"DESIGN REQUIRED"},
        {"role_id":"RCD-005","current_item":"450 mm radial reservation","controlled_role":"geometric design-space allocation around J1","arm_support_credit":"ZERO","energy_or_load_credit":"ZERO","required_correction":"complete gripper/cable/tolerance/deformation/rebound union and physical metrology","status":"KNOWN BREP FIT SCREEN ONLY"},
    ]
    write_csv(OUT / "receiver-role-disposition.csv", role_rows)

    survey_rows = []
    for index, item in enumerate((
        "J1 axis G0 transform", "complete gripper x-min", "complete gripper x-max", "complete cable x-min", "complete cable x-max",
        "as-built radial envelope", "J1 minimum boundary", "J1 maximum boundary", "J2 minimum boundary", "J2 maximum boundary",
        "arm-receiver first contact", "object-catch first contact", "post-contact travel", "maximum rebound", "final resting access",
        "cable/connector strain", "guard clearance", "configuration/review disposition",
    ), 1):
        survey_rows.append({"record_id":f"CES-{index:03d}","date":"","inspector":"","repo_commit":"","configuration_id":"","measurement":item,"nominal_or_limit":"SELECTION REQUIRED","instrument":"SELECTION REQUIRED","calibration_reference":"","measured_value":"","unit":"SELECTION REQUIRED","uncertainty":"","photo_or_scan_reference":"","deviation_reference":"","result":"NOT EXECUTED","authorization":"NOT AUTHORIZED","warning":WARNING})
    write_csv(ROOT / "tests" / "forms" / "hr-v0-collapse-envelope-metrology-template-p0.1.csv", survey_rows)

    # Review model: fixed guard frame and object catch, conservative continuous
    # cylinder, and straight-reference known moving B-Reps at J1 Z=500.
    assembly = cq.Assembly(name="HR_V0_COLLAPSE_ENVELOPE_REVIEW_ONLY")
    guard.add_frame(assembly)
    guard.add_receiver(assembly)
    cylinder = cq.Solid.makeCylinder(
        controlled_known_radius,
        x_max - x_min,
        cq.Vector(x_min, 0.0, guard.SHOULDER_Z),
        cq.Vector(1.0, 0.0, 0.0),
    )
    assembly.add(cylinder, name="KNOWN_CONTINUOUS_COLLAPSE_CYLINDER_NOT_SAFETY_DISTANCE", color=cq.Color(0.49, 0.83, 0.99, 0.22))
    for name, shape in {**upper, **fore}.items():
        assembly.add(shape.translate((0.0, 0.0, guard.SHOULDER_Z)), name=name, color=cq.Color(0.96, 0.72, 0.20))
    assembly.save(str(OUT / "HR-V0_collapse-envelope-review.glb"))
    step_path = OUT / "HR-V0_collapse-envelope-review.step"
    cq.exporters.export(cq.Compound.makeCompound([cylinder]), str(step_path))
    normalize_step(step_path)

    summary = {
        "revision": REVISION,
        "arm_revision": arm.REVISION,
        "guard_revision": guard.REVISION,
        "warning": WARNING,
        "proof_method": "continuous rigid-body radial bound for arbitrary J1/J2 X-axis rotations; J2 group uses triangle inequality",
        "known_brep_radius_bound_mm": round(known_radius, 6),
        "controlled_ledger_radius_mm": ledger_radius,
        "combined_known_input_radius_mm": round(controlled_known_radius, 6),
        "guard_reserved_radius_mm": reserved_radius,
        "radial_unallocated_margin_mm": round(radial_margin, 6),
        "known_x_extent_mm": [round(x_min, 6), round(x_max, 6)],
        "guard_x_extent_mm": [-guard.INNER_X / 2.0, guard.INNER_X / 2.0],
        "known_input_z_extent_at_g0_mm": [round(guard.SHOULDER_Z-controlled_known_radius, 6), round(guard.SHOULDER_Z+controlled_known_radius, 6)],
        "guard_z_extent_mm": [0.0, guard.INNER_Z],
        "object_catch_top_z_mm": object_catch_top,
        "object_catch_to_controlled_arm_envelope_gap_mm": round(object_catch_to_arm_gap, 6),
        "known_input_fit": known_fit,
        "current_floor_tray_role": "OBJECT CATCH ENVELOPE ONLY - ZERO ARM SUPPORT OR ENERGY CREDIT",
        "open_exclusions": ["complete gripper mechanism", "moving object geometry", "cables and strain relief", "tolerance", "backlash", "deformation", "stopping and rebound", "receiver contact geometry", "physical metrology", "qualified review"],
        "release_state": "GEOMETRIC SCREEN ONLY - EG-008 AND EG-009 REMAIN PARTIAL",
    }
    (OUT / "collapse-envelope-summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    (OUT / "collapse-envelope-poster.svg").write_text(f"""<svg xmlns=\"http://www.w3.org/2000/svg\" width=\"1200\" height=\"700\" viewBox=\"0 0 1200 700\"><style>text{{font-family:Arial,sans-serif;fill:#102a43;font-size:22px}}.title{{font-size:38px;font-weight:700}}.warn{{font-size:20px;font-weight:700;fill:#7d2b1d}}.frame{{fill:#e4f6ff;stroke:#082b55;stroke-width:8}}.env{{fill:#7dd3fc;fill-opacity:.32;stroke:#0874b9;stroke-width:5}}.arm{{fill:none;stroke:#d89a00;stroke-width:20;stroke-linecap:round}}.catch{{fill:#f4b942;stroke:#8a5b00;stroke-width:4}}</style><rect width=\"1200\" height=\"700\" fill=\"#f7fbff\"/><text x=\"60\" y=\"65\" class=\"title\">HR-V0 continuous collapse-envelope review</text><text x=\"60\" y=\"105\" class=\"warn\">PRELIMINARY - KNOWN GEOMETRY ONLY - ZERO ARM-RECEIVER CREDIT</text><rect x=\"320\" y=\"135\" width=\"560\" height=\"520\" class=\"frame\"/><circle cx=\"600\" cy=\"395\" r=\"210\" class=\"env\"/><circle cx=\"600\" cy=\"395\" r=\"9\" fill=\"#082b55\"/><path d=\"M600 395 L690 300 L790 370\" class=\"arm\"/><rect x=\"355\" y=\"620\" width=\"490\" height=\"18\" class=\"catch\"/><text x=\"635\" y=\"385\">J1</text><text x=\"725\" y=\"210\">360 mm controlled input</text><text x=\"360\" y=\"610\">P0.3 object catch only; 114 mm below arm envelope</text><text x=\"60\" y=\"665\">Drag the loaded 3D model to orbit. Complete gripper, cables, stops, tolerance and physical evidence remain open.</text></svg>""", encoding="utf-8", newline="\n")
    GUIDE.parent.mkdir(parents=True, exist_ok=True)
    GUIDE.write_text(f"""<!doctype html>
<html lang=\"en\"><head><meta charset=\"utf-8\"><meta name=\"viewport\" content=\"width=device-width,initial-scale=1\"><title>HR-V0 collapse envelope</title>
<style>:root{{--deep:#041a35;--navy:#082b55;--sky:#7dd3fc;--pale:#e4f6ff;--gold:#f4b942;--ink:#102a43;--red:#a83220;--line:#9ccfe8}}*{{box-sizing:border-box}}body{{margin:0;background:var(--pale);color:var(--ink);font:17px/1.55 system-ui,"Segoe UI",sans-serif}}header{{background:linear-gradient(135deg,var(--deep),var(--navy));color:white;padding:clamp(34px,6vw,72px) 20px}}header>div,main{{max-width:1120px;margin:auto}}h1{{font-size:clamp(36px,6vw,66px);line-height:1.05;margin:.2em 0}}h2{{font-size:clamp(27px,3.5vw,40px);line-height:1.15;color:var(--navy)}}.eyebrow{{font-size:14px;font-weight:850;color:var(--sky)}}.warning{{background:var(--gold);color:#17243a;border:3px solid #8a5b00;padding:15px 18px;font-weight:850}}main{{padding:30px 20px 80px}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(245px,1fr));gap:18px}}.card,.diagram{{background:white;border:2px solid var(--line);border-radius:16px;padding:20px;box-shadow:0 3px 0 #bddbea}}.metric{{font-size:clamp(34px,6vw,58px);font-weight:900;color:#075b9b}}.hold{{color:var(--red);font-weight:850}}.controls{{display:flex;flex-wrap:wrap;gap:18px;margin-bottom:14px}}label{{font-weight:800}}input{{width:20px;height:20px;vertical-align:middle}}svg{{width:100%;height:auto}}.guard{{fill:#dff3ff;stroke:var(--navy);stroke-width:5}}.reserve{{fill:var(--gold);opacity:.16;stroke:#b27300;stroke-width:4;stroke-dasharray:12 8}}.known{{fill:var(--sky);opacity:.28;stroke:#0874b9;stroke-width:4}}.catch{{fill:var(--gold);stroke:#8a5b00;stroke-width:3}}.axis{{fill:var(--navy)}}.label{{font:700 16px system-ui;fill:var(--ink)}}.gap{{stroke:var(--red);stroke-width:4;marker-start:url(#arrow);marker-end:url(#arrow)}}.role{{border-left:9px solid var(--gold)}}model-viewer{{width:100%;height:520px;background:#dff3ff;border:2px solid var(--line);border-radius:16px}}footer{{background:var(--deep);color:white;padding:30px 20px}}footer p{{max-width:1120px;margin:auto}}@media(max-width:760px){{body{{font-size:16px}}.controls{{display:grid}}model-viewer{{height:430px}}}}</style>
<script type=\"module\" src=\"../../vendor/model-viewer/4.1.0/model-viewer.min.js\"></script></head><body>
<header><div><p class=\"warning\">PRELIMINARY - GEOMETRIC SCREEN ONLY. NOT APPROVED FOR FABRICATION, MOTION OR ENERGIZATION.</p><p class=\"eyebrow\">{REVISION}</p><h1>The guard volume fits. The floor tray does not catch the arm.</h1><p>A continuous no-stop-credit bound covers arbitrary rotations of the known rigid bodies. Missing gripper, cable, tolerance, deformation and physical evidence remain outside the proof.</p></div></header><main>
<section><h2>Controlled result</h2><div class=\"grid\"><article class=\"card\"><div class=\"metric\">{known_radius:.3f} mm</div><p>Known B-Rep continuous radius.</p></article><article class=\"card\"><div class=\"metric\">90.000 mm</div><p>Unallocated radial margin from the controlled 360 mm input to the 450 mm reservation.</p></article><article class=\"card\"><div class=\"metric\">114.000 mm</div><p>Vertical gap between the floor-tray top and the controlled arm-envelope bottom.</p></article></div></section>
<section><h2>Front-envelope logic</h2><div class=\"diagram\"><div class=\"controls\"><label><input id=\"reserveToggle\" type=\"checkbox\" checked> 450 mm reservation</label><label><input id=\"knownToggle\" type=\"checkbox\" checked> 360 mm controlled input</label><label><input id=\"catchToggle\" type=\"checkbox\" checked> Existing floor tray</label></div><svg viewBox=\"0 0 940 650\" role=\"img\" aria-labelledby=\"title desc\"><title id=\"title\">HR-V0 front collapse envelope</title><desc id=\"desc\">Guard boundary, radial reservation, controlled arm envelope and floor object catch separated by 114 millimetres.</desc><defs><marker id=\"arrow\" markerWidth=\"8\" markerHeight=\"8\" refX=\"4\" refY=\"4\" orient=\"auto\"><path d=\"M0 4L8 0L8 8Z\" fill=\"#a83220\"/></marker></defs><rect x=\"160\" y=\"40\" width=\"620\" height=\"570\" class=\"guard\"/><g id=\"reserveLayer\"><circle cx=\"470\" cy=\"310\" r=\"270\" class=\"reserve\"/><text x=\"650\" y=\"115\" class=\"label\">450 mm reservation</text></g><g id=\"knownLayer\"><circle cx=\"470\" cy=\"310\" r=\"216\" class=\"known\"/><text x=\"500\" y=\"335\" class=\"label\">360 mm input</text></g><circle cx=\"470\" cy=\"310\" r=\"8\" class=\"axis\"/><text x=\"485\" y=\"300\" class=\"label\">J1 Z=500</text><g id=\"catchLayer\"><rect x=\"190\" y=\"575\" width=\"560\" height=\"16\" class=\"catch\"/><text x=\"200\" y=\"570\" class=\"label\">P0.3 tray top Z=26</text><line x1=\"760\" y1=\"526\" x2=\"760\" y2=\"575\" class=\"gap\"/><text x=\"650\" y=\"615\" class=\"label\">114 mm vertical separation</text></g><text x=\"520\" y=\"520\" class=\"label\">arm envelope bottom Z=140</text></svg></div></section>
<section><h2>Role correction</h2><article class=\"card role\"><p><strong>The current 320 × 820 × 50 mm floor tray is an object-catch envelope only.</strong></p><p>It receives zero arm-support, impact, energy or load credit. A separate passive arm receiver and the missing bidirectional hard stops still require exact contact geometry, material, compliant behavior, retention, force/travel/rebound limits, analysis and physical proof.</p></article></section>
<section><h2>Review the 3D evidence</h2><model-viewer src=\"../../../cad/hr-v0/generated/power-loss-envelope-p0.1/HR-V0_collapse-envelope-review.glb\" poster=\"../../../cad/hr-v0/generated/power-loss-envelope-p0.1/collapse-envelope-poster.svg\" camera-controls interaction-prompt=\"none\" shadow-intensity=\"0.5\" alt=\"Guard frame, floor object catch, straight-reference arm and conservative collapse cylinder\"></model-viewer></section>
<section><h2>What the pass does not mean</h2><div class=\"grid\"><article class=\"card\"><strong>Not complete geometry</strong><p>Gripper mechanism, foam object, cables and strain relief are absent.</p></article><article class=\"card\"><strong>Not a safety clearance</strong><p>The 90 mm residual is unallocated and may be consumed by missing geometry, tolerance, stopping, deformation and rebound.</p></article><article class=\"card\"><strong>Not physical proof</strong><p>All eighteen metrology rows remain NOT EXECUTED and NOT AUTHORIZED.</p></article><article class=\"card\"><strong>Gates remain partial</strong><p>EG-008 and EG-009 do not close.</p></article></div></section>
</main><footer><p>Project Button · {REVISION} · zero fabrication, motion, energization or functional-safety approval</p></footer><script>for(const [id,layer] of [['reserveToggle','reserveLayer'],['knownToggle','knownLayer'],['catchToggle','catchLayer']])document.getElementById(id).addEventListener('change',e=>document.getElementById(layer).style.display=e.target.checked?'':'none');</script></body></html>""", encoding="utf-8", newline="\n")
    write_generated_source_manifest()
    print(f"Generated {REVISION}: known B-Rep radius {known_radius:.6f} mm; controlled input {controlled_known_radius:.6f} mm; radial margin {radial_margin:.6f} mm")
    print(f"Known X {x_min:.6f}..{x_max:.6f} mm; guard fit inputs: {'PASS' if known_fit else 'FAIL'}")
    print(WARNING)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
