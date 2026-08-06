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
    coupon_stem = "MV0-FC01_robotis_pcd22_fit_coupon"
    coupon_files = {path.suffix.lower() for path in FIT_COUPONS.glob(f"{coupon_stem}.*")}
    if coupon_files != {".dxf", ".step", ".stl"}:
        errors.append(f"MV0-FC01 missing DXF/STEP/STL set: {sorted(coupon_files)}")
    with (FIT_COUPONS / "fit-coupons.csv").open(newline="", encoding="utf-8") as handle:
        coupon_rows = list(csv.DictReader(handle))
    if len(coupon_rows) != 1:
        errors.append(f"expected one fit-coupon record, found {len(coupon_rows)}")
    else:
        coupon = coupon_rows[0]
        expected_coupon = {
            "part_number": "MV0-FC01",
            "outer_diameter_mm": "38.0",
            "center_clearance_mm": "14.0",
            "hole_count": "8",
            "hole_diameter_mm": "2.7",
            "pcd_mm": "22.0",
            "thickness_mm": "2.0",
            "release_status": "FIT CHECK ONLY - PHYSICAL EVIDENCE REQUIRED",
        }
        for field, expected in expected_coupon.items():
            if coupon.get(field) != expected:
                errors.append(f"MV0-FC01 {field} expected {expected!r}, found {coupon.get(field)!r}")
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
    if len(record_rows) != 2 or {row.get("vendor_part") for row in record_rows} != {"FR13-H101K", "FR13-S102K"}:
        errors.append("fit-coupon inspection template must contain two unexecuted seed rows")
    for row in record_rows:
        if row.get(None) or row.get("record_id") != "NOT-EXECUTED" or row.get("disposition") != "NOT EXECUTED":
            errors.append(f"malformed or executed-looking fit-coupon template row: {row.get('vendor_part')}")
    overlay = FIT_COUPONS / f"{coupon_stem}_1to1_A4.svg"
    try:
        root = ET.parse(overlay).getroot()
    except (ET.ParseError, FileNotFoundError) as exc:
        errors.append(f"invalid or missing 1:1 fit-coupon SVG: {exc}")
    else:
        if root.get("width") != "210mm" or root.get("height") != "297mm" or root.get("viewBox") != "0 0 210 297":
            errors.append("fit-coupon overlay lost its controlled A4 physical dimensions")
        overlay_text = overlay.read_text(encoding="utf-8")
        for required in (
            "Print at ACTUAL SIZE / 100%",
            "X PRINT SCALE CHECK: 100.00 mm",
            "Y SCALE",
            "NOT RELEASED FOR FABRICATION OR ENERGIZATION",
            "FR13-H101K and FR13-S102K",
            "FIT CHECK ONLY - NOT A STRUCTURAL OR FABRICATION-RELEASED PART",
            "PHYSICAL FIT AND TOLERANCE REVIEW REQUIRED",
        ):
            if required not in overlay_text:
                errors.append(f"fit-coupon overlay missing controlled text: {required}")
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
    manifest = json.loads((GENERATED / "manifest.json").read_text(encoding="utf-8"))
    if "NOT RELEASED" not in manifest["warning"]:
        errors.append("generated manifest lost release warning")
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
    if not checks["not_credited_or_unresolved"]:
        errors.append("mechanical calculation omitted unresolved release inputs")
    if errors:
        print("HR-V0 CAD validation: FAIL")
        for error in errors:
            print(f"- {error}")
        return 1
    print(f"HR-V0 CAD validation: PASS ({len(rows)} custom parts, {len(coupon_rows)} fit coupon, {len(source_rows)} hashed generated artifacts, {len(vendor_rows)} vendor references)")
    print("Status remains PRELIMINARY—NOT RELEASED FOR FABRICATION OR ENERGIZATION")
    return 0


if __name__ == "__main__":
    sys.exit(main())
