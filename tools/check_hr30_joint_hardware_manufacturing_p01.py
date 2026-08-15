"""Validate the HR-30 actual-axis joint-hardware manufacturing package."""

from __future__ import annotations

import csv
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path

import cadquery as cq

import generate_hr30_body_architecture_p01 as body


ROOT = Path(__file__).resolve().parents[1]
WB = ROOT / "hr30" / "whole-body-p0.1"
OUT = WB / "joint-hardware-manufacturing-p0.1"
REL = ROOT / "release" / "hr30" / "whole-body-p0.1" / OUT.name
WARNING = (
    "PRELIMINARY - JOINT-HARDWARE REFINEMENT FILES ONLY - NOT APPROVED FOR "
    "PROCUREMENT, FABRICATION, ASSEMBLY, POWERED TESTING, MOTION, OR ENERGIZATION"
)
EXPECTED_TYPES = {
    "OUTPUT_SHAFT": 25,
    "CATALOGUE_BEARING_ENVELOPE": 39,
    "INTERFACE_PLATE": 39,
    "OUTPUT_PULLEY_ENVELOPE": 14,
    "MOTOR_PULLEY_ENVELOPE": 14,
    "ACTUATOR_OUTPUT_COUPLER_PLACEHOLDER": 9,
    "SYMMETRIC_DRIVE_COUPLER_PLACEHOLDER": 2,
}


def fail(message: str) -> None:
    raise SystemExit(f"FAIL: {message}")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def classify(name: str) -> str:
    if name.endswith("_OUTPUT_SHAFT"):
        return "OUTPUT_SHAFT"
    if "_BEARING_" in name:
        return "CATALOGUE_BEARING_ENVELOPE"
    if "_INTERFACE_PLATE_" in name:
        return "INTERFACE_PLATE"
    if name.endswith("_OUTPUT_PULLEY"):
        return "OUTPUT_PULLEY_ENVELOPE"
    if name.endswith("_MOTOR_PULLEY"):
        return "MOTOR_PULLEY_ENVELOPE"
    if name.endswith("_ACTUATOR_OUTPUT_COUPLER"):
        return "ACTUATOR_OUTPUT_COUPLER_PLACEHOLDER"
    if name.endswith("_SYMMETRIC_DRIVE_COUPLER"):
        return "SYMMETRIC_DRIVE_COUPLER_PLACEHOLDER"
    fail(f"unclassified source component {name}")


def axis_for(name: str, axis_ids: list[str]) -> str:
    for axis_id in sorted(axis_ids, key=len, reverse=True):
        if name.startswith(f"JMOD_{axis_id}_"):
            return axis_id
    fail(f"component has no actual-axis binding: {name}")


def assert_manifest(package: Path) -> None:
    listed = rows(package / "file-manifest.csv")
    actual = sorted(
        path.relative_to(package).as_posix()
        for path in package.rglob("*")
        if path.is_file() and path.name != "file-manifest.csv"
    )
    if sorted(row["path"] for row in listed) != actual:
        fail(f"manifest file set mismatch in {package}")
    for row in listed:
        path = package / row["path"]
        if int(row["bytes"]) != path.stat().st_size or row["sha256"] != sha256(path):
            fail(f"manifest mismatch: {path}")
        if row["warning"] != WARNING:
            fail(f"warning mismatch: {path}")


def main() -> int:
    for package in (OUT, REL):
        if not package.is_dir():
            fail(f"missing package {package}")

    status = json.loads((OUT / "joint-hardware-manufacturing-status.json").read_text(encoding="utf-8"))
    expected_counts = {
        "axis_count": 25,
        "family_count": 10,
        "axis_hardware_count": 142,
        "local_refinement_step_count": 64,
        "local_refinement_svg_count": 64,
        "interface_plate_dxf_count": 39,
        "catalogue_bearing_reference_count": 39,
        "redesign_required_count": 39,
    }
    for key, expected in expected_counts.items():
        if status.get(key) != expected:
            fail(f"status {key}: expected {expected}, found {status.get(key)}")
    if status.get("part_type_counts") != EXPECTED_TYPES:
        fail("status part-type counts drifted")
    for key, value in status.items():
        if key.endswith("authority") or key in {
            "complete_joint_hardware_manufacturing_definition",
            "materials_selected", "fits_tolerances_released", "dfm_complete",
            "fai_complete", "structural_capacity_validated",
        }:
            if value is not False:
                fail(f"unsafe status truth: {key}={value!r}")
    if status.get("warning") != WARNING:
        fail("status warning drifted")

    components, axes, _bindings, _transforms = body.build()
    axis_ids = [axis["axis_id"] for axis in axes]
    source = {
        component.name: (component, axis_for(component.name, axis_ids), classify(component.name))
        for component in components
        if component.physical and component.name.startswith("JMOD_")
        and not component.name.endswith("_ACTUATOR_VENDOR_CANDIDATE")
    }
    if len(source) != 142 or len(axis_ids) != 25:
        fail(f"source universe drifted: {len(source)} hardware / {len(axis_ids)} axes")

    register = rows(OUT / "joint-hardware-part-register.csv")
    if len(register) != 142 or len({row["part_id"] for row in register}) != 142:
        fail("part register is not 142 unique rows")
    if set(source) != {row["part_id"] for row in register}:
        fail("part register does not equal the actual source universe")
    counts = Counter(row["part_type"] for row in register)
    if dict(counts) != EXPECTED_TYPES:
        fail(f"register part-type counts drifted: {dict(counts)}")
    if {row["axis_id"] for row in register} != set(axis_ids):
        fail("not all 25 axes appear in the register")
    if len({row["family_id"] for row in register}) != 10:
        fail("not all ten joint families appear in the register")

    step_count = svg_count = dxf_count = 0
    for row in register:
        component, source_axis, source_type = source[row["part_id"]]
        if row["axis_id"] != source_axis or row["part_type"] != source_type:
            fail(f"source binding drift: {row['part_id']}")
        should_export = source_type in {"OUTPUT_SHAFT", "INTERFACE_PLATE"}
        paths = {kind: row[f"{kind}_path"] for kind in ("step", "svg", "dxf")}
        if should_export != bool(paths["step"]) or should_export != bool(paths["svg"]):
            fail(f"invalid STEP/SVG disposition: {row['part_id']}")
        if (source_type == "INTERFACE_PLATE") != bool(paths["dxf"]):
            fail(f"invalid DXF disposition: {row['part_id']}")
        if not should_export:
            if any(paths.values()) or any(row[f"{kind}_sha256"] for kind in paths):
                fail(f"withheld part has supplier file: {row['part_id']}")
            continue

        for kind, relpath in paths.items():
            if not relpath:
                continue
            path = OUT / relpath
            if not path.is_file() or row[f"{kind}_sha256"] != sha256(path):
                fail(f"missing or unhashed {kind}: {row['part_id']}")
            if kind == "step":
                step_count += 1
            elif kind == "svg":
                svg_count += 1
            else:
                dxf_count += 1

        imported = cq.importers.importStep(str(OUT / paths["step"])).val()
        source_shape = component.shape
        source_volume = float(source_shape.Volume())
        if abs(float(imported.Volume()) - source_volume) > max(1e-3, source_volume * 1e-7):
            fail(f"STEP volume drift: {row['part_id']}")
        center = imported.Center()
        if max(abs(center.x), abs(center.y), abs(center.z)) > 1e-4:
            fail(f"STEP is not local-coordinate centered: {row['part_id']}")
        bb = imported.BoundingBox()
        expected_bbox = " x ".join(f"{value:.3f}" for value in (bb.xlen, bb.ylen, bb.zlen))
        if row["bbox_local_mm"] != expected_bbox:
            fail(f"STEP/register bounding-box drift: {row['part_id']}")

    if (step_count, svg_count, dxf_count) != (64, 64, 39):
        fail(f"file counts drifted: {(step_count, svg_count, dxf_count)}")

    source_binding = json.loads((OUT / "source-binding.json").read_text(encoding="utf-8"))
    for field in ("body_architecture_generator", "mass_reconciliation_generator", "joint_family_generator"):
        bound = ROOT / source_binding[field]
        if source_binding[f"{field}_sha256"] != sha256(bound):
            fail(f"source binding drift: {field}")

    assert_manifest(OUT)
    assert_manifest(REL)
    source_files = sorted(path.relative_to(OUT).as_posix() for path in OUT.rglob("*") if path.is_file())
    release_files = sorted(path.relative_to(REL).as_posix() for path in REL.rglob("*") if path.is_file())
    if source_files != release_files:
        fail("source/release file-set mismatch")
    for relpath in source_files:
        if sha256(OUT / relpath) != sha256(REL / relpath):
            fail(f"source/release hash mismatch: {relpath}")

    page = (OUT / "index.html").read_text(encoding="utf-8")
    for token in (
        "142 / 142", "shaft and carrier refinement STEP/SVG files",
        "catalogue bearing references", "pulley and coupler definitions blocked for redesign",
    ):
        if token not in page:
            fail(f"interactive page missing {token!r}")
    for token in ("font-size:18px", "font-size:16px", "font-size:14px", "overflow:auto"):
        if token not in page.replace(" ", ""):
            fail(f"interactive page legibility token missing: {token}")
    if WARNING not in page:
        fail("interactive page warning missing")

    parent = (WB / "index.html").read_text(encoding="utf-8")
    root_page = (ROOT / "index.html").read_text(encoding="utf-8")
    if "The 98 body parts were not the complete manufacturing universe" not in parent:
        fail("parent page has not corrected the 98-part boundary")
    if "joint-hardware-manufacturing-p0.1/index.html" not in parent or "joint-hardware-manufacturing-p0.1/index.html" not in root_page:
        fail("navigation to the joint-hardware guide is missing")
    parent_status = json.loads((WB / "package-status.json").read_text(encoding="utf-8"))
    if parent_status.get("actual_axis_joint_hardware_package_present") is not True:
        fail("parent package does not record the new package")
    for key in ("joint_hardware_complete_manufacturing_definition", "fabrication_authority", "energization_authority"):
        if parent_status.get(key) is not False:
            fail(f"unsafe parent status: {key}")

    print("PASS: 142 actual-axis items classified; 64 STEP/SVG and 39 DXF files reimported/hash-bound; 39 catalogue and 39 redesign items withheld; no authority")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
