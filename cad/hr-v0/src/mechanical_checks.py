"""Reproducible HR-V0 preliminary structural screens.

PRELIMINARY—NOT A STRUCTURAL RELEASE.
"""

from __future__ import annotations

import csv
import json
import math
from pathlib import Path

from hr_v0_cad import write_source_manifest


OUT = Path(__file__).resolve().parents[1] / "generated" / "mechanical-checks.json"
CUSTOM_PARTS = OUT.parent / "custom-parts.csv"


def main():
    # Controlled preliminary inputs, N and mm.
    proof_moment = 3.83e3 * 3.0
    link_length = 160.0
    link_depth = 44.0
    plate_t = 4.75
    hole_d = 2.70
    e_al = 69_000.0
    yield_al = 240.0  # minimum screening value only; certify supplied stock
    bolt_circle_r = 11.0
    column_i = 13.787 * 10_000.0  # 80/20 40-4040 published 13.787 cm^4
    column_l = 500.0
    anchor_spacing = 420.0
    h101_frame_t = 2.0
    output_tap_depth_max = 2.5
    output_stack_nominal = plate_t + h101_frame_t
    with CUSTOM_PARTS.open(newline="", encoding="utf-8") as handle:
        custom_part_mass_g = {
            row["part_number"]: float(row["calculated_mass_g"])
            for row in csv.DictReader(handle)
        }
    moving_mass_ceiling_g = 750.0
    known_moving_mass_g = (
        custom_part_mass_g["MV0-001"]
        + 165.0
        + custom_part_mass_g["MV0-002"]
        + 82.0
        + 100.0
    )
    bucket_allocations_g = {
        "upper_link_hardware": 120.0,
        "elbow_actuator_and_bracket": 200.0,
        "forearm_hardware": 120.0,
        "gripper_assembly": 210.0,
        "payload": 100.0,
    }
    bucket_known_g = {
        "upper_link_hardware": custom_part_mass_g["MV0-001"],
        "elbow_actuator_and_bracket": 165.0,
        "forearm_hardware": custom_part_mass_g["MV0-002"],
        "gripper_assembly": 82.0,
        "payload": 100.0,
    }
    hard_stop_radius_m = 0.050
    setup_speed_rad_s = math.radians(10.0)
    auto_speed_rad_s = math.radians(30.0)
    xm540_no_load_speed_rad_s_12v = 30.0 * 2.0 * math.pi / 60.0
    xm540_ideal_stall_torque_nm_12v = 10.6
    illustrative_bumper_stroke_m = 0.002
    shoulder_allocated_inertia = sum((
        0.12 * 0.08 ** 2,
        0.20 * 0.16 ** 2,
        0.12 * 0.24 ** 2,
        0.21 * 0.32 ** 2,
        0.10 * 0.36 ** 2,
    ))
    elbow_allocated_inertia = sum((
        0.12 * 0.08 ** 2,
        0.21 * 0.16 ** 2,
        0.10 * 0.20 ** 2,
    ))

    def rotational_energy(inertia_kg_m2: float, speed_rad_s: float) -> float:
        return 0.5 * inertia_kg_m2 * speed_rad_s ** 2

    gross_i = plate_t * link_depth ** 3 / 12.0
    net_depth = link_depth - 2.0 * hole_d
    net_i = plate_t * net_depth ** 3 / 12.0
    eq_end_force = proof_moment / link_length
    results = {
        "status": "PRELIMINARY—NOT A STRUCTURAL OR FABRICATION RELEASE",
        "inputs": {
            "proof_moment_Nmm": proof_moment,
            "basis": "3.83 N·m intermittent shoulder screen times project 3.0 proof factor",
            "6061_yield_screen_MPa": yield_al,
            "link_mm": [link_length, link_depth, plate_t],
            "candidate_hole_d_mm": hole_d,
            "selected_interfaces": {
                "H101_output": "8 clearance holes on 22 mm PCD",
                "S102_body_frame": "4 clearance holes on selected 32 x 16 mm tapped rectangle",
                "distal_gripper": "DESIGN REQUIRED",
            },
            "h101_frame_nominal_thickness_mm": h101_frame_t,
            "xm540_output_tap_depth_max_mm": output_tap_depth_max,
            "hard_stop_candidate_contact_radius_mm": hard_stop_radius_m * 1000.0,
            "hard_stop_nominal_margin_beyond_software_deg": 5.0,
            "hard_stop_illustrative_bumper_stroke_mm_not_selected": illustrative_bumper_stroke_m * 1000.0,
            "xm540_no_load_speed_rpm_at_12v_candidate_endpoint": 30.0,
            "xm540_ideal_stall_torque_Nm_at_12v_endpoint": xm540_ideal_stall_torque_nm_12v,
            "column_I_mm4": column_i,
            "moving_mass_ceiling_g": moving_mass_ceiling_g,
            "xm540_manufacturer_mass_g": 165.0,
            "xm430_manufacturer_mass_g": 82.0,
        },
        "screens": {
            "link_gross_I_mm4": gross_i,
            "link_net_I_mm4_conservative_two_holes": net_i,
            "link_net_bending_stress_MPa": proof_moment * (net_depth / 2.0) / net_i,
            "link_yield_ratio_on_screen": yield_al / (proof_moment * (net_depth / 2.0) / net_i),
            "link_cantilever_deflection_mm": eq_end_force * link_length ** 3 / (3.0 * e_al * gross_i),
            "conservative_two_bolt_force_each_N": proof_moment / (2.0 * bolt_circle_r),
            "candidate_plate_bearing_stress_MPa": (proof_moment / (2.0 * bolt_circle_r)) / (plate_t * 2.5),
            "h101_output_stack_nominal_before_thread_mm": output_stack_nominal,
            "h101_output_fastener_geometric_max_underhead_mm": output_stack_nominal + output_tap_depth_max,
            "column_tip_deflection_pure_moment_mm": proof_moment * column_l ** 2 / (2.0 * e_al * column_i),
            "minimum_anchor_couple_force_each_N": proof_moment / anchor_spacing,
            "hard_stop": {
                "allocated_shoulder_inertia_kg_m2_excludes_reflected_rotor": shoulder_allocated_inertia,
                "allocated_elbow_inertia_kg_m2_excludes_reflected_rotor": elbow_allocated_inertia,
                "J1_energy_J_at_10_deg_s": rotational_energy(shoulder_allocated_inertia, setup_speed_rad_s),
                "J1_energy_J_at_30_deg_s": rotational_energy(shoulder_allocated_inertia, auto_speed_rad_s),
                "J1_energy_J_at_30_rpm_no_load_endpoint": rotational_energy(shoulder_allocated_inertia, xm540_no_load_speed_rad_s_12v),
                "J2_energy_J_at_10_deg_s": rotational_energy(elbow_allocated_inertia, setup_speed_rad_s),
                "J2_energy_J_at_30_deg_s": rotational_energy(elbow_allocated_inertia, auto_speed_rad_s),
                "J2_energy_J_at_30_rpm_no_load_endpoint": rotational_energy(elbow_allocated_inertia, xm540_no_load_speed_rad_s_12v),
                "J1_three_x_gravity_force_N_at_50_mm": 3.0 * 1.70 / hard_stop_radius_m,
                "J2_three_x_gravity_force_N_at_50_mm": 3.0 * 0.62 / hard_stop_radius_m,
                "ideal_stall_endpoint_force_N_at_50_mm": xm540_ideal_stall_torque_nm_12v / hard_stop_radius_m,
                "J1_average_force_N_if_no_load_energy_absorbed_in_2_mm_excludes_rotor": rotational_energy(shoulder_allocated_inertia, xm540_no_load_speed_rad_s_12v) / illustrative_bumper_stroke_m,
                "J2_average_force_N_if_no_load_energy_absorbed_in_2_mm_excludes_rotor": rotational_energy(elbow_allocated_inertia, xm540_no_load_speed_rad_s_12v) / illustrative_bumper_stroke_m,
                "screen_result": "KINEMATIC AND ALLOCATED-MASS SCREEN ONLY - STOP DESIGN NOT RELEASED",
            },
            "moving_mass": {
                "known_subtotal_g": known_moving_mass_g,
                "unresolved_headroom_g": moving_mass_ceiling_g - known_moving_mass_g,
                "known_fraction_of_ceiling": known_moving_mass_g / moving_mass_ceiling_g,
                "bucket_allocation_g": bucket_allocations_g,
                "bucket_known_g": bucket_known_g,
                "bucket_unresolved_headroom_g": {
                    bucket: bucket_allocations_g[bucket] - known
                    for bucket, known in bucket_known_g.items()
                },
                "unknown_items": [
                    "J1 and J2 H101 frames/idlers",
                    "J2 S102 body frame",
                    "all joint/frame/gripper fasteners and spacers",
                    "J2 moving hard-stop hardware",
                    "gripper mechanism, pads, guard and retention",
                    "all moving cable, connectors, guides and strain relief",
                ],
                "screen_result": "565.4 g KNOWN SUBTOTAL; 184.6 g UNRESOLVED HEADROOM - MASS CLOSURE OPEN",
            },
        },
        "not_credited_or_unresolved": [
            "Actual alloy/temper certificate, thickness tolerance, flatness and finish",
            "ROBOTIS frame material, measured mass, permissible load and fatigue behavior",
            "Exact M2.5 and M8 fastener part, grade, engagement, preload, torque and locking",
            "Physical FC01/FC02 pattern verification, received thread depth and stack tolerance",
            "Released distal gripper interface and its retention load path",
            "Measured mass, local COM and inertia for every row in the HR-V0 moving-mass ledger",
            "Mass of frames, fasteners, stop hardware, cable guides, moving harness and complete gripper mechanics",
            "Hard-stop bracket, bumper material/force curve, fasteners, contact geometry and load path",
            "Measured maximum joint speed, reflected rotor/gear inertia, gear compliance, drive torque duration and stop-switch latency",
            "Hard-stop tolerance stack including calibration error, backlash, bumper compression and stopping travel",
            "Joint alignment, combined load, shock and fatigue",
            "Bench substrate, anchor part, edge distance, pull-out, shear and site permission",
            "Guard and receiver-fixture impact/retention",
            "Correlation to measured first article and independent mechanical review",
        ],
        "calculation_result": "GEOMETRY SCREEN PASSES; RELEASE REMAINS OPEN",
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(results, indent=2), encoding="utf-8")
    write_source_manifest()
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
