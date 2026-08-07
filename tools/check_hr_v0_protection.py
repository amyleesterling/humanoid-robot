#!/usr/bin/env python3
"""Check the preliminary HR-V0 protection-coordination input register.

This checker prevents an unresolved candidate fuse rating from being mistaken for
a released value. It does not perform or approve protection coordination.
"""

from __future__ import annotations

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REGISTER = ROOT / "electrical" / "hr-v0-protection-coordination-inputs.csv"
FORM = ROOT / "tests" / "forms" / "hr-v0-protection-coordination-template.csv"
DOC = ROOT / "docs" / "hr-v0-protection-coordination-p0.2.md"
EXPECTED_REFERENCES = {"F0", "F1", "F2", "F3", "FSR1", "FSR2"}
OPEN_VALUE_FIELDS = {
    "fuse_rating_a",
    "source_fault_current_a",
    "cable_one_way_m",
    "conductor_part",
    "conductor_awg",
    "ambient_c",
    "bundle_count",
    "load_inrush_or_peak_a",
    "duty_cycle",
    "acceptable_drop_pct",
    "calculated_drop_v",
    "max_measured_temp_c",
    "clearing_time_s",
}


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def main() -> int:
    failures: list[str] = []
    register = rows(REGISTER)
    form = rows(FORM)
    references = {row["reference"].strip() for row in register}
    if references != EXPECTED_REFERENCES:
        failures.append(
            f"coordination register references {sorted(references)} do not equal "
            f"{sorted(EXPECTED_REFERENCES)}"
        )
    if len(register) != len(EXPECTED_REFERENCES):
        failures.append("coordination register must contain one row per controlled reference")

    for row in register:
        ref = row["reference"].strip() or "<blank>"
        if "SELECTION REQUIRED" not in row["status"]:
            failures.append(f"{ref}: unresolved status warning is missing")
        if row["fuse_rating_a"].strip() != "SELECTION REQUIRED":
            failures.append(f"{ref}: fuse rating was released without the physical evidence gate")
        if not row["evidence_needed"].strip():
            failures.append(f"{ref}: evidence_needed is blank")
        for field in OPEN_VALUE_FIELDS:
            if not row.get(field, "").strip():
                failures.append(f"{ref}: {field} must explicitly say SELECTION REQUIRED")

    holders = {row["reference"]: row["proposed_holder_or_block"] for row in register}
    expected_holders = {
        "F0": "Littelfuse FHAC0002SXJ",
        "F1": "Blue Sea Systems 5025",
        "F2": "Blue Sea Systems 5025",
        "F3": "Blue Sea Systems 5025",
        "FSR1": "Phoenix Contact PT 4-HESI (5X20) item 3211861; exact holder candidate only",
        "FSR2": "Phoenix Contact PT 4-HESI (5X20) item 3211861; exact holder candidate only",
    }
    if holders != expected_holders:
        failures.append(f"protection-holder boundary changed: {holders}")

    form_refs = {row["reference"].strip() for row in form}
    if form_refs != EXPECTED_REFERENCES:
        failures.append("execution template does not cover all six protection references")
    if any(row["record_id"] != "NOT-EXECUTED" for row in form):
        failures.append("execution template contains a record that looks executed")

    text = DOC.read_text(encoding="utf-8")
    for phrase in (
        "PRELIMINARY - NOT APPROVED FOR FABRICATION OR ENERGIZATION",
        "No fuse ampere rating is released",
        "4.4 A",
        "3 A",
        "INSPECT-ELEC-008",
        "TEST-ELEC-006",
        "ANALYSIS-ELEC-001",
        "PT 4-HESI (5X20)` item `3211861",
        "HR-V0-CP-P0.2",
    ):
        if phrase not in text:
            failures.append(f"coordination document is missing required phrase: {phrase}")

    if failures:
        print("HR-V0 protection-coordination check FAILED")
        for failure in failures:
            print(f"- {failure}")
        return 1

    open_cells = sum(
        1
        for row in register
        for field in OPEN_VALUE_FIELDS
        if row[field].strip() == "SELECTION REQUIRED"
    )
    print(
        "HR-V0 protection-coordination register OK: "
        f"{len(register)} references, {open_cells} explicit open input cells, "
        "and zero released fuse ampere ratings."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
