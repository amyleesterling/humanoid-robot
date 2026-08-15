"""Validate the HR-30 P0.1 serviceable joint-family CAD package."""

from __future__ import annotations

import csv
import hashlib
import json
import re
import struct
from collections import Counter
from pathlib import Path

import cadquery as cq


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "hr30" / "whole-body-p0.1"
REL = ROOT / "release" / "hr30" / "whole-body-p0.1"
CAD = SRC / "joint-family-cad"
REL_CAD = REL / "joint-family-cad"
WARNING = (
    "PRELIMINARY - CONFIGURATION AND PACKAGING CAD ONLY - NOT APPROVED FOR "
    "PROCUREMENT, FABRICATION, ASSEMBLY, POWERED TESTING, MOTION, OR ENERGIZATION"
)
FAMILIES = {
    "JMF-01-COMPACT", "JMF-02-GRIPPER", "JMF-03-SHOULDER-GIMBAL", "JMF-04-MEDIUM",
    "JMF-05-WAIST", "JMF-06-LEG-DIRECT", "JMF-07-LEG-REDUCED-15",
    "JMF-08-LEG-REDUCED-20", "JMF-09-KNEE-REDUCED-20", "JMF-10-ANKLE-PITCH-REDUCED-25",
}
REDUCED = {
    "JMF-07-LEG-REDUCED-15", "JMF-08-LEG-REDUCED-20",
    "JMF-09-KNEE-REDUCED-20", "JMF-10-ANKLE-PITCH-REDUCED-25",
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"FAIL: {message}")


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_csv(path: Path) -> list[dict]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def import_step(path: Path) -> cq.Shape:
    shape = cq.importers.importStep(str(path)).val()
    require(not shape.isNull() and shape.isValid() and shape.Volume() > 1e-6, f"invalid STEP {path}")
    return shape


def check_glb(path: Path) -> None:
    require(100_000 < path.stat().st_size < 100_000_000, f"GLB size invalid {path}")
    with path.open("rb") as handle:
        magic, version, declared_length = struct.unpack("<4sII", handle.read(12))
    require(magic == b"glTF" and version == 2 and declared_length == path.stat().st_size, f"GLB header/length invalid {path}")


def main() -> int:
    required = {
        "README.md", "index.html", "joint-family-stack-register.csv", "joint-family-part-register.csv",
        "fit-retention-register.csv", "assembly-sequence.csv", "joint-family-cad-source.py",
        "joint-family-cad-status.json", "HR-30_joint_family_lineup_candidate.step",
        "HR-30_joint_family_lineup_candidate.glb",
    }
    require(all((CAD / name).is_file() for name in required), "joint-family CAD root files incomplete")
    require(all((REL_CAD / name).is_file() for name in required), "release joint-family CAD root files incomplete")
    require(sha(CAD / "joint-family-cad-source.py") == sha(ROOT / "tools" / "generate_hr30_joint_family_cad_p01.py"), "joint-family generator snapshot drift")

    stacks = read_csv(CAD / "joint-family-stack-register.csv")
    require(len(stacks) == 10 and {row["family_id"] for row in stacks} == FAMILIES, "ten-family stack register drift")
    require(sum(int(row["whole_body_axis_count"]) for row in stacks) == 25, "25-axis family coverage drift")
    require(all(int(row["part_count"]) >= 12 for row in stacks), "a family lacks a serviceable physical stack")
    require(all(float(row["shaft_od_mm"]) > float(row["shaft_bore_mm"]) >= 2.0 for row in stacks), "shaft wall geometry invalid")
    require(all(float(row["support_span_mm"]) >= 28.0 for row in stacks), "support span invalid")
    require(all(row["warning"] == WARNING and "SERVICEABLE GEOMETRIC CANDIDATE" in row["release_state"] for row in stacks), "stack warning/release drift")

    parts = read_csv(CAD / "joint-family-part-register.csv")
    require(len(parts) == sum(int(row["part_count"]) for row in stacks) == 175, "joint-family visible part count drift")
    part_count = Counter(row["family_id"] for row in parts)
    require(all(part_count[row["family_id"]] == int(row["part_count"]) for row in stacks), "family part counts do not reconcile")
    require(all(int(row["solid_count"]) >= 1 and float(row["volume_mm3"]) > 1e-6 for row in parts), "empty/invalid joint part register row")
    require(all(row["warning"] == WARNING and row["authority"].startswith("NO PROCUREMENT") for row in parts), "part warning/authority drift")
    names = {(row["family_id"], row["part_name"]) for row in parts}
    for family in FAMILIES:
        for required_name in ("OUTPUT_SHAFT", "OUTPUT_ENCODER_CARRIER", "OUTPUT_MAGNET_HUB", "ACTUATOR"):
            require((family, required_name) in names, f"{family} missing {required_name}")
        require(any(fid == family and "BEARING_" in name for fid, name in names), f"{family} missing bearing geometry")
        require(any(fid == family and "CARRIER_" in name and "SCREW" not in name for fid, name in names), f"{family} missing carrier geometry")
        require(any(fid == family and "SCREW" in name for fid, name in names), f"{family} missing located screws")
    for family in REDUCED:
        for required_name in ("OUTPUT_PULLEY", "MOTOR_PULLEY", "TIMING_BELT", "TRANSMISSION_GUARD"):
            require((family, required_name) in names, f"{family} missing {required_name}")
    for required_name in ("PINION", "RACK_UPPER", "RACK_LOWER"):
        require(("JMF-02-GRIPPER", required_name) in names, f"gripper family missing {required_name}")
    for required_name in ("ROLL_ACTUATOR", "ROLL_SHAFT", "GIMBAL_RING"):
        require(("JMF-03-SHOULDER-GIMBAL", required_name) in names, f"shoulder family missing {required_name}")

    fits = read_csv(CAD / "fit-retention-register.csv")
    require(len(fits) == 60 and Counter(row["family_id"] for row in fits) == Counter({family: 6 for family in FAMILIES}), "fit/retention register drift")
    require(all("SELECTION REQUIRED" in row["unresolved_selection_or_evidence"] and row["warning"] == WARNING for row in fits), "fit rows overclaim selection")
    sequences = read_csv(CAD / "assembly-sequence.csv")
    require(len(sequences) == 80 and Counter(row["family_id"] for row in sequences) == Counter({family: 8 for family in FAMILIES}), "assembly sequence drift")
    require(all("NO ASSEMBLY OR POWERED-WORK AUTHORITY" in row["authority"] and row["warning"] == WARNING for row in sequences), "assembly sequence authority drift")

    imported = 0
    for row in stacks:
        family = row["family_id"]
        step = CAD / row["step_path"]
        glb = CAD / row["glb_path"]
        require(step == CAD / family / f"{family}_assembly.step" and glb == CAD / family / f"{family}_assembly.glb", f"{family} export path drift")
        require(step.is_file() and glb.is_file(), f"{family} exports missing")
        require(step.stat().st_size == int(row["step_bytes"]) and sha(step) == row["step_sha256"], f"{family} STEP provenance drift")
        require(glb.stat().st_size == int(row["glb_bytes"]) and sha(glb) == row["glb_sha256"], f"{family} GLB provenance drift")
        shape = import_step(step)
        imported += 1
        box = shape.BoundingBox()
        require(abs(box.xlen - float(row["bbox_x_mm"])) <= 0.01, f"{family} X bbox drift")
        require(abs(box.ylen - float(row["bbox_y_mm"])) <= 0.01, f"{family} Y bbox drift")
        require(abs(box.zlen - float(row["bbox_z_mm"])) <= 0.01, f"{family} Z bbox drift")
        require(len(shape.Faces()) >= 80, f"{family} appears to have lost detailed actuator/joint geometry")
        check_glb(glb)

    lineup = import_step(CAD / "HR-30_joint_family_lineup_candidate.step")
    imported += 1
    lineup_box = lineup.BoundingBox()
    require(lineup_box.xlen > 650.0 and lineup_box.zlen > 250.0, "ten-family lineup separation envelope missing")
    check_glb(CAD / "HR-30_joint_family_lineup_candidate.glb")
    require(all(path.stat().st_size < 100_000_000 for path in CAD.rglob("*") if path.is_file()), "joint-family artifact exceeds GitHub hard limit")

    source_files = {p.relative_to(CAD).as_posix(): p for p in CAD.rglob("*") if p.is_file()}
    release_files = {p.relative_to(REL_CAD).as_posix(): p for p in REL_CAD.rglob("*") if p.is_file()}
    require(source_files.keys() == release_files.keys(), "joint-family source/release file-set drift")
    require(all(sha(path) == sha(release_files[name]) for name, path in source_files.items()), "joint-family source/release hash drift")
    manifest = {row["path"]: row for row in read_csv(SRC / "file-manifest.csv")}
    for name, path in source_files.items():
        key = f"joint-family-cad/{name}"
        require(key in manifest and int(manifest[key]["bytes"]) == path.stat().st_size and manifest[key]["sha256"] == sha(path), f"package manifest drift for {key}")

    status = json.loads((CAD / "joint-family-cad-status.json").read_text(encoding="utf-8"))
    require(status["joint_family_count"] == 10 and status["whole_body_axis_coverage_count"] == 25 and status["visible_candidate_part_count"] == 175, "joint-family status counts drift")
    require(status["fit_retention_record_count"] == 60 and status["assembly_sequence_record_count"] == 80, "joint-family register status drift")
    require(status["lineup_step_present"] and status["lineup_glb_present"] and status["exact_vendor_actuator_geometry_present"] and status["editable_project_source_present"], "joint-family artifact flags incomplete")
    false_keys = (
        "fits_selected", "materials_selected", "exact_transmission_products_selected", "structural_capacity_validated",
        "physical_validation_complete", "manufacturing_released", "procurement_authority", "fabrication_authority",
        "assembly_authority", "powered_test_authority", "motion_authority", "energization_authority",
    )
    require(not any(status[key] for key in false_keys), "joint-family package overclaims validation or authority")
    require(status["warning"] == WARNING, "joint-family status warning drift")

    package_status = json.loads((SRC / "package-status.json").read_text(encoding="utf-8"))
    require(package_status["joint_family_cad_package_present"] and package_status["joint_family_cad_export_count"] == 10 and package_status["joint_family_cad_axis_coverage_count"] == 25, "whole-body package joint-family binding missing")
    require(package_status["joint_family_serviceable_stack_geometry_present"], "serviceable stack package flag missing")
    require(not package_status["joint_family_manufacturing_released"] and not package_status["joint_family_structural_capacity_validated"], "whole-body package overclaims joint release")

    page = (CAD / "index.html").read_text(encoding="utf-8")
    require(page.count('class="family"') == 10 and "font:17px/1.55" in page and not re.search(r"font-size:\s*(?:[0-9]|1[01])px", page), "joint-family guide count/legibility drift")
    require(all(f"{family}/{family}_assembly.step" in page and f"{family}/{family}_assembly.glb" in page for family in FAMILIES), "joint-family guide links incomplete")
    require(WARNING in page and "not released manufacturing" in page.lower(), "joint-family guide warning boundary missing")
    package_page = (SRC / "index.html").read_text(encoding="utf-8")
    require(package_page.count('id="joint-family-cad"') == 1 and "joint-family-cad/index.html" in package_page and "HR-30_joint_family_lineup_candidate.glb" in package_page, "whole-body guide joint-family section missing")
    readme = (SRC / "README.md").read_text(encoding="utf-8")
    require("## Serviceable joint-family CAD" in readme and "all 25 axes" in readme, "whole-body README joint-family section missing")
    holds = {row["hold_id"]: row for row in read_csv(SRC / "open-holds.csv")}
    h01 = holds["HR30-P01-H01"]["unresolved_item"].lower()
    require(
        "all 39 base-architecture pulley/coupler placeholders" in h01
        and "named successor artifacts" in h01
        and "156 carrier screws" in h01
        and "physical proof" in h01,
        "H01 current whole-body transmission/joint-fastener disposition missing",
    )

    print(f"PASS: reimported {imported} native STEP assemblies; ten serviceable HR-30 joint families expose 175 physical candidate parts and cover all 25 axes; fits/capacity/physical validation and all work authority remain false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
