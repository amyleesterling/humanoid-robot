"""Fail-closed checks for the HR-30 P0.1 whole-body interface atlas."""

from __future__ import annotations

import csv
import hashlib
import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "hr30" / "whole-body-p0.1"
REL = ROOT / "release" / "hr30" / "whole-body-p0.1"
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


def rows(name: str) -> list[dict]:
    with (SRC / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def main() -> int:
    required = {
        "module-interface-control-register.csv", "module-assembly-sequence.csv",
        "whole-body-interface-atlas.svg", "whole-body-interface-atlas.html", "interface-atlas-source.py",
    }
    require(all((SRC / name).is_file() for name in required), "interface atlas file set incomplete")
    require(all((REL / name).is_file() for name in required), "release interface atlas file set incomplete")
    require(all(sha(SRC / name) == sha(REL / name) for name in required), "source/release interface atlas drift")
    require(sha(SRC / "interface-atlas-source.py") == sha(ROOT / "tools" / "generate_hr30_whole_body_interface_atlas_p01.py"), "atlas generator snapshot drift")

    modules = rows("module-interface-control-register.csv")
    require(len(modules) == 12 and {r["module_id"] for r in modules} == MODULE_IDS, "12-module identity coverage drift")
    owned = []
    for row in modules:
        require(row["warning"] == WARNING, f"{row['module_id']} warning drift")
        require(all(float(row[key]) > 0 for key in ("bbox_width_x_mm", "bbox_depth_y_mm", "bbox_height_z_mm")), f"{row['module_id']} nonphysical envelope")
        require(float(row["planning_mass_kg"]) >= 0 and int(row["fabrication_part_count"]) >= 0, f"{row['module_id']} invalid planning values")
        require(row["primary_datum"] and row["upstream_interface"] and row["downstream_interface"], f"{row['module_id']} interface definition missing")
        require(row["joint_interface_summary"] and row["candidate_actuation"] and row["refinement_path"], f"{row['module_id']} mechanical/actuation/refinement path missing")
        axis_ids = [] if row["owned_axes"] == "NONE - PASSIVE BODY MODULE" else row["owned_axes"].split("; ")
        require(len(axis_ids) == int(row["owned_axis_count"]), f"{row['module_id']} owned-axis count drift")
        owned.extend(axis_ids)
    scheduled_axes = {r["axis_id"] for r in rows("joint-axis-schedule.csv")}
    require(len(owned) == 25 and len(set(owned)) == 25 and set(owned) == scheduled_axes, "25-axis module ownership incomplete or duplicated")

    mass_total = next(float(r["allocated_mass_kg"]) for r in rows("mass-properties-budget.csv") if r["link"] == "TOTAL")
    module_mass = sum(float(r["planning_mass_kg"]) for r in modules)
    require(abs(module_mass - mass_total) <= 5e-6, "module mass does not reconcile to whole-body planning mass within published-row rounding")

    assembly = rows("module-assembly-sequence.csv")
    require(len(assembly) == 12 and {r["module_id"] for r in assembly} == MODULE_IDS, "assembly sequence does not cover all modules once")
    require(all(r["warning"] == WARNING and "NO ASSEMBLY OR POWERED-WORK AUTHORITY" in r["release_state"] for r in assembly), "assembly authority/warning drift")
    require(max(int(r["assembly_step"]) for r in assembly) == 8, "controlled assembly sequence drift")

    svg_path = SRC / "whole-body-interface-atlas.svg"
    ET.parse(svg_path)
    svg = svg_path.read_text(encoding="utf-8")
    require("762 mm nominal floor-to-shell top" in svg and "25 named joint axes" in svg, "dimensioned atlas annotations missing")
    require(all(axis in svg for axis in scheduled_axes), "not all joint identities appear in SVG tooltips")

    atlas = (SRC / "whole-body-interface-atlas.html").read_text(encoding="utf-8")
    require("All 25 controlled axes" in atlas and "Module interface control" in atlas, "atlas sections missing")
    require(atlas.count('class="module"') == 12 and atlas.count("<tr><td>") == 25, "atlas module/axis rendering counts drift")
    require("font:17px/1.55" in atlas and "font-size:16px" in atlas, "atlas legibility baseline missing")
    require(not re.search(r"font-size:\s*(?:[0-9]|1[01])px", atlas), "atlas contains user-facing text below 12 px")
    require(WARNING in atlas and "not a released manufacturing drawing" in atlas.lower(), "atlas preliminary boundary missing")
    require("HR-30_installed_equipment_candidate.glb" in atlas and "HR-30_integrated_whole_robot_candidate.step" in atlas, "atlas lacks complete body model links")

    status = json.loads((SRC / "package-status.json").read_text(encoding="utf-8"))
    require(status["whole_body_interface_atlas_present"] and status["module_interface_control_count"] == 12, "package atlas status missing")
    require(status["module_interface_axis_ownership_count"] == 25, "package axis ownership status drift")
    require(abs(status["module_interface_mass_reconciliation_kg"] - mass_total) <= 5e-6, "package module mass status drift")
    require(abs(status["module_interface_mass_rounding_delta_kg"] - (mass_total - module_mass)) <= 1e-9, "module mass rounding disclosure drift")
    require(status["dimensioned_whole_body_front_side_reference_present"], "package dimensioned view status missing")
    require(not status["manufacturing_detail_complete"] and not status["fabrication_drawings_released"], "manufacturing release overclaim")
    require(not any(status[key] for key in ("procurement_authority", "fabrication_authority", "powered_test_authority", "motion_authority", "energization_authority")), "work authority overclaim")

    page = (SRC / "index.html").read_text(encoding="utf-8")
    require(page.count('id="whole-body-interface-atlas"') == 1, "main web atlas section missing or duplicated")
    require(all(name in page for name in ("whole-body-interface-atlas.html", "whole-body-interface-atlas.svg", "module-interface-control-register.csv", "module-assembly-sequence.csv")), "main web atlas links incomplete")
    require("KiCad remains open" not in page and "Actuator-side pins verified" in page and "Harness remains preliminary" in page, "stale KiCad web statement remains")

    print(f"PASS: HR-30 whole-body interface atlas covers 12 physical modules, owns all 25 axes exactly once, and reconciles {module_mass:.6f} kg; manufacturing detail and all work authority remain false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
