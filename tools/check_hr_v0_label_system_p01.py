"""Fail-closed digital checks for HR-V0-LABEL-P0.1."""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PKG = ROOT / "electrical" / "panel" / "hr-v0-label-system-p0.1"
DOC = ROOT / "docs" / "hr-v0-label-system-p0.1.md"
GUIDE = ROOT / "release" / "hr-v0" / "label-system-p0.1" / "index.html"
GATES = ROOT / "requirements" / "hr-v0-gate-evidence-supplement-r169.csv"
WARNING = "PRELIMINARY - NOT APPROVED FOR WIRING OR ENERGIZATION"


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def need(condition: bool, message: str, errors: list[str]) -> None:
    if not condition:
        errors.append(message)


def main() -> int:
    errors: list[str] = []
    expected = {
        "terminal-marker-schedule.csv",
        "device-marker-schedule.csv",
        "large-legend-schedule.csv",
        "source-register.csv",
        "open-holds.csv",
        "package-status.json",
    }
    need(PKG.is_dir() and {p.name for p in PKG.iterdir()} == expected, "package membership changed", errors)

    terminal = rows(PKG / "terminal-marker-schedule.csv")
    device = rows(PKG / "device-marker-schedule.csv")
    large = rows(PKG / "large-legend-schedule.csv")
    sources = rows(PKG / "source-register.csv")
    holds = rows(PKG / "open-holds.csv")
    status = json.loads((PKG / "package-status.json").read_text(encoding="utf-8"))

    for name, table in (("terminal", terminal), ("device", device), ("large", large), ("source", sources), ("hold", holds)):
        for index, row in enumerate(table, 1):
            need(not row.get(None), f"{name} row {index} has extra CSV fields", errors)
            need(row.get("warning") == WARNING, f"{name} row {index} warning changed", errors)

    expected_nets = {
        "XT1-01": "SAFETY_24V",
        "XT1-02": "SAFETY_0V",
        "XT1-03": "SR1_STATUS",
        "XT1-04": "SRA1_STATUS",
        "XT1-05": "K1_STATUS",
        "XT1-06": "K2_STATUS",
    }
    need(len(terminal) == 6, "terminal marker count changed", errors)
    for index, row in enumerate(terminal, 1):
        position = f"XT1-{index:02d}"
        need(row.get("terminal_position") == position, f"terminal marker order changed at {index}", errors)
        need(row.get("net") == expected_nets[position], f"{position} net changed", errors)
        need(row.get("printed_text") == f"{index:02d}", f"{position} no longer uses its two-digit marker", errors)
        need(row.get("item_number") == "0828734", f"{position} stock changed", errors)
        need("/" not in row.get("printed_text", "") and len(row.get("printed_text", "")) == 2, f"{position} contains overlong text", errors)

    need(len(device) == 34, "device/operator marker count changed", errors)
    need(sum(r.get("classification") == "device_reference" for r in device) == 30, "device-reference count changed", errors)
    need(sum(r.get("classification") == "operator_legend" for r in device) == 4, "operator-legend count changed", errors)
    need(all(r.get("item_number") == "0830839" for r in device), "small marker stock changed", errors)
    required_refs = {"S0", "S1", "S2", "H1", "SR1", "SRA1", "KWD1", "KWD2", "K1", "K2", "WDPCB1", "INJ1", "XT1", "F24", "F0", "F1", "F2", "F3", "FSR1", "FSR2", "SD1", "J24", "CCASE1", "PI1", "COOL1", "U2D2", "PSU3", "PSA1", "PSU2", "ENC1"}
    actual_refs = {r["reference_or_location"] for r in device if r["classification"] == "device_reference"}
    need(actual_refs == required_refs, "device-reference set changed", errors)
    operator_text = {r["printed_text"] for r in device if r["classification"] == "operator_legend"}
    need(operator_text == {"EMERGENCY STOP", "RESET", "ARM REQUEST", "RESET STAGE READY"}, "operator text changed", errors)

    need(len(large) == 4 and all(r.get("item_number") == "0828805" for r in large), "large legend allocation changed", errors)
    large_text = " ".join(r.get("printed_lines", "") for r in large)
    for token in ("NOT APPROVED FOR | ENERGIZATION", "NO MOTION | AUTHORITY", "ACTUATOR SOURCE | MUST BE ABSENT", "CONFIGURATION CONTROLLED"):
        need(token in large_text, f"large legend missing {token}", errors)

    need({r.get("item_number") for r in sources} == {"0828734", "0830839", "0828805"}, "source item set changed", errors)
    need(all(r.get("verified_date") == "2026-08-09" for r in sources), "source verification date changed", errors)
    need(len(holds) == 12 and {r.get("hold_id") for r in holds} == {f"LBL-HOLD-{i:03d}" for i in range(1, 13)}, "hold register changed", errors)

    need(status.get("identifier") == "HR-V0-LABEL-P0.1" and status.get("review_round") == "R169", "status identity changed", errors)
    need(status.get("terminal_marker_rows") == 6 and status.get("device_and_operator_marker_rows") == 34 and status.get("large_legend_rows") == 4 and status.get("open_holds") == 12, "status counts changed", errors)
    for flag in ("wire_marker_selection_complete", "printer_or_service_selected", "artwork_approved", "procurement_authorized", "printing_authorized", "installation_authorized", "wiring_authorized", "energization_authorized", "safety_credit_claimed"):
        need(status.get(flag) is False, f"{flag} must remain false", errors)

    bom = {r["item_id"]: r for r in rows(ROOT / "bom" / "bom.csv")}
    bom62 = bom.get("BOM-062", {})
    need(bom62.get("manufacturer") == "Phoenix Contact" and bom62.get("baseline_status") == "exact_candidate_hold", "BOM-062 exact hold missing", errors)
    for token in ("0828734", "0830839", "0828805"):
        need(token in bom62.get("manufacturer_part_number", ""), f"BOM-062 missing {token}", errors)
    basis = bom62.get("selection_basis", "").lower().replace("wire-marker", "wire marker")
    need("wire marker" in basis and "selection required" in basis, "BOM-062 does not retain wire-marker hold", errors)

    xt1 = rows(ROOT / "electrical" / "panel" / "hr-v0-xt1-terminal-group-p0.1" / "accessory-allocation.csv")
    marker = next((r for r in xt1 if r.get("item_number") == "0828734"), {})
    need(marker.get("bom_owner") == "BOM-062" and "PRINT/INSTALL HOLD" in marker.get("state", ""), "XT1 marker ownership/state changed", errors)

    panel_terms = rows(ROOT / "electrical" / "panel" / "hr-v0-control-panel-p0.6" / "terminal-allocation.csv")
    need([r.get("marker_text") for r in panel_terms] == [f"{i:02d}" for i in range(1, 7)], "panel terminal marker text not corrected", errors)

    gate_rows = rows(GATES)
    need({r.get("gate_id") for r in gate_rows} == {"EG-003", "EG-015"} and all(r.get("disposition") == "REMAINS PARTIAL" for r in gate_rows), "gate supplement changed", errors)

    doc = DOC.read_text(encoding="utf-8")
    guide = GUIDE.read_text(encoding="utf-8")
    for token in ("HR-V0-LABEL-P0.1", "4.6 x 10.5 mm", "BOM-062", "wire markers", "EG-015", "NOT APPROVED"):
        need(token in doc, f"document missing {token}", errors)
    for token in ("HR-V0-LABEL-P0.1", "Everything", "XT1 markers", "Device references", "Door legends", "NOT APPROVED FOR PROCUREMENT", "font-size:14px", "font:16px"):
        need(token in guide, f"guide missing {token}", errors)

    if errors:
        print("HR-V0 label system P0.1 check FAILED")
        for error in errors:
            print(f"- {error}")
        return 1
    print("HR-V0 label system P0.1 check passed: 6 short terminal markers, 34 device/operator markers, 4 large legends, 12 open holds")
    print("BOM-062 remains an exact-candidate HOLD; printing, wire markers, adhesion, installed inspection, code marking and qualified review remain open")
    print("PRELIMINARY - NOT APPROVED FOR WIRING OR ENERGIZATION")
    return 0


if __name__ == "__main__":
    sys.exit(main())
