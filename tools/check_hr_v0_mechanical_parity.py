#!/usr/bin/env python3
"""Fail-closed validation for HR-V0-MECH-PARITY-P0.1."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "release" / "hr-v0" / "mechanical-parity-p0.1"
WARNING = "PRELIMINARY - NOT APPROVED FOR QUOTATION, FABRICATION, ASSEMBLY, MOTION, OR ENERGIZATION"


def rows(name: str) -> list[dict[str, str]]:
    with (OUT / name).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def main() -> int:
    errors: list[str] = []
    profiles = rows("profile-parity.csv")
    features = rows("feature-parity.csv")
    coverage = rows("drawing-control-coverage.csv")
    findings = rows("finding-register.csv")
    status = json.loads((OUT / "package-status.json").read_text(encoding="utf-8"))
    guide = (OUT / "index.html").read_text(encoding="utf-8")
    doc = (ROOT / "docs" / "hr-v0-mechanical-parity-p0.1.md").read_text(encoding="utf-8")

    expected_parts = ["MV0-C01", "MV0-C04", "MV0-C05", "MV0-C06", "MV0-C07"]
    if [row.get("part_id") for row in profiles] != expected_parts:
        errors.append("profile rows are not exactly C01/C04/C05/C06/C07")
    if len(features) != 38 or len(coverage) != 26 or len(findings) != 4:
        errors.append(f"unexpected counts: features={len(features)} coverage={len(coverage)} findings={len(findings)}")
    if sum(row.get("coverage_class") == "SCHEDULE_BOUND_CONTROL" for row in coverage) != 6:
        errors.append("schedule-bound control count is not six")
    for row in profiles:
        if row.get("result") != "PASS NOMINAL FILE PARITY" or float(row.get("maximum_profile_extent_delta_mm", "1")) > 1e-9:
            errors.append(f"profile parity failed for {row.get('part_id')}")
        for role in ("step", "dxf", "drawing"):
            path = ROOT / row.get(f"{role}_path", "")
            if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != row.get(f"{role}_sha256"):
                errors.append(f"{row.get('part_id')} {role} identity mismatch")
        if row.get("step_solid_count") != "1" or row.get("step_thickness_mm") != "9.525":
            errors.append(f"{row.get('part_id')} STEP topology/thickness changed")
        if row.get("warning") != WARNING:
            errors.append(f"{row.get('part_id')} warning changed")
    c07 = next((row for row in profiles if row.get("part_id") == "MV0-C07"), {})
    if c07.get("step_face_recess_mm") != "1.0":
        errors.append("C07 STEP face recess is not 1.0 mm")
    exact = [row for row in features if row.get("result") == "EXACT NOMINAL MATCH"]
    upper = [row for row in features if row.get("result") == "CONTROLLED UPPER-LIMIT MATCH"]
    if len(exact) != 30 or len(upper) != 8:
        errors.append(f"feature disposition counts changed: exact={len(exact)} upper={len(upper)}")
    if any(float(row.get("center_delta_mm", "1")) > 1e-9 for row in features):
        errors.append("one or more DXF/STEP feature centers differ")
    if any(float(row.get("radius_delta_mm", "1")) > 1e-9 for row in exact):
        errors.append("an exact feature has nonzero radius delta")
    if any(row.get("dxf_layer") != "M5_COUNTERSINK_NOMINAL" or row.get("radius_delta_mm") != "0.05" or row.get("diameter_delta_mm") != "0.1" for row in upper):
        errors.append("controlled upper-limit countersink evidence changed")
    if any(row.get("physical_execution_state") != "UNEXECUTED" or row.get("fabrication_authorized") != "FALSE" for row in coverage):
        errors.append("drawing coverage is not physical-evidence fail closed")
    if any(row.get("status") != "OPEN" for row in findings):
        errors.append("one or more parity findings are not open")
    for key in ("provider_contacted", "upload_authorized", "quotation_authorized", "fabrication_authorized", "assembly_authorized", "motion_authorized", "energization_authorized"):
        if status.get(key) is not False:
            errors.append(f"status {key} is not false")
    for key, expected in (("part_count", 5), ("feature_parity_count", 38), ("drawing_control_count", 26), ("schedule_bound_control_count", 6), ("exact_feature_match_count", 30), ("controlled_upper_limit_match_count", 8), ("open_finding_count", 4)):
        if status.get(key) != expected:
            errors.append(f"status {key} != {expected}")
    for token in ("font:16px", "font-size:14px", "font-size:13px", "Do the geometry files actually agree?", "DXF outlines are explicitly pre-fillet construction", "Eight countersink STEP edges are at the controlled upper diameter limit", "finding-register.csv"):
        if token not in guide:
            errors.append(f"guide omits {token!r}")
    for token in ("Thirty DXF hole entities", "Eight countersink entities", "Six controls are schedule-bound", "A provider must not machine from STEP or DXF alone"):
        if token not in doc:
            errors.append(f"document omits {token!r}")

    if errors:
        print("HR-V0 mechanical parity check FAILED")
        for error in errors:
            print(f"- {error}")
        return 1
    print("HR-V0 mechanical parity P0.1 check passed: 5 STEP/DXF profiles; 30 exact feature matches; 8 controlled upper-limit countersinks; 26 drawing controls; 6 schedule-bound controls; 4 open findings")
    print("Nominal file parity only; no provider, fabrication, assembly, motion or energization authority")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
