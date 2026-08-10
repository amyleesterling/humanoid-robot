"""Generate the P1.1 X430 moving-load and stop-load basis.

This package separates exact nominal CAD properties, catalog-mass geometry
estimates, program allocations, and unresolved physical quantities.  It is not
a structural, actuator, motion, fabrication, or energization release.
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
from OCP.BRepExtrema import BRepExtrema_DistShapeShape


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import generate_hr_v0_arm_architecture as p07  # noqa: E402
import generate_hr_v0_x430_elbow_architecture as p08  # noqa: E402
import generate_hr_v0_x430_lowered_forearm as p11  # noqa: E402


REVISION = "HR-V0-ARM-LOAD-P1.1-X430-CANDIDATE"
WARNING = (
    "PRELIMINARY - ANALYTICAL CANDIDATE ONLY - NOT APPROVED FOR QUOTATION, "
    "PROCUREMENT, FABRICATION, ASSEMBLY, MOTION, CONNECTION, OR ENERGIZATION"
)
OUT = ROOT / "cad" / "hr-v0" / "generated" / "arm-load-basis-p1.1-x430"
P11 = ROOT / "cad" / "hr-v0" / "generated" / "arm-architecture-p1.1-x430-lowered-forearm"
G = 9.80665
AL_DENSITY_G_MM3 = 2.70 / 1000.0
BEAM_MASS_PER_M_KG = 0.0428 * 0.45359237 / 0.0254
GRIPPER_ALLOCATION_G = 210.0
PAYLOAD_REQUIREMENT_G = 100.0
GRIPPER_POINT_Y_MM = p08.G1_Y
PAYLOAD_POINT_Y_MM = p08.OBJECT_CENTER_Y
POINT_Z_MM = p11.FOREARM_Z_OFFSET
GRAVITY_SCREEN_MULTIPLIER = 2.25
PROOF_MULTIPLIER = 3.0


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        raise ValueError(f"refusing to write empty CSV: {path}")
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def radius_bound_mm(shape: cq.Shape) -> float:
    box = shape.BoundingBox()
    return max(
        math.hypot(y - p11.J2_Y, z)
        for y in (box.ymin, box.ymax)
        for z in (box.zmin, box.zmax)
    )


def nominal_mass_properties(shape: cq.Shape, mass_g: float) -> dict[str, float]:
    center = shape.Center()
    ixx_com_g_mm2 = cq.Shape.matrixOfInertia(shape)[0][0] * mass_g / shape.Volume()
    ixx_j2_g_mm2 = ixx_com_g_mm2 + mass_g * ((center.y - p11.J2_Y) ** 2 + center.z**2)
    radius = radius_bound_mm(shape)
    return {
        "mass_g": mass_g,
        "y_from_j2_mm": center.y - p11.J2_Y,
        "z_mm": center.z,
        "ixx_com_kg_m2": ixx_com_g_mm2 * 1e-9,
        "ixx_j2_kg_m2": ixx_j2_g_mm2 * 1e-9,
        "support_radius_mm": radius,
        "point_support_ixx_kg_m2": mass_g * radius**2 * 1e-9,
    }


def point_ixx_kg_m2(mass_g: float, y_from_j2_mm: float, z_mm: float) -> float:
    return mass_g * (y_from_j2_mm**2 + z_mm**2) * 1e-9


def gravity_torque_nm(mass_g: float, y_mm: float, z_mm: float, q_deg: float) -> float:
    q = math.radians(q_deg)
    world_y_mm = y_mm * math.cos(q) - z_mm * math.sin(q)
    return mass_g / 1000.0 * G * world_y_mm / 1000.0


def main() -> int:
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)

    striker = p11.lowered_striker(p11.MOVING_FACE_Y)
    beam = p07.beam(p11.MOVING_FACE_Y + p08.PLATE_T, p08.FOREARM_BEAM_L).translate((0.0, 0.0, p11.FOREARM_Z_OFFSET))
    distal = p07.gripper_adapter(p11.MOVING_FACE_Y + p08.PLATE_T + p08.FOREARM_BEAM_L).translate((0.0, 0.0, p11.FOREARM_Z_OFFSET))
    fixed = p08.stop_adapter(p11.J2_Y - p08.S102_FIXED_FACE - p08.PLATE_T, p08.STOP_FIXED_WING_Z)

    striker_props = nominal_mass_properties(striker, striker.Volume() * AL_DENSITY_G_MM3)
    beam_mass_g = BEAM_MASS_PER_M_KG * (p08.FOREARM_BEAM_L / 1000.0) * 1000.0
    beam_props = nominal_mass_properties(beam, beam_mass_g)
    distal_props = nominal_mass_properties(distal, distal.Volume() * AL_DENSITY_G_MM3)
    known = [striker_props, beam_props, distal_props]
    known_mass_g = sum(item["mass_g"] for item in known)
    known_nominal_ixx = sum(item["ixx_j2_kg_m2"] for item in known)
    known_support_ixx = sum(item["point_support_ixx_kg_m2"] for item in known)

    gripper_y = GRIPPER_POINT_Y_MM - p11.J2_Y
    payload_y = PAYLOAD_POINT_Y_MM - p11.J2_Y
    gripper_point_ixx = point_ixx_kg_m2(GRIPPER_ALLOCATION_G, gripper_y, POINT_Z_MM)
    payload_point_ixx = point_ixx_kg_m2(PAYLOAD_REQUIREMENT_G, payload_y, POINT_Z_MM)
    reference_mass_g = known_mass_g + GRIPPER_ALLOCATION_G + PAYLOAD_REQUIREMENT_G
    reference_point_ixx = known_nominal_ixx + gripper_point_ixx + payload_point_ixx
    reference_support_ixx = known_support_ixx + gripper_point_ixx + payload_point_ixx

    component_rows = []
    for component_id, item, evidence_class, props, basis in (
        ("P11-C02", "lowered-forearm moving striker", "EXACT NOMINAL CAD + SPECIFIED DENSITY", striker_props, "P11 STEP volume/centroid/inertia; 6061 candidate density 2.70 g/cm3"),
        ("20-2040-050", "50 mm forearm member", "CATALOG MASS + UNIFORM COLLISION-ENVELOPE ESTIMATE", beam_props, "0.0428 lb/in line mass converted to 38.216050 g; nominal 20 x 40 x 50 mm envelope"),
        ("P11-DISTAL", "distal H104 adapter", "EXACT NOMINAL CAD + SPECIFIED DENSITY", distal_props, "P1.1 nominal CAD volume/centroid/inertia; 6061 candidate density 2.70 g/cm3"),
    ):
        component_rows.append({
            "component_id": component_id,
            "item": item,
            "evidence_class": evidence_class,
            "mass_g": f"{props['mass_g']:.6f}",
            "local_y_from_j2_mm": f"{props['y_from_j2_mm']:.6f}",
            "local_z_mm": f"{props['z_mm']:.6f}",
            "nominal_ixx_about_j2_kg_m2": f"{props['ixx_j2_kg_m2']:.12f}",
            "geometry_support_ixx_kg_m2": f"{props['point_support_ixx_kg_m2']:.12f}",
            "basis": basis,
            "state": "NOMINAL ANALYTICAL INPUT; RECEIVED MASS/COM/INERTIA OPEN",
        })
    component_rows.extend([
        {"component_id": "GRIP-ALLOC", "item": "complete gripper allocation at H104 datum", "evidence_class": "PROGRAM MASS/POINT ALLOCATION", "mass_g": f"{GRIPPER_ALLOCATION_G:.6f}", "local_y_from_j2_mm": f"{gripper_y:.6f}", "local_z_mm": f"{POINT_Z_MM:.6f}", "nominal_ixx_about_j2_kg_m2": f"{gripper_point_ixx:.12f}", "geometry_support_ixx_kg_m2": "SELECTION REQUIRED", "basis": "210 g program allocation placed at H104 datum; mechanism extent and own inertia absent", "state": "REFERENCE POINT MODEL ONLY - NOT MASS/INERTIA EVIDENCE"},
        {"component_id": "PAYLOAD-REQ", "item": "maximum soft payload", "evidence_class": "REQUIREMENT POINT MODEL", "mass_g": f"{PAYLOAD_REQUIREMENT_G:.6f}", "local_y_from_j2_mm": f"{payload_y:.6f}", "local_z_mm": f"{POINT_Z_MM:.6f}", "nominal_ixx_about_j2_kg_m2": f"{payload_point_ixx:.12f}", "geometry_support_ixx_kg_m2": "SELECTION REQUIRED", "basis": "100 g requirement placed at nominal object center; payload extent/retention/drop dynamics absent", "state": "REFERENCE POINT MODEL ONLY - NOT PHYSICAL EVIDENCE"},
        {"component_id": "FR12-H101", "item": "moving output frame and idler hardware", "evidence_class": "UNRESOLVED PHYSICAL ITEM", "mass_g": "SELECTION REQUIRED", "local_y_from_j2_mm": "SELECTION REQUIRED", "local_z_mm": "SELECTION REQUIRED", "nominal_ixx_about_j2_kg_m2": "SELECTION REQUIRED", "geometry_support_ixx_kg_m2": "SELECTION REQUIRED", "basis": "official geometry exists but no accepted mass distribution", "state": "OPEN - EXCLUDED FROM ALL NUMERIC TOTALS"},
        {"component_id": "MOVE-HARDWARE", "item": "fasteners bumper connectors strain relief and moving harness", "evidence_class": "UNRESOLVED PHYSICAL ITEMS", "mass_g": "SELECTION REQUIRED", "local_y_from_j2_mm": "SELECTION REQUIRED", "local_z_mm": "SELECTION REQUIRED", "nominal_ixx_about_j2_kg_m2": "SELECTION REQUIRED", "geometry_support_ixx_kg_m2": "SELECTION REQUIRED", "basis": "items not selected or measured", "state": "OPEN - EXCLUDED FROM ALL NUMERIC TOTALS"},
    ])
    write_csv(OUT / "component-mass-properties.csv", component_rows)

    gravity_rows = []
    for index in range(401):
        q = p11.Q2_LO + index * 0.25
        known_torque = sum(gravity_torque_nm(item["mass_g"], item["y_from_j2_mm"], item["z_mm"], q) for item in known)
        reference_torque = known_torque + gravity_torque_nm(GRIPPER_ALLOCATION_G, gripper_y, POINT_Z_MM, q) + gravity_torque_nm(PAYLOAD_REQUIREMENT_G, payload_y, POINT_Z_MM, q)
        gravity_rows.append({
            "j2_deg": f"{q:.2f}",
            "known_subset_gravity_torque_nm": f"{known_torque:.9f}",
            "reference_allocated_gravity_torque_nm": f"{reference_torque:.9f}",
            "reference_absolute_torque_nm": f"{abs(reference_torque):.9f}",
            "status": "INCOMPLETE REFERENCE - FR12-H101/HARDWARE/HARNESS/GRIPPER DISTRIBUTION EXCLUDED",
        })
    write_csv(OUT / "gravity-envelope.csv", gravity_rows)
    maximum_reference = max(gravity_rows, key=lambda row: float(row["reference_absolute_torque_nm"]))
    max_gravity_nm = float(maximum_reference["reference_absolute_torque_nm"])
    screen_moment_nm = max_gravity_nm * GRAVITY_SCREEN_MULTIPLIER
    proof_moment_nm = screen_moment_nm * PROOF_MULTIPLIER

    contact_angle_deg = float(json.loads((P11 / "architecture-summary.json").read_text(encoding="utf-8"))["stop_sequencing"]["nominal_first_contact_deg"])
    moved = p07.rotate_x(striker, contact_angle_deg, p11.J2_Y)
    extrema = BRepExtrema_DistShapeShape(fixed.wrapped, moved.wrapped)
    extrema.Perform()
    if extrema.Value() > 1e-6 or extrema.NbSolution() < 1:
        raise RuntimeError("P1.1 nominal stop contact could not be reconstructed")
    contact_radii = []
    for index in range(1, extrema.NbSolution() + 1):
        point = extrema.PointOnShape1(index)
        contact_radii.append(math.hypot(point.Y() - p11.J2_Y, point.Z()))
    contact_radius_mm = sum(contact_radii) / len(contact_radii)
    if max(contact_radii) - min(contact_radii) > 1e-5:
        raise RuntimeError("nominal stop rails do not share one lever radius")

    energy_rows = []
    inertia_cases = (
        ("KNOWN-NOMINAL", known_nominal_ixx, "exact custom CAD plus catalog-mass uniform beam-envelope estimate"),
        ("KNOWN-SUPPORT-BOUND", known_support_ixx, "known masses placed at farthest nominal geometry-support radii"),
        ("REFERENCE-POINT", reference_point_ixx, "known nominal plus 210 g gripper and 100 g payload point allocations"),
        ("REFERENCE-SUPPORT", reference_support_ixx, "known support bound plus gripper/payload point allocations; not a complete upper bound"),
    )
    for case_id, inertia, basis in inertia_cases:
        for speed_deg_s in (5.0, 10.0, 20.0, 30.0, 180.0):
            speed_rad_s = math.radians(speed_deg_s)
            energy = 0.5 * inertia * speed_rad_s**2
            energy_rows.append({
                "case_id": case_id,
                "ixx_about_j2_kg_m2": f"{inertia:.12f}",
                "speed_deg_s": f"{speed_deg_s:.3f}",
                "kinetic_energy_j": f"{energy:.12f}",
                "basis": basis,
                "status": "SENSITIVITY ONLY - SPEED/COMPLETE INERTIA/ROTOR REFLECTION/PEAK FORCE OPEN",
            })
    write_csv(OUT / "inertia-energy-sensitivity.csv", energy_rows)

    stop_rows = []
    for case_id, moment_nm, basis in (
        ("REFERENCE-GRAVITY", max_gravity_nm, "maximum incomplete reference gravity moment"),
        ("2.25X-GRAVITY-SCREEN", screen_moment_nm, "project analytical screen multiplier"),
        ("3X-PROOF-SCREEN", proof_moment_nm, "three times the 2.25x incomplete gravity screen"),
        ("MOMENT-1NM", 1.0, "sensitivity input"),
        ("MOMENT-3NM", 3.0, "sensitivity input"),
        ("MOMENT-5NM", 5.0, "sensitivity input"),
        ("MOMENT-10NM", 10.0, "sensitivity input"),
    ):
        stop_rows.append({
            "case_id": case_id,
            "input_type": "JOINT_MOMENT",
            "moment_nm": f"{moment_nm:.9f}",
            "energy_j": "",
            "stroke_mm": "",
            "nominal_contact_radius_mm": f"{contact_radius_mm:.9f}",
            "derived_average_force_n": f"{moment_nm * 1000.0 / contact_radius_mm:.9f}",
            "basis": basis,
            "status": "ONE-RAIL WORST-SHARE STATIC EQUIVALENT - NOT PEAK/IMPACT/CAPACITY",
        })
    reference_energies = {float(row["speed_deg_s"]): float(row["kinetic_energy_j"]) for row in energy_rows if row["case_id"] == "REFERENCE-SUPPORT"}
    for speed_deg_s in (10.0, 30.0, 180.0):
        energy = reference_energies[speed_deg_s]
        for stroke_mm in (0.5, 1.0, 2.0):
            stop_rows.append({
                "case_id": f"ENERGY-{speed_deg_s:.0f}DPS-{stroke_mm:.1f}MM",
                "input_type": "ENERGY_OVER_STROKE",
                "moment_nm": "",
                "energy_j": f"{energy:.12f}",
                "stroke_mm": f"{stroke_mm:.3f}",
                "nominal_contact_radius_mm": f"{contact_radius_mm:.9f}",
                "derived_average_force_n": f"{energy / (stroke_mm / 1000.0):.9f}",
                "basis": "REFERENCE-SUPPORT inertia sensitivity; excludes drivetrain/rotor/compliance and uses energy/stroke average",
                "status": "AVERAGE ENERGY FORCE ONLY - NOT PEAK/IMPACT/CAPACITY",
            })
    write_csv(OUT / "stop-load-sensitivity.csv", stop_rows)

    open_rows = [
        {"input_id": "LOAD-OPEN-01", "input": "FR12-H101/idler mass COM and inertia", "evidence_required": "calibrated received-subassembly measurement or accepted manufacturer mass-property record", "blocks": "complete mass COM inertia gravity and energy"},
        {"input_id": "LOAD-OPEN-02", "input": "moving fasteners bumper connectors guides strain relief and harness", "evidence_required": "selected BOM plus received mass/geometry and assembled routing", "blocks": "complete mass COM inertia collision and load"},
        {"input_id": "LOAD-OPEN-03", "input": "complete gripper mass distribution and payload retention", "evidence_required": "released mechanism CAD plus calibrated mass/COM/inertia and retained payload test", "blocks": "gripper allocation and reference point model"},
        {"input_id": "LOAD-OPEN-04", "input": "joint speed acceleration duty and trajectory", "evidence_required": "released limits plus HIL and bounded physical characterization", "blocks": "kinetic energy and actuator demand"},
        {"input_id": "LOAD-OPEN-05", "input": "reflected rotor/gear inertia efficiency backlash and compliance", "evidence_required": "manufacturer/application data and measured drive-line characterization", "blocks": "complete stop energy peak load and control model"},
        {"input_id": "LOAD-OPEN-06", "input": "bumper stiffness damping stroke retention temperature and life", "evidence_required": "selected part/material characterization plus dynamic proof", "blocks": "stop force deformation rebound and life"},
        {"input_id": "LOAD-OPEN-07", "input": "two-rail contact distribution tolerance friction and local stress", "evidence_required": "accepted nonlinear/contact analysis correlated to marked physical proof", "blocks": "rail/adapter/fastener capacity"},
        {"input_id": "LOAD-OPEN-08", "input": "continuous/cyclic actuator torque current and temperature", "evidence_required": "bounded duty test with external current and calibrated temperature evidence", "blocks": "X430 selection and worst-duty release"},
        {"input_id": "LOAD-OPEN-09", "input": "material allowables fatigue method proof multiplier and acceptance", "evidence_required": "MTR FAI qualified calculation review and signed proof procedure/results", "blocks": "structural fabrication and proof release"},
        {"input_id": "LOAD-OPEN-10", "input": "measurement uncertainty", "evidence_required": "approved instruments calibration and measurement-system analysis", "blocks": "physical comparison to calculated limits"},
    ]
    write_csv(OUT / "open-input-register.csv", [{**row, "state": "OPEN"} for row in open_rows])

    source_rows = [
        {"source_id": "LOAD-SRC-01", "path": str((P11 / "architecture-summary.json").relative_to(ROOT)).replace("\\", "/"), "sha256": sha256(P11 / "architecture-summary.json"), "use": "P1.1 transforms, stop and mass boundary"},
        {"source_id": "LOAD-SRC-02", "path": str((P11 / "HR-V0_arm_P1.1_X430_lowered_forearm_candidate.step").relative_to(ROOT)).replace("\\", "/"), "sha256": sha256(P11 / "HR-V0_arm_P1.1_X430_lowered_forearm_candidate.step"), "use": "controlled nominal assembly geometry"},
        {"source_id": "LOAD-SRC-03", "path": "tools/generate_hr_v0_x430_lowered_forearm.py", "sha256": sha256(ROOT / "tools" / "generate_hr_v0_x430_lowered_forearm.py"), "use": "reproducible P1.1 component construction"},
        {"source_id": "LOAD-SRC-04", "path": "cad/vendor/8020/README.md", "sha256": sha256(ROOT / "cad" / "vendor" / "8020" / "README.md"), "use": "controlled 20-2040 material and 0.0428 lb/in catalog-mass evidence"},
    ]
    write_csv(OUT / "source-register.csv", source_rows)

    flags = {
        "p1_1_selected": False,
        "x430_selected": False,
        "mass_closed": False,
        "com_closed": False,
        "inertia_closed": False,
        "continuous_torque_closed": False,
        "stop_load_closed": False,
        "structural_release": False,
        "motion_authorized": False,
        "fabrication_authorized": False,
        "connection_authorized": False,
        "energization_authorized": False,
    }
    summary = {
        "revision": REVISION,
        "warning": WARNING,
        "source_binding": {"count": len(source_rows), "status": "SHA256_BOUND_TO_R95"},
        "known_subset": {"mass_g": round(known_mass_g, 6), "nominal_ixx_about_j2_kg_m2": round(known_nominal_ixx, 12), "geometry_support_ixx_kg_m2": round(known_support_ixx, 12), "status": "NOMINAL/ESTIMATED INPUTS ONLY"},
        "reference_allocation": {"mass_g": round(reference_mass_g, 6), "point_model_ixx_about_j2_kg_m2": round(reference_point_ixx, 12), "support_plus_point_ixx_kg_m2": round(reference_support_ixx, 12), "status": "INCOMPLETE REFERENCE; NOT UPPER BOUND OR PHYSICAL RESULT"},
        "gravity": {"domain_deg": [p11.Q2_LO, p11.SOFT_LIMIT], "sample_increment_deg": 0.25, "maximum_reference_absolute_nm": round(max_gravity_nm, 9), "angle_of_maximum_deg": float(maximum_reference["j2_deg"]), "screen_2_25x_nm": round(screen_moment_nm, 9), "proof_3x_screen_nm": round(proof_moment_nm, 9), "status": "INCOMPLETE REFERENCE"},
        "stop": {"nominal_contact_deg": contact_angle_deg, "nominal_contact_radius_mm": round(contact_radius_mm, 9), "contact_solution_count": len(contact_radii), "proof_screen_one_rail_force_n": round(proof_moment_nm * 1000.0 / contact_radius_mm, 9), "status": "STATIC/ENERGY SENSITIVITY ONLY; PEAK/CAPACITY OPEN"},
        "counts": {"component_rows": len(component_rows), "gravity_rows": len(gravity_rows), "energy_rows": len(energy_rows), "stop_rows": len(stop_rows), "open_inputs": len(open_rows)},
        "release_flags": flags,
    }
    (OUT / "load-basis-summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8", newline="\n")
    (OUT / "package-status.json").write_text(json.dumps({"revision": REVISION, "state": "ANALYTICAL_CANDIDATE_NOT_SELECTED", "warning": WARNING, "release_flags": flags}, indent=2) + "\n", encoding="utf-8", newline="\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
