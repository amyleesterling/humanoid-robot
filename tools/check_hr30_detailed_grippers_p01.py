"""Fail-closed checks for the HR-30 detailed bilateral gripper package."""

from __future__ import annotations

import csv
import hashlib
import json
import math
from pathlib import Path

import cadquery as cq


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "hr30" / "whole-body-p0.1"
OUT = PACKAGE / "grippers-p0.1"
RELEASE = ROOT / "release" / "hr30" / "whole-body-p0.1" / "grippers-p0.1"
WARNING = "PRELIMINARY - CONFIGURATION AND PACKAGING CAD ONLY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, POWERED TESTING, MOTION, OR ENERGIZATION"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"FAIL: {message}")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rows(name: str) -> list[dict]:
    with (OUT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def main() -> int:
    status = json.loads((OUT / "gripper-status.json").read_text(encoding="utf-8"))
    require(status["bilateral_hand_count"] == 2, "bilateral hand count drift")
    require(status["visible_part_count_per_hand"] == 18, "part count per hand drift")
    require(status["unique_part_record_count"] == 18 and status["custom_fabrication_candidate_count"] == 17, "part register population drift")
    require(status["total_coupled_stroke_mm"] == 26.0 and status["closed_pad_gap_mm"] == 8.0 and status["open_pad_gap_mm"] == 34.0, "gripper travel/gap definition drift")
    require(status["standard_involute_gear_geometry_present"] is True, "involute gear geometry missing")
    require(status["matching_standard_rack_geometry_present"] is True, "matching rack geometry missing")
    require(status["transmission_geometry_candidate_defined"] is True and status["gear_mesh_state_count"] == 2, "transmission candidate state drift")
    require(abs(float(status["nominal_total_tangential_backlash_mm"]) - 0.08) < 1e-12, "nominal backlash drift")
    require(float(status["nominal_mesh_interference_volume_mm3_max"]) <= 1e-6, "nominal gear/rack solid interference")
    for key in ("mechanism_selected", "materials_selected", "force_calibrated", "physical_validation_complete", "procurement_authority", "fabrication_authority", "assembly_authority", "powered_test_authority", "motion_authority", "energization_authority"):
        require(status[key] is False, f"authority or validation overclaim: {key}")

    parts = rows("gripper-part-register.csv")
    require(len(parts) == 18 and len({row["part_id"] for row in parts}) == 18, "part register identity drift")
    require(sum(row["fabrication_candidate"] == "TRUE" for row in parts) == 17, "custom part count drift")
    require(all(row["warning"] == WARNING for row in parts), "part warning drift")
    for row in parts:
        path = ROOT / row["source_path"] if not row["source_path"].startswith("parts/") else OUT / row["source_path"]
        require(path.is_file() and sha256(path) == row["source_sha256"], f"part source/hash mismatch: {row['part_id']}")

    states = rows("gripper-kinematic-state-register.csv")
    require(len(states) == 4, "bilateral state population drift")
    for state in ("CLOSED", "OPEN"):
        selected = [row for row in states if row["state"] == state]
        require(len(selected) == 2 and {row["side"] for row in selected} == {"L", "R"}, f"state bilateral coverage drift: {state}")
        expected_gap = 8.0 if state == "CLOSED" else 34.0
        expected_travel = 0.0 if state == "CLOSED" else 26.0
        require(all(abs(float(row["pad_gap_mm"]) - expected_gap) < 1e-6 for row in selected), f"state gap drift: {state}")
        require(all(abs(float(row["total_coupled_travel_mm"]) - expected_travel) < 1e-6 for row in selected), f"state travel drift: {state}")

    force = rows("gripper-force-screen.csv")
    require(len(force) == 3, "force screen count drift")
    require(any(row["case_id"] == "GF-02" and abs(float(row["pinion_torque_nm"]) - 0.10) < 1e-9 and abs(float(row["ideal_total_normal_force_n"]) - 20.0) < 1e-9 for row in force), "20 N force geometry missing")
    require(any(row["case_id"] == "GF-03" and abs(float(row["ideal_total_normal_force_n"]) - 200.0) < 1e-9 and "NO" in row["credit"] for row in force), "stall endpoint boundary missing")
    gear = rows("gripper-gear-geometry-register.csv")
    require(len(gear) == 1, "gear geometry register population drift")
    geometry = gear[0]
    module = float(geometry["module_mm"])
    teeth = int(geometry["pinion_teeth"])
    angle = math.radians(float(geometry["pressure_angle_deg"]))
    pitch_diameter = module * teeth
    require(abs(float(geometry["pitch_diameter_mm"]) - pitch_diameter) < 1e-6, "pitch diameter equation drift")
    require(abs(float(geometry["base_diameter_mm"]) - pitch_diameter * math.cos(angle)) < 1e-6, "base diameter equation drift")
    require(abs(float(geometry["outside_diameter_mm"]) - (pitch_diameter + 2.0 * module)) < 1e-6, "outside diameter equation drift")
    require(abs(float(geometry["root_diameter_mm"]) - (pitch_diameter - 2.5 * module)) < 1e-6, "root diameter equation drift")
    require(abs(float(geometry["circular_pitch_mm"]) - math.pi * module) < 1e-6, "circular pitch equation drift")
    require(abs(float(geometry["nominal_total_tangential_backlash_mm"]) - 0.08) < 1e-9, "gear-register backlash drift")
    require("no conformity claim" in geometry["geometry_basis"], "ISO/conformity boundary missing")

    mesh = rows("gripper-mesh-state-register.csv")
    require(len(mesh) == 2 and {row["state"] for row in mesh} == {"CLOSED", "OPEN"}, "mesh-state population drift")
    for row in mesh:
        travel = float(row["rack_travel_each_mm"])
        expected_angle = travel / 5.0
        require(abs(float(row["pinion_rotation_rad"]) - expected_angle) < 1e-8, f"pinion/rack kinematics drift: {row['state']}")
        require(abs(float(row["expected_pitch_displacement_mm"]) - travel) < 1e-8 and float(row["kinematic_error_mm"]) < 1e-9, f"pitch displacement drift: {row['state']}")
        require(float(row["upper_solid_interference_volume_mm3"]) <= 1e-6 and float(row["lower_solid_interference_volume_mm3"]) <= 1e-6, f"solid interference: {row['state']}")
        require(float(row["upper_minimum_solid_distance_mm"]) > 0.0 and float(row["lower_minimum_solid_distance_mm"]) > 0.0, f"nominal clearance absent: {row['state']}")
    opened = next(row for row in mesh if row["state"] == "OPEN")
    require(abs(float(opened["pinion_rotation_deg"]) - math.degrees(13.0 / 5.0)) < 1e-7, "open-state pinion rotation drift")
    require(len(rows("gripper-interface-register.csv")) == 7, "interface population drift")
    require(len(rows("gripper-candidate-bom.csv")) == 11, "candidate BOM population drift")
    require(len(rows("source-register.csv")) == 8, "source register population drift")

    expected_steps = []
    for module in ("G01", "G02"):
        for state in ("closed", "open"):
            step = OUT / module / f"{module}_detailed_gripper_{state}_candidate.step"
            glb = step.with_suffix(".glb")
            require(step.is_file() and glb.is_file() and glb.stat().st_size > 1000, f"missing hand state export: {module}/{state}")
            expected_steps.append(step)
    for state in ("closed", "open"):
        step = OUT / f"HR-30_detailed_hands_installed_{state}_candidate.step"
        glb = step.with_suffix(".glb")
        require(step.is_file() and glb.is_file() and glb.stat().st_size > 1000, f"missing installed state export: {state}")
        expected_steps.append(step)
    for step in expected_steps:
        shape = cq.importers.importStep(str(step)).val()
        require(not shape.isNull() and shape.isValid() and len(shape.Solids()) >= 18, f"STEP reimport/solid count failed: {step.name}")

    manifest = rows("file-manifest.csv")
    actual = sorted(
        path for path in OUT.rglob("*")
        if path.is_file() and path.name != "file-manifest.csv" and "__pycache__" not in path.parts
    )
    require(len(manifest) == len(actual), "manifest file count drift")
    manifest_by_path = {row["path"]: row for row in manifest}
    for path in actual:
        rel = path.relative_to(OUT).as_posix()
        require(rel in manifest_by_path and int(manifest_by_path[rel]["bytes"]) == path.stat().st_size and manifest_by_path[rel]["sha256"] == sha256(path), f"manifest mismatch: {rel}")

    source_files = sorted(
        path.relative_to(OUT).as_posix() for path in OUT.rglob("*")
        if path.is_file() and "__pycache__" not in path.parts
    )
    release_files = sorted(
        path.relative_to(RELEASE).as_posix() for path in RELEASE.rglob("*")
        if path.is_file() and "__pycache__" not in path.parts
    )
    require(source_files == release_files, "source/release file-set mismatch")
    require(all(sha256(OUT / rel) == sha256(RELEASE / rel) for rel in source_files), "source/release hash mismatch")

    root_status = json.loads((PACKAGE / "package-status.json").read_text(encoding="utf-8"))
    require(root_status["detailed_bilateral_gripper_package_present"] is True and root_status["detailed_gripper_visible_part_count_per_hand"] == 18, "root status not integrated")
    require(root_status["detailed_gripper_involute_transmission_candidate_defined"] is True and abs(float(root_status["detailed_gripper_nominal_tangential_backlash_mm"]) - 0.08) < 1e-12, "root transmission integration missing")
    require(root_status["detailed_gripper_mechanism_selected"] is False and root_status["detailed_gripper_physical_validation_complete"] is False, "root validation overclaim")
    page = (PACKAGE / "index.html").read_text(encoding="utf-8")
    readme = (PACKAGE / "README.md").read_text(encoding="utf-8")
    spec = (PACKAGE / "gripper-functional-specification.md").read_text(encoding="utf-8")
    require("HR30-GRIPPERS-P01-START" in page and "grippers-p0.1/index.html" in page and "8–34 mm" in page and "20° involute" in page, "root page integration missing")
    require("Detailed bilateral hand mechanisms" in readme and "18-part" in readme, "root README integration missing")
    require("20 N" in spec and "0.10 N·m" in spec and "200 N" in spec and "148.969 degrees" in spec and "never commands raw position" in spec, "functional/control boundary incomplete")
    guide = (OUT / "index.html").read_text(encoding="utf-8")
    require(WARNING in guide and WARNING in (OUT / "README.md").read_text(encoding="utf-8"), "package warning missing")
    require("gripper-gear-geometry-register.csv" in guide and "gripper-mesh-state-register.csv" in guide and "0.08 mm" in guide, "gear evidence links missing")
    require("font:17px/1.55" in guide and "body{font-size:16px}" in guide and "button{font:800 16px" in guide and "overflow-x:clip" in guide, "legible responsive CSS boundary missing")

    print("PASS: two 18-part HR-30 grippers reimport with explicit module-0.5 20-degree involute/rack geometry, coupled 148.969-degree open-state pinion rotation, zero nominal solid interference, 26 mm stroke and all no-authority gates hold")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
