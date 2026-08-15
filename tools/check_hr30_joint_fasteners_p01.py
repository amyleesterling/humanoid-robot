"""Fail-closed validation for located HR-30 whole-body joint fasteners."""

from __future__ import annotations

import csv
import hashlib
import json
import re
import struct
from collections import Counter, defaultdict
from pathlib import Path

import cadquery as cq

import generate_hr30_body_architecture_p01 as body
import generate_hr30_joint_fasteners_p01 as fasteners


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "hr30" / "whole-body-p0.1"
REL = ROOT / "release" / "hr30" / "whole-body-p0.1"
FAST = SRC / "fasteners"
REL_FAST = REL / "fasteners"
WARNING = body.WARNING


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"FAIL: {message}")


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rows(path: Path) -> list[dict]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def main() -> int:
    required = {
        "README.md", "index.html", "joint-fastener-source.py", "joint-fastener-status.json",
        "joint-fastener-register.csv", "joint-fastener-family-summary.csv",
        "HR-30_joint_fastener_candidates.step", "HR-30_fastened_whole_body_candidate.glb",
    }
    source_files = {p.relative_to(FAST).as_posix(): p for p in FAST.rglob("*") if p.is_file()}
    release_files = {p.relative_to(REL_FAST).as_posix(): p for p in REL_FAST.rglob("*") if p.is_file()}
    require(required <= source_files.keys(), "fastener package file set incomplete")
    require(source_files.keys() == release_files.keys(), "fastener source/release file-set drift")
    require(all(sha(path) == sha(release_files[name]) for name, path in source_files.items()), "fastener source/release hash drift")
    require(sha(FAST / "joint-fastener-source.py") == sha(ROOT / "tools" / "generate_hr30_joint_fasteners_p01.py"), "fastener generator snapshot drift")

    register = rows(FAST / "joint-fastener-register.csv")
    require(len(register) == len({row["fastener_id"] for row in register}) == 156, "fastener identity/count drift")
    require(len({row["axis_id"] for row in register}) == 25, "fastener axis coverage drift")
    require(Counter(row["candidate_size"] for row in register) == Counter({"M3": 24, "M4": 40, "M5": 92}), "fastener size population drift")
    by_plate = defaultdict(list)
    for row in register:
        by_plate[(row["axis_id"], row["carrier_end"])].append(row)
        require(float(row["diametral_clearance_mm"]) > 0.0, f"nonpositive clearance {row['fastener_id']}")
        require(float(row["provisional_thread_engagement_mm"]) >= 2.0 * float(row["nominal_diameter_mm"]), f"low provisional engagement {row['fastener_id']}")
        require("SELECTION REQUIRED" in row["retention_boundary"] and row["warning"] == WARNING, f"selection/warning boundary drift {row['fastener_id']}")
    require(len(by_plate) == 39 and all(len(items) == 4 and {int(r["hole_index"]) for r in items} == {1, 2, 3, 4} for items in by_plate.values()), "carrier-hole occupation drift")

    components, axes, _bindings, _transforms = body.build()
    expected = fasteners.build(axes)
    expected_by_id = {item.fastener_id: item for item in expected}
    require(set(expected_by_id) == {row["fastener_id"] for row in register}, "generated/register fastener identity drift")
    plate_shapes = {component.name: component.shape for component in components if "_INTERFACE_PLATE_" in component.name}
    require(len(plate_shapes) == 39, "body carrier plate population drift")
    maximum_plate_intersection_mm3 = 0.0
    for row in register:
        item = expected_by_id[row["fastener_id"]]
        for key in (
            "axis_id", "module_id", "dynamic_link", "joint_module_family", "carrier_end",
            "candidate_size", "hole_center_xyz_mm", "outward_access_direction",
        ):
            require(row[key] == item.row[key], f"generated/register field drift {row['fastener_id']} {key}")
        require(abs(float(row["planning_mass_kg"]) - float(item.row["planning_mass_kg"])) < 1e-12, f"fastener mass drift {row['fastener_id']}")
        plate_name = f"JMOD_{row['axis_id']}_INTERFACE_PLATE_{row['carrier_end']}"
        require(plate_name in plate_shapes, f"missing carrier plate {plate_name}")
        intersection = float(item.shape.intersect(plate_shapes[plate_name]).Volume())
        maximum_plate_intersection_mm3 = max(maximum_plate_intersection_mm3, intersection)
        require(intersection <= 1e-4, f"fastener collides with its actual carrier plate {row['fastener_id']}: {intersection}")

    step = cq.importers.importStep(str(FAST / "HR-30_joint_fastener_candidates.step")).val()
    require(not step.isNull() and step.isValid() and len(step.Solids()) == 156, "fastener STEP reimport/solid count drift")
    require(abs(float(step.Volume()) - sum(float(item.shape.Volume()) for item in expected)) <= 0.1, "fastener STEP volume drift")

    glb = FAST / "HR-30_fastened_whole_body_candidate.glb"
    magic, version, declared = struct.unpack("<4sII", glb.open("rb").read(12))
    require(magic == b"glTF" and version == 2 and declared == glb.stat().st_size and 100_000 < declared < 100_000_000, "fastened whole-body GLB invalid or too large")

    total_mass = sum(float(row["planning_mass_kg"]) for row in register)
    status = json.loads((FAST / "joint-fastener-status.json").read_text(encoding="utf-8"))
    require(status["axis_count"] == 25 and status["carrier_plate_count"] == 39 and status["fastener_count"] == 156, "fastener status population drift")
    require(abs(status["planning_mass_kg"] - total_mass) < 1e-9 and status["all_carrier_holes_occupied"], "fastener status mass/coverage drift")
    require(not any(status[key] for key in ("fasteners_selected", "torque_preload_locking_validated", "procurement_authority", "fabrication_authority", "assembly_authority", "powered_test_authority", "motion_authority", "energization_authority")), "fastener status release/authority overclaim")

    mass_items = rows(SRC / "mass-item-reconciliation.csv")
    mass_fasteners = [row for row in mass_items if row["category"] == "LOCATED JOINT FASTENER CAD DENSITY SCREEN"]
    require(len(mass_fasteners) == 156 and {row["item_id"] for row in mass_fasteners} == set(expected_by_id), "mass register fastener population drift")
    require(abs(sum(float(row["planning_candidate_mass_kg"]) for row in mass_fasteners) - total_mass) < 2e-9, "mass register fastener subtotal drift")
    mass_summary = json.loads((SRC / "mass-reconciliation-summary.json").read_text(encoding="utf-8"))
    require(mass_summary["located_joint_fastener_count"] == 156 and abs(mass_summary["located_joint_fastener_planning_mass_kg"] - total_mass) < 2e-9, "mass summary fastener drift")
    require(mass_summary["remaining_integration_contingency_kg"] < mass_summary["integration_contingency_before_fastener_allocation_kg"], "fastener mass was not charged against contingency")

    package_status = json.loads((SRC / "package-status.json").read_text(encoding="utf-8"))
    require(package_status["joint_fastener_candidate_geometry_present"] and package_status["joint_fastener_candidate_count"] == 156 and package_status["joint_fastener_carrier_plate_count"] == 39, "main package fastener status missing")
    require(not package_status["joint_fastener_selected"] and not package_status["joint_fastener_preload_validated"], "main package fastener selection/validation overclaim")

    manifest = {row["path"]: row for row in rows(SRC / "file-manifest.csv")}
    for name, path in source_files.items():
        key = f"fasteners/{name}"
        require(key in manifest and int(manifest[key]["bytes"]) == path.stat().st_size and manifest[key]["sha256"] == sha(path), f"package manifest drift {key}")

    page = (FAST / "index.html").read_text(encoding="utf-8")
    require("font:17px/1.55" in page and not re.search(r"font-size:\s*(?:[0-9]|1[01])px", page), "fastener guide legibility drift")
    require(WARNING in page and "156" in page and "M3 / M4 / M5" in page and "No procurement" in page, "fastener guide content/boundary drift")
    main_page = (SRC / "index.html").read_text(encoding="utf-8")
    require(main_page.count('id="joint-fasteners"') == 1 and "fasteners/index.html" in main_page and "HR-30_fastened_whole_body_candidate.glb" in main_page, "main package fastener section missing")

    print(f"PASS: 156 explicit joint fasteners occupy all holes in 39 actual carrier plates across 25 axes; STEP reimport has 156 solids, maximum plate intersection is {maximum_plate_intersection_mm3:.3g} mm^3, and {total_mass:.3f} kg is charged against the planning reserve; selection, preload, strength and all work authority remain false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
