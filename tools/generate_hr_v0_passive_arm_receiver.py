"""Generate the R127 passive arm-receiver geometry and sizing candidate.

The package places a guided, shock-supported platen below the complete current
commanded envelope of the known P0.7 rigid bodies.  Product ratings and nominal
CAD screens are not application approval, structural allowables, physical
evidence, or authority to fabricate, move, connect, or energize anything.
"""

from __future__ import annotations

import csv
import json
import math
import shutil
from pathlib import Path

import cadquery as cq

import generate_hr_v0_arm_architecture as arm
import generate_hr_v0_collapse_envelope as collapse
import generate_hr_v0_guard_receiver as guard


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "cad" / "hr-v0" / "generated" / "passive-arm-receiver-p0.1"
GUIDE = ROOT / "release" / "hr-v0" / "passive-arm-receiver-p0.1" / "index.html"
FORM = ROOT / "tests" / "forms" / "hr-v0-passive-arm-receiver-template-p0.1.csv"
IDENTIFIER = "HR-V0-PASSIVE-ARM-RECEIVER-P0.1"
WARNING = "PRELIMINARY - DESIGN AND SIZING CANDIDATE ONLY - NOT APPROVED FOR FABRICATION, MOTION OR ENERGIZATION"

J1_MIN_DEG = -20.0
J1_MAX_DEG = 70.0
J2_MIN_DEG = 15.0
J2_MAX_DEG = 115.0
GRID_STEP_DEG = 0.25
SHOULDER_Z_MM = 500.0

PLATEN_X_MM = 180.0
PLATEN_Y_MM = 800.0
PLATEN_T_MM = 6.0
PAD_T_MM = 10.0
RECEIVER_TOP_Z_MM = 320.0
PLATEN_TOP_Z_MM = RECEIVER_TOP_Z_MM - PAD_T_MM
PLATEN_BOTTOM_Z_MM = PLATEN_TOP_Z_MM - PLATEN_T_MM
RAIL_X_CENTRES_MM = (-60.0, 60.0)
RAIL_Y_MM = 840.0
RAIL_X_MM = 20.0
RAIL_Z_MM = 40.0
RAIL_BOTTOM_Z_MM = 220.0
POST_Y_CENTRES_MM = (-420.0, 420.0)
SHOCK_Y_CENTRES_MM = (-300.0, 0.0, 300.0)
GUIDE_X_CENTRES_MM = (-70.0, 70.0)
GUIDE_Y_CENTRES_MM = (-350.0, 350.0)

MOVING_MASS_KG = 0.750
GRAVITY_BOUND_J = 5.295591
MA30_COUNT = 3
MA30_ENERGY_IN_LB = 31.0
IN_LB_TO_J = 0.1129848290276167
MA30_STROKE_IN = 0.32
IN_TO_MM = 25.4
LB_TO_KG = 0.45359237
MA30_MIN_EFFECTIVE_LB = 0.5
MA30_MAX_EFFECTIVE_LB = 31.0
MA30_MIN_VELOCITY_FTPS = 2.2
MA30_MAX_VELOCITY_FTPS = 14.6
FT_TO_M = 0.3048
STRUCTURAL_SCREEN_N = 2000.0
RAIL_I_CM4 = 4.5357
RAIL_I_MM4 = RAIL_I_CM4 * 10_000.0
RAIL_C_MM = 20.0
RAIL_E_MPA_TYPICAL = 68_900.0
RAIL_PUBLISHED_YIELD_MPA = 172.37


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


def corners(shape: cq.Shape) -> list[tuple[float, float, float]]:
    bounds = shape.BoundingBox()
    return [
        (x, y, z)
        for x in (bounds.xmin, bounds.xmax)
        for y in (bounds.ymin, bounds.ymax)
        for z in (bounds.zmin, bounds.zmax)
    ]


def rotate_point_x(point: tuple[float, float, float], angle_deg: float, origin_y: float = 0.0) -> tuple[float, float, float]:
    x, y, z = point
    angle = math.radians(angle_deg)
    relative_y = y - origin_y
    return (
        x,
        origin_y + relative_y * math.cos(angle) - z * math.sin(angle),
        relative_y * math.sin(angle) + z * math.cos(angle),
    )


def commanded_envelope() -> dict[str, object]:
    upper, fore = collapse.controlled_shapes()
    upper_points = {name: corners(shape) for name, shape in upper.items()}
    fore_points = {name: corners(shape) for name, shape in fore.items()}
    q1_values = [J1_MIN_DEG + GRID_STEP_DEG * index for index in range(round((J1_MAX_DEG - J1_MIN_DEG) / GRID_STEP_DEG) + 1)]
    q2_values = [J2_MIN_DEG + GRID_STEP_DEG * index for index in range(round((J2_MAX_DEG - J2_MIN_DEG) / GRID_STEP_DEG) + 1)]
    sampled_min = math.inf
    sampled_max = -math.inf
    y_min = math.inf
    y_max = -math.inf
    controlling: tuple[str, float, float | None] | None = None
    for q1 in q1_values:
        for name, points in upper_points.items():
            for point in points:
                _, y, z = rotate_point_x(point, q1)
                z += SHOULDER_Z_MM
                if z < sampled_min:
                    sampled_min = z
                    controlling = (name, q1, None)
                sampled_max = max(sampled_max, z)
                y_min = min(y_min, y)
                y_max = max(y_max, y)
        for q2 in q2_values:
            for name, points in fore_points.items():
                for point in points:
                    relative = rotate_point_x(point, q2, arm.J2_Y)
                    _, y, z = rotate_point_x(relative, q1)
                    z += SHOULDER_Z_MM
                    if z < sampled_min:
                        sampled_min = z
                        controlling = (name, q1, q2)
                    sampled_max = max(sampled_max, z)
                    y_min = min(y_min, y)
                    y_max = max(y_max, y)

    half_step_rad = math.radians(GRID_STEP_DEG / 2.0)
    upper_radius = max(arm.bbox_radius_about_x(shape) for shape in upper.values())
    fore_local_radius = max(arm.bbox_radius_about_x(shape, arm.J2_Y) for shape in fore.values())
    continuous_cell_motion = max(
        upper_radius * half_step_rad,
        (arm.J2_Y + 2.0 * fore_local_radius) * half_step_rad,
    )
    continuous_min = sampled_min - continuous_cell_motion
    return {
        "sampled_min_z_mm": sampled_min,
        "sampled_max_z_mm": sampled_max,
        "continuous_cell_motion_bound_mm": continuous_cell_motion,
        "continuous_min_z_bound_mm": continuous_min,
        "receiver_clearance_mm": continuous_min - RECEIVER_TOP_Z_MM,
        "sampled_y_min_mm": y_min,
        "sampled_y_max_mm": y_max,
        "controlling_component": controlling[0] if controlling else "",
        "controlling_q1_deg": controlling[1] if controlling else None,
        "controlling_q2_deg": controlling[2] if controlling else None,
        "sample_count": len(q1_values) * len(q2_values),
    }


def receiver_shapes() -> dict[str, cq.Shape]:
    shapes: dict[str, cq.Shape] = {}
    for index, x_center in enumerate(RAIL_X_CENTRES_MM, 1):
        shapes[f"FIXED-RAIL-{index}"] = box(RAIL_X_MM, RAIL_Y_MM, RAIL_Z_MM, x_center - RAIL_X_MM / 2, -RAIL_Y_MM / 2, RAIL_BOTTOM_Z_MM)
    for x_index, x_center in enumerate(RAIL_X_CENTRES_MM, 1):
        for y_index, y_center in enumerate(POST_Y_CENTRES_MM, 1):
            shapes[f"SUPPORT-POST-{x_index}-{y_index}"] = box(20.0, 20.0, RAIL_BOTTOM_Z_MM - 20.0, x_center - 10.0, y_center - 10.0, 20.0)
    for index, y_center in enumerate(SHOCK_Y_CENTRES_MM, 1):
        shapes[f"SHOCK-MOUNT-{index}"] = box(160.0, 40.0, 6.0, -80.0, y_center - 20.0, RAIL_BOTTOM_Z_MM + RAIL_Z_MM)
        shapes[f"MA30M-ENVELOPE-{index}"] = cq.Solid.makeCylinder(4.0, PLATEN_BOTTOM_Z_MM - (RAIL_BOTTOM_Z_MM + RAIL_Z_MM + 6.0), cq.Vector(0.0, y_center, RAIL_BOTTOM_Z_MM + RAIL_Z_MM + 6.0), cq.Vector(0, 0, 1))
    for x_center in GUIDE_X_CENTRES_MM:
        for y_center in GUIDE_Y_CENTRES_MM:
            shapes[f"GUIDE-ENVELOPE-{x_center:g}-{y_center:g}"] = cq.Solid.makeCylinder(4.0, PLATEN_BOTTOM_Z_MM - (RAIL_BOTTOM_Z_MM + RAIL_Z_MM), cq.Vector(x_center, y_center, RAIL_BOTTOM_Z_MM + RAIL_Z_MM), cq.Vector(0, 0, 1))
    shapes["MOVING-PLATEN"] = box(PLATEN_X_MM, PLATEN_Y_MM, PLATEN_T_MM, -PLATEN_X_MM / 2, -PLATEN_Y_MM / 2, PLATEN_BOTTOM_Z_MM)
    shapes["COMPLIANT-CONTACT-LAYER-SELECTION-REQUIRED"] = box(PLATEN_X_MM, PLATEN_Y_MM, PAD_T_MM, -PLATEN_X_MM / 2, -PLATEN_Y_MM / 2, PLATEN_TOP_Z_MM)
    return shapes


def pose_shapes(q1_deg: float, q2_deg: float) -> dict[str, cq.Shape]:
    upper, fore = collapse.controlled_shapes()
    result = {name: arm.rotate_x(shape, q1_deg).translate((0, 0, SHOULDER_Z_MM)) for name, shape in upper.items()}
    result.update({name: arm.rotate_x(arm.rotate_x(shape, q2_deg, arm.J2_Y), q1_deg).translate((0, 0, SHOULDER_Z_MM)) for name, shape in fore.items()})
    return result


def main() -> int:
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)
    envelope = commanded_envelope()
    ma30_each_j = MA30_ENERGY_IN_LB * IN_LB_TO_J
    ma30_total_j = MA30_COUNT * ma30_each_j
    stroke_mm = MA30_STROKE_IN * IN_TO_MM
    effective_each_kg = MOVING_MASS_KG / MA30_COUNT
    energy_ratio = ma30_total_j / GRAVITY_BOUND_J
    rail_each_load_n = STRUCTURAL_SCREEN_N / 2.0
    rail_span_mm = RAIL_Y_MM
    rail_moment_nmm = rail_each_load_n * rail_span_mm / 4.0
    rail_modulus_mm3 = RAIL_I_MM4 / RAIL_C_MM
    rail_stress_mpa = rail_moment_nmm / rail_modulus_mm3
    rail_deflection_mm = rail_each_load_n * rail_span_mm**3 / (48.0 * RAIL_E_MPA_TYPICAL * RAIL_I_MM4)

    envelope_rows = [
        {"screen_id":"REC-ENV-001","quantity":"sampled known-B-Rep minimum Z","value":f"{envelope['sampled_min_z_mm']:.6f}","unit":"mm","method":"0.25 degree grid over J1 -20..70 and J2 15..115 using conservative source AABB corners","result":"INPUT"},
        {"screen_id":"REC-ENV-002","quantity":"continuous between-grid motion deduction","value":f"{envelope['continuous_cell_motion_bound_mm']:.6f}","unit":"mm","method":"Lipschitz radial displacement over half-cell for both parallel X axes","result":"CONSERVATIVE DEDUCTION"},
        {"screen_id":"REC-ENV-003","quantity":"continuous known-B-Rep lower Z bound","value":f"{envelope['continuous_min_z_bound_mm']:.6f}","unit":"mm","method":"sampled minimum minus cell-motion deduction","result":"PASS KNOWN BREP ONLY"},
        {"screen_id":"REC-ENV-004","quantity":"receiver contact-surface top Z","value":f"{RECEIVER_TOP_Z_MM:.6f}","unit":"mm","method":"candidate geometry","result":"INPUT"},
        {"screen_id":"REC-ENV-005","quantity":"nominal continuous commanded-workspace clearance","value":f"{envelope['receiver_clearance_mm']:.6f}","unit":"mm","method":"continuous lower Z bound minus receiver top","result":"PASS KNOWN BREP ONLY"},
        {"screen_id":"REC-ENV-006","quantity":"receiver height above full-collapse-envelope bottom","value":f"{RECEIVER_TOP_Z_MM - 140.0:.6f}","unit":"mm","method":"receiver top minus R126 controlled bottom","result":"INTERCEPTS LOWER REGION GEOMETRICALLY"},
    ]
    write_csv(OUT / "commanded-envelope-screen.csv", envelope_rows)

    geometry_rows = [
        {"item":"moving platen","quantity":1,"candidate_geometry_mm":"180 X x 800 Y x 6 Z","datum":"bottom Z 304; top Z 310","selection_state":"MATERIAL LOCAL CONTACT BENDING EDGE AND FASTENERS SELECTION REQUIRED"},
        {"item":"compliant contact layer","quantity":1,"candidate_geometry_mm":"180 X x 800 Y x 10 Z","datum":"top Z 320","selection_state":"MATERIAL FORCE-TRAVEL ENERGY REBOUND RETENTION AND LIFE SELECTION REQUIRED"},
        {"item":"80/20 20-2040 fixed rail","quantity":2,"candidate_geometry_mm":"20 X x 840 Y x 40 Z","datum":"bottom Z 220; x centres +/-60","selection_state":"EXACT PROFILE CANDIDATE; CUT END JOINT AND PROOF OPEN"},
        {"item":"support post envelope","quantity":4,"candidate_geometry_mm":"20 X x 20 Y x 200 Z","datum":"x +/-60; y +/-420; bottom Z 20","selection_state":"PROFILE JOINT BASE ATTACHMENT AND PROOF SELECTION REQUIRED"},
        {"item":"ACE MA30M adjustable shock absorber","quantity":3,"candidate_geometry_mm":"M8x1; 8.128 stroke; extended envelope per 21_22_0019","datum":"y -300/0/+300; axial vertical","selection_state":"EVALUATION CANDIDATE ONLY; ACE APPLICATION APPROVAL AND RECEIVED IDENTITY REQUIRED"},
        {"item":"platen linear guide","quantity":4,"candidate_geometry_mm":"8 diameter planning envelope","datum":"x +/-70; y +/-350","selection_state":"EXACT SHAFT BUSHING RETENTION LOAD ALIGNMENT AND LIFE SELECTION REQUIRED"},
    ]
    write_csv(OUT / "receiver-geometry.csv", geometry_rows)

    absorber_rows = [
        {"record":"ABS-001","input":"MA30M published energy per cycle","value":f"{ma30_each_j:.6f}","unit":"J","source":"ACE live MA30M product page; 31 in-lb/cycle","disposition":"CATALOG ENDPOINT ONLY"},
        {"record":"ABS-002","input":"three-unit arithmetic capacity","value":f"{ma30_total_j:.6f}","unit":"J","source":"3 x ABS-001","disposition":"LOAD SHARING AND APPLICATION APPROVAL REQUIRED"},
        {"record":"ABS-003","input":"capacity / gravitational allocation","value":f"{energy_ratio:.6f}","unit":"ratio","source":"ABS-002 / 5.295591 J","disposition":"NOT AN ACCEPTED DESIGN FACTOR"},
        {"record":"ABS-004","input":"nominal mass share","value":f"{effective_each_kg:.6f}","unit":"kg/unit","source":"0.750 kg / 3","disposition":"EFFECTIVE MASS MUST BE CALCULATED; PLATEN AND COUPLING DYNAMICS OMITTED"},
        {"record":"ABS-005","input":"published effective-weight range","value":f"{MA30_MIN_EFFECTIVE_LB*LB_TO_KG:.6f}..{MA30_MAX_EFFECTIVE_LB*LB_TO_KG:.6f}","unit":"kg/unit","source":"ACE live MA30M product page; 0.5..31 lb","disposition":"NOMINAL SHARE FALLS INSIDE; APPLICATION NOT VALIDATED"},
        {"record":"ABS-006","input":"published impact-velocity range","value":f"{MA30_MIN_VELOCITY_FTPS*FT_TO_M:.6f}..{MA30_MAX_VELOCITY_FTPS*FT_TO_M:.6f}","unit":"m/s","source":"ACE live MA30M product page; 2.2..14.6 ft/s","disposition":"ACTUAL CONTACT VELOCITY UNKNOWN; SLOW CASE MAY FALL BELOW RANGE"},
        {"record":"ABS-007","input":"stroke","value":f"{stroke_mm:.6f}","unit":"mm","source":"ACE live MA30M product page; 0.32 in","disposition":"FULL STROKE AND POSITIVE-STOP CLEARANCE REQUIRED"},
    ]
    write_csv(OUT / "absorber-application-screen.csv", absorber_rows)

    load_rows = [
        {"record":"LOAD-001","quantity":"provisional vertical platen input","value":f"{STRUCTURAL_SCREEN_N:.6f}","unit":"N","method":"round candidate screen above full-capacity average force; peak force remains unknown","result":"NOT AN ACCEPTANCE LOAD"},
        {"record":"LOAD-002","quantity":"load per rail","value":f"{rail_each_load_n:.6f}","unit":"N","method":"ideal equal sharing","result":"UNEQUAL SHARING OPEN"},
        {"record":"LOAD-003","quantity":"maximum simple-span rail moment","value":f"{rail_moment_nmm:.6f}","unit":"N mm","method":"each rail simply supported; central point load","result":"SCREEN"},
        {"record":"LOAD-004","quantity":"nominal strong-axis bending stress","value":f"{rail_stress_mpa:.6f}","unit":"MPa","method":"M c / I with published Ix 4.5357 cm4","result":"BELOW PUBLISHED YIELD; NOT AN ALLOWABLE PASS"},
        {"record":"LOAD-005","quantity":"nominal simple-span deflection","value":f"{rail_deflection_mm:.6f}","unit":"mm","method":"P L3 / 48 E I; E=68.9 GPa typical","result":"TYPICAL-PROPERTY SCREEN ONLY"},
        {"record":"LOAD-006","quantity":"ideal reaction per rail end","value":f"{STRUCTURAL_SCREEN_N/4.0:.6f}","unit":"N","method":"two rails; two supports each","result":"JOINT/POST/BASE CAPACITY OPEN"},
        {"record":"LOAD-007","quantity":"80/20 published yield comparison","value":f"{RAIL_PUBLISHED_YIELD_MPA:.6f}","unit":"MPa","method":"live 20-2040 page","result":"PUBLISHED VALUE; NOT PROJECT ALLOWABLE"},
    ]
    write_csv(OUT / "receiver-load-path-screen.csv", load_rows)

    sources = [
        {"source_id":"REC-SRC-001","manufacturer":"ACE Controls Inc.","title":"MA30M live product page","document_revision_date":"live page; no formal revision exposed","url":"https://www.acecontrols.com/us/products/automation-control/miniature-shock-absorbers/ma30-to-ma900/ma30m.html","accessed":"2026-08-09","use":"31 in-lb/cycle; 0.32 in stroke; 0.5..31 lb effective weight; 2.2..14.6 ft/s impact velocity; integrated positive stop","boundary":"catalog data only; exact application and factory approval required"},
        {"source_id":"REC-SRC-002","manufacturer":"ACE Stossdaempfer GmbH","title":"MA30 to MA900 operating and mounting instructions","document_revision_date":"21_22_0019; Stand 03.2021; Issue 05.2022","url":"https://www.acecontrols.com/media/msimages/pdf/ACE_MA30-MA900_Operating-Mounting_EN_21_22_0019.pdf","accessed":"2026-08-09","use":"parallel use permitted; axial loading; <=2 degree side-load angle; sizing inputs; additional safety elements required where failure can injure","boundary":"manufacturer instructions do not approve this project application"},
        {"source_id":"REC-SRC-003","manufacturer":"80/20 Inc.","title":"20-2040 product page","document_revision_date":"live page; no formal revision exposed","url":"https://8020.net/20-2040.html","accessed":"2026-08-07","use":"20x40 6063-T6 profile; Ix 4.5357 cm4; published 172.37 MPa yield comparison","boundary":"received identity, joints, cuts, design allowables and proof remain open"},
        {"source_id":"REC-SRC-004","manufacturer":"Project Button","title":"R125/R126 controlled inputs","document_revision_date":"2026-08-08","url":"../../../../docs/hr-v0-power-loss-containment-p0.1.md","accessed":"2026-08-09","use":"0.750 kg, 5.295591 J and 360 mm collapse input","boundary":"gravitational-only allocation; not impact prediction or rating"},
    ]
    write_csv(OUT / "source-register.csv", sources)

    holds = [
        ("REC-HOLD-001","complete moving geometry","gripper mechanism, foam object, cables and strain relief"),
        ("REC-HOLD-002","as-built dynamics","mass, COM, inertia, backlash, friction, contact velocity and coupling"),
        ("REC-HOLD-003","absorber application","ACE sizing/application approval, exact model/adjustment, parallel load sharing, temperature and life"),
        ("REC-HOLD-004","guided platen","exact guides, alignment, side load, binding, retention and failure containment"),
        ("REC-HOLD-005","contact layer","material, thickness, force-travel, energy, rebound, wear, flammability and retention"),
        ("REC-HOLD-006","platen structure","material, local contact, bending, edges, fasteners, fatigue and impact"),
        ("REC-HOLD-007","subframe load path","rail allowables, cuts, brackets, posts, base/guard joints, anchors and proof"),
        ("REC-HOLD-008","joint boundaries","J1 minimum/maximum and J2 minimum stops plus physical J2 positive acceptance"),
        ("REC-HOLD-009","guard interaction","access, pinch, rebound, final-rest, recovery and panel/retention containment"),
        ("REC-HOLD-010","continued drive/stored energy","drive persistence, regeneration, elastic and detached-part cases"),
        ("REC-HOLD-011","physical evidence","FAI, metrology, protected drop/backdrive/fault tests and uncertainty"),
        ("REC-HOLD-012","qualified disposition","mechanical and functional-safety review plus controlled work authorization"),
    ]
    write_csv(OUT / "receiver-closure-holds.csv", [{"hold_id":i,"scope":s,"evidence_required":e,"status":"OPEN - BLOCKS FABRICATION MOTION AND ENERGIZATION"} for i,s,e in holds])

    evidence_items = [
        "received MA30M identity and date code", "ACE application calculation/approval", "received 20-2040 identity and cut length",
        "platen material certificate", "contact-layer identity", "guide identity", "as-built receiver top Z", "as-built platen X/Y envelope",
        "as-built shock stroke", "guide parallelism and free travel", "unpowered commanded-workspace clearance", "static 25 percent load",
        "static 50 percent load", "static 100 percent accepted proof load", "platen local deformation", "rail deflection", "post/joint slip",
        "shock side-load alignment", "single-shock failure containment", "first low-energy contact", "maximum authorized gravitational case",
        "rebound and secondary contact", "object escape", "cable/connector damage", "final-rest access", "restart prevention",
        "post-test leakage/return", "qualified disposition",
    ]
    write_csv(FORM, [{"record_id":f"REC-EVID-{index:03d}","date":"","inspector":"","repo_commit":"","configuration_id":"","evidence":item,"nominal_or_limit":"SELECTION REQUIRED","instrument":"SELECTION REQUIRED","calibration_reference":"","measured_value":"","unit":"SELECTION REQUIRED","uncertainty":"","photo_or_log_reference":"","deviation_reference":"","result":"NOT EXECUTED","authorization":"NOT AUTHORIZED","warning":WARNING} for index,item in enumerate(evidence_items,1)])

    summary = {
        "identifier": IDENTIFIER,
        "warning": WARNING,
        "parent_revisions": [arm.REVISION, collapse.REVISION, guard.REVISION, "HR-V0-POWERLOSS-P0.1"],
        "commanded_envelope": envelope,
        "receiver_top_z_mm": RECEIVER_TOP_Z_MM,
        "platen_envelope_mm": [PLATEN_X_MM, PLATEN_Y_MM, PLATEN_T_MM],
        "nominal_clearance_mm": round(float(envelope["receiver_clearance_mm"]), 6),
        "absorber_candidate": {"type":"ACE MA30M","quantity":MA30_COUNT,"catalog_total_energy_j":round(ma30_total_j,6),"catalog_to_gravity_ratio":round(energy_ratio,6),"stroke_mm":stroke_mm,"status":"EVALUATION ONLY - APPLICATION APPROVAL REQUIRED"},
        "structural_screen": {"input_n":STRUCTURAL_SCREEN_N,"rail_stress_mpa":round(rail_stress_mpa,6),"rail_deflection_mm":round(rail_deflection_mm,6),"status":"NOMINAL SCREEN ONLY - NO ALLOWABLE OR JOINT PASS"},
        "closure_holds": len(holds),
        "physical_records": len(evidence_items),
        "gate_state": "EG-008 AND EG-009 REMAIN PARTIAL",
    }
    (OUT / "receiver-summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")

    receiver = receiver_shapes()
    worst_pose = pose_shapes(J1_MIN_DEG, J2_MIN_DEG)
    assembly = cq.Assembly(name="HR_V0_PASSIVE_ARM_RECEIVER_REVIEW_ONLY")
    guard.add_frame(assembly)
    for name, shape in receiver.items():
        if name.startswith("MA30M"):
            color = cq.Color(0.78, 0.18, 0.12)
        elif name.startswith("GUIDE"):
            color = cq.Color(0.30, 0.36, 0.44)
        elif name == "COMPLIANT-CONTACT-LAYER-SELECTION-REQUIRED":
            color = cq.Color(0.96, 0.72, 0.20)
        elif name == "MOVING-PLATEN":
            color = cq.Color(0.45, 0.78, 0.94)
        else:
            color = cq.Color(0.18, 0.35, 0.55)
        assembly.add(shape, name=name, color=color)
    for name, shape in worst_pose.items():
        assembly.add(shape, name=f"COMMAND-BOUNDARY-{name}", color=cq.Color(0.96, 0.58, 0.08))
    assembly.save(str(OUT / "HR-V0_passive-arm-receiver-review.glb"))
    step_path = OUT / "HR-V0_passive-arm-receiver-candidate.step"
    cq.exporters.export(cq.Compound.makeCompound(list(receiver.values())), str(step_path))
    normalize_step(step_path)

    poster = f'''<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="700" viewBox="0 0 1200 700"><style>text{{font-family:Arial,sans-serif;fill:#102a43;font-size:21px}}.t{{font-size:38px;font-weight:700}}.w{{font-size:18px;font-weight:700;fill:#7d2b1d}}.g{{fill:#e4f6ff;stroke:#082b55;stroke-width:7}}.r{{fill:#7dd3fc;stroke:#075b9b;stroke-width:4}}.p{{fill:#f4b942;stroke:#8a5b00;stroke-width:4}}.a{{fill:none;stroke:#d97706;stroke-width:18;stroke-linecap:round}}</style><rect width="1200" height="700" fill="#f7fbff"/><text x="55" y="60" class="t">Passive arm-receiver candidate</text><text x="55" y="96" class="w">PRELIMINARY - THREE MA30M EVALUATION CANDIDATES - ZERO FABRICATION OR SAFETY CREDIT</text><rect x="260" y="125" width="680" height="520" class="g"/><rect x="395" y="465" width="410" height="34" class="p"/><rect x="410" y="505" width="25" height="110" class="r"/><rect x="765" y="505" width="25" height="110" class="r"/><path d="M600 330 L725 280 L790 350" class="a"/><circle cx="600" cy="330" r="8" fill="#082b55"/><text x="615" y="320">J1 Z=500</text><text x="820" y="490">receiver top Z=320</text><text x="820" y="365">known commanded minimum &gt; {envelope['continuous_min_z_bound_mm']:.1f}</text><text x="55" y="675">Complete gripper/cables, guides, contact layer, stops, dynamics, joints, proof and qualified review remain open.</text></svg>'''
    (OUT / "receiver-poster.svg").write_text(poster, encoding="utf-8", newline="\n")

    GUIDE.parent.mkdir(parents=True, exist_ok=True)
    GUIDE.write_text(f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>HR-V0 passive arm receiver</title><style>:root{{--deep:#041a35;--navy:#082b55;--sky:#7dd3fc;--pale:#e4f6ff;--gold:#f4b942;--ink:#102a43;--red:#a83220;--line:#9ccfe8}}*{{box-sizing:border-box}}body{{margin:0;background:var(--pale);color:var(--ink);font:17px/1.55 system-ui,"Segoe UI",sans-serif}}header{{background:linear-gradient(135deg,var(--deep),var(--navy));color:white;padding:clamp(34px,6vw,72px) 20px}}header>div,main{{max-width:1120px;margin:auto}}h1{{font-size:clamp(36px,6vw,64px);line-height:1.05;margin:.2em 0}}h2{{font-size:clamp(27px,3.5vw,39px);line-height:1.15;color:var(--navy)}}.eyebrow{{font-size:14px;font-weight:850;color:var(--sky)}}.warning{{background:var(--gold);color:#17243a;border:3px solid #8a5b00;padding:15px 18px;font-weight:850}}main{{padding:30px 20px 80px}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(245px,1fr));gap:18px}}.card,.diagram{{background:white;border:2px solid var(--line);border-radius:16px;padding:20px;box-shadow:0 3px 0 #bddbea}}.metric{{font-size:clamp(34px,6vw,55px);font-weight:900;color:#075b9b}}.hold{{border-left:9px solid var(--gold)}}svg{{width:100%;height:auto}}.guard{{fill:#e4f6ff;stroke:var(--navy);stroke-width:6}}.arm{{fill:none;stroke:#d97706;stroke-width:18;stroke-linecap:round}}.receiver{{fill:var(--gold);stroke:#8a5b00;stroke-width:4}}.clearance{{stroke:#a83220;stroke-width:4;stroke-dasharray:10 7}}.label{{font:700 16px system-ui;fill:var(--ink)}}model-viewer{{width:100%;height:520px;background:#dff3ff;border:2px solid var(--line);border-radius:16px}}table{{width:100%;border-collapse:collapse;background:white}}th,td{{padding:13px;border:1px solid #8aa8ba;text-align:left;vertical-align:top;font-size:16px}}th{{background:#d5effc}}footer{{background:var(--deep);color:white;padding:30px 20px}}footer p{{max-width:1120px;margin:auto}}@media(max-width:760px){{body{{font-size:16px}}model-viewer{{height:430px}}.table{{overflow:auto}}}}</style><script type="module" src="../../vendor/model-viewer/4.1.0/model-viewer.min.js"></script></head><body><header><div><p class="warning">{WARNING}</p><p class="eyebrow">{IDENTIFIER}</p><h1>A raised passive receiver now has a controlled design zone.</h1><p>The candidate sits below the known commanded workspace and above the uncontrolled lower-collapse region. Three guided adjustable shock absorbers are evaluation candidates, not an approved application.</p></div></header><main><section><h2>Controlled geometry</h2><div class="grid"><article class="card"><div class="metric">{envelope['continuous_min_z_bound_mm']:.3f} mm</div><p>Continuous lower bound for the known rigid bodies in the current command domain.</p></article><article class="card"><div class="metric">{envelope['receiver_clearance_mm']:.3f} mm</div><p>Nominal known-geometry clearance above the receiver contact surface.</p></article><article class="card"><div class="metric">{ma30_total_j:.3f} J</div><p>Arithmetic catalog capacity of three MA30M candidates. It is not an application rating.</p></article></div></section><section><h2>Front-elevation logic</h2><div class="diagram"><svg viewBox="0 0 940 650" role="img" aria-labelledby="t d"><title id="t">Raised passive receiver below the commanded arm workspace</title><desc id="d">Guard, shoulder axis, boundary arm pose and receiver at Z 320 millimetres.</desc><rect x="160" y="35" width="620" height="580" class="guard"/><path d="M470 300 L620 240 L710 330" class="arm"/><circle cx="470" cy="300" r="8" fill="#082b55"/><rect x="330" y="480" width="300" height="32" class="receiver"/><line x1="675" y1="395" x2="675" y2="480" class="clearance"/><text x="485" y="290" class="label">J1 Z=500</text><text x="640" y="345" class="label">commanded known geometry</text><text x="640" y="505" class="label">receiver top Z=320</text><text x="690" y="440" class="label">{envelope['receiver_clearance_mm']:.1f} mm nominal residual</text><text x="185" y="585" class="label">Object catch remains separate at Z=26</text></svg></div></section><section><h2>Candidate energy chain</h2><div class="table"><table><thead><tr><th>Item</th><th>Candidate input</th><th>What remains open</th></tr></thead><tbody><tr><td>Moving allocation</td><td>0.750 kg; 5.295591 J gravitational-only</td><td>As-built mass, inertia, contact speed, drive persistence and stored energy.</td></tr><tr><td>Absorbers</td><td>3 × ACE MA30M; 31 in-lb/cycle each; 0.32 in stroke</td><td>ACE sizing/application approval, actual effective mass and speed, adjustment, load sharing, temperature and life.</td></tr><tr><td>Guided platen</td><td>180 × 800 mm; top Z=320; four guide envelopes</td><td>Exact platen, guides, contact layer, side load, local impact and retention.</td></tr><tr><td>Fixed subframe</td><td>Two 840 mm 20-2040 rails plus four posts</td><td>Joints, posts, base/guard transfer, anchors, peak force, allowables and proof.</td></tr></tbody></table></div></section><section><h2>Review the 3D candidate</h2><model-viewer src="../../../cad/hr-v0/generated/passive-arm-receiver-p0.1/HR-V0_passive-arm-receiver-review.glb" poster="../../../cad/hr-v0/generated/passive-arm-receiver-p0.1/receiver-poster.svg" camera-controls interaction-prompt="none" shadow-intensity="0.5" alt="Guard frame, passive receiver and current lower commanded arm pose"></model-viewer></section><section><h2>Why this still fails closed</h2><div class="grid"><article class="card hold"><strong>Incomplete moving body</strong><p>Gripper mechanism, object, cables and strain relief remain outside the envelope proof.</p></article><article class="card hold"><strong>Catalog data is not approval</strong><p>ACE must accept the real mass, velocity, angle, parallel-sharing, cycle and environmental application.</p></article><article class="card hold"><strong>Load path is unfinished</strong><p>Platen, guides, brackets, posts, base and anchors lack accepted peak-force and proof evidence.</p></article><article class="card hold"><strong>Physical proof is absent</strong><p>All 28 evidence rows remain NOT EXECUTED and NOT AUTHORIZED. EG-008 and EG-009 remain partial.</p></article></div></section></main><footer><p>Project Button · {IDENTIFIER} · zero fabrication, motion, energization or functional-safety approval</p></footer></body></html>''', encoding="utf-8", newline="\n")

    collapse.write_generated_source_manifest()
    print(f"Generated {IDENTIFIER}: continuous commanded minimum Z {envelope['continuous_min_z_bound_mm']:.6f} mm; receiver clearance {envelope['receiver_clearance_mm']:.6f} mm")
    print(f"Three MA30M arithmetic catalog capacity {ma30_total_j:.6f} J / {GRAVITY_BOUND_J:.6f} J = {energy_ratio:.6f}; application approval remains required")
    print(WARNING)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
