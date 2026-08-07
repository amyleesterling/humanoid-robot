#!/usr/bin/env python3
"""Fail-closed check for the HR-V0 SD1 exact-candidate package."""

from __future__ import annotations

import csv
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs" / "hr-v0-service-disconnect-p0.2.md"
SCHEMATIC_BOM = ROOT / "electrical" / "kicad" / "project-button-v3" / "bom.csv"
SYSTEM_BOM = ROOT / "bom" / "bom.csv"
SIDEWALL = ROOT / "electrical" / "panel" / "hr-v0-control-panel-p0.4" / "sidewall-placement.csv"
FORM = ROOT / "tests" / "forms" / "hr-v0-service-disconnect-receiving-application-template.csv"
WARNING = "PRELIMINARY - NOT APPROVED FOR WIRING OR ENERGIZATION"


def main() -> int:
    errors: list[str] = []
    text = DOC.read_text(encoding="utf-8") if DOC.is_file() else ""
    for required in (
        "Littelfuse `75920-01` is frozen as the exact `SD1` **catalog candidate on hold**",
        "not the emergency stop",
        "receives no functional-safety credit",
        "Blue Sea Systems `6004200`",
        "ABB `OTDCP25SA11M`",
        "two-pole diagram conflicts",
        "4/0 AWG",
        "terminals remain `TBD-IN` and `TBD-OUT`",
        "component-level lockout feature does not establish Project Button compliance",
        "ACTUATOR DC SERVICE DISCONNECT - LOCK OFF FOR SERVICE - NOT E-STOP",
        "All 15 rows remain `NOT EXECUTED`",
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

    schematic_rows: list[dict[str, str]] = []
    if SCHEMATIC_BOM.is_file():
        with SCHEMATIC_BOM.open(newline="", encoding="utf-8-sig") as handle:
            schematic_rows = list(csv.DictReader(handle))
    sd1 = next((row for row in schematic_rows if row.get("reference") == "SD1"), {})
    if "75920-01" not in sd1.get("value", ""):
        errors.append("V3 schematic BOM does not freeze SD1 as 75920-01")
    if "APPLICATION" not in sd1.get("status", "") or "SELECTION REQUIRED" not in sd1.get("status", ""):
        errors.append("V3 SD1 status no longer retains the application hold")

    system_rows: list[dict[str, str]] = []
    if SYSTEM_BOM.is_file():
        with SYSTEM_BOM.open(newline="", encoding="utf-8-sig") as handle:
            system_rows = list(csv.DictReader(handle))
    system_sd1 = next((row for row in system_rows if row.get("item_id") == "BOM-042"), {})
    if system_sd1.get("manufacturer") != "Littelfuse" or not system_sd1.get("manufacturer_part_number", "").startswith("75920-01"):
        errors.append("system BOM-042 does not retain the exact Littelfuse candidate")
    if system_sd1.get("baseline_status") != "exact_candidate_hold":
        errors.append("BOM-042 no longer has exact_candidate_hold status")

    sidewall_rows: list[dict[str, str]] = []
    if SIDEWALL.is_file():
        with SIDEWALL.open(newline="", encoding="utf-8-sig") as handle:
            sidewall_rows = list(csv.DictReader(handle))
    if len(sidewall_rows) != 1 or sidewall_rows[0].get("reference") != "SD1":
        errors.append("SD1 sidewall package must contain exactly one placement option")
    elif any(sidewall_rows[0].get(field) != "SELECTION REQUIRED" for field in ("cutout", "rear_envelope", "conductor_route")):
        errors.append("SD1 sidewall option infers unreleased physical geometry or routing")
    elif "NO CUTOUT" not in sidewall_rows[0].get("release_state", ""):
        errors.append("SD1 sidewall option does not fail closed")

    if errors:
        print("HR-V0 service-disconnect screen FAILED")
        for error in errors:
            print(f"- {error}")
        return 1
    print("HR-V0 service-disconnect P0.2 check passed: 15 records remain NOT EXECUTED")
    print("SD1 exact catalog identity/topology are frozen on hold; no cutout, conductor, lockout procedure, wiring or energization release exists")
    print(WARNING)
    return 0


if __name__ == "__main__":
    sys.exit(main())
