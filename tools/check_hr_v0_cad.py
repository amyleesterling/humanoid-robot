"""Validate the checked-in HR-V0 CAD release structure and vendor references."""

from __future__ import annotations

import csv
import hashlib
import json
import math
import sys
import xml.etree.ElementTree as ET
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CAD = ROOT / "cad" / "hr-v0"
GENERATED = CAD / "generated"
VENDOR = ROOT / "cad" / "vendor" / "robotis"
FIT_COUPONS = GENERATED / "fit-coupons"
HARD_STOPS = GENERATED / "hard-stops"
SAFETY_ENCLOSURE = GENERATED / "safety-enclosure"
FIT_RECORD_TEMPLATE = ROOT / "tests" / "forms" / "hr-v0-fit-coupon-inspection-template.csv"
FRAME_KIT_CONTENTS = ROOT / "bom" / "hr-v0-frame-kit-contents.csv"
FRAME_KIT_RECORD_TEMPLATE = ROOT / "tests" / "forms" / "hr-v0-frame-kit-receiving-template.csv"
HARD_STOP_RECORD_TEMPLATE = ROOT / "tests" / "forms" / "hr-v0-hard-stop-validation-template.csv"
MOVING_MASS_LEDGER = ROOT / "bom" / "hr-v0-moving-mass-ledger.csv"
MOVING_MASS_RECORD_TEMPLATE = ROOT / "tests" / "forms" / "hr-v0-moving-mass-measurement-template.csv"
GRIPPER_KIT_CONTENTS = ROOT / "bom" / "hr-v0-gripper-kit-contents.csv"
GRIPPER_KIT_RECORD_TEMPLATE = ROOT / "tests" / "forms" / "hr-v0-gripper-kit-receiving-template.csv"
GRIPPER_INTERFACE_RECORD_TEMPLATE = ROOT / "tests" / "forms" / "hr-v0-gripper-interface-inspection-template.csv"
GUARD_RECORD_TEMPLATE = ROOT / "tests" / "forms" / "hr-v0-guard-clearance-inspection-template.csv"
CABLE_RECORD_TEMPLATE = ROOT / "tests" / "forms" / "hr-v0-cable-route-inspection-template.csv"
DROP_RECORD_TEMPLATE = ROOT / "tests" / "forms" / "hr-v0-drop-containment-template.csv"


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
        "MV0-FC03": "MV0-FC03_h104_24x12_mount_pattern_coupon",
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
        "MV0-FC03": {
            "part_number": "MV0-FC03",
            "outer_diameter_mm": "",
            "outer_x_mm": "36.0",
            "outer_z_mm": "24.0",
            "center_clearance_mm": "",
            "hole_count": "4",
            "hole_diameter_mm": "2.7",
            "pcd_mm": "",
            "pattern_x_mm": "24.0",
            "pattern_z_mm": "12.0",
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
    with GRIPPER_INTERFACE_RECORD_TEMPLATE.open(newline="", encoding="utf-8") as handle:
        gripper_interface_reader = csv.DictReader(handle)
        gripper_interface_rows = list(gripper_interface_reader)
    expected_gripper_interface_fields = (
        "record_id", "date", "inspector", "repo_commit", "cad_revision", "coupon_file",
        "coupon_sha256", "vendor_part", "parent_order_code", "received_label", "serial_or_lot",
        "manufacturer_drawing_sha256", "manufacturer_step_sha256", "coupon_method", "coupon_material",
        "measuring_instrument", "calibration_reference", "measured_thickness_mm", "scale_x_mm", "scale_y_mm",
        "hole_index", "candidate_fastener_or_gauge", "seats_flat", "enters_without_force",
        "fastener_and_nut_access", "measured_x_offset_mm", "measured_y_offset_mm", "photo_reference", "notes",
        "disposition",
    )
    if tuple(gripper_interface_reader.fieldnames or ()) != expected_gripper_interface_fields:
        errors.append("gripper-interface inspection template fields changed")
    expected_gripper_interface_keys = {
        ("MV0-FC03_h104_24x12_mount_pattern_coupon.dxf", "FR12-H104K", str(index))
        for index in range(1, 5)
    }
    actual_gripper_interface_keys = {
        (row.get("coupon_file"), row.get("vendor_part"), row.get("hole_index"))
        for row in gripper_interface_rows
    }
    if actual_gripper_interface_keys != expected_gripper_interface_keys:
        errors.append("gripper-interface template lost its four controlled per-hole rows")
    for row in gripper_interface_rows:
        if row.get(None) or row.get("record_id") != "NOT-EXECUTED" or row.get("disposition") != "NOT EXECUTED":
            errors.append(f"malformed or executed-looking gripper-interface row: {row.get('hole_index')}")
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
    with GRIPPER_KIT_CONTENTS.open(newline="", encoding="utf-8") as handle:
        gripper_kit_rows = list(csv.DictReader(handle))
    expected_gripper_kit_ids = {f"GKC-{index:03d}" for index in range(1, 21)}
    if {row.get("content_id") for row in gripper_kit_rows} != expected_gripper_kit_ids:
        errors.append("gripper-kit schedule does not contain controlled GKC-001 through GKC-020")
    for row in gripper_kit_rows:
        expected_status = "proposed" if row.get("content_id") == "GKC-001" else "received_verification_required"
        if row.get("status") != expected_status:
            errors.append(f"gripper-kit row has wrong status: {row.get('content_id')}")
        if row.get("parent_orderable") != "OpenMANIPULATOR-X Frame Set RM-X52" or row.get("order_code") != "905-0023-000":
            errors.append(f"gripper-kit row lost parent identity: {row.get('content_id')}")
    with GRIPPER_KIT_RECORD_TEMPLATE.open(newline="", encoding="utf-8") as handle:
        gripper_kit_record_rows = list(csv.DictReader(handle))
    if {row.get("content_id") for row in gripper_kit_record_rows} != expected_gripper_kit_ids:
        errors.append("gripper-kit receiving template does not contain one seed row per controlled content item")
    for row in gripper_kit_record_rows:
        if row.get(None) or row.get("record_id") != "NOT-EXECUTED" or row.get("disposition") != "NOT EXECUTED":
            errors.append(f"malformed or executed-looking gripper-kit receiving row: {row.get('content_id')}")
    overlay_requirements = {
        "MV0-FC01": ("FR13-H101K and FR13-S102K", "PHYSICAL FIT AND TOLERANCE REVIEW REQUIRED"),
        "MV0-FC02": ("32.00 x 16.00", "PHYSICAL FIT AND THREAD INSPECTION REQUIRED"),
        "MV0-FC03": ("24.00 x 12.00", "PHYSICAL FIT AND FASTENER ACCESS INSPECTION REQUIRED"),
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
        if svg.name == "MV0-002_forearm_link.svg":
            for required in ("GRIPPER/H104", "12 LONGITUDINAL x 24 TRANSVERSE", "MV0-FC03 PHYSICAL FIT PASSES"):
                if required not in text:
                    errors.append(f"forearm-link drawing missing controlled gripper text: {required}")
        if svg.name == "MV0-003_adapter_s102.svg" and "ON 32 x 16 RECTANGLE" not in text:
            errors.append("shoulder-adapter drawing does not preserve the selected S102 interface")
    hard_stop_csv = HARD_STOPS / "hard-stop-datums.csv"
    with hard_stop_csv.open(newline="", encoding="utf-8") as handle:
        hard_stop_rows = list(csv.DictReader(handle))
    expected_stop_values = {
        "HS-J1-MIN": ("J1", "-20.0", "-25.0", "-25.0", "45.315", "-21.131"),
        "HS-J1-MAX": ("J1", "70.0", "75.0", "75.0", "12.941", "48.296"),
        "HS-J2-MIN": ("J2", "15.0", "10.0", "170.0", "-49.24", "8.682"),
        "HS-J2-MAX": ("J2", "125.0", "130.0", "50.0", "32.139", "38.302"),
    }
    hard_stop_by_id = {row.get("stop_id"): row for row in hard_stop_rows}
    if set(hard_stop_by_id) != set(expected_stop_values):
        errors.append("hard-stop datum table lost the four controlled candidate boundaries")
    for stop_id, expected in expected_stop_values.items():
        row = hard_stop_by_id.get(stop_id, {})
        actual = tuple(row.get(field) for field in (
            "joint", "software_joint_value_deg", "mechanical_datum_joint_value_deg",
            "layout_ray_deg", "contact_x_mm", "contact_z_mm",
        ))
        if actual != expected:
            errors.append(f"{stop_id} datum expected {expected}, found {actual}")
        if row.get("moving_contact_radius_mm") != "50.0" or row.get("required_nominal_margin_deg") != "5.0":
            errors.append(f"{stop_id} lost the 50 mm radius or 5 degree nominal margin")
        if "DESIGN REQUIRED" not in row.get("status", ""):
            errors.append(f"{stop_id} falsely appears released")
    hard_stop_svg = HARD_STOPS / "HR-V0_hard-stop-kinematic-layout.svg"
    try:
        ET.parse(hard_stop_svg)
    except (ET.ParseError, FileNotFoundError) as exc:
        errors.append(f"invalid or missing hard-stop layout SVG: {exc}")
    else:
        hard_stop_text = hard_stop_svg.read_text(encoding="utf-8")
        for required in (
            "font: 16px", "NO BRACKET OR BUMPER IS RELEASED", "J1 convention",
            "J2 convention", "5 deg beyond provisional software limits", "IMPACT TEST REMAIN DESIGN REQUIRED",
        ):
            if required not in hard_stop_text:
                errors.append(f"hard-stop layout missing controlled text: {required}")
    with HARD_STOP_RECORD_TEMPLATE.open(newline="", encoding="utf-8") as handle:
        hard_stop_record_rows = list(csv.DictReader(handle))
    expected_record_keys = {
        (joint, stop_id, stage)
        for joint, stop_id in (
            ("J1", "HS-J1-MIN"), ("J1", "HS-J1-MAX"),
            ("J2", "HS-J2-MIN"), ("J2", "HS-J2-MAX"),
        )
        for stage in ("UNPOWERED_GEOMETRY", "GUARDED_INCREMENTAL_IMPACT")
    }
    actual_record_keys = {
        (row.get("joint"), row.get("stop_id"), row.get("test_stage"))
        for row in hard_stop_record_rows
    }
    if actual_record_keys != expected_record_keys:
        errors.append("hard-stop validation template lost its eight controlled seed rows")
    for row in hard_stop_record_rows:
        if row.get(None) or row.get("record_id") != "NOT-EXECUTED" or row.get("disposition") != "NOT EXECUTED":
            errors.append(f"malformed or executed-looking hard-stop template row: {row.get('stop_id')}")
    with (SAFETY_ENCLOSURE / "guard-receiver-assumptions.csv").open(newline="", encoding="utf-8") as handle:
        guard_rows = list(csv.DictReader(handle))
    guard_by_parameter = {row.get("parameter"): row for row in guard_rows}
    expected_guard_values = {
        "shoulder_axis_height": "500.0",
        "maximum_object_center_reach": "360.0",
        "maximum_object_half_extent": "35.0",
        "stopping_travel_space_reservation": "25.0",
        "guard_clearance_space_reservation": "25.0",
        "envelope_tolerance_space_reservation": "5.0",
        "guard_radial_envelope": "450.0",
        "guard_internal_width": "900.0",
        "guard_internal_depth": "400.0",
        "guard_internal_height": "950.0",
        "candidate_panel_thickness": "6.0",
        "catch_tray_plan": "820 x 320",
        "catch_tray_wall_height": "50.0",
        "catch_tray_bottom_thickness": "3.0",
    }
    if set(guard_by_parameter) != set(expected_guard_values):
        errors.append("guard/receiver assumptions lost the controlled 14-parameter set")
    for parameter, expected_value in expected_guard_values.items():
        row = guard_by_parameter.get(parameter, {})
        if row.get("value") != expected_value:
            errors.append(f"guard parameter {parameter} expected {expected_value}, found {row.get('value')}")
        if parameter in {
            "stopping_travel_space_reservation", "guard_clearance_space_reservation",
            "envelope_tolerance_space_reservation", "guard_internal_depth",
            "candidate_panel_thickness", "catch_tray_wall_height", "catch_tray_bottom_thickness",
        } and "SELECTION REQUIRED" not in row.get("status", ""):
            errors.append(f"guard parameter {parameter} falsely appears released")
    with (SAFETY_ENCLOSURE / "cable-route-datums.csv").open(newline="", encoding="utf-8") as handle:
        cable_route_rows = list(csv.DictReader(handle))
    expected_cable_zone_ids = {f"CR-{index:03d}" for index in range(1, 6)}
    if {row.get("zone_id") for row in cable_route_rows} != expected_cable_zone_ids:
        errors.append("cable-route datum set lost CR-001 through CR-005")
    for row in cable_route_rows:
        if row.get("status") not in {"DESIGN REQUIRED", "PRELIMINARY SPACE CLAIM"}:
            errors.append(f"cable-route zone falsely appears released: {row.get('zone_id')}")
    guard_step = SAFETY_ENCLOSURE / "HR-V0_guard_receiver_envelope_NOT_RELEASED.step"
    if not guard_step.exists() or guard_step.stat().st_size < 100_000:
        errors.append("guard/receiver envelope STEP is missing or implausibly small")
    for svg_name, required_text in {
        "HR-V0_guard_receiver_layout.svg": (
            "font: 16px", "25 mm stopping travel is NOT measured", "No door interlock is selected or credited",
            "NOT A FABRICATION DRAWING OR PERMISSION TO ENERGIZE",
        ),
        "HR-V0_cable_route_datums.svg": (
            "font: 16px", "NO CABLE, CLAMP, LOOP OR BEND RADIUS IS RELEASED",
            "VERIFY ALL COMBINED JOINT POSES", "NOT A HARNESS DRAWING OR PERMISSION TO ENERGIZE",
        ),
    }.items():
        path = SAFETY_ENCLOSURE / svg_name
        try:
            ET.parse(path)
        except (ET.ParseError, FileNotFoundError) as exc:
            errors.append(f"invalid or missing safety-enclosure SVG {svg_name}: {exc}")
            continue
        svg_text = path.read_text(encoding="utf-8")
        for required in required_text:
            if required not in svg_text:
                errors.append(f"{svg_name} missing controlled text: {required}")
    with GUARD_RECORD_TEMPLATE.open(newline="", encoding="utf-8") as handle:
        guard_record_rows = list(csv.DictReader(handle))
    expected_guard_case_ids = {f"GC-{index:03d}" for index in range(1, 11)}
    if {row.get("case_id") for row in guard_record_rows} != expected_guard_case_ids:
        errors.append("guard-clearance template lost GC-001 through GC-010")
    for row in guard_record_rows:
        if row.get(None) or row.get("record_id") != "NOT-EXECUTED" or row.get("disposition") != "NOT EXECUTED":
            errors.append(f"malformed or executed-looking guard-clearance row: {row.get('case_id')}")
    with CABLE_RECORD_TEMPLATE.open(newline="", encoding="utf-8") as handle:
        cable_record_rows = list(csv.DictReader(handle))
    expected_cable_record_keys = {
        (zone_id, pose_id)
        for zone_id in expected_cable_zone_ids
        for pose_id in ("FULL_RANGE_ARTICULATION", "WORST_CASE_IDENTIFIED")
    }
    if {(row.get("zone_id"), row.get("pose_id")) for row in cable_record_rows} != expected_cable_record_keys:
        errors.append("cable-route template lost its ten controlled zone/pose seed rows")
    for row in cable_record_rows:
        if row.get(None) or row.get("record_id") != "NOT-EXECUTED" or row.get("disposition") != "NOT EXECUTED":
            errors.append(f"malformed or executed-looking cable-route row: {row.get('zone_id')}")
    with DROP_RECORD_TEMPLATE.open(newline="", encoding="utf-8") as handle:
        drop_record_rows = list(csv.DictReader(handle))
    expected_drop_case_ids = {f"DR-{index:03d}" for index in range(1, 7)}
    if {row.get("case_id") for row in drop_record_rows} != expected_drop_case_ids:
        errors.append("drop-containment template lost DR-001 through DR-006")
    for row in drop_record_rows:
        if row.get(None) or row.get("record_id") != "NOT-EXECUTED" or row.get("disposition") != "NOT EXECUTED":
            errors.append(f"malformed or executed-looking drop-containment row: {row.get('case_id')}")
    with MOVING_MASS_LEDGER.open(newline="", encoding="utf-8") as handle:
        moving_mass_rows = list(csv.DictReader(handle))
    expected_mass_ids = {f"V0M-{index:03d}" for index in range(1, 14)}
    if {row.get("mass_id") for row in moving_mass_rows} != expected_mass_ids:
        errors.append("moving-mass ledger does not contain controlled V0M-001 through V0M-013 rows")
    known_mass_total = sum(float(row["known_subtotal_g"]) for row in moving_mass_rows if row.get("known_subtotal_g"))
    if not math.isclose(known_mass_total, 565.4, abs_tol=1e-9):
        errors.append(f"moving-mass known subtotal expected 565.4 g, found {known_mass_total}")
    expected_bucket_allocations = {
        "upper_link_hardware": 120.0,
        "elbow_actuator_and_bracket": 200.0,
        "forearm_hardware": 120.0,
        "gripper_assembly": 210.0,
        "payload": 100.0,
    }
    actual_bucket_allocations: dict[str, float] = {}
    for row in moving_mass_rows:
        bucket = row.get("allocation_bucket", "")
        allocation = float(row["bucket_allocation_g"])
        if bucket in actual_bucket_allocations and actual_bucket_allocations[bucket] != allocation:
            errors.append(f"moving-mass bucket {bucket} has inconsistent allocations")
        actual_bucket_allocations[bucket] = allocation
        if row.get("mass_basis") in {"MEASURE RECEIVED", "DESIGN AND MEASURE"} and row.get("known_subtotal_g"):
            errors.append(f"unresolved moving-mass row falsely contains known mass: {row.get('mass_id')}")
    if actual_bucket_allocations != expected_bucket_allocations:
        errors.append(f"moving-mass bucket allocations changed: {actual_bucket_allocations}")
    with MOVING_MASS_RECORD_TEMPLATE.open(newline="", encoding="utf-8") as handle:
        moving_mass_record_rows = list(csv.DictReader(handle))
    if {row.get("mass_id") for row in moving_mass_record_rows} != expected_mass_ids:
        errors.append("moving-mass measurement template lost its 13 controlled seed rows")
    for row in moving_mass_record_rows:
        if row.get(None) or row.get("record_id") != "NOT-EXECUTED" or row.get("disposition") != "NOT EXECUTED":
            errors.append(f"malformed or executed-looking moving-mass template row: {row.get('mass_id')}")
    manifest = json.loads((GENERATED / "manifest.json").read_text(encoding="utf-8"))
    if "NOT RELEASED" not in manifest["warning"]:
        errors.append("generated manifest lost release warning")
    if manifest["controlled_parameters"].get("s102_selected_tapped_rectangle_mm") != [32.0, 16.0]:
        errors.append("generated manifest lost the selected S102 32 x 16 tapped pattern")
    if manifest["controlled_parameters"].get("gripper_h104_selected_rectangle_mm") != [24.0, 12.0]:
        errors.append("generated manifest lost the selected FR12-H104K 24 x 12 pattern")
    if manifest["controlled_parameters"].get("gripper_fit_coupon_mm") != [36.0, 24.0, 2.0]:
        errors.append("generated manifest lost the MV0-FC03 coupon dimensions")
    expected_guard_space = {
        "radial_envelope": 450.0,
        "internal_width": 900.0,
        "internal_depth": 400.0,
        "internal_height": 950.0,
        "candidate_panel_thickness": 6.0,
    }
    if manifest["controlled_parameters"].get("guard_space_reservation_mm") != expected_guard_space:
        errors.append("generated manifest lost the controlled guard space reservation")
    if manifest["controlled_parameters"].get("guard_provisional_allowances_mm") != {
        "stopping_travel": 25.0, "guard_clearance": 25.0, "envelope_tolerance": 5.0,
    }:
        errors.append("generated manifest lost the explicitly provisional guard allowances")
    if manifest["controlled_parameters"].get("catch_tray_space_reservation_mm") != [820.0, 320.0, 50.0, 3.0]:
        errors.append("generated manifest lost the catch-tray space reservation")
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
    hard_stop_screen = checks["screens"].get("hard_stop", {})
    if not math.isclose(hard_stop_screen.get("allocated_shoulder_inertia_kg_m2_excludes_reflected_rotor", 0), 0.047264, rel_tol=1e-9):
        errors.append("hard-stop screen lost the allocated J1 inertia calculation")
    if not math.isclose(hard_stop_screen.get("allocated_elbow_inertia_kg_m2_excludes_reflected_rotor", 0), 0.010144, rel_tol=1e-9):
        errors.append("hard-stop screen lost the allocated J2 inertia calculation")
    if hard_stop_screen.get("screen_result") != "KINEMATIC AND ALLOCATED-MASS SCREEN ONLY - STOP DESIGN NOT RELEASED":
        errors.append("hard-stop calculation no longer preserves its unreleased status")
    moving_mass_screen = checks["screens"].get("moving_mass", {})
    if not math.isclose(moving_mass_screen.get("known_subtotal_g", 0), 565.4, abs_tol=1e-9):
        errors.append("mechanical calculation lost the 565.4 g known moving-mass subtotal")
    if not math.isclose(moving_mass_screen.get("unresolved_headroom_g", 0), 184.6, abs_tol=1e-9):
        errors.append("mechanical calculation lost the 184.6 g unresolved moving-mass headroom")
    if moving_mass_screen.get("screen_result") != "565.4 g KNOWN SUBTOTAL; 184.6 g UNRESOLVED HEADROOM - MASS CLOSURE OPEN":
        errors.append("moving-mass calculation no longer preserves its open status")
    guard_screen = checks["screens"].get("guard_receiver", {})
    expected_guard_screen = {
        "maximum_object_center_reach_mm": 360.0,
        "maximum_object_half_extent_mm": 35.0,
        "stopping_travel_space_reservation_mm_not_measured": 25.0,
        "guard_clearance_space_reservation_mm_not_selected": 25.0,
        "envelope_tolerance_space_reservation_mm_not_closed": 5.0,
        "derived_radial_envelope_mm": 450.0,
        "preliminary_internal_width_mm": 900.0,
        "preliminary_internal_depth_mm": 400.0,
        "preliminary_internal_height_mm": 950.0,
        "screen_result": "SPACE RESERVATION ONLY - STOPPING CLEARANCE PANEL RECEIVER AND HARNESS RELEASE OPEN",
    }
    if guard_screen != expected_guard_screen:
        errors.append("mechanical calculation lost the controlled preliminary guard/receiver screen")
    if checks["inputs"].get("selected_interfaces", {}).get("distal_gripper") != "FR12-H104K selected four-hole subset on 24 x 12 mm rectangle; physical fit required":
        errors.append("mechanical calculation lost the selected but unreleased gripper interface")
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
