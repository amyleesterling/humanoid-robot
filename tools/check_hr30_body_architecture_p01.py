"""Fail-closed checks for HR-30-BODY-ARCH-P0.1."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

import cadquery as cq


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "hr30" / "whole-body-p0.1"
REL = ROOT / "release" / "hr30" / "whole-body-p0.1"
WARNING = "PRELIMINARY - CONFIGURATION AND PACKAGING CAD ONLY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, POWERED TESTING, MOTION, OR ENERGIZATION"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"FAIL: {message}")


def main() -> int:
    required_files = {
        "HR-30_body_architecture_candidate.step",
        "HR-30_body_kinematic_reference.step",
        "HR-30_body_architecture_candidate.glb",
        "joint-axis-schedule.csv",
        "joint-module-family-schedule.csv",
        "joint-module-axis-binding.csv",
        "actuator-transmission-allocation.csv",
        "asimov-1-reuse-adapt-reject.csv",
        "component-envelope-schedule.csv",
        "mass-allocation-register.csv",
        "geometry-checks.json",
        "open-holds.csv",
        "README.md",
        "front-elevation.svg",
        "index.html",
        "package-status.json",
        "whole-body-source.py",
        "file-manifest.csv",
        "vendor/model-viewer.min.js",
        "vendor/LICENSE",
        "vendor/SOURCE.md",
    }
    require(SRC.is_dir() and REL.is_dir(), "source/release package missing")
    source_files = {p.relative_to(SRC).as_posix() for p in SRC.rglob("*") if p.is_file()}
    release_files = {p.relative_to(REL).as_posix() for p in REL.rglob("*") if p.is_file()}
    require(required_files <= source_files, "required source file set incomplete")
    require(source_files == release_files, "source/release file set mismatch")
    for name in source_files:
        require(sha(SRC / name) == sha(REL / name), f"source/release mismatch {name}")

    manifest = list(csv.DictReader((SRC / "file-manifest.csv").open(encoding="utf-8")))
    require({r["path"] for r in manifest} == source_files - {"file-manifest.csv"}, "manifest payload set mismatch")
    for row in manifest:
        p = SRC / row["path"]
        require(int(row["bytes"]) == p.stat().st_size and row["sha256"] == sha(p), f"manifest mismatch {p.name}")
        require(row["warning"] == WARNING, f"manifest warning mismatch {p.name}")

    checks = json.loads((SRC / "geometry-checks.json").read_text(encoding="utf-8"))
    require(checks["identifier"] == "HR-30-BODY-ARCH-P0.1", "identifier mismatch")
    require(checks["joint_axis_count"] == 25, "axis count not 25")
    require(checks["checks"]["overall_height_exact_762"], "height gate failed")
    require(checks["checks"]["joint_axis_count_exact_25"], "axis gate failed")
    require(checks["checks"]["shoulder_shell_target_met"], "shoulder shell target failed")
    require(checks["checks"]["hip_shell_target_met"], "hip shell target failed")
    require(checks["checks"]["foot_spacing_inside_walking_band"], "foot spacing gate failed")
    require(not checks["checks"]["straight_arm_reach_target_met"], "reach target must remain disclosed false")
    require(checks["checks"]["straight_arm_reach_hard_limit_met"], "reach hard limit failed")
    require(not checks["checks"]["straight_arm_span_target_met"], "span target must remain disclosed false")
    require(checks["checks"]["straight_arm_span_hard_limit_met"], "span hard limit failed")
    require(not any(checks["authority"].values()), "authority overclaim")

    axes = list(csv.DictReader((SRC / "joint-axis-schedule.csv").open(encoding="utf-8")))
    require(len(axes) == 25 and len({r["axis_id"] for r in axes}) == 25, "joint schedule identity/count mismatch")
    require(sum(r["region"] == "leg" for r in axes) == 12, "leg axis count mismatch")
    require(sum(r["region"] in {"arm", "hand"} for r in axes) == 10, "arm/hand axis count mismatch")
    allocation = list(csv.DictReader((SRC / "actuator-transmission-allocation.csv").open(encoding="utf-8")))
    require(len(allocation) == 25 and {r["axis_id"] for r in allocation} == {r["axis_id"] for r in axes}, "actuator allocation does not cover every axis")
    require(sum(r["candidate_disposition"] == "DIRECT DRIVE REJECTED/BLOCKED" for r in allocation) == 2, "both hip-roll direct-drive allocations must be blocked")
    module_families = list(csv.DictReader((SRC / "joint-module-family-schedule.csv").open(encoding="utf-8")))
    module_bindings = list(csv.DictReader((SRC / "joint-module-axis-binding.csv").open(encoding="utf-8")))
    require(len(module_families) == 8 and len({r["family_id"] for r in module_families}) == 8, "joint-module family identity/count mismatch")
    require(sum(int(r["axis_count"]) for r in module_families) == 25, "joint-module family counts do not cover 25 axes")
    require(len(module_bindings) == 25 and {r["axis_id"] for r in module_bindings} == {r["axis_id"] for r in axes}, "joint-module binding does not cover every axis")
    require({r["family_id"] for r in module_bindings} == {r["family_id"] for r in module_families}, "joint-module family/binding mismatch")
    require(sum(r["shared_assembly_id"] == "L_SHOULDER_GIMBAL" for r in module_bindings) == 2 and sum(r["shared_assembly_id"] == "R_SHOULDER_GIMBAL" for r in module_bindings) == 2, "intersecting shoulder axes are not bound to shared gimbals")
    require(all("SELECTION REQUIRED" in r["selection_state"] and r["authority"].startswith("NO PROCUREMENT") for r in module_bindings), "joint-module selection/authority boundary missing")
    asimov = list(csv.DictReader((SRC / "asimov-1-reuse-adapt-reject.csv").open(encoding="utf-8")))
    require(len(asimov) >= 12 and {r["decision"] for r in asimov} == {"REUSE", "ADAPT", "REJECT"}, "Asimov matrix incomplete")
    require(all(r["source_archive_sha256"].lower() == "ae126d212e8c56486ce014bd9b01b3779b0086867f9b47615ddefbbf32fa5167" for r in asimov), "Asimov source identity mismatch")

    holds = list(csv.DictReader((SRC / "open-holds.csv").open(encoding="utf-8")))
    require(len(holds) == 10 and all(r["state"] == "OPEN" for r in holds), "open holds not fail-closed")
    mass = list(csv.DictReader((SRC / "mass-allocation-register.csv").open(encoding="utf-8")))
    require(mass[-1]["cad_mass_kg"] == "P0.1 ALLOCATION ESTIMATE 9.630" and "AS-BUILT MASS OPEN" in mass[-1]["status"], "mass allocation must remain explicitly provisional")

    model = cq.importers.importStep(str(SRC / "HR-30_body_architecture_candidate.step"))
    vertices = [vertex.Center() for vertex in model.val().Vertices()]
    require(abs(min(vertex.z for vertex in vertices)) < 1e-6 and abs(max(vertex.z for vertex in vertices) - 762.0) < 1e-6, "independent STEP vertex height/bottom mismatch")
    require((SRC / "HR-30_body_architecture_candidate.glb").stat().st_size > 10000, "GLB too small")
    require((SRC / "vendor" / "model-viewer.min.js").stat().st_size > 100000, "vendored interactive viewer missing or too small")
    require(WARNING in (SRC / "README.md").read_text(encoding="utf-8"), "README warning missing")
    require(sha(SRC / "whole-body-source.py") == sha(ROOT / "tools" / "generate_hr30_body_architecture_p01.py"), "editable source snapshot drift")
    status = json.loads((SRC / "package-status.json").read_text(encoding="utf-8"))
    require(status["whole_body_geometry_present"] and status["joint_axis_count"] == 25 and status["actuator_allocation_count"] == 25, "whole-body package status incomplete")
    require(status["joint_module_geometry_present"] and status["joint_module_family_count"] == 8 and status["joint_module_binding_count"] == 25, "joint-module status incomplete")
    require(not any(status[key] for key in ("procurement_authority", "fabrication_authority", "powered_test_authority", "motion_authority", "energization_authority")), "package status authority overclaim")
    page = (SRC / "index.html").read_text(encoding="utf-8")
    require(WARNING in page and "font:17px/1.55" in page and "font-size:16px" in page, "web warning/legibility controls missing")
    require("HR-30_body_architecture_candidate.glb" in page and "front-elevation.svg" in page, "web model/elevation links missing")
    require('src="vendor/model-viewer.min.js"' in page and "ajax.googleapis.com" not in page, "web viewer must be repository-local")
    components = list(csv.DictReader((SRC / "component-envelope-schedule.csv").open(encoding="utf-8")))
    component_names = {row["component"] for row in components}
    require("FACE_SCREEN_PANEL" in component_names and {"L_INBOARD_GRIPPER_FINGER", "L_OUTBOARD_GRIPPER_FINGER", "R_INBOARD_GRIPPER_FINGER", "R_OUTBOARD_GRIPPER_FINGER"} <= component_names, "screen face or functional two-finger hands missing")
    for axis_id in {r["axis_id"] for r in axes}:
        require({f"JMOD_{axis_id}_OUTPUT_SHAFT", f"JMOD_{axis_id}_BEARING_A_RING", f"JMOD_{axis_id}_BEARING_B_RING", f"JMOD_{axis_id}_INTERFACE_PLATE_A", f"JMOD_{axis_id}_INTERFACE_PLATE_B", f"JMOD_{axis_id}_ACTUATOR_ENVELOPE"} <= component_names, f"visible joint-module geometry incomplete for {axis_id}")
    print("PASS: native HR-30 body architecture has exact 762 mm height, 25 named axes, synchronized STEP/GLB/source-release evidence; body remains preliminary and all work authority false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
