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
        "installed-equipment-status.json", "installed-equipment-source.py",
        "HR-30_installed_equipment_candidate.step", "HR-30_installed_equipment_candidate.glb",
        "HR-30_integrated_whole_robot_candidate.step",
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
    require(power[-1]["load"] == "WHOLE ROBOT" and float(power[-1]["operating_budget_w"]) == 197.0 and float(power[-1]["short_peak_budget_w"]) == 811.0, "power budget total mismatch")
    thermal = read_csv("thermal-budget.csv")
    require(thermal[-1]["domain"] == "TOTAL" and float(thermal[-1]["candidate_heat_w"]) == 135.0, "thermal budget total mismatch")
    cost = read_csv("cost-budget.csv")
    require(cost[-1]["cost_group"] == "TOTAL" and float(cost[-1]["planning_allowance_usd"]) == 21000.0, "cost allowance total mismatch")
    compute = read_csv("compute-sensor-network-budget.csv")
    require(any(row["function"] == "Conversational compute" and "never writes actuator registers" in row["role_boundary"] for row in compute), "conversation/motion boundary missing")
    require(any(row["function"] == "Actuator buses" and float(row["quantity"]) == 5 for row in compute), "five segmented actuator buses missing")

    bom = read_csv("whole-robot-candidate-bom.csv")
    require(len(bom) == 32 and sum(int(row["quantity"]) for row in bom if "actuator" in row["function"]) >= 25, "candidate BOM population incomplete")
    require(any(row["item_id"] == "HR30-BOM-019" and int(row["quantity"]) == 10 and "2.0:1 roll-axis" in row["candidate"] for row in bom), "leg reduction BOM does not cover six pitch and four roll axes")
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
    require(all(status[key] for key in ("whole_body_system_package_present", "urdf_present", "mjcf_present", "whole_robot_candidate_bom_present", "walking_architecture_present", "embodied_agent_boundary_present", "modular_build_plan_present", "mass_reconciliation_present", "installed_equipment_layout_present")), "system package status incomplete")
    require(status["installed_equipment_item_count"] == 53 and status["tether_first_equipment_configuration"] and not status["onboard_energy_installed"], "installed-equipment configuration boundary drift")
    require(status["floating_base_dynamics_present"], "floating-base dynamics status missing")
    require(not any(status[key] for key in ("dynamics_validated", "walking_validated", "physical_build_ready", "procurement_authority", "fabrication_authority", "powered_test_authority", "motion_authority", "energization_authority")), "status validation/authority overclaim")
    require(sha(SRC / "system-package-source.py") == sha(ROOT / "tools" / "generate_hr30_system_package_p01.py"), "system generator snapshot drift")
    page = (SRC / "index.html").read_text(encoding="utf-8")
    require("The P0.1 engineering package is whole-body" in page and "font:17px/1.55" in page and "font-size:16px" in page, "web package summary/legibility missing")
    require(all(name in page for name in ("hr30.urdf", "hr30.xml", "whole-robot-candidate-bom.csv", "embodied-agent-architecture.md", "mass-reconciliation.md", "installed-equipment-register.csv")), "web system links incomplete")
    require(page.count('id="equipment-layout"') == 1, "web installed-equipment viewer missing or duplicated")
    print(f"PASS: HR-30 whole-body P0.1 has 25-DOF URDF/MJCF, 53 located equipment/harness items and {reconciled_mass:.3f} kg tether-first planning mass plus budgets, BOM, hands, walking, agent and build artifacts; all validation and work authority remain false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
