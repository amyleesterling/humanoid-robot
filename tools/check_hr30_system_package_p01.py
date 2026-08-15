"""Fail-closed consistency checks for the complete HR-30 whole-body P0.1 package."""

from __future__ import annotations

import csv
import hashlib
import json
import math
import xml.etree.ElementTree as ET
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "hr30" / "whole-body-p0.1"
REL = ROOT / "release" / "hr30" / "whole-body-p0.1"
WARNING = "PRELIMINARY - CONFIGURATION AND PACKAGING CAD ONLY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, POWERED TESTING, MOTION, OR ENERGIZATION"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"FAIL: {message}")


def read_csv(name: str) -> list[dict]:
    return list(csv.DictReader((SRC / name).open(encoding="utf-8")))


def main() -> int:
    required = {
        "hr30.urdf", "hr30.xml", "mass-properties-budget.csv", "power-energy-budget.csv",
        "thermal-budget.csv", "compute-sensor-network-budget.csv", "cost-budget.csv",
        "whole-robot-candidate-bom.csv", "gripper-functional-specification.md",
        "walking-development-architecture.md", "embodied-agent-architecture.md",
        "structured-action-request.schema.json", "modular-fabrication-assembly-electrification-plan.md",
        "system-package-source.py", "index.html", "README.md", "package-status.json", "file-manifest.csv",
        "mass-reconciliation-summary.json", "mass-item-reconciliation.csv", "link-mass-reconciliation.csv",
        "lightweight-architecture-register.csv",
        "installed-equipment-register.csv", "installed-equipment-source-register.csv",
        "battery-energy-source-register.csv",
        "installed-equipment-status.json", "installed-equipment-source.py",
        "HR-30_installed_equipment_candidate.step", "HR-30_installed_equipment_candidate.glb",
        "module-interface-control-register.csv", "module-assembly-sequence.csv",
        "whole-body-interface-atlas.svg", "whole-body-interface-atlas.html", "interface-atlas-source.py",
        "module-cad/module-export-register.csv", "module-cad/index.html", "module-cad/module-cad-source.py",
        "module-cad/module-cad-status.json", "module-cad/HR-30_module_exploded_candidate.step",
        "module-cad/HR-30_module_exploded_candidate.glb",
        "fasteners/joint-fastener-register.csv", "fasteners/joint-fastener-family-summary.csv",
        "fasteners/joint-fastener-status.json", "fasteners/joint-fastener-source.py",
        "fasteners/HR-30_joint_fastener_candidates.step", "fasteners/HR-30_fastened_whole_body_candidate.glb",
        "HR-30_integrated_whole_robot_candidate.step",
        "joint-load-screen.csv", "joint-load-architecture.md", "joint-load-architecture-status.json",
        "actuator-endpoint-source-register.csv", "bearing-candidate-source-register.csv",
        "transmission-candidate-source-register.csv",
        "actuator-bus-topology.csv", "actuator-bus-axis-binding.csv",
        "actuator-bus-source-register.csv", "whole-body-electrical-integration.md",
        "actuator-bus-architecture-source.py",
        "electrical/kicad/hr30-whole-body-electrical-p0.1/hr30-whole-body-electrical-p0.1.kicad_pro",
        "electrical/kicad/hr30-whole-body-electrical-p0.1/hr30-whole-body-electrical-p0.1.kicad_sch",
        "electrical/kicad/hr30-whole-body-electrical-p0.1/validation/hr30-whole-body-electrical-p0.1-erc.rpt",
        "electrical/actuator-branch-pdu-p0.1/hr30-actuator-branch-pdu-p0.1.kicad_pro",
        "electrical/actuator-branch-pdu-p0.1/hr30-actuator-branch-pdu-p0.1.kicad_sch",
        "electrical/actuator-branch-pdu-p0.1/hr30-actuator-branch-pdu-p0.1.kicad_pcb",
        "electrical/actuator-branch-pdu-p0.1/board-instance-channel-allocation.csv",
        "electrical/actuator-branch-pdu-p0.1/current-limit-torque-consequence-register.csv",
        "electrical/actuator-branch-pdu-p0.1/pdu-status.json",
        "electrical/actuator-branch-pdu-p0.1/index.html",
        "leg-drivetrain-p0.1/leg-drivetrain-status.json",
        "leg-drivetrain-p0.1/axis-drivetrain-allocation.csv",
        "leg-drivetrain-p0.1/candidate-product-register.csv",
        "leg-drivetrain-p0.1/belt-center-geometry.csv",
        "leg-drivetrain-p0.1/HR-30_leg_drivetrain_lineup_candidate.step",
        "leg-drivetrain-p0.1/HR-30_leg_drivetrain_lineup_candidate.glb",
        "leg-drivetrain-installation-p0.1/installation-status.json",
        "leg-drivetrain-installation-p0.1/installed-drivetrain-register.csv",
        "leg-drivetrain-installation-p0.1/installed-component-register.csv",
        "leg-drivetrain-installation-p0.1/inter-drive-clearance-register.csv",
        "leg-drivetrain-installation-p0.1/HR-30_leg_drivetrains_installed_candidate.step",
        "leg-drivetrain-installation-p0.1/HR-30_leg_drivetrains_installed_candidate.glb",
    }
    source_files = {p.relative_to(SRC).as_posix() for p in SRC.rglob("*") if p.is_file()}
    release_files = {p.relative_to(REL).as_posix() for p in REL.rglob("*") if p.is_file()}
    require(required <= source_files, "whole-body system artifacts missing")
    require(source_files == release_files, "source/release file-set mismatch")
    for name in source_files:
        require(sha(SRC / name) == sha(REL / name), f"source/release byte mismatch {name}")

    manifest = read_csv("file-manifest.csv")
    require({row["path"] for row in manifest} == source_files - {"file-manifest.csv"}, "manifest file set mismatch")
    for row in manifest:
        path = SRC / row["path"]
        require(int(row["bytes"]) == path.stat().st_size and row["sha256"] == sha(path), f"manifest mismatch {row['path']}")
        require(row["warning"] == WARNING, f"manifest warning mismatch {row['path']}")

    scheduled_axes = {row["axis_id"] for row in read_csv("joint-axis-schedule.csv")}
    mass_reconciliation = json.loads((SRC / "mass-reconciliation-summary.json").read_text(encoding="utf-8"))
    reconciled_mass = float(mass_reconciliation["reconciled_dynamics_planning_mass_kg"])
    urdf = ET.parse(SRC / "hr30.urdf").getroot()
    urdf_joints = [node for node in urdf.findall("joint") if node.get("type") != "fixed"]
    require(len(urdf_joints) == 25 and {node.get("name") for node in urdf_joints} == scheduled_axes, "URDF does not implement exact 25-axis schedule")
    require(len(urdf.findall("link")) == 26 and not urdf.findall("joint[@type='fixed']") and not urdf.findall("link[@name='world']"), "URDF must expose base_link as the unanchored walking root")
    require("base_link" not in {node.find("child").get("link") for node in urdf_joints}, "URDF base_link is not the root")
    require(len({node.find("child").get("link") for node in urdf_joints}) == 25, "URDF child-link tree is not unique")
    require(all(float(node.find("limit").get("effort")) == 0.0 for node in urdf_joints), "URDF must remain effort-disabled until physical selection")
    urdf_masses = [float(node.find("inertial/mass").get("value")) for node in urdf.findall("link") if node.find("inertial/mass") is not None]
    require(abs(sum(urdf_masses) - reconciled_mass) < 5e-6, "URDF reconciled mass total drift")
    joint_origins = {node.get("name"): tuple(float(value) for value in node.find("origin").get("xyz").split()) for node in urdf_joints}
    for side in ("L", "R"):
        require(abs(joint_origins[f"{side}_HIP_YAW"][2] - 0.020) < 1e-9, f"{side} hip-yaw serial datum drift")
        require(abs(joint_origins[f"{side}_HIP_ROLL"][2] + 0.020) < 1e-9 and abs(joint_origins[f"{side}_HIP_PITCH"][2] + 0.020) < 1e-9, f"{side} hip 20 mm serial stack drift")
        require(abs(joint_origins[f"{side}_ANKLE_ROLL"][2] + 0.020) < 1e-9, f"{side} ankle 20 mm serial stack drift")
        foot = urdf.find(f"link[@name='{side}_foot']")
        visual_xyz = tuple(float(value) for value in foot.find("visual/origin").get("xyz").split())
        collision_xyz = tuple(float(value) for value in foot.find("collision/origin").get("xyz").split())
        inertial_xyz = tuple(float(value) for value in foot.find("inertial/origin").get("xyz").split())
        require(visual_xyz == collision_xyz and abs(visual_xyz[1] + 0.025) < 1e-9 and abs(visual_xyz[2] + 0.0175) < 1e-9, f"{side} foot canonical geometry origin drift")
        require(inertial_xyz != visual_xyz, f"{side} provisional inertial COM was incorrectly collapsed onto geometry origin")

    torso = urdf.find("link[@name='torso']")
    torso_visual_xyz = tuple(float(value) for value in torso.find("visual/origin").get("xyz").split())
    torso_collision_xyz = tuple(float(value) for value in torso.find("collision/origin").get("xyz").split())
    torso_size = tuple(float(value) for value in torso.find("collision/geometry/box").get("size").split())
    require(torso_visual_xyz == torso_collision_xyz and abs(torso_visual_xyz[2] - 0.0875) < 1e-9, "torso physical geometry center drift")
    require(torso_size == (0.190, 0.110, 0.145), "torso/hip service-gap geometry drift")

    mjcf = ET.parse(SRC / "hr30.xml").getroot()
    mjcf_joints = mjcf.findall("./worldbody//joint")
    mjcf_motors = mjcf.findall("./actuator/motor")
    require(len(mjcf_joints) == 25 and {node.get("name") for node in mjcf_joints} == scheduled_axes, "MJCF axis schedule mismatch")
    freejoints = mjcf.findall("./worldbody//freejoint")
    require(len(freejoints) == 1 and freejoints[0].get("name") == "floating_base", "MJCF must contain exactly one floating-base joint")
    require(len(mjcf_motors) == 25 and {node.get("joint") for node in mjcf_motors} == scheduled_axes, "MJCF actuator map mismatch")

    mass = read_csv("mass-properties-budget.csv")
    total = mass[-1]
    require(total["link"] == "TOTAL" and abs(float(total["allocated_mass_kg"]) - reconciled_mass) < 2e-6, "mass budget total drift")
    require(abs(float(total["neutral_com_x_m"])) < 0.002, "neutral COM lateral offset outside P0.1 planning bound")
    require(0.25 < float(total["neutral_com_z_m"]) < 0.40, "neutral COM height outside controlled P0.1 band")
    require(all(float(total[key]) > 0 for key in ("local_ixx_kg_m2", "local_iyy_kg_m2", "local_izz_kg_m2")), "whole-body inertia budget nonpositive")

    power = read_csv("power-energy-budget.csv")
    require(power[-1]["load"] == "WHOLE ROBOT" and float(power[-1]["operating_budget_w"]) == 179.0 and float(power[-1]["short_peak_budget_w"]) == 727.0, "power budget total mismatch")
    thermal = read_csv("thermal-budget.csv")
    require(thermal[-1]["domain"] == "TOTAL" and float(thermal[-1]["candidate_heat_w"]) == 135.0, "thermal budget total mismatch")
    cost = read_csv("cost-budget.csv")
    require(cost[-1]["cost_group"] == "TOTAL" and float(cost[-1]["planning_allowance_usd"]) == 20300.0, "cost allowance total mismatch")
    compute = read_csv("compute-sensor-network-budget.csv")
    require(any(row["function"] == "Conversational compute" and "never writes actuator registers" in row["role_boundary"] for row in compute), "conversation/motion boundary missing")
    require(any(row["function"] == "Actuator buses" and float(row["quantity"]) == 8 and "RS-485" in row["candidate"] and "TTL" in row["candidate"] for row in compute), "eight mixed-protocol actuator buses missing")

    bom = read_csv("whole-robot-candidate-bom.csv")
    require(len(bom) == 32 and sum(int(row["quantity"]) for row in bom if "actuator" in row["function"]) >= 25, "candidate BOM population incomplete")
    require(any(row["item_id"] == "HR30-BOM-001" and int(row["quantity"]) == 8 and row["function"] == "hip/knee actuator" for row in bom), "XH540 whole-body allocation drift")
    require(any(row["item_id"] == "HR30-BOM-002" and int(row["quantity"]) == 3 and row["function"] == "waist/shoulder-pitch actuator" for row in bom), "XM540 whole-body allocation drift")
    require(any(row["item_id"] == "HR30-BOM-003" and int(row["quantity"]) == 8 and row["function"] == "shoulder-roll/elbow/ankle actuator" for row in bom), "XM430 whole-body allocation drift")
    require(any(row["item_id"] == "HR30-BOM-004" and int(row["quantity"]) == 6 and row["function"] == "head/gripper/wrist actuator" for row in bom), "XC330 whole-body allocation drift")
    require(any(row["item_id"] == "HR30-BOM-018" and int(row["quantity"]) == 10 for row in bom), "reduced-leg output encoder allocation drift")
    require(any(row["item_id"] == "HR30-BOM-020" and int(row["quantity"]) == 39 and "6803" in row["candidate"] and "6901" in row["candidate"] for row in bom), "standard external-bearing BOM population incomplete")
    require(any(row["item_id"] == "HR30-BOM-019" and int(row["quantity"]) == 10 and "GPA16/20/30/40GT5090" in row["candidate"] and "GBN225/250/255EV5GT-090" in row["candidate"] and "capacity" in row["candidate"] for row in bom), "leg reduction BOM does not bind the exact candidate package for all ten reduced axes")
    require(any(row["item_id"] == "HR30-BOM-026" and "Bioenno" in row["manufacturer"] and "BLF-1209WS" in row["candidate"] and "rejected" in row["candidate"] for row in bom), "onboard-energy BOM candidate/boundary missing")
    require(any(row["item_id"] == "HR30-BOM-010" and int(row["quantity"]) == 8 and "RS-485" in row["candidate"] and "TTL" in row["candidate"] for row in bom), "mixed-protocol actuator interface BOM missing")
    require(all(row["authority"] == "NO PROCUREMENT OR FABRICATION AUTHORITY" for row in bom), "BOM authority overclaim")

    schema = json.loads((SRC / "structured-action-request.schema.json").read_text(encoding="utf-8"))
    actions = set(schema["properties"]["action"]["enum"])
    require({"SPEAK", "PRESENT_OBJECT", "RELEASE_OBJECT", "WEIGHT_SHIFT_REQUEST", "STEP_REQUEST", "STOP_REQUEST"} <= actions, "action schema missing required high-level behavior")
    require(not any("JOINT" in action or "TORQUE" in action or "CURRENT" in action for action in actions), "action schema exposes raw actuator authority")
    require(schema["properties"]["expires_after_ms"]["maximum"] == 2000 and schema["properties"]["constraints"]["properties"]["max_speed_scale"]["maximum"] == 0.25, "action expiry/speed bound drift")

    agent_doc = (SRC / "embodied-agent-architecture.md").read_text(encoding="utf-8")
    require("developers.openai.com/api/docs/guides/function-calling" in agent_doc and "no actuator-bus credentials" in agent_doc and "never closes the permit chain" in agent_doc, "embodied-agent boundary incomplete")
    walking = (SRC / "walking-development-architecture.md").read_text(encoding="utf-8")
    require(all(stage in walking for stage in ("S0", "S1", "S2", "S3", "S4", "S5", "S6", "S7")) and "untethered walking" in walking.lower(), "walking stages incomplete")
    build = (SRC / "modular-fabrication-assembly-electrification-plan.md").read_text(encoding="utf-8")
    require(all(stage in build for stage in ("E0", "E1", "E2", "E3", "E4", "E5", "E6")), "electrification stages incomplete")
    hands = (SRC / "gripper-functional-specification.md").read_text(encoding="utf-8")
    require(all(word in hands for word in ("grasp", "hold", "present", "release")) and "two-finger" in hands, "functional hand specification incomplete")

    status = json.loads((SRC / "package-status.json").read_text(encoding="utf-8"))
    require(all(status[key] for key in ("whole_body_system_package_present", "urdf_present", "mjcf_present", "whole_robot_candidate_bom_present", "walking_architecture_present", "embodied_agent_boundary_present", "modular_build_plan_present", "mass_reconciliation_present", "installed_equipment_layout_present", "whole_body_joint_load_architecture_present", "whole_body_pose_architecture_present", "pose_support_geometry_screen_complete", "whole_body_nominal_self_collision_screen_present", "whole_body_actuator_bus_architecture_present", "protocol_compatibility_screen_complete", "whole_body_interface_atlas_present", "dimensioned_whole_body_front_side_reference_present", "module_cad_exports_present", "exploded_module_step_present", "exploded_module_glb_present", "joint_fastener_candidate_geometry_present", "joint_fastener_hole_alignment_screen_complete")), "system package status incomplete")
    require(status["module_cad_export_count"] == status["module_fabrication_step_count"] == status["module_integration_reference_step_count"] == 12, "module CAD export status count drift")
    require(not status["module_cad_manufacturing_released"] and not status["fabrication_drawings_released"], "module CAD manufacturing-release overclaim")
    require(status["joint_fastener_candidate_count"] == 156 and status["joint_fastener_carrier_plate_count"] == 39, "whole-body fastener population drift")
    require(not status["joint_fastener_selected"] and not status["joint_fastener_preload_validated"], "fastener selection/validation overclaim")
    require(status.get("reduced_leg_drivetrain_package_present") and status.get("reduced_leg_drivetrain_module_count") == 3 and status.get("reduced_leg_drivetrain_axis_count") == 10 and status.get("reduced_leg_drivetrain_candidate_products_defined"), "whole-body reduced-leg drivetrain package missing")
    require(status.get("reduced_leg_drivetrain_horn_adapters_complete") and status.get("leg_drivetrain_adapter_nominal_geometry_complete") and not status.get("leg_drivetrain_adapter_fit_and_tolerance_released") and not status.get("leg_drivetrain_adapter_capacity_validated"), "reduced-leg adapter geometry/release boundary drift")
    require(not status.get("reduced_leg_drivetrain_capacity_validated"), "reduced-leg drivetrain capacity overclaim")
    require(status.get("installed_leg_drivetrain_whole_body_cad_present") and status.get("installed_leg_drivetrain_axis_count") == 10 and status.get("installed_leg_drivetrain_nominal_inter_axis_common_volume_count") == 0, "whole-body installed-leg-drive package missing")
    require(status.get("installed_leg_drivetrain_adapters_complete") and not status.get("installed_leg_drivetrain_adapter_material_fit_fasteners_released") and not status.get("installed_leg_drivetrain_adapter_physical_fit_validated"), "installed-leg-drive adapter geometry/release boundary drift")
    require(not status.get("installed_leg_drivetrain_motion_sweep_validated") and not status.get("installed_leg_drivetrain_capacity_validated"), "installed-leg-drive validation overclaim")
    require(status["module_interface_control_count"] == 12 and status["module_interface_axis_ownership_count"] == 25, "whole-body interface atlas coverage drift")
    require((status["actuator_bus_segment_count"], status["actuator_bus_axis_binding_count"], status["rs485_actuator_axis_count"], status["ttl_actuator_axis_count"]) == (8, 25, 19, 6), "actuator bus status counts drift")
    require(status["native_hr30_kicad_present"] and status["native_hr30_kicad_logical_connectivity_reconciled"] and status["native_hr30_kicad_sheet_count"] == 19 and status["native_hr30_kicad_axis_binding_count"] == 25 and status["native_hr30_kicad_actuator_bus_controller_pins_selected"] and status["native_hr30_kicad_interface_device_candidates_selected"] and status["native_hr30_kicad_data_only_connector_candidates_selected"] and status["native_hr30_kicad_erc_errors"] == status["native_hr30_kicad_erc_warnings"] == 0, "native whole-body KiCad integration missing")
    require(not any(status[key] for key in ("native_hr30_kicad_reconciled", "actuator_bus_interface_selected", "actuator_bus_connector_harness_validated")), "electrical implementation overclaim")
    require(status["whole_body_pose_count"] == 8, "bilateral articulated pose set incomplete")
    require(status["whole_body_pose_common_volume_interference_count"] == 0 and status["whole_body_pose_minimum_nominal_clearance_mm"] >= 8.0, "whole-body nominal collision status not closed")
    require(status["installed_equipment_item_count"] == 54 and status["tether_first_equipment_configuration"] and status["tether_development_interface_retained"] and status["onboard_energy_candidate_geometry_present"] and not status["onboard_energy_installed"], "installed-equipment configuration boundary drift")
    require(status.get("energy_safety_spine_present") and status.get("direct_4s_lipo_architecture_rejected") and not status.get("energy_safety_native_kicad_correction_required") and status.get("energy_safety_native_kicad_topology_corrected") and status.get("energy_safety_physical_terminal_release_required") and status.get("energy_safety_individual_actuator_power_feed_count") == 25, "energy/safety architecture integration missing")
    require(not status.get("energy_safety_protection_released") and not status.get("energy_safety_functional_safety_approved"), "energy/safety release or approval overclaim")
    require(status["floating_base_dynamics_present"], "floating-base dynamics status missing")
    require(not any(status[key] for key in ("dynamics_validated", "walking_validated", "physical_build_ready", "procurement_authority", "fabrication_authority", "powered_test_authority", "motion_authority", "energization_authority")), "status validation/authority overclaim")
    require(sha(SRC / "system-package-source.py") == sha(ROOT / "tools" / "generate_hr30_system_package_p01.py"), "system generator snapshot drift")
    page = (SRC / "index.html").read_text(encoding="utf-8")
    require("The P0.1 engineering package is whole-body" in page and "font:17px/1.55" in page and "font-size:16px" in page, "web package summary/legibility missing")
    require(all(name in page for name in ("hr30.urdf", "hr30.xml", "whole-robot-candidate-bom.csv", "embodied-agent-architecture.md", "mass-reconciliation.md", "installed-equipment-register.csv", "battery-energy-source-register.csv", "whole-body-pose-register.csv", "pose-support-metrics.csv", "HR-30_whole_body_pose_lineup_candidate.glb", "whole-body-collision-register.csv", "collision-exclusion-register.csv", "actuator-bus-topology.csv", "actuator-bus-axis-binding.csv", "actuator-bus-source-register.csv", "whole-body-electrical-integration.md", "hr30-whole-body-electrical-p0.1.kicad_pro", "hr30-whole-body-electrical-p0.1-erc.rpt", "whole-body-interface-atlas.html", "module-interface-control-register.csv", "module-assembly-sequence.csv", "module-cad/index.html", "HR-30_module_exploded_candidate.glb", "fasteners/index.html", "joint-fastener-register.csv", "HR-30_fastened_whole_body_candidate.glb", "energy-safety-spine-p0.1/index.html", "leg-drivetrain-installation-p0.1/index.html", "HR-30_leg_drivetrains_installed_candidate.glb")), "web system links incomplete")
    require(page.count('id="equipment-layout"') == 1, "web installed-equipment viewer missing or duplicated")
    print(f"PASS: HR-30 whole-body P0.1 has 25-DOF URDF/MJCF, eight bilateral articulated S2-S5 pose candidates with zero nominal common-volume interference, 54 located equipment/harness items including two four-channel interface-carrier reservations, separate head power/data routes and a dimensioned onboard-energy candidate, and {reconciled_mass:.3f} kg planning mass plus budgets, BOM, hands, walking, agent and build artifacts; tolerance/physical validation and all work authority remain false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
