#!/usr/bin/env python3
"""Fail-closed checker for the HR-30 first-energization cell P0.1."""

from __future__ import annotations

import csv
import hashlib
import json
import math
import re
from pathlib import Path

import cadquery as cq


ROOT = Path(__file__).resolve().parents[1]
WHOLE = ROOT / "hr30" / "whole-body-p0.1"
OUT = WHOLE / "first-energization-cell-p0.1"
RELEASE = ROOT / "release" / "hr30" / "whole-body-p0.1" / "first-energization-cell-p0.1"
GEN = ROOT / "tools" / "generate_hr30_first_energization_cell_p01.py"
ROBOT = WHOLE / "HR-30_p00_neutral_stand_candidate.step"
IDENTIFIER = "HR30-FIRST-ENERGIZATION-CELL-P0.1"
WARNING = (
    "PRELIMINARY - UNBUILT STATIC FIRST-ENERGIZATION CELL CANDIDATE - "
    "NOT A WALKING GANTRY OR RATED FALL-ARREST SYSTEM - NOT APPROVED FOR "
    "PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, "
    "WALKING OR ENERGIZATION"
)


def need(value: bool, message: str) -> None:
    if not value:
        raise SystemExit(f"FAIL: {message}")


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rows(name: str) -> list[dict[str, str]]:
    with (OUT / name).open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def close(a: float, b: float, tolerance: float = 0.2) -> bool:
    return math.isclose(a, b, abs_tol=tolerance)


def check_manifest() -> None:
    manifest = rows("file-manifest.csv")
    listed = {row["path"] for row in manifest}
    actual = {p.relative_to(OUT).as_posix() for p in OUT.rglob("*") if p.is_file() and p.name != "file-manifest.csv"}
    need(listed == actual, f"manifest set mismatch missing={sorted(actual-listed)} extra={sorted(listed-actual)}")
    for row in manifest:
        path = OUT / row["path"]
        need(path.stat().st_size == int(row["bytes"]), f"manifest byte mismatch {row['path']}")
        need(sha(path) == row["sha256"], f"manifest hash mismatch {row['path']}")
        need(row["warning"] == WARNING, f"manifest warning drift {row['path']}")
    source = {p.relative_to(OUT).as_posix(): sha(p) for p in OUT.rglob("*") if p.is_file()}
    release = {p.relative_to(RELEASE).as_posix(): sha(p) for p in RELEASE.rglob("*") if p.is_file()}
    need(source == release, "source/release file-set or hash parity failed")


def check_geometry() -> None:
    robot = cq.importers.importStep(str(ROBOT)).val().BoundingBox()
    need(close(robot.xlen, 330.0) and close(robot.ylen, 152.5) and close(robot.zlen, 764.5), "bound robot extent drift")
    whole = cq.importers.importStep(str(OUT / "HR30_first_energization_cell_with_robot_candidate.step")).val().BoundingBox()
    structure = cq.importers.importStep(str(OUT / "HR30_first_energization_cell_structure_candidate.step")).val().BoundingBox()
    need(whole.xmin <= -995 and whole.xmax >= 995, "whole cell exclusion-zone x extent missing")
    need(whole.ymin <= -910 and whole.ymax >= 910, "whole cell exclusion-zone y extent missing")
    need(whole.zmax >= 1400 and whole.zmin <= 0.1, "whole cell height/floor extent drift")
    need(structure.xlen >= 1970 and structure.ylen >= 1770 and structure.zlen >= 1390, "structure extent drift")
    binding = json.loads((OUT / "source-binding.json").read_text(encoding="utf-8"))
    need(binding["identifier"] == IDENTIFIER and binding["warning"] == WARNING, "source binding identity drift")
    need(binding["robot_source_sha256"] == sha(ROBOT), "robot source SHA binding drift")
    need(binding["robot_translation_z_mm"] == 92.5, "robot cell translation drift")
    need(binding["pelvis_reservation_cell_xyz_mm"] == {"x":[-40,40],"y":[6,58],"z":[496.5,516.5]}, "pelvis reservation transform drift")


def check_registers() -> None:
    frame = rows("frame-member-register.csv")
    need(len(frame) == 13 and len({r["member_id"] for r in frame}) == 13, "frame must contain 13 unique members")
    need({r["role"] for r in frame} >= {"BASE FRONT","BASE REAR","VERTICAL UPRIGHT","TOP FRONT","POSITION-ONLY TETHER CROSSBAR"}, "frame roles incomplete")
    need(all(r["candidate_profile"] == "80/20 40-4040-Lite 40 x 40 mm" for r in frame), "frame product-family drift")
    need(all(r["structural_release"] == "NO" for r in frame), "frame cannot be structurally released")

    guards = rows("guard-panel-register.csv")
    need(len(guards) == 6 and {r["panel_id"] for r in guards} == {"GP-LEFT","GP-RIGHT","GP-REAR","GP-FRONT-L","GP-FRONT-R","GP-ROOF"}, "guard-panel set drift")
    need(all(r["impact_containment_credit"] == "NONE" and r["door_interlock_credit"] == "NONE" for r in guards), "guard/interlock credit overclaim")
    need(all(float(r["width_x_mm"]) == 6 or float(r["depth_y_mm"]) == 6 or float(r["height_z_mm"]) == 6 for r in guards), "all guards must encode 6 mm panel thickness")

    restraint = rows("restraint-interface-register.csv")
    need(len(restraint) == 10, "restraint package must contain 8 support components and 2 tethers")
    need(sum(r["support_id"].startswith("SP-PAD") for r in restraint) == 2, "two pelvis pads required")
    need(sum(r["support_id"].startswith("TR-") for r in restraint) == 2, "two secondary tethers required")
    need(all(r["walking_credit"] == "NONE" for r in restraint), "restraint cannot claim walking credit")
    need(all(r["fall_arrest_credit"] == "NONE" for r in restraint if r["support_id"].startswith("TR-")), "tether fall-arrest overclaim")

    dimensions = rows("cell-dimension-register.csv")
    by_id = {r["dimension_id"]: r for r in dimensions}
    need(set(by_id) == {"CELL-OUTER","CELL-INNER","EXCLUSION","PLATFORM","ROBOT","PELVIS-RESERVATION"}, "dimension register drift")
    need((float(by_id["CELL-OUTER"]["x_mm"]), float(by_id["CELL-OUTER"]["y_mm"]), float(by_id["CELL-OUTER"]["z_mm"])) == (1200,1000,1400), "outer cell dimensions drift")
    need((float(by_id["EXCLUSION"]["x_mm"]), float(by_id["EXCLUSION"]["y_mm"])) == (2000,1800), "exclusion zone drift")

    stages = rows("stage-use-register.csv")
    need(len(stages) == 8 and {r["stage_id"] for r in stages} == {f"FER-E{i}" for i in range(8)}, "stage E0-E7 coverage drift")
    need(all(r["execution_state"] == "OPEN - NOT EXECUTED" and r["cell_authorizes_stage"] == "NO" for r in stages), "stage execution/authority overclaim")
    e7 = next(r for r in stages if r["stage_id"] == "FER-E7")
    need("RIGIDLY SUPPORTED" in e7["cell_use"] and "TORQUE DISABLED" in e7["motion_boundary"], "E7 static boundary missing")

    stations = rows("operator-and-instrument-location-register.csv")
    need(len(stations) == 3 and {r["station_id"] for r in stations} == {"ST-ESTOP","ST-INSTRUMENT","ST-FIRE"}, "external station set drift")
    need(all(r["installed"] == "NO" and r["calibrated_or_verified"] == "NO" for r in stations), "station evidence overclaim")
    instruments = rows("instrument-location-register.csv")
    need(len(instruments) == 6 and all(r["installed"] == "NO" and r["abort_limits_frozen"] == "NO" for r in instruments), "instrument register overclaim")

    bom = rows("candidate-bom.csv")
    need(len(bom) == 10 and all(r["procurement_released"] == "NO" for r in bom), "candidate BOM release drift")
    need(any(r["candidate_part_or_family"] == "40-4040-Lite" for r in bom), "40-4040-Lite candidate absent")
    need(any("LEXAN 9030 OR 9034" in r["candidate_part_or_family"] for r in bom), "polycarbonate family absent")
    need(any(r["candidate_part_or_family"] == "SELECTION REQUIRED" for r in bom), "unresolved selections falsely closed")

    sources = rows("primary-source-register.csv")
    need(len(sources) == 6 and all(r["url"].startswith("https://") for r in sources), "primary source register drift")
    need({r["manufacturer"] for r in sources} == {"80/20", "SABIC"}, "manufacturer source set drift")
    need(all("accessed 2026-08-18" in r["revision_date"] for r in sources), "source access date missing")

    traveler = rows("inspection-traveler.csv")
    need(len(traveler) == 15 and all(r["result"] == "NOT EXECUTED" and r["evidence"] == "REQUIRED" for r in traveler), "traveler evidence overclaim")
    holds = rows("open-holds.csv")
    need(len(holds) == 10 and all(r["state"] == "OPEN" for r in holds), "open holds must remain open")
    need(any("walking" in r["unresolved_item"].lower() for r in holds), "separate walking-gantry hold missing")


def check_status_and_guides() -> None:
    status = json.loads((OUT / "cell-status.json").read_text(encoding="utf-8"))
    need(status["identifier"] == IDENTIFIER and status["warning"] == WARNING, "cell status identity drift")
    need(status["whole_robot_cad_bound"] is True and status["complete_humanoid_visible"] is True, "complete robot not status-bound")
    need(status["frame_member_count"] == 13 and status["guard_panel_count"] == 6 and status["support_component_count"] == 8 and status["secondary_tether_count"] == 2, "status counts drift")
    need(status["static_first_energization_use_only"] is True and status["walking_gantry"] is False, "static/non-walking boundary drift")
    for key in ("structure_calculated","restraint_rated","guard_impact_validated","fabricated","site_commissioned","instrumentation_calibrated","fire_response_approved","fall_arrest_credit","walking_credit","functional_safety_credit","procurement_authority","fabrication_authority","assembly_authority","connection_authority","powered_test_authority","motion_authority","walking_authority","energization_authority"):
        need(status[key] is False, f"status must remain false: {key}")
    need(status["fer_g02_state"] == status["fer_g10_state"] == status["fer_g11_state"] == "OPEN - NOT EXECUTED", "FER gate status drift")

    html_text = (OUT / "index.html").read_text(encoding="utf-8")
    need("model-viewer" in html_text and "HR30_first_energization_cell_with_robot_candidate.glb" in html_text, "interactive whole-cell viewer missing")
    need("The complete robot now has a physical static test cell" in html_text, "guide outcome missing")
    need("not a walking gantry" in html_text.lower() and "FER-G02, G10 and G11 remain open" in html_text, "guide authority boundary missing")
    need("font:17px" in html_text and "font-size:14px" in html_text, "web legibility floors missing")
    need(not re.search(r"font-size:\s*(?:[0-9]|1[01])px", html_text), "user-facing text below 12 px")
    readme = (OUT / "README.md").read_text(encoding="utf-8")
    need(WARNING in readme and "complete neutral-pose HR-30" in readme, "package README identity/binding missing")

    whole_status = json.loads((WHOLE / "package-status.json").read_text(encoding="utf-8"))
    need(whole_status["first_energization_cell_present"] is True and whole_status["first_energization_cell_whole_robot_bound"] is True, "whole-body status integration missing")
    need(whole_status["first_energization_cell_walking_gantry"] is False and whole_status["fer_g02_closed"] is False and whole_status["fer_g10_closed"] is False and whole_status["fer_g11_closed"] is False, "whole-body fail-closed status drift")
    need("first-energization-cell-p0.1/index.html" in (WHOLE / "README.md").read_text(encoding="utf-8"), "whole-body README link missing")
    need('id="first-energization-cell"' in (WHOLE / "index.html").read_text(encoding="utf-8"), "whole-body web section missing")


def main() -> int:
    need(OUT.is_dir() and RELEASE.is_dir(), "source/release package missing")
    need((OUT / "first-energization-cell-source.py").read_bytes() == GEN.read_bytes(), "editable source snapshot drift")
    for name in ("HR30_first_energization_cell_structure_candidate.step","HR30_first_energization_cell_structure_candidate.glb","HR30_first_energization_cell_with_robot_candidate.step","HR30_first_energization_cell_with_robot_candidate.glb"):
        need((OUT / name).is_file() and (OUT / name).stat().st_size > 1000, f"missing/non-substantive CAD export: {name}")
    check_manifest(); check_geometry(); check_registers(); check_status_and_guides()
    print("PASS: whole HR-30 bound into dimensioned static first-energization cell; guards/support/stations/stages complete; all validation and authority gates fail closed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
