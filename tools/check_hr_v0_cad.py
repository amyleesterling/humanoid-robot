"""Validate the checked-in HR-V0 CAD release structure and vendor references."""

from __future__ import annotations

import csv
import hashlib
import json
import sys
import xml.etree.ElementTree as ET
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CAD = ROOT / "cad" / "hr-v0"
GENERATED = CAD / "generated"
VENDOR = ROOT / "cad" / "vendor" / "robotis"
FIT_COUPONS = GENERATED / "fit-coupons"
FIT_RECORD_TEMPLATE = ROOT / "tests" / "forms" / "hr-v0-fit-coupon-inspection-template.csv"
FRAME_KIT_CONTENTS = ROOT / "bom" / "hr-v0-frame-kit-contents.csv"
FRAME_KIT_RECORD_TEMPLATE = ROOT / "tests" / "forms" / "hr-v0-frame-kit-receiving-template.csv"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def main() -> int:
    errors: list[str] = []
    required_parts = ["MV0-001", "MV0-002", "MV0-003", "MV0-004"]
    with (GENERATED / "custom-parts.csv").open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    if [row["part_number"] for row in rows] != required_parts:
        errors.append("custom-parts.csv does not contain the controlled four-part sequence")
    for row in rows:
        matches = list((GENERATED / "parts").glob(f'{row["part_number"]}_*'))
        suffixes = {path.suffix.lower() for path in matches}
        if suffixes != {".dxf", ".step", ".stl"}:
            errors.append(f'{row["part_number"]} missing DXF/STEP/STL set: {sorted(suffixes)}')
        if "QUOTE GEOMETRY ONLY" not in row["release_status"]:
            errors.append(f'{row["part_number"]} lost the preliminary release status')
    coupon_stems = {
        "MV0-FC01": "MV0-FC01_robotis_pcd22_fit_coupon",
        "MV0-FC02": "MV0-FC02_s102_32x16_tapped_pattern_coupon",
    }
    for coupon_id, coupon_stem in coupon_stems.items():
        coupon_files = {path.suffix.lower() for path in FIT_COUPONS.glob(f"{coupon_stem}.*")}
        if coupon_files != {".dxf", ".step", ".stl"}:
            errors.append(f"{coupon_id} missing DXF/STEP/STL set: {sorted(coupon_files)}")
    with (FIT_COUPONS / "fit-coupons.csv").open(newline="", encoding="utf-8") as handle:
        coupon_rows = list(csv.DictReader(handle))
    coupon_by_id = {row.get("part_number"): row for row in coupon_rows}
    expected_coupons = {
        "MV0-FC01": {
            "part_number": "MV0-FC01",
            "outer_diameter_mm": "38.0",
            "outer_x_mm": "",
            "outer_z_mm": "",
            "center_clearance_mm": "14.0",
            "hole_count": "8",
            "hole_diameter_mm": "2.7",
            "pcd_mm": "22.0",
            "pattern_x_mm": "",
            "pattern_z_mm": "",
            "thickness_mm": "2.0",
            "release_status": "FIT CHECK ONLY - PHYSICAL EVIDENCE REQUIRED",
        },
        "MV0-FC02": {
            "part_number": "MV0-FC02",
            "outer_diameter_mm": "",
            "outer_x_mm": "44.0",
            "outer_z_mm": "30.0",
            "center_clearance_mm": "",
            "hole_count": "4",
            "hole_diameter_mm": "2.7",
            "pcd_mm": "",
            "pattern_x_mm": "32.0",
            "pattern_z_mm": "16.0",
            "thickness_mm": "2.0",
            "release_status": "FIT CHECK ONLY - PHYSICAL EVIDENCE REQUIRED",
        },
    }
    if set(coupon_by_id) != set(expected_coupons):
        errors.append(f"fit-coupon records expected {sorted(expected_coupons)}, found {sorted(coupon_by_id)}")
    for coupon_id, expected_coupon in expected_coupons.items():
        coupon = coupon_by_id.get(coupon_id, {})
        for field, expected in expected_coupon.items():
            if coupon.get(field) != expected:
                errors.append(f"{coupon_id} {field} expected {expected!r}, found {coupon.get(field)!r}")
    with FIT_RECORD_TEMPLATE.open(newline="", encoding="utf-8") as handle:
        record_reader = csv.DictReader(handle)
        record_rows = list(record_reader)
    expected_record_fields = (
        "record_id", "date", "inspector", "repo_commit", "cad_revision", "coupon_file",
        "coupon_sha256", "vendor_part", "received_label", "serial_or_lot",
        "manufacturer_drawing_sha256", "coupon_method", "coupon_material",
        "measuring_instrument", "calibration_reference", "measured_thickness_mm",
        "scale_x_mm", "scale_y_mm", "hole_index", "candidate_fastener_or_gauge",
        "seats_flat", "enters_without_force", "measured_x_offset_mm",
        "measured_y_offset_mm", "photo_reference", "notes", "disposition",
    )
    if tuple(record_reader.fieldnames or ()) != expected_record_fields:
        errors.append("fit-coupon inspection template fields changed")
    expected_record_keys = {
        ("MV0-FC01_robotis_pcd22_fit_coupon.dxf", "FR13-H101K", str(index))
        for index in range(1, 9)
    } | {
        ("MV0-FC01_robotis_pcd22_fit_coupon.dxf", "FR13-S102K", str(index))
        for index in range(1, 9)
    } | {
        ("MV0-FC02_s102_32x16_tapped_pattern_coupon.dxf", "FR13-S102K", str(index))
        for index in range(1, 5)
    }
    actual_record_keys = {
        (row.get("coupon_file"), row.get("vendor_part"), row.get("hole_index"))
        for row in record_rows
    }
    if actual_record_keys != expected_record_keys:
        errors.append("fit-coupon inspection template does not contain the controlled 20 per-hole seed rows")
    for row in record_rows:
        if row.get(None) or row.get("record_id") != "NOT-EXECUTED" or row.get("disposition") != "NOT EXECUTED":
            errors.append(f"malformed or executed-looking fit-coupon template row: {row.get('vendor_part')}")
    with FRAME_KIT_CONTENTS.open(newline="", encoding="utf-8") as handle:
        kit_rows = list(csv.DictReader(handle))
    expected_kit_ids = {f"FKC-{index:03d}" for index in range(1, 12)}
    if {row.get("kit_content_id") for row in kit_rows} != expected_kit_ids:
        errors.append("frame-kit content schedule does not contain controlled FKC-001 through FKC-011")
    aggregate_expected: dict[str, int] = {}
    for row in kit_rows:
        aggregate_expected[row["included_item"]] = aggregate_expected.get(row["included_item"], 0) + int(row["total_expected_quantity"])
        if row.get("status") != "received_verification_required":
            errors.append(f"frame-kit row lost received-verification status: {row.get('kit_content_id')}")
    expected_fastener_totals = {
        "FWB M2.5x17": 16,
        "WB M2.5x5": 32,
        "WB M2.5x4": 56,
        "Spacer Ring": 40,
    }
    for item, expected in expected_fastener_totals.items():
        if aggregate_expected.get(item) != expected:
            errors.append(f"frame-kit {item} total expected {expected}, found {aggregate_expected.get(item)}")
    with FRAME_KIT_RECORD_TEMPLATE.open(newline="", encoding="utf-8") as handle:
        kit_record_reader = csv.DictReader(handle)
        kit_record_rows = list(kit_record_reader)
    if {row.get("kit_content_id") for row in kit_record_rows} != expected_kit_ids:
        errors.append("frame-kit receiving template does not contain one seed row per kit-content item")
    for row in kit_record_rows:
        if row.get(None) or row.get("record_id") != "NOT-EXECUTED" or row.get("disposition") != "NOT EXECUTED":
            errors.append(f"malformed or executed-looking frame-kit receiving row: {row.get('kit_content_id')}")
    overlay_requirements = {
        "MV0-FC01": ("FR13-H101K and FR13-S102K", "PHYSICAL FIT AND TOLERANCE REVIEW REQUIRED"),
        "MV0-FC02": ("32.00 x 16.00", "PHYSICAL FIT AND THREAD INSPECTION REQUIRED"),
    }
    for coupon_id, coupon_stem in coupon_stems.items():
        overlay = FIT_COUPONS / f"{coupon_stem}_1to1_A4.svg"
        try:
            root = ET.parse(overlay).getroot()
        except (ET.ParseError, FileNotFoundError) as exc:
            errors.append(f"invalid or missing {coupon_id} 1:1 fit-coupon SVG: {exc}")
            continue
        if root.get("width") != "210mm" or root.get("height") != "297mm" or root.get("viewBox") != "0 0 210 297":
            errors.append(f"{coupon_id} fit-coupon overlay lost its controlled A4 physical dimensions")
        overlay_text = overlay.read_text(encoding="utf-8")
        for required in (
            "Print at ACTUAL SIZE / 100%",
            "X PRINT SCALE CHECK: 100.00 mm",
            "Y SCALE",
            "NOT RELEASED FOR FABRICATION OR ENERGIZATION",
            "FIT CHECK ONLY - NOT A STRUCTURAL OR FABRICATION-RELEASED PART",
            *overlay_requirements[coupon_id],
        ):
            if required not in overlay_text:
                errors.append(f"{coupon_id} overlay missing controlled text: {required}")
    expected_drawings = {
        "MV0-001_upper_link.svg",
        "MV0-002_forearm_link.svg",
        "MV0-003_adapter_s102.svg",
        "MV0-004_anchor.svg",
    }
    actual_drawings = {path.name for path in (GENERATED / "drawings").glob("*.svg")}
    if actual_drawings != expected_drawings:
        errors.append(f"drawing set expected {sorted(expected_drawings)}, found {sorted(actual_drawings)}")
    for svg in (GENERATED / "drawings").glob("*.svg"):
        try:
            ET.parse(svg)
        except ET.ParseError as exc:
            errors.append(f"invalid SVG {svg.name}: {exc}")
        text = svg.read_text(encoding="utf-8")
        if "PRELIMINARY—NOT RELEASED FOR FABRICATION" not in text:
            errors.append(f"{svg.name} lacks fabrication warning")
        if "font: 16px" not in text:
            errors.append(f"{svg.name} lacks 16 px drawing text baseline")
        if svg.name in {"MV0-001_upper_link.svg", "MV0-002_forearm_link.svg"} and 'height="420"' not in text:
            errors.append(f"{svg.name} lacks the checked 420 px warning-clearance canvas")
        if svg.name == "MV0-001_upper_link.svg":
            for required in ("J1/H101", "J2/S102", "32 x 16 RECTANGLE"):
                if required not in text:
                    errors.append(f"upper-link drawing missing interface text: {required}")
        if svg.name == "MV0-002_forearm_link.svg" and "DISTAL GRIPPER HOLES: DESIGN REQUIRED" not in text:
            errors.append("forearm-link drawing does not preserve the open gripper interface")
        if svg.name == "MV0-003_adapter_s102.svg" and "ON 32 x 16 RECTANGLE" not in text:
            errors.append("shoulder-adapter drawing does not preserve the selected S102 interface")
    manifest = json.loads((GENERATED / "manifest.json").read_text(encoding="utf-8"))
    if "NOT RELEASED" not in manifest["warning"]:
        errors.append("generated manifest lost release warning")
    if manifest["controlled_parameters"].get("s102_selected_tapped_rectangle_mm") != [32.0, 16.0]:
        errors.append("generated manifest lost the selected S102 32 x 16 tapped pattern")
    for name in ("HR-V0_preliminary_assembly.step", "HR-V0_preliminary_assembly.glb"):
        path = GENERATED / name
        if not path.exists() or path.stat().st_size < 10_000:
            errors.append(f"missing or implausibly small assembly export: {name}")
    source_manifest_path = GENERATED / "SOURCE-MANIFEST.csv"
    with source_manifest_path.open(newline="", encoding="utf-8") as handle:
        source_rows = list(csv.DictReader(handle))
    source_by_file = {row["file"]: row for row in source_rows}
    generated_files = {
        path.relative_to(GENERATED).as_posix()
        for path in GENERATED.rglob("*")
        if path.is_file() and path != source_manifest_path
    }
    if set(source_by_file) != generated_files:
        missing = sorted(generated_files - set(source_by_file))
        stale = sorted(set(source_by_file) - generated_files)
        errors.append(f"generated source manifest mismatch; missing={missing}, stale={stale}")
    for relative, row in source_by_file.items():
        path = GENERATED / relative
        if path.exists() and sha256(path) != row["sha256"].upper():
            errors.append(f"generated hash mismatch {relative}")
        if row.get("revision") != manifest["revision"]:
            errors.append(f"generated manifest revision mismatch {relative}")
        if "NOT RELEASED" not in row.get("status", ""):
            errors.append(f"generated manifest status missing warning {relative}")
    with (VENDOR / "vendor-manifest.csv").open(newline="", encoding="utf-8") as handle:
        vendor_rows = list(csv.DictReader(handle))
    for row in vendor_rows:
        path = VENDOR / row["file"]
        if not path.exists():
            errors.append(f'missing vendor reference {row["file"]}')
        elif sha256(path) != row["sha256"].upper():
            errors.append(f'vendor hash mismatch {row["file"]}')
    checks = json.loads((GENERATED / "mechanical-checks.json").read_text(encoding="utf-8"))
    if checks["calculation_result"] != "GEOMETRY SCREEN PASSES; RELEASE REMAINS OPEN":
        errors.append("mechanical calculation status is not the controlled preliminary result")
    if checks["screens"].get("h101_output_fastener_geometric_max_underhead_mm") != 9.25:
        errors.append("mechanical calculation lost the H101 output-stack geometric limit")
    if checks["inputs"].get("selected_interfaces", {}).get("distal_gripper") != "DESIGN REQUIRED":
        errors.append("mechanical calculation failed to preserve the open gripper interface")
    if not checks["not_credited_or_unresolved"]:
        errors.append("mechanical calculation omitted unresolved release inputs")
    if errors:
        print("HR-V0 CAD validation: FAIL")
        for error in errors:
            print(f"- {error}")
        return 1
    print(f"HR-V0 CAD validation: PASS ({len(rows)} custom parts, {len(coupon_rows)} fit coupons, {len(source_rows)} hashed generated artifacts, {len(vendor_rows)} vendor references)")
    print("Status remains PRELIMINARY—NOT RELEASED FOR FABRICATION OR ENERGIZATION")
    return 0


if __name__ == "__main__":
    sys.exit(main())
