"""Fail-closed checks for the HR-30 modular fabrication architecture P0.1."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

import cadquery as cq


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "hr30" / "whole-body-p0.1"
REL = ROOT / "release" / "hr30" / "whole-body-p0.1"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"FAIL: {message}")


def main() -> int:
    required = {
        "HR-30_modular_fabrication_candidate.step",
        "HR-30_modular_fabrication_reference.step",
        "HR-30_modular_fabrication_reference.glb",
        "fabrication-part-register.csv",
        "service-panel-interface-register.csv",
        "harness-route-register.csv",
        "fabrication-architecture-status.json",
        "fabrication-architecture-source.py",
    }
    require(required <= {path.relative_to(SRC).as_posix() for path in SRC.rglob("*") if path.is_file()}, "fabrication artifact set incomplete")
    for name in required:
        require((REL / name).is_file() and sha(SRC / name) == sha(REL / name), f"source/release fabrication mismatch {name}")

    status = json.loads((SRC / "fabrication-architecture-status.json").read_text(encoding="utf-8"))
    require(status["identifier"] == "HR-30-FABRICATION-ARCH-P0.1", "fabrication identifier mismatch")
    require(status["physical_fabrication_part_count"] >= 60, "fabrication assembly lacks complete physical part population")
    require(status["service_panel_count"] == 26, "service panel count mismatch")
    require(status["harness_route_count"] == 11, "harness route count mismatch")
    require(status["all_geometry_valid"] and status["frame_geometry_present"] and status["hollow_split_shell_geometry_present"], "frame/shell geometry status incomplete")
    require(status["service_access_geometry_present"] and status["segregated_harness_corridors_present"], "service/harness geometry status incomplete")
    require(not any(status[key] for key in ("drawings_released", "materials_selected", "fasteners_selected", "harness_selected", "structural_capacity_validated", "fabrication_authority", "powered_test_authority", "motion_authority", "energization_authority")), "fabrication status overclaims release or authority")

    parts = list(csv.DictReader((SRC / "fabrication-part-register.csv").open(encoding="utf-8")))
    panels = list(csv.DictReader((SRC / "service-panel-interface-register.csv").open(encoding="utf-8")))
    routes = list(csv.DictReader((SRC / "harness-route-register.csv").open(encoding="utf-8")))
    require(len({row["part_id"] for row in parts}) == len(parts), "duplicate fabrication part identity")
    require({row["module"] for row in parts} >= {"H01", "N01", "T01", "P01", "A01", "A02", "G01", "G02", "L01", "L02", "F01", "F02", "HN01"}, "fabrication geometry does not cover every body module")
    require(len(panels) == 26 and len({row["panel_id"] for row in panels}) == 26, "service panel register incomplete")
    require(all(float(row["nominal_wall_mm"]) >= 1.8 and "SELECTION REQUIRED" in row["release_state"] for row in panels), "panel wall/release boundary missing")
    require(len(routes) == 11 and {row["service_class"] for row in routes} == {"ACTUATOR POWER", "DATA/LOW VOLTAGE", "DATA/ENCODER"}, "harness route service classes incomplete")
    require(all(float(row["minimum_dynamic_bend_radius_mm"]) >= 40 and row["connector_boundary"] == "SELECTION REQUIRED" for row in routes), "harness bend/connector boundary incomplete")
    require(sum(row["service_class"] == "ACTUATOR POWER" for row in routes) == 5, "actuator-power route count mismatch")
    require(sum(row["service_class"] != "ACTUATOR POWER" for row in routes) == 6, "data/low-voltage route count mismatch")

    frame_mass = sum(float(row["cad_mass_screen_kg"]) for row in parts if row["role"] not in {"removable cover", "harness corridor reference"})
    cover_mass = sum(float(row["cad_mass_screen_kg"]) for row in parts if row["role"] == "removable cover")
    require(abs(frame_mass - status["frame_mass_screen_kg"]) < 1e-4, "frame mass screen mismatch")
    require(abs(cover_mass - status["cover_mass_screen_kg"]) < 1e-4, "cover mass screen mismatch")
    require(frame_mass > 0.2 and cover_mass > 0.1, "fabrication mass screens implausibly empty")

    model = cq.importers.importStep(str(SRC / "HR-30_modular_fabrication_candidate.step")).val()
    require(model.isValid() and model.Volume() > 100000, "fabrication STEP invalid or empty")
    box = model.BoundingBox()
    require(box.zmin >= -1e-7 and box.zmax > 750, "fabrication assembly floor/height coverage invalid")
    require((SRC / "HR-30_modular_fabrication_reference.glb").stat().st_size > 10000, "fabrication GLB empty")
    require(sha(SRC / "fabrication-architecture-source.py") == sha(ROOT / "tools" / "generate_hr30_fabrication_architecture_p01.py"), "fabrication source snapshot drift")

    package = json.loads((SRC / "package-status.json").read_text(encoding="utf-8"))
    require(package["modular_fabrication_architecture_present"] and package["fabrication_part_count"] == status["physical_fabrication_part_count"], "main package fabrication status mismatch")
    require(package["service_panel_count"] == 26 and package["harness_route_count"] == 11, "main package service/harness counts mismatch")
    require(not package["fabrication_drawings_released"] and not package["harness_selected_or_validated"], "main package release boundary overclaim")

    bom = {row["item_id"]: row for row in csv.DictReader((SRC / "whole-robot-candidate-bom.csv").open(encoding="utf-8"))}
    require(bom["HR30-BOM-003"]["quantity"] == "2" and "wrist" in bom["HR30-BOM-003"]["function"], "wrist actuator BOM allocation stale")
    require(bom["HR30-BOM-004"]["quantity"] == "4" and "head/gripper" in bom["HR30-BOM-004"]["function"], "XC330 head/gripper BOM allocation stale")
    require("11 located route-derived" in bom["HR30-BOM-030"]["candidate"], "harness BOM not synchronized to installed route architecture")
    require("Released interface-control drawings" in (SRC / "modular-fabrication-assembly-electrification-plan.md").read_text(encoding="utf-8"), "build plan does not disclose unreleased interface drawings")
    page = (SRC / "index.html").read_text(encoding="utf-8")
    require("HR-30_modular_fabrication_candidate.step" in page and "harness-route-register.csv" in page, "web guide does not expose fabrication artifacts")
    require('src="HR-30_modular_fabrication_reference.glb"' in page and "Inspect the modular frame" in page, "web guide does not expose the interactive fabrication assembly")
    print(f"PASS: HR-30 modular fabrication architecture has {status['physical_fabrication_part_count']} physical parts, 26 service panels, 11 harness corridors, synchronized STEP/GLB/source-release evidence; no fabrication or powered authority")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
