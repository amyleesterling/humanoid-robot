"""Fail closed unless every obsolete HR-V0 fabrication RFI is withdrawn."""

from __future__ import annotations

import csv
import sys
from pathlib import Path

from generate_hr_v0_fabrication_rfi_packets import OUT, ROWS, WARNING


def main() -> int:
    errors: list[str] = []
    expected = {"WITHDRAWN.md", "withdrawal-register.csv"}
    actual = {path.name for path in OUT.iterdir() if path.is_file()}
    if actual != expected:
        errors.append(f"fabrication-RFI directory must contain only withdrawal controls, found {sorted(actual)}")
    if list(OUT.glob("*.zip")):
        errors.append("obsolete supplier ZIP remains active")
    try:
        with (OUT / "withdrawal-register.csv").open(newline="", encoding="utf-8") as handle:
            rows = list(csv.DictReader(handle))
    except FileNotFoundError as exc:
        errors.append(str(exc))
        rows = []
    if [row.get("packet_id") for row in rows] != [row[0] for row in ROWS]:
        errors.append("withdrawal register does not cover RFI-001 through RFI-006 in order")
    for row in rows[:5]:
        if row.get("state") != "WITHDRAWN" or row.get("superseded_revision") != "HR-V0-FAB-RFI-P0.1":
            errors.append(f"{row.get('packet_id')} is not unambiguously withdrawn")
    if len(rows) == 6 and rows[5].get("state") != "SITE HOLD":
        errors.append("RFI-006 lost its bench-site hold")
    text = (OUT / "WITHDRAWN.md").read_text(encoding="utf-8") if (OUT / "WITHDRAWN.md").is_file() else ""
    for token in (WARNING, "exact ROBOTIS STEP", "978119f", "MECH-005", "AUDIT-MECH-012"):
        if token not in text:
            errors.append(f"withdrawal notice omits {token}")
    if errors:
        print("HR-V0 fabrication RFI withdrawal validation: FAIL", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print("HR-V0 fabrication RFI withdrawal validation: PASS")
    print("0 active packets; RFI-001 through RFI-005 withdrawn; RFI-006 remains on site hold")
    print(WARNING)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
