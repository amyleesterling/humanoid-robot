"""Check that the watchdog PCB physical route is complete and unexecuted."""

from __future__ import annotations

import csv
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WARNING = "PRELIMINARY - NOT APPROVED FOR FABRICATION OR ENERGIZATION"
FORMS = {
    "hr-v0-watchdog-pcb-cam-review-template.csv": (24, "record_status"),
    "hr-v0-watchdog-pcb-receiving-assembly-template.csv": (18, "record_status"),
    "hr-v0-watchdog-pcb-current-limited-bringup-template.csv": (16, "record_status"),
    "hr-v0-watchdog-pcb-inspection-template.csv": (13, "status"),
}


def rows(name: str) -> list[dict[str, str]]:
    with (ROOT / "tests" / "forms" / name).open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def main() -> int:
    failures: list[str] = []
    for name, (count, status_key) in FORMS.items():
        data = rows(name)
        if len(data) != count:
            failures.append(f"{name}: expected {count} rows, found {len(data)}")
        if any(row.get(status_key) not in {"NOT_EXECUTED", "NOT-EXECUTED"} for row in data):
            failures.append(f"{name}: execution status changed")
        if name != "hr-v0-watchdog-pcb-inspection-template.csv" and any(row.get("warning") != WARNING for row in data):
            failures.append(f"{name}: warning missing or changed")
        if any(row.get("disposition") != "OPEN" for row in data):
            failures.append(f"{name}: every disposition must remain OPEN")

    inspection = rows("hr-v0-watchdog-pcb-inspection-template.csv")
    if any(row["electrical_revision"] != "V3-P1.13" or row["pcb_revision"] != "PCB-P0.5" for row in inspection):
        failures.append("inspection form configuration mismatch")
    bringup = rows("hr-v0-watchdog-pcb-current-limited-bringup-template.csv")
    if {row["step"] for row in bringup} != {f"BR-{i:03d}" for i in range(0, 160, 10)}:
        failures.append("bring-up step set mismatch")
    if not all("SELECTION REQUIRED" in (row["current_limit"] + row["voltage_command"]) or row["step"] in {"BR-000", "BR-010", "BR-140", "BR-150"} for row in bringup):
        failures.append("bring-up power stages must retain selection-required limits")

    traveler = (ROOT / "docs" / "hr-v0-watchdog-pcb-build-test-traveler-p0.1.md").read_text(encoding="utf-8")
    for term in (WARNING, "zero safety credit", "No supplier upload", "isolated, current-limited", "E2-HOLD-008", "does **not** close"):
        if term not in traveler:
            failures.append(f"traveler missing boundary: {term}")
    if traveler.count("| WD-TG-") != 9:
        failures.append("traveler must define nine phase gates")

    with (ROOT / "electrical" / "e2" / "hr-v0-e2-hardware-p0.2" / "e2-blocking-holds.csv").open(newline="", encoding="utf-8-sig") as handle:
        e2_holds = list(csv.DictReader(handle))
    hold8 = next((row for row in e2_holds if row["hold_id"] == "E2-HOLD-008"), None)
    if not hold8 or "PCB-P0.7" not in hold8["open_item"] or "no CAM or manufacturing release" not in hold8["open_item"] or "PCB-P0.5 CAM" not in hold8["open_item"]:
        failures.append("E2-HOLD-008 disposition not synchronized")

    with (ROOT / "tests" / "procedures" / "procedure-registry.csv").open(newline="", encoding="utf-8-sig") as handle:
        registry = list(csv.DictReader(handle))
    ids = {row["verification_id"] for row in registry}
    expected = {"AUDIT-ELEC-002", "INSPECT-ELEC-007", "INSPECT-ELEC-010", "TEST-ELEC-008"}
    if not expected <= ids:
        failures.append(f"procedure registry missing: {sorted(expected - ids)}")
    for item in registry:
        if item["verification_id"] in expected and item["status"] != "selection_required":
            failures.append(f"{item['verification_id']}: status must be selection_required")

    if failures:
        print("HR-V0-WD-TRAVELER-P0.1 FAIL")
        for failure in failures:
            print(" -", failure)
        return 1
    print("HR-V0-WD-TRAVELER-P0.1 PASS")
    print("  24 CAM + 18 receiving/assembly + 16 bring-up + 13 inspection rows")
    print("  9 phase gates; all physical rows NOT_EXECUTED and OPEN")
    print("  Historical PCB-P0.5 route only; E2-HOLD-008 now points to PCB-P0.7 with no current CAM")
    print("  Fabrication and energization remain prohibited")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
