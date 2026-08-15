"""Fail-closed checks for the HR-30 reduced-leg drivetrain P0.1 package."""

from __future__ import annotations

import csv
import hashlib
import json
import math
from pathlib import Path

import cadquery as cq


ROOT = Path(__file__).resolve().parents[1]
WHOLE = ROOT / "hr30" / "whole-body-p0.1"
SRC = WHOLE / "leg-drivetrain-p0.1"
REL = ROOT / "release" / "hr30" / "whole-body-p0.1" / "leg-drivetrain-p0.1"
GENERATOR = ROOT / "tools" / "generate_hr30_leg_drivetrain_p01.py"
WARNING = "PRELIMINARY - PRODUCT/GEOMETRY CANDIDATE ONLY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, POWERED TESTING, MOTION, OR ENERGIZATION"
PITCH_MM = 5.0

EXPECTED = {
    "LD-15": {
        "motor": 20, "output": 30, "belt": 45, "center": 49.358512477,
        "motor_code": "GPA20GT5090-A-H10", "output_code": "GPA30GT5090-A-H12",
        "belt_code": "GBN225EV5GT-090", "axes": {"L_HIP_PITCH", "R_HIP_PITCH"},
    },
    "LD-20": {
        "motor": 20, "output": 40, "belt": 51, "center": 49.965206523,
        "motor_code": "GPA20GT5090-A-H10", "output_code": "GPA40GT5090-A-H12",
        "belt_code": "GBN255EV5GT-090",
        "axes": {"L_HIP_ROLL", "R_HIP_ROLL", "L_KNEE_PITCH", "R_KNEE_PITCH", "L_ANKLE_ROLL", "R_ANKLE_ROLL"},
    },
    "LD-25": {
        "motor": 16, "output": 40, "belt": 50, "center": 51.455622919,
        "motor_code": "GPA16GT5090-A-H8", "output_code": "GPA40GT5090-A-H12",
        "belt_code": "GBN250EV5GT-090", "axes": {"L_ANKLE_PITCH", "R_ANKLE_PITCH"},
    },
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"FAIL: {message}")


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rows(path: Path) -> list[dict]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def pitch_diameter(teeth: int) -> float:
    return teeth * PITCH_MM / math.pi


def belt_length(center: float, motor: int, output: int) -> float:
    small = pitch_diameter(motor)
    large = pitch_diameter(output)
    return 2.0 * center + math.pi * (large + small) / 2.0 + (large - small) ** 2 / (4.0 * center)


def solve_center(motor: int, output: int, belt_teeth: int) -> float:
    target = belt_teeth * PITCH_MM
    low = abs(pitch_diameter(output) - pitch_diameter(motor)) / 2.0 + 0.01
    high = 150.0
    for _ in range(120):
        mid = (low + high) / 2.0
        if belt_length(mid, motor, output) < target:
            low = mid
        else:
            high = mid
    return (low + high) / 2.0


def check_step(path: Path, minimum_solids: int) -> None:
    imported = cq.importers.importStep(str(path)).val()
    require(imported.isValid(), f"invalid STEP {path.name}")
    require(len(imported.Solids()) >= minimum_solids, f"STEP lacks physical solids {path.name}")
    box = imported.BoundingBox()
    require(box.xlen > 20 and box.ylen > 5 and box.zlen > 40, f"implausible STEP envelope {path.name}")


def main() -> int:
    require(SRC.is_dir() and REL.is_dir(), "source/release drivetrain package missing")
    source_files = {p.relative_to(SRC).as_posix() for p in SRC.rglob("*") if p.is_file()}
    release_files = {p.relative_to(REL).as_posix() for p in REL.rglob("*") if p.is_file()}
    required = {
        "README.md", "index.html", "belt-center-geometry.csv", "axis-drivetrain-allocation.csv",
        "candidate-product-register.csv", "transmission-source-register.csv", "leg-drivetrain-status.json",
        "leg-drivetrain-source.py", "file-manifest.csv", "HR-30_leg_drivetrain_lineup_candidate.step",
        "HR-30_leg_drivetrain_lineup_candidate.glb",
    }
    for drive_id in EXPECTED:
        required |= {
            f"{drive_id}/{drive_id}_candidate.step", f"{drive_id}/{drive_id}_candidate.glb",
            f"{drive_id}/{drive_id}_layout.svg",
        }
    require(required <= source_files, "required drivetrain artifacts missing")
    require(source_files == release_files, "drivetrain source/release file-set mismatch")
    for name in source_files:
        require(sha(SRC / name) == sha(REL / name), f"drivetrain source/release byte mismatch {name}")

    manifest = rows(SRC / "file-manifest.csv")
    require({row["path"] for row in manifest} == source_files - {"file-manifest.csv"}, "drivetrain manifest file set mismatch")
    for row in manifest:
        path = SRC / row["path"]
        require(row["sha256"] == sha(path) and int(row["bytes"]) == path.stat().st_size, f"manifest mismatch {row['path']}")
        require(row["warning"] == WARNING, f"manifest warning mismatch {row['path']}")
    require((SRC / "leg-drivetrain-source.py").read_bytes() == GENERATOR.read_bytes(), "generator snapshot drift")

    geometry = rows(SRC / "belt-center-geometry.csv")
    require({row["drive_id"] for row in geometry} == set(EXPECTED), "drive-family geometry set mismatch")
    for row in geometry:
        expected = EXPECTED[row["drive_id"]]
        motor, output, belt = int(row["motor_teeth"]), int(row["output_teeth"]), int(row["belt_teeth"])
        require((motor, output, belt) == (expected["motor"], expected["output"], expected["belt"]), f"tooth-count drift {row['drive_id']}")
        center = float(row["solved_nominal_center_distance_mm"])
        independent = solve_center(motor, output, belt)
        require(abs(center - expected["center"]) < 2e-9 and abs(center - independent) < 2e-9, f"center solve drift {row['drive_id']}")
        require(abs(belt_length(center, motor, output) - belt * PITCH_MM) < 2e-8, f"belt-length closure drift {row['drive_id']}")
        require(float(row["length_closure_error_mm"]) < 1e-8, f"reported belt closure failure {row['drive_id']}")
        require("VENDOR TOOTH B-REP NOT CLAIMED" in row["cad_scope"], f"CAD scope overclaim {row['drive_id']}")
        require(row["warning"] == WARNING, f"geometry warning drift {row['drive_id']}")

    allocations = rows(SRC / "axis-drivetrain-allocation.csv")
    require(len(allocations) == 10 and len({row["axis_id"] for row in allocations}) == 10, "ten-axis allocation incomplete")
    require({row["axis_id"] for row in allocations} == set().union(*(item["axes"] for item in EXPECTED.values())), "leg axis set mismatch")
    for row in allocations:
        expected = EXPECTED[row["drive_id"]]
        require(row["axis_id"] in expected["axes"], f"axis assigned to wrong drive {row['axis_id']}")
        require((row["motor_pulley"], row["output_pulley"], row["belt"]) == (expected["motor_code"], expected["output_code"], expected["belt_code"]), f"candidate code drift {row['axis_id']}")
        require("CUSTOM ADAPTER" in row["horn_to_pulley_adapter"] and "VALIDATION OPEN" in row["release_state"], f"unresolved axis boundary lost {row['axis_id']}")

    products = rows(SRC / "candidate-product-register.csv")
    expected_products = {
        "GPA16GT5090-A-H8": 2, "GPA20GT5090-A-H10": 8, "GPA30GT5090-A-H12": 2,
        "GPA40GT5090-A-H12": 8, "GBN225EV5GT-090": 2, "GBN250EV5GT-090": 2,
        "GBN255EV5GT-090": 6,
    }
    require(len(products) == 7 and {row["candidate_order_code"]: int(row["whole_robot_quantity"]) for row in products} == expected_products, "product register/quantity mismatch")
    require(all(row["authority"] == "NO PROCUREMENT AUTHORITY" and "WRITTEN QUOTE" in row["selection_state"] for row in products), "product authority overclaim")

    sources = rows(SRC / "transmission-source-register.csv")
    require(len(sources) == 5 and all(row["accessed_date"] == "2026-08-14" for row in sources), "source register incomplete")
    urls = {row["url"] for row in sources}
    require("https://uk.misumi-ec.com/pdf/fa/p1_1117.pdf" in urls and "https://us.misumi-ec.com/pdf/fa/2019/2019_US_1432.pdf" in urls, "official MISUMI sources missing")
    require("https://www.robotis.us/hn13-n101-set/" in urls and "https://www.robotis.us/hn12-n101-set/" in urls, "official ROBOTIS horn sources missing")

    for drive_id in EXPECTED:
        check_step(SRC / drive_id / f"{drive_id}_candidate.step", 4)
        require((SRC / drive_id / f"{drive_id}_candidate.glb").stat().st_size > 1000, f"empty GLB {drive_id}")
    check_step(SRC / "HR-30_leg_drivetrain_lineup_candidate.step", 12)
    require((SRC / "HR-30_leg_drivetrain_lineup_candidate.glb").stat().st_size > 3000, "empty lineup GLB")

    status = json.loads((SRC / "leg-drivetrain-status.json").read_text(encoding="utf-8"))
    require((status["module_count"], status["axis_count"], status["candidate_product_count"]) == (3, 10, 7), "drivetrain status count drift")
    require(status["exact_candidate_product_allocation_present"] and not status["vendor_tooth_brep_present"], "drivetrain CAD truth boundary drift")
    false_keys = (
        "horn_adapter_complete", "capacity_validated", "tension_validated", "physical_validation_complete",
        "procurement_authority", "fabrication_authority", "assembly_authority", "powered_test_authority",
        "motion_authority", "energization_authority",
    )
    require(not any(status[key] for key in false_keys), "drivetrain status grants unsupported authority")

    whole_status = json.loads((WHOLE / "package-status.json").read_text(encoding="utf-8"))
    require(whole_status["reduced_leg_drivetrain_package_present"] and whole_status["reduced_leg_drivetrain_module_count"] == 3 and whole_status["reduced_leg_drivetrain_axis_count"] == 10, "whole-body status lacks drivetrain package")
    require(not whole_status["reduced_leg_drivetrain_capacity_validated"] and not whole_status["reduced_leg_drivetrain_horn_adapters_complete"], "whole-body drivetrain overclaim")
    hold = next((row for row in rows(WHOLE / "open-holds.csv") if row["hold_id"] == "HR30-P01-H03"), None)
    require(hold is not None and hold["state"] == "OPEN" and "three exact MISUMI" in hold["unresolved_item"] and "physical proof remain open" in hold["unresolved_item"], "leg hold not honestly advanced")

    page = (SRC / "index.html").read_text(encoding="utf-8")
    require("font:17px/1.55" in page and "font-size:16px" in page and "overflow-x:clip" in page, "drivetrain guide legibility/responsiveness drift")
    require(WARNING in page and "model-viewer" in page and all(drive_id in page for drive_id in EXPECTED), "drivetrain guide incomplete")
    require("Â" not in page and "â€”" not in page, "drivetrain guide contains mojibake")
    root_page = (WHOLE / "index.html").read_text(encoding="utf-8")
    root_readme = (WHOLE / "README.md").read_text(encoding="utf-8")
    require(root_page.count("<!-- HR30-LEG-DRIVETRAIN-P01-START -->") == 1 and "leg-drivetrain-p0.1/index.html" in root_page, "whole-body page drivetrain integration missing")
    require(root_readme.count("<!-- HR30-LEG-DRIVETRAIN-P01-README-START -->") == 1 and "49.359/49.965/51.456" in root_readme, "whole-body README drivetrain integration missing")

    print("PASS: 3 physical candidate drivetrains cover all 10 reduced leg axes; exact product codes and solved centers verified; capacity and all work authority remain open")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
