"""Validate HR-V0-WD-MOUNT-IF-P0.1 without implying fabrication release."""

from __future__ import annotations

import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "electrical" / "panel" / "hr-v0-watchdog-pcb-mounting-p0.1"
WEB = ROOT / "release" / "hr-v0" / "watchdog-pcb-mounting-p0.1" / "index.html"
BOARD = ROOT / "electrical" / "kicad" / "project-button-v3" / "project-button-v3.kicad_pcb"
OLD_BOARD = ROOT / "release" / "hr-v0" / "watchdog-pcb-fabrication-candidate-p0.1" / "source" / "project-button-v3.kicad_pcb"
DRC = ROOT / "electrical" / "kicad" / "project-button-v3" / "validation" / "project-button-v3-r131-audit-drc.rpt"
WARNING = "PRELIMINARY - NOT APPROVED FOR FABRICATION OR ENERGIZATION"


def rows(name: str) -> list[dict[str, str]]:
    with (OUT / name).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def main() -> int:
    failures: list[str] = []
    reconciliation = rows("current-board-reconciliation.csv")
    holes = rows("mount-coordinate-register.csv")
    candidates = rows("standoff-candidate-register.csv")
    holds = rows("closure-holds.csv")
    receiving = rows("receiving-template.csv")
    sources = rows("source-register.csv")
    screens = rows("interface-screen.csv")
    summary = json.loads((OUT / "mounting-interface-summary.json").read_text(encoding="utf-8"))

    if len(reconciliation) != 2:
        failures.append("expected two configuration-reconciliation rows")
    if [row["reference"] for row in holes] != ["MH1", "MH2", "MH3", "MH4"]:
        failures.append("mount-hole reference/order mismatch")
    expected_coords = [("5.000", "5.000"), ("155.000", "5.000"), ("5.000", "95.000"), ("155.000", "95.000")]
    if [(row["board_x_from_left_mm"], row["board_y_from_top_mm"]) for row in holes] != expected_coords:
        failures.append("board-relative mounting coordinates changed")
    if {row["manufacturer_part_number"] for row in candidates} != {"R30-1611000", "R30-1611300", "R30-1611500"}:
        failures.append("exact Harwin candidate set changed")
    if any(row["state"] != "EXACT CATALOG CANDIDATE - NOT SELECTED" for row in candidates):
        failures.append("a standoff candidate appears selected")
    if len(holds) != 12 or sum(row["status"] == "PARTIAL" for row in holds) != 2 or sum(row["status"] == "OPEN" for row in holds) != 10:
        failures.append("hold count/state changed")
    if len(receiving) != 8 or any(row["state"] != "NOT EXECUTED / NOT AUTHORIZED" or row["result"] for row in receiving):
        failures.append("receiving template is not blank/fail-closed")
    if len(sources) != 6 or len(screens) != 6:
        failures.append("source or screen row count changed")
    if summary.get("selected_standoff") != "SELECTION REQUIRED" or summary.get("selected_fasteners") != "SELECTION REQUIRED":
        failures.append("summary improperly selects mounting hardware")
    if summary.get("iso1_current_inner_gap_mm") != 8.01 or summary.get("iso1_current_overall_span_mm") != 11.05:
        failures.append("ISO1 current geometry arithmetic changed")

    current = BOARD.read_text(encoding="utf-8-sig")
    historical = OLD_BOARD.read_text(encoding="utf-8-sig")
    for token in ('rev "PCB-P1.0 / Electrical V3-P1.15"', '(at -4.765 -1.27)', '(size 1.52 1.78)', 'https://www.vishay.com/docs/83432/vo618a.pdf'):
        if token not in current:
            failures.append(f"current board missing {token}")
    for token in ('rev "PCB-P0.5 / Electrical V3-P1.1"', '(at -4.4 -1.27)', '(size 2 1.6)', '(property "Datasheet" ""'):
        if token not in historical:
            failures.append(f"historical board evidence missing {token}")
    drc = DRC.read_text(encoding="utf-8-sig")
    for token in ("Found 0 DRC violations", "Found 0 unconnected pads", "Found 0 Footprint errors"):
        if token not in drc:
            failures.append(f"R131 native DRC missing {token}")
    page = WEB.read_text(encoding="utf-8")
    for token in ("HR-V0-WD-MOUNT-IF-P0.1", "PCB-P0.6", "8.01 mm", "150 × 90 mm", WARNING, "font:17px", "font-size:16px", "font:14px"):
        if token not in page:
            failures.append(f"web guide missing {token}")
    if "font-size:11px" in page or "font-size:10px" in page:
        failures.append("web guide contains user-facing text below 12 px")

    if failures:
        print("HR-V0 watchdog PCB mounting interface P0.1 check failed")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("HR-V0 watchdog PCB mounting interface P0.1 check passed")
    print("Historical P0.5 defect reconciled; current metadata-only P0.9 retains the ISO1 correction and mounting pattern with 3 exact unselected standoff candidates and 12 holds")
    print(WARNING)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
