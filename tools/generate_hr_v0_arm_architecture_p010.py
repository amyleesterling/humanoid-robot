#!/usr/bin/env python3
"""Generate the R270 P0.10 integral-boss J2-stop development candidate.

This is deliberately an unselected geometry and calculation screen.  It
supersedes the non-conservative R269 torque-to-force model, but it does not
provide a fabrication release, a structural allowable, safety credit, or
authority to energize.
"""
from __future__ import annotations

import csv
import json
import math
from pathlib import Path

import cadquery as cq
from OCP.BRepExtrema import BRepExtrema_DistShapeShape

import generate_hr_v0_arm_architecture as arm
import generate_hr_v0_arm_architecture_p09 as p09

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "cad/hr-v0/generated/arm-architecture-p0.10-bossed-stop"
REV = "HR-V0-ARM-ARCH-P0.10-BOSSED-STOP-CANDIDATE"
STOP_REV = "HR-V0-J2-STOP-P0.3"
LOAD_REV = "HR-V0-J2-STOP-LOAD-MODEL-P0.2"
WARNING = "PRELIMINARY - NOT APPROVED FOR PROCUREMENT, QUOTATION, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION"

STRIKER_INNER = 35.0
STRIKER_OUTER = 51.0
CATCH_INNER = 34.0
CATCH_OUTER = 52.0
STOCK_T = 15.875
MIN_STRUCTURAL_T = 15.0
BACK_EXTENSION = STOCK_T - arm.PLATE_T
PROJECT_MTR_THRESHOLD_MPA = 240.0


def write_csv(path: Path, records: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(records[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(records)


def boss_profile(y0: float, *, outer: float, inner: float, top: float) -> cq.Shape:
    """Two rear bosses; central interface lands remain at the original stack."""
    shapes: list[cq.Shape] = []
    for sign in (-1.0, 1.0):
        points = [
            (sign * 32.0, -20.0),
            (sign * outer, -20.0),
            (sign * outer, top),
            (sign * inner, top),
            (sign * inner, -7.0),
            (sign * 32.0, -10.0),
        ]
        if sign < 0:
            points.reverse()
        shapes.append(arm._profile_plate(points, y0 - BACK_EXTENSION, BACK_EXTENSION))
    return cq.Compound.makeCompound(shapes)


def nearest_contact(fixed: cq.Shape, moving: cq.Shape, angle_deg: float) -> dict[str, object]:
    transformed = arm.rotate_x(moving, angle_deg, arm.J2_Y)
    distance = BRepExtrema_DistShapeShape(fixed.wrapped, transformed.wrapped)
    distance.Perform()
    candidates: list[dict[str, object]] = []
    for index in range(1, distance.NbSolution() + 1):
        pf = distance.PointOnShape1(index)
        pm = distance.PointOnShape2(index)
        delta = (pm.X() - pf.X(), pm.Y() - pf.Y(), pm.Z() - pf.Z())
        gap = math.sqrt(sum(value * value for value in delta))
        normal = tuple(value / gap for value in delta)
        radius = (pm.X(), pm.Y() - arm.J2_Y, pm.Z())
        # J2 torque is about +X.  Only the X component of r cross n converts
        # normal contact force to opposing joint torque.
        effective_arm = abs(radius[1] * normal[2] - radius[2] * normal[1])
        candidates.append(
            {
                "fixed_point_mm": [pf.X(), pf.Y(), pf.Z()],
                "moving_point_mm": [pm.X(), pm.Y(), pm.Z()],
                "normal_fixed_to_moving": list(normal),
                "joint_axis_radius_vector_mm": list(radius),
                "j2_effective_normal_moment_arm_mm": effective_arm,
            }
        )
    # Inner contact is conservative for this axis because it has the smaller
    # effective moment arm.  Equal/twin sharing receives no strength credit.
    selected = min(candidates, key=lambda row: float(row["j2_effective_normal_moment_arm_mm"]))
    return {
        "sample_angle_deg": angle_deg,
        "face_gap_mm": distance.Value(),
        "solution_count": distance.NbSolution(),
        "selected_conservative_solution": selected,
        "all_solutions": candidates,
    }


def main() -> int:
    # Reuse the deterministic full-arm/collision generator, while replacing
    # C06/C07 with one-piece rear bosses and retaining every interface face and
    # hole axis.  P0.8 and P0.9 outputs are untouched.
    p09.OUT = OUT
    p09.REV = REV
    p09.STOP_REV = STOP_REV
    p09.STRIKER_INNER = STRIKER_INNER
    p09.STRIKER_OUTER = STRIKER_OUTER
    p09.CATCH_INNER = CATCH_INNER
    p09.CATCH_OUTER = CATCH_OUTER

    original_striker = arm.j2_positive_striker_adapter
    original_catch = arm.j2_positive_catch_adapter

    def striker(y0: float, top_z_mm: float = arm.STOP_STRIKER_TOP_Z_MM) -> cq.Shape:
        base = original_striker(y0, top_z_mm)
        return base.fuse(boss_profile(y0, outer=STRIKER_OUTER, inner=STRIKER_INNER, top=top_z_mm))

    def catch(y0: float, face_recess_mm: float = arm.STOP_CATCH_FACE_RECESS_MM) -> cq.Shape:
        base = original_catch(y0, face_recess_mm)
        return base.fuse(boss_profile(y0, outer=CATCH_OUTER, inner=CATCH_INNER, top=arm.STOP_CATCH_TOP_Z_MM))

    arm.j2_positive_striker_adapter = striker
    arm.j2_positive_catch_adapter = catch
    result = p09.main()
    if result:
        return result

    legacy = OUT / "p09-status.json"
    if legacy.exists():
        legacy.unlink()

    fixed = catch(32.0 + arm.PLATE_T + arm.UPPER_BEAM_L)
    moving = striker(arm.J2_Y + 32.0)
    contact = nearest_contact(fixed, moving, 117.9999)
    chosen = contact["selected_conservative_solution"]
    effective_arm = float(chosen["j2_effective_normal_moment_arm_mm"])

    summary = json.loads((OUT / "architecture-summary.json").read_text(encoding="utf-8"))
    gravity_nm = float(summary["mass_and_load_screen"]["allocated_elbow_gravity_nm"])
    rail_width = STRIKER_OUTER - STRIKER_INNER
    lever_mm = arm.STOP_STRIKER_TOP_Z_MM + 15.0
    section_modulus = rail_width * MIN_STRUCTURAL_T**2 / 6.0

    static_rows: list[dict[str, object]] = []
    for case_id, drive_nm, basis in (
        ("STATIC-RAW800", 5.18, "ideal current-to-torque line plus worst-sign CAD gravity; current-limit proof absent"),
        ("STATIC-PUBLISHED-ENDPOINT", 10.6, "published 12 V momentary stall endpoint plus worst-sign CAD gravity; not continuous torque"),
    ):
        reaction_nm = drive_nm + gravity_nm
        force_n = reaction_nm * 1000.0 / effective_arm
        stress_mpa = force_n * lever_mm / section_modulus
        static_rows.append(
            {
                "case_id": case_id,
                "drive_torque_nm": f"{drive_nm:.6f}",
                "worst_sign_gravity_nm": f"{gravity_nm:.6f}",
                "reaction_torque_nm": f"{reaction_nm:.6f}",
                "cad_effective_normal_arm_mm": f"{effective_arm:.6f}",
                "single_rail_normal_force_n": f"{force_n:.3f}",
                "minimum_rail_width_mm": f"{rail_width:.3f}",
                "minimum_structural_thickness_mm": f"{MIN_STRUCTURAL_T:.3f}",
                "beam_screen_lever_mm": f"{lever_mm:.6f}",
                "nominal_beam_stress_mpa": f"{stress_mpa:.3f}",
                "ratio_to_project_240_mpa_mtr_threshold": f"{PROJECT_MTR_THRESHOLD_MPA / stress_mpa:.3f}",
                "basis": basis,
                "status": "INTERIM GEOMETRY REJECTION SCREEN ONLY - Kt, CONTACT, PRYING, DEFORMATION, FATIGUE AND FULL LOAD PATH OPEN",
                "warning": WARNING,
            }
        )
    write_csv(OUT / "corrected-static-stop-screen.csv", static_rows)

    stall_stress = float(static_rows[-1]["nominal_beam_stress_mpa"])
    factor_rows = []
    for factor in (1.0, 2.0, 3.0, 4.0):
        factored = stall_stress * factor
        factor_rows.append(
            {
                "factor": f"{factor:.1f}",
                "nominal_stress_mpa": f"{stall_stress:.3f}",
                "factored_stress_mpa": f"{factored:.3f}",
                "ratio_to_240_mpa_threshold": f"{PROJECT_MTR_THRESHOLD_MPA / factored:.3f}",
                "result": "PASS INTERIM REJECTION SCREEN" if factored <= PROJECT_MTR_THRESHOLD_MPA else "FAIL INTERIM REJECTION SCREEN",
                "interpretation": "not an impact factor, allowable, safety factor or release criterion",
                "warning": WARNING,
            }
        )
    write_csv(OUT / "static-geometry-factor-screen.csv", factor_rows)

    inertia = 0.010144
    impact_rows = []
    for speed_deg_s in (10.0, 30.0):
        energy_j = 0.5 * inertia * math.radians(speed_deg_s) ** 2
        for travel_deg in (0.01, 0.05, 0.10, 0.50, 1.00):
            travel_rad = math.radians(travel_deg)
            average_nm = energy_j / travel_rad
            impact_rows.append(
                {
                    "speed_deg_s": f"{speed_deg_s:.2f}",
                    "unaccepted_inertia_kg_m2": f"{inertia:.6f}",
                    "kinetic_energy_j": f"{energy_j:.9f}",
                    "assumed_stop_travel_deg": f"{travel_deg:.3f}",
                    "average_energy_torque_nm": f"{average_nm:.6f}",
                    "linear_spring_peak_torque_nm": f"{2.0 * average_nm:.6f}",
                    "omissions": "reflected rotor inertia, motor/gravity work, damping, hysteresis, tolerances, rebound and fault overspeed",
                    "status": "SENSITIVITY ONLY - INPUTS UNACCEPTED",
                    "warning": WARNING,
                }
            )
    write_csv(OUT / "impact-energy-sensitivity.csv", impact_rows)

    contact.update(
        {
            "identifier": LOAD_REV,
            "joint_axis": "+X through (0, J2_Y, 0)",
            "governing_relation": "T_x = F_n * abs((r cross n)_x)",
            "disposition": "supersedes R269 F=T/radius model",
            "warning": WARNING,
        }
    )
    (OUT / "cad-contact-normal-evidence.json").write_text(json.dumps(contact, indent=2) + "\n", encoding="utf-8")

    bumper_rows = [
        {
            "candidate": "Rogers PORON 4790-92-25024-04P",
            "manufacturer_product_number": "2300327",
            "nominal_thickness_mm": "0.61",
            "tolerance_mm": "+/-0.08",
            "maximum_thickness_mm": "0.69",
            "role": "sacrificial soft-contact/noise/rebound test coupon ahead of metal backup only",
            "structural_stop_credit": "NONE",
            "source_revision": "Rogers 17-085 rev 1224-PDF (2024); availability brochure effective 2026-02-27",
            "selection_state": "SELECTION REQUIRED - TEST COUPON ONLY",
            "warning": WARNING,
        }
    ]
    write_csv(OUT / "bumper-test-candidate.csv", bumper_rows)

    # Replace P0.9 post-processing records that the reused generator emitted;
    # those contain the superseded radius-force model and P0.9 wording.
    for obsolete in ("j2-positive-stop-load-screen.csv", "combined-factor-envelope.csv"):
        path = OUT / obsolete
        if path.exists():
            path.unlink()
    changes = [
        {
            "change_id": "R270-CH-01",
            "part_id": "MV0-C06",
            "change": "16 mm rails with integral rear bosses from 15.875 mm nominal stock; >=15.00 mm finished structural thickness",
            "preserved_interfaces": "four M2.5 axes, two M5 axes, central 9.525 mm mounting lands, +Y contact face and striker top datum",
            "state": "UNSELECTED CAD CANDIDATE",
            "warning": WARNING,
        },
        {
            "change_id": "R270-CH-02",
            "part_id": "MV0-C07",
            "change": "18 mm catches with integral rear bosses; existing 1 mm contact recess and interfaces retained",
            "preserved_interfaces": "four M2.5 axes, two M5 axes, central 9.525 mm mounting lands and recessed +Y contact face",
            "state": "UNSELECTED CAD CANDIDATE",
            "warning": WARNING,
        },
        {
            "change_id": "R270-CH-03",
            "part_id": "load model",
            "change": "replace F=T/radius with T_x=F_n*abs((r cross n)_x); separate static and energy sensitivity cases",
            "preserved_interfaces": "none",
            "state": "R269 STRESS RESULT SUPERSEDED",
            "warning": WARNING,
        },
    ]
    write_csv(OUT / "design-change-register.csv", changes)
    hold_text = [
        "Qualified reviewer accepts the exact contact-normal and J2 effective-arm extraction",
        "Converged nonlinear one-rail and two-rail C06/C07 contact/root/interface analysis is accepted",
        "Worst-tolerance first-contact, rail sharing, edge contact and single-rail fault cases are accepted",
        "As-built moving inertia including reflected rotor inertia is measured and accepted",
        "Maximum approach and fault-overspeed values are configuration-bound and physically verified",
        "Motor current and torque decay after contact are measured and included in the energy balance",
        "Bumper force-stroke, hysteresis, bottom-out, rebound, temperature, aging and retention are validated",
        "C06/C07 drawings, tolerance controls, DFM and first articles are accepted",
        "Material lot MTR and finished minimum thickness are verified",
        "Fastener, frame, extrusion, prying, deflection, overtravel and fatigue load paths are accepted",
        "Single-rail and twin-rail physical proof and stopping tests pass qualified limits",
        "Configuration-bound qualified release and separate work authority are signed",
    ]
    holds = [
        {
            "hold_id": f"R270-H{index:02d}",
            "hold": value,
            "state": "OPEN",
            "closure_evidence": "NOT EXECUTED",
            "release_effect": "BLOCKS P0.10 SELECTION/FABRICATION/MOTION",
            "warning": WARNING,
        }
        for index, value in enumerate(hold_text, 1)
    ]
    write_csv(OUT / "open-holds.csv", holds)
    acceptance = [
        {
            "acceptance_id": f"R270-ACC-{index:02d}",
            "criterion": value,
            "execution_state": "NOT EXECUTED",
            "result": "OPEN",
            "evidence_uri": "",
            "approver": "",
            "warning": WARNING,
        }
        for index, value in enumerate(hold_text, 1)
    ]
    write_csv(OUT / "acceptance-matrix.csv", acceptance)

    status = {
        "identifier": REV,
        "stop_identifier": STOP_REV,
        "load_model_identifier": LOAD_REV,
        "round": "R270",
        "parent": "HR-V0-ARM-ARCH-P0.9-STOP-STRENGTH-CANDIDATE",
        "stock_material_family": "6061-T651 plate - exact source/lot/MTR SELECTION REQUIRED",
        "nominal_stock_thickness_mm": STOCK_T,
        "minimum_structural_boss_thickness_mm": MIN_STRUCTURAL_T,
        "striker_rail_width_mm": rail_width,
        "catch_rail_width_mm": CATCH_OUTER - CATCH_INNER,
        "contact_face_and_hole_axes_changed": False,
        "cad_effective_normal_moment_arm_mm": round(effective_arm, 6),
        "single_rail_static_endpoint_nominal_stress_mpa": round(stall_stress, 3),
        "four_x_static_geometry_screen_result": factor_rows[-1]["result"],
        "selected": False,
        "physical_evidence_complete": False,
        "qualified_review_complete": False,
        "fabrication_authorized": False,
        "powered_testing_authorized": False,
        "motion_authorized": False,
        "energization_authorized": False,
        "safety_credit": False,
        "warning": WARNING,
    }
    (OUT / "p010-status.json").write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8")

    summary["revision"] = REV
    summary["disposition"] = "unselected integral-boss stop candidate; corrected CAD contact-arm model; physical and qualified closure absent"
    summary["corrected_stop_model"] = status
    (OUT / "architecture-summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
