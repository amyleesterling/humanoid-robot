"""Fail-closed checks for HR-30 leg-drive adapter geometry and allocation."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

import cadquery as cq


ROOT = Path(__file__).resolve().parents[1]
WHOLE = ROOT / "hr30" / "whole-body-p0.1"
SRC = WHOLE / "leg-drivetrain-adapters-p0.1"
REL = ROOT / "release" / "hr30" / "whole-body-p0.1" / "leg-drivetrain-adapters-p0.1"
WARNING = "PRELIMINARY - DIMENSIONED ADAPTER GEOMETRY CANDIDATE ONLY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, POWERED TESTING, MOTION, OR ENERGIZATION"
PARTS = {"MA-HN13-P10": 6, "MA-HN12-P10": 2, "MA-HN12-P8": 2, "OS-P12-45": 8, "OS-P12-55": 2}
AXES = {
    "L_HIP_PITCH", "R_HIP_PITCH", "L_HIP_ROLL", "R_HIP_ROLL", "L_KNEE_PITCH", "R_KNEE_PITCH",
    "L_ANKLE_PITCH", "R_ANKLE_PITCH", "L_ANKLE_ROLL", "R_ANKLE_ROLL",
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"FAIL: {message}")


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rows(path: Path) -> list[dict]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def main() -> int:
    require(SRC.is_dir() and REL.is_dir(), "adapter source/release package missing")
    source_files = {path.relative_to(SRC).as_posix() for path in SRC.rglob("*") if path.is_file()}
    release_files = {path.relative_to(REL).as_posix() for path in REL.rglob("*") if path.is_file()}
    required = {
        "README.md", "index.html", "adapter-status.json", "adapter-part-register.csv",
        "interface-definition-register.csv", "axis-adapter-allocation.csv", "fastener-selection-register.csv",
        "source-binding.csv", "file-manifest.csv", "leg-drivetrain-adapters-source.py",
        "HR-30_leg_drivetrain_adapter_lineup_candidate.step", "HR-30_leg_drivetrain_adapter_lineup_candidate.glb",
    }
    required |= {f"parts/{part}.step" for part in PARTS} | {f"drawings/{part}.svg" for part in PARTS}
    require(required <= source_files, "adapter artifacts missing")
    require(source_files == release_files, "adapter source/release file-set mismatch")
    for name in source_files:
        require(sha(SRC / name) == sha(REL / name), f"adapter source/release mismatch {name}")

    manifest = rows(SRC / "file-manifest.csv")
    require({row["path"] for row in manifest} == source_files - {"file-manifest.csv"}, "adapter manifest file-set mismatch")
    for row in manifest:
        path = SRC / row["path"]
        require(int(row["bytes"]) == path.stat().st_size and row["sha256"] == sha(path), f"adapter manifest mismatch {row['path']}")
        require(row["warning"] == WARNING, f"adapter manifest warning drift {row['path']}")

    part_rows = rows(SRC / "adapter-part-register.csv")
    require({row["part_id"]: int(row["quantity"]) for row in part_rows} == PARTS, "adapter part family/quantity drift")
    require(all(row["nominal_geometry_complete"] == "True" and row["fit_tolerance_released"] == "False" and row["capacity_validated"] == "False" for row in part_rows), "adapter geometry/release boundary drift")
    interfaces = rows(SRC / "interface-definition-register.csv")
    require(len(interfaces) == 8 and {row["part_id"] for row in interfaces} == set(PARTS), "adapter interface register incomplete")
    require(all(row["nominal_definition"] == "COMPLETE" and row["tolerance_fit"] == "SELECTION REQUIRED" and "OPEN" in row["validation"] for row in interfaces), "adapter interface release overclaim")

    allocations = rows(SRC / "axis-adapter-allocation.csv")
    require(len(allocations) == 10 and {row["axis_id"] for row in allocations} == AXES, "adapter ten-axis coverage mismatch")
    require(all(row["motor_adapter"] in PARTS and row["output_adapter"] in PARTS and row["nominal_allocation_complete"] == "True" and row["fit_capacity_physical_validation"] == "OPEN" for row in allocations), "adapter allocation boundary drift")
    require({row["motor_pulley"] for row in allocations} == {"GPA16GT5090-A-P8", "GPA20GT5090-A-P10"}, "motor P-bore candidate drift")
    require({row["output_pulley"] for row in allocations} == {"GPA30GT5090-A-P12", "GPA40GT5090-A-P12"}, "output P-bore candidate drift")

    bindings = rows(SRC / "source-binding.csv")
    require(len(bindings) == 4, "adapter source register count drift")
    local = {row["source_id"]: row for row in bindings}
    require(local["ADS-01"]["sha256"].upper() == "6DE6851B85132EC496F24A177729ECA5CE43416707652E79183BFA51E7F978FD", "HN12 source identity drift")
    require(local["ADS-02"]["sha256"].upper() == "F3308807BC92C17E13F0785353B59D117DE8CEF96D3F7638D1388A92B46ABC6F", "HN13 source identity drift")
    require(local["ADS-03"]["sha256"].upper() == "0799620CEB55DB471F4C4A16CB70751119B0478F970D0F47C301215E4C25CCBF", "MISUMI source identity drift")
    require(local["ADS-04"]["sha256"] == sha(ROOT / local["ADS-04"]["path_or_url"]), "adapter generator hash drift")

    for part in PARTS:
        shape = cq.importers.importStep(str(SRC / "parts" / f"{part}.step")).val()
        require(shape.isValid() and shape.Volume() > 100, f"adapter STEP invalid {part}")
        require(len(shape.Solids()) >= 2, f"adapter STEP lacks assembled part boundary {part}")
    lineup = cq.importers.importStep(str(SRC / "HR-30_leg_drivetrain_adapter_lineup_candidate.step")).val()
    require(lineup.isValid() and len(lineup.Solids()) >= 10 and lineup.BoundingBox().xlen > 180, "adapter lineup STEP invalid")
    require((SRC / "HR-30_leg_drivetrain_adapter_lineup_candidate.glb").stat().st_size > 20_000, "adapter lineup GLB empty")

    status = json.loads((SRC / "adapter-status.json").read_text(encoding="utf-8"))
    require((status["motor_adapter_family_count"], status["output_adapter_family_count"], status["whole_robot_reduced_axis_count"]) == (3, 2, 10), "adapter status count drift")
    require(status["axis_allocation_complete"] and status["exact_vendor_horn_step_bound"] and status["nominal_adapter_geometry_complete"] and status["editable_source_cad_present"] and status["misumi_p_bore_retention_topology_selected"], "adapter completion flags missing")
    false_keys = (
        "material_selected", "fits_and_tolerances_released", "fasteners_released", "capacity_validated",
        "physical_fit_validated", "procurement_authority", "fabrication_authority", "assembly_authority",
        "powered_test_authority", "motion_authority", "energization_authority",
    )
    require(not any(status[key] for key in false_keys), "adapter status grants unsupported release/authority")

    whole = json.loads((WHOLE / "package-status.json").read_text(encoding="utf-8"))
    require(whole["leg_drivetrain_adapter_package_present"] and whole["leg_drivetrain_adapter_nominal_geometry_complete"] and whole["reduced_leg_drivetrain_horn_adapters_complete"], "whole-body adapter integration missing")
    require(not whole["leg_drivetrain_adapter_fit_and_tolerance_released"] and not whole["leg_drivetrain_adapter_capacity_validated"] and not whole["leg_drivetrain_adapter_physical_fit_validated"], "whole-body adapter release overclaim")
    require(not any(whole[key] for key in ("procurement_authority", "fabrication_authority", "assembly_authority", "powered_test_authority", "motion_authority", "energization_authority")), "whole-body work authority overclaim")

    page = (SRC / "index.html").read_text(encoding="utf-8")
    require("font:17px/1.55" in page and "font-size:16px" in page and "overflow-x:clip" in page, "adapter guide legibility/responsiveness drift")
    require(WARNING in page and "model-viewer" in page and all(part in page for part in PARTS), "adapter guide content incomplete")
    require(not any(token in page for token in ("Ãƒ", "Ã‚", "Ã¢â‚¬")), "adapter guide contains mojibake")
    root_page = (WHOLE / "index.html").read_text(encoding="utf-8")
    root_readme = (WHOLE / "README.md").read_text(encoding="utf-8")
    require(root_page.count("<!-- HR30-LEG-ADAPTERS-P01-START -->") == 1 and "leg-drivetrain-adapters-p0.1/index.html" in root_page, "whole-body page adapter integration missing")
    require(root_readme.count("<!-- HR30-LEG-ADAPTERS-P01-README-START -->") == 1 and "leg-drivetrain-adapters-p0.1/index.html" in root_readme, "whole-body README adapter integration missing")

    print("PASS: five dimensioned adapter families cover all ten reduced leg axes; exact horn sources and nominal CAD verified; fits/capacity and all work authority remain open")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
