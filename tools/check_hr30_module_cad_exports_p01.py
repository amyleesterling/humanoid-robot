"""Fail-closed validation for the HR-30 P0.1 separable module CAD."""

from __future__ import annotations

import csv
import hashlib
import json
import re
import struct
from pathlib import Path

import cadquery as cq


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "hr30" / "whole-body-p0.1"
REL = ROOT / "release" / "hr30" / "whole-body-p0.1"
MOD = SRC / "module-cad"
REL_MOD = REL / "module-cad"
WARNING = (
    "PRELIMINARY - CONFIGURATION AND PACKAGING CAD ONLY - NOT APPROVED FOR "
    "PROCUREMENT, FABRICATION, ASSEMBLY, POWERED TESTING, MOTION, OR ENERGIZATION"
)
MODULE_IDS = {"H01", "N01", "T01", "P01", "A01", "G01", "A02", "G02", "L01", "F01", "L02", "F02"}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"FAIL: {message}")


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_csv(path: Path) -> list[dict]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def import_step(path: Path) -> cq.Shape:
    result = cq.importers.importStep(str(path)).val()
    require(not result.isNull() and result.isValid() and result.Volume() > 1e-6, f"invalid STEP {path}")
    return result


def main() -> int:
    required_root = {
        "README.md", "index.html", "module-export-register.csv", "module-cad-source.py", "module-cad-status.json",
        "HR-30_module_exploded_candidate.step", "HR-30_module_exploded_candidate.glb",
    }
    require(all((MOD / name).is_file() for name in required_root), "module CAD root file set incomplete")
    require(all((REL_MOD / name).is_file() for name in required_root), "release module CAD root file set incomplete")
    require(sha(MOD / "module-cad-source.py") == sha(ROOT / "tools" / "generate_hr30_module_cad_exports_p01.py"), "module CAD generator snapshot drift")

    rows = read_csv(MOD / "module-export-register.csv")
    require(len(rows) == 12 and {r["module_id"] for r in rows} == MODULE_IDS, "12-module export register drift")
    require(sum(int(r["fabrication_part_count"]) for r in rows) == 98, "98 fabrication parts are not owned exactly once")
    require(all(int(r["fabrication_part_count"]) > 0 for r in rows), "a module has no fabrication geometry")
    require(all(int(r["body_component_count"]) > 0 for r in rows), "a module has no body/joint/hand geometry")
    require(all(int(r["integration_physical_solid_count"]) >= int(r["fabrication_part_count"]) for r in rows), "integration solid count below fabrication count")
    require(next(int(r["body_component_count"]) for r in rows if r["module_id"] == "H01") >= 6, "head geometry incomplete")
    require(all(next(int(r["body_component_count"]) for r in rows if r["module_id"] == module) >= 12 for module in ("G01", "G02")), "functional hand geometry incomplete")
    require(all(next(int(r["body_component_count"]) for r in rows if r["module_id"] == module) >= 69 for module in ("L01", "L02")), "articulated leg geometry incomplete")

    imported = 0
    for row in rows:
        require(row["warning"] == WARNING and "SEPARABLE P0.1 MODULE CAD" in row["release_state"], f"{row['module_id']} warning/release drift")
        fab = MOD / row["fabrication_step"]
        integration = MOD / row["integration_reference_step"]
        require(fab.is_file() and integration.is_file(), f"{row['module_id']} STEP file missing")
        require(fab.stat().st_size == int(row["fabrication_step_bytes"]) and sha(fab) == row["fabrication_step_sha256"], f"{row['module_id']} fabrication STEP provenance drift")
        require(integration.stat().st_size == int(row["integration_reference_step_bytes"]) and sha(integration) == row["integration_reference_step_sha256"], f"{row['module_id']} integration STEP provenance drift")
        fab_shape = import_step(fab)
        integration_shape = import_step(integration)
        imported += 2
        require(integration_shape.Volume() >= fab_shape.Volume() * 0.999999, f"{row['module_id']} integration volume below fabrication volume")
        box = integration_shape.BoundingBox()
        require(abs(box.xlen - float(row["integration_bbox_x_mm"])) <= 0.01, f"{row['module_id']} X bbox drift")
        require(abs(box.ylen - float(row["integration_bbox_y_mm"])) <= 0.01, f"{row['module_id']} Y bbox drift")
        require(abs(box.zlen - float(row["integration_bbox_z_mm"])) <= 0.01, f"{row['module_id']} Z bbox drift")

    exploded = import_step(MOD / "HR-30_module_exploded_candidate.step")
    imported += 1
    exploded_box = exploded.BoundingBox()
    require(exploded_box.xlen > 780 and exploded_box.zlen > 950, "exploded whole-body separation envelope is not present")
    glb_path = MOD / "HR-30_module_exploded_candidate.glb"
    glb_bytes = glb_path.stat().st_size
    require(100_000 < glb_bytes < 100_000_000, "exploded GLB is empty or exceeds GitHub's single-file limit")
    magic, version, declared_length = struct.unpack("<4sII", glb_path.open("rb").read(12))
    require(magic == b"glTF" and version == 2 and declared_length == glb_bytes, "exploded GLB header/length is invalid")

    source_files = {p.relative_to(MOD).as_posix(): p for p in MOD.rglob("*") if p.is_file()}
    release_files = {p.relative_to(REL_MOD).as_posix(): p for p in REL_MOD.rglob("*") if p.is_file()}
    require(source_files.keys() == release_files.keys(), "module CAD source/release file-set drift")
    require(all(sha(path) == sha(release_files[name]) for name, path in source_files.items()), "module CAD source/release hash drift")

    manifest = {r["path"]: r for r in read_csv(SRC / "file-manifest.csv")}
    for name, path in source_files.items():
        key = f"module-cad/{name}"
        require(key in manifest and int(manifest[key]["bytes"]) == path.stat().st_size and manifest[key]["sha256"] == sha(path), f"package manifest drift for {key}")

    status = json.loads((MOD / "module-cad-status.json").read_text(encoding="utf-8"))
    require(status["module_count"] == status["fabrication_step_count"] == status["integration_reference_step_count"] == 12, "module CAD status count drift")
    require(status["fabrication_part_ownership_count"] == 98 and status["exploded_step_present"] and status["exploded_glb_present"], "module CAD status incomplete")
    require(status["exploded_glb_display_linear_tolerance_mm"] == 0.50 and status["exploded_glb_display_angular_tolerance_rad"] == 0.25, "GLB display-tessellation provenance drift")
    require(not any(status[key] for key in ("drawings_released", "materials_selected", "fasteners_selected", "structural_capacity_validated", "fabrication_authority", "powered_test_authority", "motion_authority", "energization_authority")), "module CAD status overclaims release or authority")
    package_status = json.loads((SRC / "package-status.json").read_text(encoding="utf-8"))
    require(package_status["module_cad_exports_present"] and package_status["module_cad_export_count"] == 12, "package module CAD status missing")
    require(package_status["module_fabrication_step_count"] == package_status["module_integration_reference_step_count"] == 12, "package module STEP count drift")
    require(package_status["exploded_module_step_present"] and package_status["exploded_module_glb_present"], "package exploded assembly status missing")
    require(not package_status["module_cad_manufacturing_released"] and not package_status["fabrication_drawings_released"], "package manufacturing release overclaim")

    page = (MOD / "index.html").read_text(encoding="utf-8")
    require(
        page.count('class="module"') == 12
        and "font:17px/1.55" in page
        and not re.search(r"font-size:\s*(?:[0-9]|1[01])px", page),
        "module CAD guide count/legibility drift",
    )
    require(all(f"{module}/{module}_fabrication_candidate.step" in page and f"{module}/{module}_integration_reference.step" in page for module in MODULE_IDS), "module CAD guide links incomplete")
    require(WARNING in page and "neither is a released part drawing" in page.lower(), "module CAD guide warning boundary missing")
    package_page = (SRC / "index.html").read_text(encoding="utf-8")
    require(package_page.count('id="module-cad"') == 1 and "module-cad/index.html" in package_page and "HR-30_module_exploded_candidate.glb" in package_page, "main package module CAD section missing")
    atlas = (SRC / "whole-body-interface-atlas.html").read_text(encoding="utf-8")
    require("Separate the robot into build modules" in atlas and "module-cad/HR-30_module_exploded_candidate.glb" in atlas, "interface atlas exploded-module view missing")

    print(f"PASS: reimported {imported} native STEP assemblies; 12 HR-30 modules own all 98 fabrication parts including both detailed hand mechanisms and include body/joint/hand/equipment reference geometry; drawings and all work authority remain false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
