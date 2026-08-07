#!/usr/bin/env python3
"""Fail-closed check for the HR-V0 SD1 screening package."""

from __future__ import annotations

import csv
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs" / "hr-v0-service-disconnect-p0.1.md"
FORM = ROOT / "tests" / "forms" / "hr-v0-service-disconnect-receiving-application-template.csv"
WARNING = "PRELIMINARY - NOT APPROVED FOR WIRING OR ENERGIZATION"


def main() -> int:
    errors: list[str] = []
    text = DOC.read_text(encoding="utf-8") if DOC.is_file() else ""
    for required in (
        "SD1` remains **SELECTION REQUIRED**",
        "not the emergency stop",
        "Blue Sea Systems `6004200` is a dimensioned screening candidate only",
        "4/0 AWG",
        "turn loads off before switching OFF",
        "not evidence of a padlockable energy-isolation procedure",
        "do not select `SD1`",
    ):
        if required not in text:
            errors.append(f"service-disconnect document omits: {required}")

    rows: list[dict[str, str]] = []
    if FORM.is_file():
        with FORM.open(newline="", encoding="utf-8-sig") as handle:
            rows = list(csv.DictReader(handle))
    if len(rows) != 15 or {row.get("step_id") for row in rows} != {f"SD-{i:03d}" for i in range(1, 16)}:
        errors.append("service-disconnect form must contain SD-001..SD-015")
    for row in rows:
        if row.get(None):
            errors.append(f"{row.get('step_id')} has extra CSV fields")
        if row.get("record_id") != "NOT-EXECUTED" or row.get("status") != "NOT EXECUTED":
            errors.append(f"{row.get('step_id')} contains executed-looking evidence")
        if row.get("warning") != WARNING:
            errors.append(f"{row.get('step_id')} lacks the exact warning")

    if errors:
        print("HR-V0 service-disconnect screen FAILED")
        for error in errors:
            print(f"- {error}")
        return 1
    print("HR-V0 service-disconnect P0.1 screen passed: 15 records remain NOT EXECUTED")
    print("SD1 remains SELECTION REQUIRED; no cutout, conductor, lockout, wiring or energization release exists")
    print(WARNING)
    return 0


if __name__ == "__main__":
    sys.exit(main())
