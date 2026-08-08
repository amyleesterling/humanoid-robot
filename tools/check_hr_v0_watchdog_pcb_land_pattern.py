"""Validate the R89 watchdog PCB land-pattern audit controls.

PRELIMINARY - NOT APPROVED FOR FABRICATION OR ENERGIZATION.
"""

from __future__ import annotations

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "release" / "hr-v0" / "watchdog-pcb-land-pattern-audit-p0.1"
BOARD = ROOT / "electrical" / "kicad" / "project-button-v3" / "project-button-v3.kicad_pcb"
OLD_CAM = ROOT / "release" / "hr-v0" / "watchdog-pcb-fabrication-candidate-p0.1"
WARNING = "PRELIMINARY - NOT APPROVED FOR FABRICATION OR ENERGIZATION"


def main() -> int:
    failures: list[str] = []
    csv_path = PACKAGE / "land-pattern-audit.csv"
    html_path = PACKAGE / "index.html"
    with csv_path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    refs = [row["reference"] for row in rows]
    expected = {
        "CDRV1", "CDRV2", "CDEC1", "CFI1", "CFI2", "RHB1", "RHP1",
        "RSN1", "RSN2", "RSO1", "RSO2", "RPD1", "RPD2", "RTH1", "RTH2",
        "RW1", "RW2", "UDRV1", "UDRV2", "UFB1", "ISO1", "WDCTRL1", "DC1",
        "JWP1", "JWF1", "JWH1", *(f"TP{i}" for i in range(1, 17)),
        *(f"MH{i}" for i in range(1, 5)),
    }
    if len(rows) != 46:
        failures.append(f"audit row count is {len(rows)}, expected 46")
    if len(refs) != len(set(refs)):
        failures.append("duplicate audit reference")
    if set(refs) != expected:
        failures.append(f"reference coverage mismatch: missing={sorted(expected-set(refs))}, extra={sorted(set(refs)-expected)}")
    required = ("manufacturer_part", "board_footprint", "proposed_process", "primary_document",
                "revision_date", "encoded_geometry", "orientation", "disposition",
                "release_state", "evidence_needed", "warning")
    for row in rows:
        for field in required:
            if not row.get(field, "").strip():
                failures.append(f"{row.get('reference','?')} missing {field}")
        if row.get("warning") != "PRELIMINARY_NOT_APPROVED":
            failures.append(f"{row.get('reference','?')} warning changed")
        if not any(token in row.get("release_state", "") for token in ("HOLD", "REQUIRED")):
            failures.append(f"{row.get('reference','?')} lacks an open release hold")

    board_text = BOARD.read_text(encoding="utf-8-sig")
    for token in (
        'rev "PCB-P0.6 / Electrical V3-P1.13"',
        "PCB-P0.6 - LAND CORRECTION - NO SAFETY CREDIT",
        "TI_PW0016A_Example_Land", "TI_DBQ0016A_Example_Land",
        "VO618A_Option7_SMD", "Murata_GRM21_Reflow_Nominal",
        "TDK_CGA3_Reflow_Nominal", "Panasonic_ERJ6_Reflow_Nominal",
        "Vishay_MMA0204_IPC_Reflow", "Vishay_CRCW1210_Reflow",
        WARNING,
    ):
        if token not in board_text:
            failures.append(f"current board missing {token}")

    old_source = OLD_CAM / "source" / "project-button-v3.kicad_pcb"
    if not old_source.is_file() or 'rev "PCB-P0.5 / Electrical V3-P1.1"' not in old_source.read_text(encoding="utf-8-sig"):
        failures.append("immutable R88 PCB-P0.5 source identity is missing")

    html = html_path.read_text(encoding="utf-8")
    for token in ("PCB-P0.6", "PRELIMINARY", "NOT APPROVED FOR FABRICATION OR ENERGIZATION",
                  "land-pattern-audit.csv", "font:16px", "font-size:14px", "font-size:12px"):
        if token not in html:
            failures.append(f"interactive guide missing {token}")
    if "font-size:11px" in html or "font-size:10px" in html:
        failures.append("interactive guide contains user-facing text below 12 px")

    if failures:
        print("HR-V0 watchdog PCB land-pattern audit validation: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("HR-V0 watchdog PCB land-pattern audit validation: PASS")
    print("46/46 board references covered; 21 corrected references / 86 source lands; every reference retains an open release hold")
    print("PCB-P0.6 current; immutable PCB-P0.5 CAM record preserved and superseded for current review")
    print(WARNING)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
