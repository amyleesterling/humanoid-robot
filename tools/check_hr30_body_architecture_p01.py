"""Fail-closed checks for HR-30-BODY-ARCH-P0.1."""

from __future__ import annotations

import csv
import hashlib
import json
import ast
import math
from pathlib import Path

import cadquery as cq


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "hr30" / "whole-body-p0.1"
REL = ROOT / "release" / "hr30" / "whole-body-p0.1"
WARNING = "PRELIMINARY - CONFIGURATION AND PACKAGING CAD ONLY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, POWERED TESTING, MOTION, OR ENERGIZATION"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def vendor_identity_sha(path: Path) -> str:
    data = path.read_bytes()
    if path.suffix.lower() in {".stp", ".step"} and b"\r\n" not in data:
        data = data.replace(b"\n", b"\r\n")
    return hashlib.sha256(data).hexdigest()


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
        "vendor-actuator-source-register.csv",
        "bearing-candidate-source-register.csv",
        "vendor-actuator-transform-register.csv",
        "actuator-transmission-allocation.csv",
        "asimov-1-reuse-adapt-reject.csv",
        "component-envelope-schedule.csv",
        "joint-packaging-screen.json",
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
    blocked_roll_axes = {r["axis_id"] for r in allocation if r["candidate_disposition"] == "DIRECT DRIVE REJECTED/BLOCKED BY WHOLE-BODY PACKAGING"}
    require(blocked_roll_axes == {"L_HIP_ROLL", "R_HIP_ROLL"}, "hip-roll direct-drive packaging dispositions are incomplete")
    elbow_rows = [r for r in allocation if "ELBOW" in r["axis_id"]]
    require(len(elbow_rows) == 2 and all(r["candidate_actuator"] == "ROBOTIS XM430-W350-R candidate" for r in elbow_rows), "whole-body elbow candidate allocation drift")
    shoulder_roll_rows = [r for r in allocation if "SHOULDER_ROLL" in r["axis_id"]]
    wrist_rows = [r for r in allocation if "WRIST" in r["axis_id"]]
    ankle_rows = [r for r in allocation if "ANKLE" in r["axis_id"]]
    knee_rows = [r for r in allocation if "KNEE" in r["axis_id"]]
    require(len(shoulder_roll_rows) == 2 and all("XM430-W350-R" in r["candidate_actuator"] for r in shoulder_roll_rows), "shoulder-roll XM430 allocation drift")
    require(len(wrist_rows) == 2 and all("XC330-T288-T" in r["candidate_actuator"] for r in wrist_rows), "wrist XC330 allocation drift")
    require(len(ankle_rows) == 4 and all("XM430-W350-R" in r["candidate_actuator"] for r in ankle_rows), "reduced ankle XM430 allocation drift")
    require(len(knee_rows) == 2 and all("2.5:1" in r["candidate_transmission"] for r in knee_rows), "2.5:1 knee allocation drift")
    module_families = list(csv.DictReader((SRC / "joint-module-family-schedule.csv").open(encoding="utf-8")))
    module_bindings = list(csv.DictReader((SRC / "joint-module-axis-binding.csv").open(encoding="utf-8")))
    require(len(module_families) == 10 and len({r["family_id"] for r in module_families}) == 10, "joint-module family identity/count mismatch")
    require(sum(int(r["axis_count"]) for r in module_families) == 25, "joint-module family counts do not cover 25 axes")
    support_counts = {r["family_id"]: int(r["external_bearing_count_per_axis"]) for r in module_families}
    require(support_counts == {
        "JMF-01-COMPACT": 1, "JMF-02-GRIPPER": 1, "JMF-03-SHOULDER-GIMBAL": 2,
        "JMF-04-MEDIUM": 1, "JMF-05-WAIST": 1, "JMF-06-LEG-DIRECT": 1,
        "JMF-07-LEG-REDUCED-15": 2, "JMF-08-LEG-REDUCED-20": 2,
        "JMF-09-KNEE-REDUCED-25": 2, "JMF-10-ANKLE-PITCH-REDUCED-25": 2,
    }, "direct versus remote-output external-bearing architecture drift")
    require(len(module_bindings) == 25 and {r["axis_id"] for r in module_bindings} == {r["axis_id"] for r in axes}, "joint-module binding does not cover every axis")
    require({r["family_id"] for r in module_bindings} == {r["family_id"] for r in module_families}, "joint-module family/binding mismatch")
    bearings = list(csv.DictReader((SRC / "bearing-candidate-source-register.csv").open(encoding="utf-8")))
    require(len(bearings) == 7 and len({r["bearing_id"] for r in bearings}) == 7, "standard bearing candidate set incomplete")
    require({r["bearing_evaluation_candidate"] for r in module_families} <= {r["designation"] for r in bearings}, "module bearing candidate/source mismatch")
    require(all(float(r["published_mass_kg"]) > 0 and float(r["published_dynamic_rating_n"]) > 0 and float(r["published_static_rating_n"]) > 0 for r in bearings), "bearing source facts incomplete")
    require(all("EVALUATION CANDIDATE" in r["application_state"] and r["authority"] == "NO PROCUREMENT OR FABRICATION AUTHORITY" for r in bearings), "bearing application/authority boundary missing")
    require(sum(r["shared_assembly_id"] == "L_SHOULDER_GIMBAL" for r in module_bindings) == 2 and sum(r["shared_assembly_id"] == "R_SHOULDER_GIMBAL" for r in module_bindings) == 2, "intersecting shoulder axes are not bound to shared gimbals")
    require(all("SELECTION REQUIRED" in r["selection_state"] and r["authority"].startswith("NO PROCUREMENT") for r in module_bindings), "joint-module selection/authority boundary missing")
    vendor_sources = list(csv.DictReader((SRC / "vendor-actuator-source-register.csv").open(encoding="utf-8")))
    vendor_transforms = list(csv.DictReader((SRC / "vendor-actuator-transform-register.csv").open(encoding="utf-8")))
    expected_vendor_hashes = {
        "ROBOTIS-540": "6E0DF65638B3A23B12C7EE1114D4D06F5EC2DE9E84E3FFDDD7E115E8F8FAF39F",
        "ROBOTIS-X430": "7FF4E39475245D5C1FC4F703E9241FCA1A09D57AED920274498DBE2CD5E31E22",
        "ROBOTIS-XC330": "E2F7B060801A1D6A21F23BCA2554F29A402F7D73B8498CB201C9E6ADF3139EB6",
    }
    require({r["source_id"]: r["sha256"] for r in vendor_sources} == expected_vendor_hashes, "vendor actuator source identity/hash mismatch")
    for row in vendor_sources:
        path = ROOT / row["repository_path"]
        require(vendor_identity_sha(path).upper() == row["sha256"], f"vendor actuator source identity drifted: {row['source_id']}")
        require(sha(path).upper() == row["checkout_sha256"] and "NORMALIZED TO CRLF" in row["identity_hash_policy"], f"vendor checkout provenance missing: {row['source_id']}")
    require(len(vendor_transforms) == 25 and {r["axis_id"] for r in vendor_transforms} == {r["axis_id"] for r in axes}, "vendor actuator transform register does not cover every axis")
    axis_by_id = {row["axis_id"]: row for row in axes}
    for row in vendor_transforms:
        basis = [tuple(float(v) for v in ast.literal_eval(row[key])) for key in ("project_basis_local_x", "project_basis_local_y", "project_basis_local_z_output")]
        require(all(abs(math.sqrt(sum(v * v for v in vector)) - 1.0) < 1e-9 for vector in basis), f"non-unit actuator transform basis {row['axis_id']}")
        require(all(abs(sum(basis[i][k] * basis[j][k] for k in range(3))) < 1e-9 for i, j in ((0, 1), (0, 2), (1, 2))), f"non-orthogonal actuator transform basis {row['axis_id']}")
        expected_z = (0.0, 1.0, 0.0) if "GRIPPER" in row["axis_id"] else tuple(float(axis_by_id[row["axis_id"]][key]) for key in ("direction_x", "direction_y", "direction_z"))
        require(basis[2] == expected_z, f"vendor output axis does not match controlled axis {row['axis_id']}")
        expected_relation = "TRANSVERSE PALM DRIVE THROUGH SYMMETRIC COUPLER" if "GRIPPER" in row["axis_id"] else "COAXIAL WITH CONTROLLED ROTARY AXIS"
        require(row["controlled_axis_relation"] == expected_relation, f"actuator/controlled-axis relationship mismatch {row['axis_id']}")
        require(row["source_sha256"] == expected_vendor_hashes[row["vendor_source_id"]] and "SELECTION REQUIRED" in row["interface_status"], f"vendor transform source/interface boundary mismatch {row['axis_id']}")
    asimov = list(csv.DictReader((SRC / "asimov-1-reuse-adapt-reject.csv").open(encoding="utf-8")))
    require(len(asimov) >= 12 and {r["decision"] for r in asimov} == {"REUSE", "ADAPT", "REJECT"}, "Asimov matrix incomplete")
    require(all(r["source_archive_sha256"].lower() == "ae126d212e8c56486ce014bd9b01b3779b0086867f9b47615ddefbbf32fa5167" for r in asimov), "Asimov source identity mismatch")

    holds = list(csv.DictReader((SRC / "open-holds.csv").open(encoding="utf-8")))
    require(len(holds) >= 10 and all(r["state"] == "OPEN" for r in holds), "open holds not fail-closed")
    mass = list(csv.DictReader((SRC / "mass-allocation-register.csv").open(encoding="utf-8")))
    total_mass = float(mass[-1]["cad_mass_kg"].split()[-1])
    require(mass[-1]["assembly"] == "TOTAL" and 10.0 < total_mass < 12.0 and "WITHIN MAXIMUM" in mass[-1]["status"], "mass allocation must preserve the 10 kg stretch miss and 12 kg P0.1 maximum")

    model = cq.importers.importStep(str(SRC / "HR-30_body_architecture_candidate.step"))
    vertices = [vertex.Center() for vertex in model.val().Vertices()]
    require(abs(min(vertex.z for vertex in vertices)) < 1e-6 and abs(max(vertex.z for vertex in vertices) - 762.0) < 1e-6, "independent STEP vertex height/bottom mismatch")
    glb_size = (SRC / "HR-30_body_architecture_candidate.glb").stat().st_size
    require(10000 < glb_size < 25_000_000, "GLB must remain a practical web asset while preserving the whole-body model")
    require((SRC / "vendor" / "model-viewer.min.js").stat().st_size > 100000, "vendored interactive viewer missing or too small")
    require(WARNING in (SRC / "README.md").read_text(encoding="utf-8"), "README warning missing")
    require(sha(SRC / "whole-body-source.py") == sha(ROOT / "tools" / "generate_hr30_body_architecture_p01.py"), "editable source snapshot drift")
    status = json.loads((SRC / "package-status.json").read_text(encoding="utf-8"))
    require(status["whole_body_geometry_present"] and status["joint_axis_count"] == 25 and status["actuator_allocation_count"] == 25, "whole-body package status incomplete")
    require(status["joint_module_geometry_present"] and status["joint_module_family_count"] == 10 and status["joint_module_binding_count"] == 25, "joint-module status incomplete")
    require(status["sha_bound_vendor_actuator_geometry_present"] and status["vendor_actuator_source_count"] == 3 and status["vendor_actuator_transform_count"] == 25, "vendor actuator geometry status incomplete")
    require(status["web_glb_uses_dimension_matched_simplified_actuator_bodies"], "web GLB simplification disclosure missing")
    packaging = json.loads((SRC / "joint-packaging-screen.json").read_text(encoding="utf-8"))
    require(status["neutral_pose_joint_packaging_screen_pass"] and packaging["pass"], "neutral-pose joint packaging screen not passed")
    require(not packaging["detached"] and not packaging["cross_assembly_actuator_collisions"] and not packaging["floor_crossings"], "neutral-pose joint packaging findings remain")
    require(not any(status[key] for key in ("procurement_authority", "fabrication_authority", "powered_test_authority", "motion_authority", "energization_authority")), "package status authority overclaim")
    page = (SRC / "index.html").read_text(encoding="utf-8")
    require(WARNING in page and "font:17px/1.55" in page and "font-size:16px" in page, "web warning/legibility controls missing")
    require("HR-30_body_architecture_candidate.glb" in page and "front-elevation.svg" in page, "web model/elevation links missing")
    require('src="vendor/model-viewer.min.js"' in page and "ajax.googleapis.com" not in page, "web viewer must be repository-local")
    components = list(csv.DictReader((SRC / "component-envelope-schedule.csv").open(encoding="utf-8")))
    component_names = {row["component"] for row in components}
    require("FACE_SCREEN_PANEL" in component_names and {"L_INBOARD_GRIPPER_FINGER", "L_OUTBOARD_GRIPPER_FINGER", "R_INBOARD_GRIPPER_FINGER", "R_OUTBOARD_GRIPPER_FINGER"} <= component_names, "screen face or functional two-finger hands missing")
    family_by_axis = {row["axis_id"]: row["family_id"] for row in module_bindings}
    for axis_id in {r["axis_id"] for r in axes}:
        required = {f"JMOD_{axis_id}_OUTPUT_SHAFT", f"JMOD_{axis_id}_BEARING_B_RING", f"JMOD_{axis_id}_INTERFACE_PLATE_B", f"JMOD_{axis_id}_ACTUATOR_VENDOR_CANDIDATE"}
        if support_counts[family_by_axis[axis_id]] == 2:
            required |= {f"JMOD_{axis_id}_BEARING_A_RING", f"JMOD_{axis_id}_INTERFACE_PLATE_A"}
        require(required <= component_names, f"visible joint-module geometry incomplete for {axis_id}")
    print("PASS: native HR-30 body architecture has exact 762 mm height, 25 named axes, synchronized STEP/GLB/source-release evidence; body remains preliminary and all work authority false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
