#!/usr/bin/env python3
"""Fail-closed checks for HR-V0-PANEL-RD-P0.1 / R123."""

from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PANEL = ROOT / "electrical" / "panel" / "hr-v0-control-panel-p0.6"
WARNING = "PRELIMINARY - NOT APPROVED FOR FABRICATION OR ENERGIZATION"


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def main() -> None:
    failures: list[str] = []

    def require(condition: bool, message: str) -> None:
        if not condition:
            failures.append(message)

    bom = {row["item_id"]: row for row in rows(ROOT / "bom" / "bom.csv")}
    closure = {row["item_id"]: row for row in rows(ROOT / "bom" / "hr-v0-bom-closure.csv")}
    panel_bom = {row["item_id"]: row for row in rows(PANEL / "panel-bom.csv")}
    layout = {row["layout_id"]: row for row in rows(PANEL / "backplate-layout.csv")}
    cut_plan = rows(PANEL / "rail-duct-cut-plan-p0.1.csv")
    holds = rows(PANEL / "rail-duct-holds-p0.1.csv")
    sources = rows(ROOT / "electrical" / "vendor" / "phoenix-contact" / "panel-rail-duct-r123" / "source-manifest-p0.1.csv")
    receiving = rows(ROOT / "tests" / "forms" / "hr-v0-panel-rail-duct-receiving-template-p0.1.csv")
    installation = rows(ROOT / "tests" / "forms" / "hr-v0-panel-rail-duct-installation-template-p0.1.csv")
    gates = {row["gate_id"]: row for row in rows(ROOT / "requirements" / "hr-v0-energization-gates.csv")}
    metadata = json.loads((ROOT / "release" / "hr-v0" / "release-candidate.json").read_text(encoding="utf-8"))
    doc = (ROOT / "docs" / "hr-v0-panel-rail-duct-p0.1.md").read_text(encoding="utf-8")
    guide = (ROOT / "release" / "hr-v0" / "panel-rail-duct-p0.1" / "index.html").read_text(encoding="utf-8")

    require(len(bom) == 85, "system BOM must contain 85 groups")
    require(len(panel_bom) == 34, "P0.6 panel BOM must remain 34 rows")
    require(len(cut_plan) == 7, "cut plan must contain seven planning segments")
    require(len(holds) == 12, "rail/duct package must retain 12 holds")
    require(len(sources) == 3, "source manifest must contain three Phoenix Contact rows")
    require(len(receiving) == 18, "receiving template must contain 18 rows")
    require(len(installation) == 16, "installation template must contain 16 rows")

    exact = {
        "BOM-083": ("Phoenix Contact", "NS 35/7,5 UNPERF 500MM; item 1207648", "2"),
        "BOM-084": ("Phoenix Contact", "CD 40X40; item 3240189", "1"),
        "BOM-085": ("Phoenix Contact", "CLIPFIX 35; item 3022218", "6"),
    }
    for item_id, values in exact.items():
        row = bom.get(item_id, {})
        require((row.get("manufacturer"), row.get("manufacturer_part_number"), row.get("quantity")) == values, f"{item_id} identity/quantity changed")
        require(row.get("baseline_status") == "exact_candidate_hold", f"{item_id} is not exact candidate hold")
        require(closure.get(item_id, {}).get("closure_class") == "exact_candidate_hold" and closure.get(item_id, {}).get("allowed_action") == "HOLD", f"{item_id} closure is not fail-closed")
    require(bom.get("BOM-059", {}).get("baseline_status") == "selection_required", "BOM-059 residual must remain selection required")
    require(closure.get("BOM-059", {}).get("closure_class") == "selection_required", "BOM-059 closure class changed")

    require(panel_bom.get("PAN-008", {}).get("manufacturer_part_number") == "1207648" and panel_bom.get("PAN-008", {}).get("quantity") == "2", "PAN-008 corrected rail identity/quantity changed")
    require(panel_bom.get("PAN-009", {}).get("manufacturer_part_number") == "3240189" and panel_bom.get("PAN-009", {}).get("quantity") == "1", "PAN-009 duct identity/quantity changed")
    require(panel_bom.get("PAN-006", {}).get("manufacturer_part_number") == "3022218" and panel_bom.get("PAN-006", {}).get("quantity") == "6", "PAN-006 end-bracket identity/quantity changed")
    require("DR4 deliberately excluded" in panel_bom.get("PAN-006", {}).get("description", ""), "DR4 CLIPFIX exclusion missing")

    for layout_id in ("BP-004", "BP-014", "BP-017", "BP-021"):
        require("1207648" in layout.get(layout_id, {}).get("mounting_basis", ""), f"{layout_id} lacks corrected unperforated rail")
    require("no CLIPFIX allocation" in layout.get("BP-021", {}).get("mounting_basis", ""), "DR4 end-retention hold missing")

    by_stock: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in cut_plan:
        by_stock[row["stock_id"]].append(row)
        require(row["warning"] == WARNING, f"{row['cut_id']} warning changed")
        require(row["release_state"] == "HOLD - PLANNING LENGTH NOT CUT RELEASE", f"{row['cut_id']} became a cut release")
    expected_stock = {"RAIL-A": (500.0, 388.8), "RAIL-B": (500.0, 253.8), "DUCT-A": (2000.0, 1655.4)}
    for stock_id, (stock_length, expected_used) in expected_stock.items():
        group = by_stock.get(stock_id, [])
        require(group and all(float(row["stock_length_mm"]) == stock_length for row in group), f"{stock_id} stock length changed")
        used = sum(float(row["planning_cut_length_mm"]) for row in group)
        require(abs(used - expected_used) < 1e-9 and used < stock_length, f"{stock_id} planning allocation changed or exceeds stock")
    for row in cut_plan:
        if row["manufacturer_item"] == "1207648":
            require(float(row["planning_cut_length_mm"]) > 20.0, f"{row['reference']} violates published unperforated minimum")

    require(all(row["warning"] == WARNING and row["current_state"] in {"OPEN", "SELECTION REQUIRED"} for row in holds), "hold warning/state changed")
    for name, group in (("receiving", receiving), ("installation", installation)):
        require(all(row["state"] == "NOT_EXECUTED" and row["authorization"] == "NOT_AUTHORIZED" for row in group), f"{name} contains executed/authorized evidence")
        require(all(not row["actual"] and not row["evidence_hash"] and row["warning"] == WARNING for row in group), f"{name} contains invented evidence or warning change")

    for gate_id in ("EG-003", "EG-006", "EG-010", "EG-015", "EG-016", "EG-018"):
        require(gates.get(gate_id, {}).get("status") == "partial", f"{gate_id} must remain partial")
        require("check_hr_v0_panel_rail_duct_p01.py" in gates.get(gate_id, {}).get("evidence_location", ""), f"{gate_id} evidence path lacks R123 checker")
    electrical = next((item for item in metadata.get("current_products", []) if item.get("domain") == "electrical"), {})
    require("HR-V0-PANEL-RD-P0.1" in electrical.get("supporting_identifiers", []), "release metadata lacks R123 identifier")

    combined = doc + guide + "\n".join(str(value) for row in cut_plan + holds + sources + receiving + installation for value in row.values())
    for token in ("HR-V0-PANEL-RD-P0.1", "1207648", "3240189", "3022218", "642.6", "1655.4", "DR4", "SELECTION REQUIRED", "NOT_EXECUTED", "NOT_AUTHORIZED", "not an order quantity"):
        require(token.lower() in combined.lower(), f"controlled token missing: {token}")
    require("font:16px" in guide and "font-size:14px" in guide and "font-size:12px" in guide, "guide text floors are not explicit")
    require("data-mode=\"receiving\"" in guide and "data-mode=\"fabrication\"" in guide and "data-mode=\"installation\"" in guide, "interactive guide filters missing")

    if failures:
        raise SystemExit("HR-V0 panel rail/duct P0.1 check failed:\n- " + "\n- ".join(failures))
    print("HR-V0 panel rail/duct P0.1 check passed: 85 BOM groups, 7 planning cuts, 12 holds, 3 primary sources, 18 blank receiving rows and 16 blank installation rows")
    print("BOM-059 and DR4 end retention remain SELECTION REQUIRED; no cut, drill, assembly, connection or energization authorization exists")
    print(WARNING)


if __name__ == "__main__":
    main()
