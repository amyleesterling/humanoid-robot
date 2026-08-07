"""Validate the controlled HR-V0 flat-plate RFQ process register."""

from __future__ import annotations

import csv
import math
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REGISTER = ROOT / "cad" / "hr-v0" / "manufacturing" / "hr-v0-flat-plate-process-register.csv"


def main() -> int:
    errors: list[str] = []
    with REGISTER.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))

    expected = {
        "MV0-001": (1, 4.75),
        "MV0-002": (1, 4.75),
        "MV0-003": (1, 6.35),
        "MV0-004": (2, 6.35),
    }
    by_part = {row.get("part_number"): row for row in rows}
    if set(by_part) != set(expected) or len(rows) != len(expected):
        errors.append(f"expected exactly {sorted(expected)}, found {sorted(by_part)}")

    for part, (quantity, thickness) in expected.items():
        row = by_part.get(part, {})
        try:
            actual_quantity = int(row.get("quantity", ""))
            actual_thickness = float(row.get("nominal_thickness_mm", ""))
            feature = float(row.get("current_feature_mm", ""))
            scs_min = float(row.get("sendcutsend_recommended_min_hole_mm", ""))
            xometry_min = float(row.get("xometry_50pct_min_feature_mm", ""))
        except ValueError:
            errors.append(f"{part} contains a nonnumeric controlled value")
            continue
        if actual_quantity != quantity or not math.isclose(actual_thickness, thickness, abs_tol=1e-9):
            errors.append(f"{part} quantity/thickness mismatch")
        if not math.isclose(scs_min, thickness, abs_tol=1e-9):
            errors.append(f"{part} SendCutSend screen must equal stock thickness")
        if not math.isclose(xometry_min, 0.5 * thickness, abs_tol=1e-9):
            errors.append(f"{part} Xometry screen must equal 50 percent of stock thickness")
        expected_scs = "yes" if feature >= scs_min else "no"
        expected_xometry = "yes" if feature >= xometry_min else "no"
        if row.get("sendcutsend_laser_only_compatible") != expected_scs:
            errors.append(f"{part} SendCutSend compatibility does not match the controlled screen")
        if row.get("xometry_50pct_feature_compatible") != expected_xometry:
            errors.append(f"{part} Xometry compatibility does not match the controlled screen")
        if row.get("dimensional_release_status") != "SELECTION REQUIRED":
            errors.append(f"{part} falsely appears dimensionally released")
        closure = row.get("required_closure_evidence", "")
        for required in ("supplier DFM acceptance", "FAI"):
            if required not in closure:
                errors.append(f"{part} closure evidence omits {required}")

    for part in ("MV0-001", "MV0-002", "MV0-003"):
        row = by_part.get(part, {})
        if row.get("selected_rfq_process") != "One-stop CNC OR profile-only blank plus qualified secondary CNC/drill":
            errors.append(f"{part} lost its controlled one-stop/two-process routes")
        if row.get("one_stop_route") != "FAB-001 or FAB-002" or row.get("two_process_route") != "FAB-003":
            errors.append(f"{part} fabrication routes changed")
        blank = ROOT / row.get("profile_only_blank_artifact", "")
        if not blank.is_file() or "PROFILE_ONLY_RFQ" not in blank.name:
            errors.append(f"{part} profile-only blank is missing or misnamed")
        if "separately frozen drawing" not in row.get("secondary_operation", ""):
            errors.append(f"{part} secondary-operation control is incomplete")
        if row.get("sendcutsend_laser_only_compatible") != "no":
            errors.append(f"{part} falsely permits the current laser-only finished-hole route")
    if by_part.get("MV0-004", {}).get("selected_rfq_process") != "Profile cutting or one-stop CNC candidate after bench survey":
        errors.append("MV0-004 lost its bench-survey hold")
    if by_part.get("MV0-004", {}).get("profile_only_blank_artifact") != "NOT GENERATED - SITE HOLD":
        errors.append("MV0-004 falsely exposes a pre-survey blank")

    if errors:
        print("HR-V0 manufacturing register check FAILED")
        for error in errors:
            print(f"- {error}")
        return 1
    print("HR-V0 manufacturing register check passed: 4 controlled parts; no dimensional release")
    print("Status remains PRELIMINARY—NOT APPROVED FOR FABRICATION OR ENERGIZATION")
    return 0


if __name__ == "__main__":
    sys.exit(main())
