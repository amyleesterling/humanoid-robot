"""Fail-closed validation of HR-V0 fabrication route and quote controls."""

from __future__ import annotations

import csv
import sys
import xml.etree.ElementTree as ET
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REGISTER = ROOT / "cad" / "hr-v0" / "manufacturing" / "hr-v0-fabrication-route-register.csv"
FORM = ROOT / "tests" / "forms" / "hr-v0-fabrication-supplier-quote-template.csv"
BLANKS = ROOT / "cad" / "hr-v0" / "generated" / "manufacturing-blanks"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def main() -> int:
    errors: list[str] = []
    rows = read_csv(REGISTER)
    by_id = {row.get("route_id"): row for row in rows}
    expected = {f"FAB-{index:03d}" for index in range(1, 8)}
    if set(by_id) != expected or len(rows) != 7:
        errors.append(f"expected exactly FAB-001 through FAB-007, found {sorted(by_id)}")

    for route in ("FAB-001", "FAB-002", "FAB-003", "FAB-004"):
        if by_id.get(route, {}).get("release_state") != "SELECTION REQUIRED":
            errors.append(f"{route} falsely appears selected or released")
    if by_id.get("FAB-005", {}).get("release_state") != "PROTOTYPING ONLY":
        errors.append("FabVille must remain prototyping only")
    if by_id.get("FAB-006", {}).get("release_state") != "EXCLUDED FROM STRUCTURAL METAL ROUTE":
        errors.append("Boston Public Library must remain excluded from the structural-metal route")
    if by_id.get("FAB-007", {}).get("release_state") != "SITE HOLD":
        errors.append("MV0-004 route lost its site hold")

    scs = by_id.get("FAB-003", {})
    if "Profile-only blank" not in scs.get("process_sequence", ""):
        errors.append("FAB-003 is not constrained to a profile-only first operation")
    for required in ("PROFILE_ONLY_RFQ", "No finished holes"):
        combined = " ".join(scs.values())
        if required not in combined:
            errors.append(f"FAB-003 omits required control: {required}")

    expected_blank_files = {
        "MV0-001_upper_link_PROFILE_ONLY_RFQ.dxf",
        "MV0-001_upper_link_PROFILE_ONLY_RFQ.step",
        "MV0-002_forearm_link_PROFILE_ONLY_RFQ.dxf",
        "MV0-002_forearm_link_PROFILE_ONLY_RFQ.step",
        "MV0-003_shoulder_adapter_PROFILE_ONLY_RFQ.dxf",
        "MV0-003_shoulder_adapter_PROFILE_ONLY_RFQ.step",
        "HR-V0_profile-only-blank-RFQ-guide.svg",
        "profile-only-blanks.csv",
    }
    actual_blank_files = {path.name for path in BLANKS.glob("*") if path.is_file()}
    if actual_blank_files != expected_blank_files:
        errors.append(f"profile-only blank set mismatch: {sorted(actual_blank_files)}")
    if (BLANKS / "profile-only-blanks.csv").is_file():
        blank_rows = read_csv(BLANKS / "profile-only-blanks.csv")
        if [row.get("part_number") for row in blank_rows] != ["MV0-001", "MV0-002", "MV0-003"]:
            errors.append("blank manifest lost controlled part sequence")
        for row in blank_rows:
            if row.get("finished_holes_included") != "0":
                errors.append(f"{row.get('part_number')} blank falsely includes finished holes")
            if row.get("blank_revision") != "HR-V0-FAB-RFQ-P0.1":
                errors.append(f"{row.get('part_number')} blank revision mismatch")
    guide = BLANKS / "HR-V0_profile-only-blank-RFQ-guide.svg"
    try:
        svg_root = ET.parse(guide).getroot()
        if svg_root.get("width") != "1200" or svg_root.get("height") != "820" or svg_root.get("viewBox") != "0 0 1200 820":
            errors.append("profile-only guide lost its controlled 1200 x 820 canvas")
        guide_text = guide.read_text(encoding="utf-8")
        for required in (
            "font: 16px",
            "HOLES ARE DELIBERATELY OMITTED",
            "PRELIMINARY - NOT APPROVED FOR FABRICATION OR ENERGIZATION",
        ):
            if required not in guide_text:
                errors.append(f"profile-only guide omits required readable control: {required}")
    except (FileNotFoundError, ET.ParseError) as exc:
        errors.append(f"profile-only guide missing or invalid: {exc}")

    form_rows = read_csv(FORM)
    if {row.get("route_id") for row in form_rows} != {"FAB-001", "FAB-002", "FAB-003", "FAB-004", "FAB-007"}:
        errors.append("quote template does not cover every eligible route")
    for row in form_rows:
        if row.get("record_id") != "NOT-EXECUTED" or not row.get("status", "").startswith("PRELIMINARY"):
            errors.append(f"quote template contains executed-looking row {row.get('route_id')}")
        if row.get("rfq_revision") != "HR-V0-FAB-RFQ-P0.1":
            errors.append(f"quote template revision mismatch at {row.get('route_id')}")

    if errors:
        print("HR-V0 fabrication-route check FAILED")
        for error in errors:
            print(f"- {error}")
        return 1
    print("HR-V0 fabrication-route check passed: 7 routes; 3 hole-free blank packages; no supplier or fabrication release")
    print("Status remains PRELIMINARY - NOT APPROVED FOR FABRICATION OR ENERGIZATION")
    return 0


if __name__ == "__main__":
    sys.exit(main())
