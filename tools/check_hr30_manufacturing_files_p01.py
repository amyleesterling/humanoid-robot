"""Validate the HR-30 P0.1 individual manufacturing-candidate package."""

from __future__ import annotations

import csv
import hashlib
import json
import re
from collections import Counter
from pathlib import Path

import cadquery as cq


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "hr30" / "whole-body-p0.1"
REL = ROOT / "release" / "hr30" / "whole-body-p0.1"
PKG = SRC / "manufacturing-files"
REL_PKG = REL / "manufacturing-files"
WARNING = (
    "PRELIMINARY - CONFIGURATION AND PACKAGING CAD ONLY - NOT APPROVED FOR "
    "PROCUREMENT, FABRICATION, ASSEMBLY, POWERED TESTING, MOTION, OR ENERGIZATION"
)
MODULES = {"H01", "N01", "T01", "P01", "A01", "G01", "A02", "G02", "L01", "F01", "L02", "F02"}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"FAIL: {message}")


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_csv(path: Path) -> list[dict]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def main() -> int:
    required = {
        "README.md", "index.html", "part-file-register.csv", "material-cut-list.csv",
        "process-route-register.csv", "inspection-characteristic-register.csv",
        "source-binding.json", "manufacturing-files-status.json", "manufacturing-files-source.py",
    }
    require(all((PKG / name).is_file() for name in required), "manufacturing-file package root files incomplete")
    require(all((REL_PKG / name).is_file() for name in required), "release manufacturing-file root files incomplete")
    require(sha(PKG / "manufacturing-files-source.py") == sha(ROOT / "tools" / "generate_hr30_manufacturing_files_p01.py"), "generator snapshot drift")

    rows = read_csv(PKG / "part-file-register.csv")
    require(len(rows) == 66 and len({row["part_id"] for row in rows}) == 66, "66 unique physical parts not present")
    require({row["module"] for row in rows} == MODULES, "twelve-module part coverage drift")
    require(all(not row["part_id"].startswith("HN01_") for row in rows), "nonmaterial harness route leaked into physical parts")
    require(all(float(row["volume_mm3"]) > 0 and float(row["candidate_mass_kg"]) > 0 for row in rows), "empty part geometry or mass")
    require(all(row["warning"] == WARNING and "CANDIDATE FILE" in row["release_state"] for row in rows), "part warning/release boundary drift")

    dxf_rows = [row for row in rows if row["dxf_path"]]
    stl_rows = [row for row in rows if row["stl_path"]]
    require(len(dxf_rows) == 35, "planar profile DXF count drift")
    require(len(stl_rows) == 26 and all(row["role"] == "removable cover" for row in stl_rows), "printed-cover STL count/scope drift")
    require(all(("2.5D" in row["process_candidate"] or "waterjet" in row["process_candidate"]) for row in dxf_rows), "DXF assigned outside planar candidate process")

    imported = 0
    for row in rows:
        step = PKG / row["step_path"]
        svg = PKG / row["svg_path"]
        require(step.is_file() and step.stat().st_size == int(row["step_bytes"]) and sha(step) == row["step_sha256"], f"STEP provenance drift: {row['part_id']}")
        require(svg.is_file() and svg.stat().st_size == int(row["svg_bytes"]) and sha(svg) == row["svg_sha256"], f"SVG provenance drift: {row['part_id']}")
        require("<svg" in svg.read_text(encoding="utf-8", errors="replace")[:2000].lower(), f"invalid SVG: {row['part_id']}")
        shape = cq.importers.importStep(str(step)).val()
        require(not shape.isNull() and shape.isValid() and shape.Volume() > 1e-6, f"invalid STEP: {row['part_id']}")
        require(abs(shape.Volume() - float(row["volume_mm3"])) <= max(0.01, shape.Volume() * 1e-6), f"STEP volume drift: {row['part_id']}")
        imported += 1
        if row["dxf_path"]:
            dxf = PKG / row["dxf_path"]
            text = dxf.read_text(encoding="ascii", errors="ignore")
            require(dxf.is_file() and dxf.stat().st_size == int(row["dxf_bytes"]) and sha(dxf) == row["dxf_sha256"], f"DXF provenance drift: {row['part_id']}")
            require("SECTION" in text and "ENTITIES" in text and float(row["largest_planar_profile_area_mm2"]) > 0, f"invalid DXF profile: {row['part_id']}")
        if row["stl_path"]:
            stl = PKG / row["stl_path"]
            require(stl.is_file() and stl.stat().st_size == int(row["stl_bytes"]) and sha(stl) == row["stl_sha256"] and stl.stat().st_size > 84, f"STL provenance drift: {row['part_id']}")

    materials = read_csv(PKG / "material-cut-list.csv")
    processes = read_csv(PKG / "process-route-register.csv")
    inspections = read_csv(PKG / "inspection-characteristic-register.csv")
    require(len(materials) == len(processes) == 66, "material/process register count drift")
    require({row["part_id"] for row in materials} == {row["part_id"] for row in rows} == {row["part_id"] for row in processes}, "part registers do not reconcile")
    require(len(inspections) == 330 and Counter(row["part_id"] for row in inspections) == Counter({row["part_id"]: 5 for row in rows}), "five inspection characteristics per part not present")
    require(all("SELECTION REQUIRED" in row["acceptance_requirement"] and row["result"] == "NOT EXECUTED" for row in inspections), "inspection register overclaims release/evidence")

    binding = json.loads((PKG / "source-binding.json").read_text(encoding="utf-8"))
    require(binding["physical_source_part_count"] == 66 and binding["excluded_reference_volume_count"] == 12, "source binding counts drift")
    require(binding["source_generator_sha256"] == sha(ROOT / binding["source_generator"]), "fabrication source hash drift")
    require(binding["manufacturing_file_generator_sha256"] == sha(ROOT / binding["manufacturing_file_generator"]), "manufacturing generator hash drift")

    status = json.loads((PKG / "manufacturing-files-status.json").read_text(encoding="utf-8"))
    expected_counts = {
        "physical_part_count": 66, "individual_step_count": 66,
        "individual_svg_drawing_view_count": 66, "planar_profile_dxf_count": 35,
        "printed_cover_stl_count": 26, "inspection_characteristic_count": 330,
        "module_count": 12, "reference_route_volumes_excluded": 12,
    }
    require(all(status[key] == value for key, value in expected_counts.items()), "manufacturing status counts drift")
    false_keys = (
        "drawings_released", "materials_selected", "tolerances_gdt_released", "dfm_complete", "fai_complete",
        "structural_capacity_validated", "physical_validation_complete", "procurement_authority",
        "fabrication_authority", "assembly_authority", "powered_test_authority", "motion_authority", "energization_authority",
    )
    require(not any(status[key] for key in false_keys) and status["warning"] == WARNING, "manufacturing package overclaims validation/authority")

    source_files = {path.relative_to(PKG).as_posix(): path for path in PKG.rglob("*") if path.is_file()}
    release_files = {path.relative_to(REL_PKG).as_posix(): path for path in REL_PKG.rglob("*") if path.is_file()}
    require(source_files.keys() == release_files.keys(), "manufacturing source/release file-set drift")
    require(all(sha(path) == sha(release_files[name]) for name, path in source_files.items()), "manufacturing source/release hash drift")
    require(all(path.stat().st_size < 100_000_000 for path in source_files.values()), "manufacturing artifact exceeds GitHub hard limit")
    manifest = {row["path"]: row for row in read_csv(SRC / "file-manifest.csv")}
    for name, path in source_files.items():
        key = f"manufacturing-files/{name}"
        require(key in manifest and int(manifest[key]["bytes"]) == path.stat().st_size and manifest[key]["sha256"] == sha(path), f"parent manifest drift: {key}")

    page = (PKG / "index.html").read_text(encoding="utf-8")
    require(page.count('class="part"') == 66 and page.count("<details open>") == 12, "manufacturing guide body/module counts drift")
    require("font:17px/1.55" in page and not re.search(r"font-size:\s*(?:[0-9]|1[01])px", page), "manufacturing guide legibility drift")
    require(all(row["step_path"] in page and row["svg_path"] in page for row in rows), "manufacturing guide links incomplete")
    require(WARNING in page and "not released drawings" in page.lower(), "manufacturing guide authority boundary missing")
    parent_page = (SRC / "index.html").read_text(encoding="utf-8")
    require(parent_page.count('id="manufacturing-files"') == 1 and "manufacturing-files/index.html" in parent_page, "whole-body guide manufacturing section missing")
    parent_status = json.loads((SRC / "package-status.json").read_text(encoding="utf-8"))
    require(parent_status["individual_manufacturing_file_package_present"] and parent_status["individual_physical_part_step_count"] == 66, "whole-body package manufacturing binding missing")
    require(not parent_status["individual_part_files_fabrication_released"] and not parent_status["individual_part_drawings_released"], "whole-body package overclaims part release")
    readme = (SRC / "README.md").read_text(encoding="utf-8")
    require("## Individual manufacturing-candidate files" in readme and "66 physical frame" in readme, "whole-body README manufacturing section missing")
    holds = {row["hold_id"]: row for row in read_csv(SRC / "open-holds.csv")}
    require("All 66 physical frame/cover candidates" in holds["HR30-P01-H06"]["unresolved_item"], "H06 manufacturing disposition missing")
    require("individual candidate files for all 66" in holds["HR30-P01-H10"]["unresolved_item"], "H10 manufacturing disposition missing")

    print(f"PASS: reimported {imported} individual STEP files; 66 physical HR-30 candidates have STEP/SVG, 35 planar candidates have DXF and 26 covers have STL; drawing release, DFM/FAI, proof and all work authority remain false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
