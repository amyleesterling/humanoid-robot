"""Fail-closed checks for leg drivetrains installed in the complete HR-30 body."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter
from itertools import combinations
from pathlib import Path

import cadquery as cq


ROOT = Path(__file__).resolve().parents[1]
WHOLE = ROOT / "hr30" / "whole-body-p0.1"
SRC = WHOLE / "leg-drivetrain-installation-p0.1"
REL = ROOT / "release" / "hr30" / "whole-body-p0.1" / "leg-drivetrain-installation-p0.1"
WARNING = "PRELIMINARY - WHOLE-BODY PRODUCT PACKAGING CANDIDATE ONLY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, POWERED TESTING, MOTION, OR ENERGIZATION"

AXES = {
    "L_ANKLE_PITCH": ("LD-25", 55.0, 45.0, 51.455622919),
    "R_ANKLE_PITCH": ("LD-25", 55.0, -45.0, 51.455622919),
    "L_ANKLE_ROLL": ("LD-20", 35.0, -55.0, 49.965206523),
    "R_ANKLE_ROLL": ("LD-20", 35.0, -55.0, 49.965206523),
    "L_KNEE_PITCH": ("LD-20", 210.0, 45.0, 49.965206523),
    "R_KNEE_PITCH": ("LD-20", 210.0, -45.0, 49.965206523),
    "L_HIP_PITCH": ("LD-15", 370.0, 45.0, 49.358512477),
    "R_HIP_PITCH": ("LD-15", 370.0, -45.0, 49.358512477),
    "L_HIP_ROLL": ("LD-20", 390.0, -55.0, 49.965206523),
    "R_HIP_ROLL": ("LD-20", 390.0, -55.0, 49.965206523),
}

PRODUCTS = {
    "LD-15": ("GPA20GT5090-A-P10", "GPA30GT5090-A-P12", "GBN225EV5GT-090"),
    "LD-20": ("GPA20GT5090-A-P10", "GPA40GT5090-A-P12", "GBN255EV5GT-090"),
    "LD-25": ("GPA16GT5090-A-P8", "GPA40GT5090-A-P12", "GBN250EV5GT-090"),
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"FAIL: {message}")


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rows(path: Path) -> list[dict]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def xyz_z(value: str) -> float:
    return float(value.strip("()").split(",")[2])


def main() -> int:
    require(SRC.is_dir() and REL.is_dir(), "installed-drive source/release package missing")
    source_files = {path.relative_to(SRC).as_posix() for path in SRC.rglob("*") if path.is_file()}
    release_files = {path.relative_to(REL).as_posix() for path in REL.rglob("*") if path.is_file()}
    required = {
        "README.md", "index.html", "installation-status.json", "source-binding.csv",
        "installed-drivetrain-register.csv", "installed-component-register.csv",
        "inter-drive-clearance-register.csv", "installed-leg-drivetrains-source.py",
        "HR-30_leg_drivetrains_installed_candidate.step", "HR-30_leg_drivetrains_installed_candidate.glb",
        "HR-30_installed_leg_drivetrains_only_candidate.step", "HR-30_installed_leg_drivetrains_only_candidate.glb",
        "file-manifest.csv",
    }
    require(required <= source_files, "installed-drive artifacts missing")
    require(source_files == release_files, "installed-drive source/release file-set mismatch")
    for name in source_files:
        require(sha(SRC / name) == sha(REL / name), f"installed-drive source/release mismatch {name}")

    manifest = rows(SRC / "file-manifest.csv")
    require({row["path"] for row in manifest} == source_files - {"file-manifest.csv"}, "installed-drive manifest file set mismatch")
    for row in manifest:
        path = SRC / row["path"]
        require(int(row["bytes"]) == path.stat().st_size and row["sha256"] == sha(path), f"installed-drive manifest mismatch {row['path']}")
        require(row["warning"] == WARNING, f"installed-drive manifest warning drift {row['path']}")

    bindings = rows(SRC / "source-binding.csv")
    expected_bindings = {
        "tools/generate_hr30_body_architecture_p01.py",
        "tools/generate_hr30_leg_drivetrain_p01.py",
        "tools/generate_hr30_leg_drivetrain_adapters_p01.py",
        "tools/generate_hr30_installed_leg_drivetrains_p01.py",
    }
    require({row["source"] for row in bindings} == expected_bindings, "installed-drive source binding set mismatch")
    for row in bindings:
        require(row["sha256"] == sha(ROOT / row["source"]), f"installed-drive source hash drift {row['source']}")
        require(row["warning"] == WARNING, f"installed-drive source warning drift {row['source']}")

    installs = rows(SRC / "installed-drivetrain-register.csv")
    require(len(installs) == 10 and {row["axis_id"] for row in installs} == set(AXES), "installed-drive ten-axis coverage mismatch")
    for row in installs:
        drive_id, datum_z, plane_offset, center = AXES[row["axis_id"]]
        require(row["drive_id"] == drive_id, f"installed drive-family mismatch {row['axis_id']}")
        require(abs(xyz_z(row["joint_center_mm"]) - datum_z) < 1e-9, f"installed joint datum drift {row['axis_id']}")
        require(abs(float(row["external_drive_plane_offset_mm"]) - plane_offset) < 1e-9, f"installed service-plane drift {row['axis_id']}")
        require(abs(float(row["solved_pitch_center_distance_mm"]) - center) < 2e-9, f"installed center-distance drift {row['axis_id']}")
        require((row["motor_pulley_code"], row["output_pulley_code"], row["belt_code"]) == PRODUCTS[drive_id], f"installed product-code drift {row['axis_id']}")
        require("NOMINAL SOLIDS INSTALLED" in row["adapter_boundary"] and "PHYSICAL PROOF OPEN" in row["adapter_boundary"] and row["warning"] == WARNING, f"installed unresolved boundary lost {row['axis_id']}")

    components = rows(SRC / "installed-component-register.csv")
    require(len(components) == 90 and Counter(row["axis_id"] for row in components) == Counter({axis: 9 for axis in AXES}), "installed component population mismatch")
    expected_kinds = {"catalog P-bore-plus-tap pulley envelope": 2, "catalog belt routing envelope": 1, "removable guard envelope": 1, "shifted manufacturer actuator": 1, "exact manufacturer horn": 1, "project horn-to-pulley adapter": 1, "shouldered hollow output shaft": 1, "removable output capture washer": 1}
    for axis in AXES:
        require(Counter(row["kind"] for row in components if row["axis_id"] == axis) == Counter(expected_kinds), f"installed component kinds mismatch {axis}")
    require(all(float(row["volume_mm3"]) > 0 and row["warning"] == WARNING for row in components), "installed component geometry/warning invalid")

    clearances = rows(SRC / "inter-drive-clearance-register.csv")
    expected_pairs = {tuple(sorted(pair)) for pair in combinations(AXES, 2)}
    actual_pairs = {tuple(sorted((row["first_axis"], row["second_axis"]))) for row in clearances}
    require(len(clearances) == 45 and actual_pairs == expected_pairs, "installed 45-pair clearance coverage mismatch")
    require(all(float(row["common_volume_mm3"]) <= 1e-6 and row["state"] == "NO COMMON VOLUME" and row["warning"] == WARNING for row in clearances), "installed drivetrain nominal interference found")

    status = json.loads((SRC / "installation-status.json").read_text(encoding="utf-8"))
    require((status["installed_axis_count"], status["installed_component_count"], status["inter_axis_pair_count"], status["inter_axis_common_volume_count"]) == (10, 90, 45, 0), "installed-drive status count drift")
    require(status["nominal_rigid_envelope_inter_axis_screen_pass"] and status["complete_humanoid_present"] and status["whole_body_step_present"] and status["whole_body_glb_present"] and status["generic_reduced_drive_placeholders_removed"] and status["exact_candidate_product_envelopes_installed"], "installed-drive package completion flags missing")
    false_keys = (
        "motion_sweep_validated", "tolerance_validated", "cable_and_cover_clearance_validated",
        "horn_and_hub_adapter_material_fit_fasteners_released", "capacity_validated", "mass_com_reconciled",
        "physical_validation_complete", "procurement_authority", "fabrication_authority",
        "assembly_authority", "powered_test_authority", "motion_authority", "energization_authority",
    )
    require(not any(status[key] for key in false_keys), "installed-drive unsupported validation/authority claim")

    whole_step = cq.importers.importStep(str(SRC / "HR-30_leg_drivetrains_installed_candidate.step")).val()
    drive_step = cq.importers.importStep(str(SRC / "HR-30_installed_leg_drivetrains_only_candidate.step")).val()
    require(whole_step.isValid() and len(whole_step.Solids()) >= 250, "complete installed-drive STEP invalid/incomplete")
    box = whole_step.BoundingBox()
    require(abs(box.zmin) < 1e-6 and abs(box.zmax - 762.0) < 1e-6 and box.xlen > 300 and box.ylen > 150, "installed whole-body STEP is not the complete 762 mm humanoid")
    require(drive_step.isValid() and len(drive_step.Solids()) >= 60, "drivetrain-only STEP invalid/incomplete")
    require((SRC / "HR-30_leg_drivetrains_installed_candidate.glb").stat().st_size > 100_000 and (SRC / "HR-30_installed_leg_drivetrains_only_candidate.glb").stat().st_size > 20_000, "installed-drive GLB export empty")

    whole_status = json.loads((WHOLE / "package-status.json").read_text(encoding="utf-8"))
    require(whole_status["installed_leg_drivetrain_whole_body_cad_present"] and whole_status["installed_leg_drivetrain_axis_count"] == 10 and whole_status["installed_leg_drivetrain_nominal_inter_axis_common_volume_count"] == 0, "whole-body installed-drive integration missing")
    require(whole_status["installed_leg_drivetrain_adapters_complete"] and not whole_status["installed_leg_drivetrain_adapter_material_fit_fasteners_released"] and not whole_status["installed_leg_drivetrain_adapter_physical_fit_validated"], "whole-body adapter geometry/release boundary drift")
    require(not whole_status["installed_leg_drivetrain_motion_sweep_validated"] and not whole_status["installed_leg_drivetrain_capacity_validated"], "whole-body installed-drive overclaim")
    hold = next((row for row in rows(WHOLE / "open-holds.csv") if row["hold_id"] == "HR30-P01-H03"), None)
    require(hold and hold["state"] == "OPEN" and "all 45 nominal inter-drive pairs have zero common volume" in hold["unresolved_item"].lower(), "installed-drive open hold missing")

    page = (SRC / "index.html").read_text(encoding="utf-8")
    require("font:17px/1.55" in page and "font-size:16px" in page and "overflow-x:clip" in page, "installed-drive guide legibility/responsiveness drift")
    require("45 / 55 mm" in page and WARNING in page and "model-viewer" in page, "installed-drive guide content drift")
    require(not any(token in page for token in ("Ã", "Â", "â€")), "installed-drive guide contains mojibake")
    root_page = (WHOLE / "index.html").read_text(encoding="utf-8")
    root_readme = (WHOLE / "README.md").read_text(encoding="utf-8")
    require(root_page.count("<!-- HR30-INSTALLED-LEG-DRIVES-P01-START -->") == 1 and "leg-drivetrain-installation-p0.1/index.html" in root_page, "whole-body page installed-drive integration missing")
    require(root_readme.count("<!-- HR30-INSTALLED-LEG-DRIVES-P01-README-START -->") == 1 and "leg-drivetrain-installation-p0.1/index.html" in root_readme, "whole-body README installed-drive integration missing")

    print("PASS: ten product-specific reduced leg drives are installed in the complete 762 mm humanoid; 90 components, nominal adapters and all 45 inter-drive pairs verified; fits/capacity and all work authority remain open")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
