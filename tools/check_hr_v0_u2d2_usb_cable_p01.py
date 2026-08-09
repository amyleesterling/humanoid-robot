#!/usr/bin/env python3
"""Fail-closed consistency checks for HR-V0-U2D2-USB-P0.1."""

from __future__ import annotations

import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WARNING = "PRELIMINARY - NOT APPROVED FOR FABRICATION OR ENERGIZATION"


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def main() -> None:
    failures: list[str] = []

    def require(condition: bool, message: str) -> None:
        if not condition:
            failures.append(message)

    interface = rows(ROOT / "electrical" / "interfaces" / "hr-v0-u2d2-usb-cable-p0.1.csv")
    trade = rows(ROOT / "electrical" / "interfaces" / "hr-v0-u2d2-usb-cable-trade-p0.1.csv")
    sources = rows(ROOT / "electrical" / "vendor" / "startech" / "usb2ac50cm-r122" / "source-manifest-p0.1.csv")
    receiving = rows(ROOT / "tests" / "forms" / "hr-v0-u2d2-usb-cable-receiving-template-p0.1.csv")
    tests = rows(ROOT / "tests" / "forms" / "hr-v0-u2d2-usb-cable-test-template-p0.1.csv")
    bom = {row["item_id"]: row for row in rows(ROOT / "bom" / "bom.csv")}
    closure = {row["item_id"]: row for row in rows(ROOT / "bom" / "hr-v0-bom-closure.csv")}
    panel = rows(ROOT / "electrical" / "panel" / "hr-v0-control-panel-p0.6" / "panel-bom.csv")
    layout = {row["layout_id"]: row for row in rows(ROOT / "electrical" / "panel" / "hr-v0-control-panel-p0.6" / "backplate-layout.csv")}
    holds = {row["hold_id"]: row for row in rows(ROOT / "electrical" / "panel" / "hr-v0-control-panel-p0.6" / "compute-installation-holds.csv")}
    thermal = {row["screen_id"]: row for row in rows(ROOT / "electrical" / "panel" / "hr-v0-control-panel-p0.6" / "thermal-space-screen.csv")}
    gates = {row["gate_id"]: row for row in rows(ROOT / "requirements" / "hr-v0-energization-gates.csv")}
    metadata = json.loads((ROOT / "release" / "hr-v0" / "release-candidate.json").read_text(encoding="utf-8"))
    doc = (ROOT / "docs" / "hr-v0-u2d2-usb-cable-p0.1.md").read_text(encoding="utf-8")
    guide = (ROOT / "release" / "hr-v0" / "u2d2-usb-cable-p0.1" / "index.html").read_text(encoding="utf-8")

    require(len(interface) == 14, "interface register must contain 14 rows")
    require(len(trade) == 4, "trade register must contain 4 rows")
    require(len(sources) == 4, "source manifest must contain 4 primary-source rows")
    require(len(receiving) == 18, "receiving template must contain 18 rows")
    require(len(tests) == 16, "test template must contain 16 rows")
    require(len(panel) == 34, "P0.6 panel BOM must contain 34 rows")

    cable = bom.get("BOM-070", {})
    require(cable.get("manufacturer") == "StarTech.com", "BOM-070 manufacturer changed")
    require(cable.get("manufacturer_part_number") == "USB2AC50CM", "BOM-070 exact candidate changed")
    require(cable.get("baseline_status") == "exact_candidate_hold", "BOM-070 is not an exact candidate hold")
    require(closure.get("BOM-070", {}).get("closure_class") == "exact_candidate_hold", "BOM-070 closure class changed")
    require(closure.get("BOM-070", {}).get("allowed_action") == "HOLD", "BOM-070 action must remain HOLD")

    panel_cable = next((row for row in panel if row["item_id"] == "PAN-034"), {})
    require(panel_cable.get("reference") == "PI-U2D2-CABLE", "PAN-034 reference changed")
    require(panel_cable.get("manufacturer_part_number") == "USB2AC50CM", "PAN-034 exact identity changed")
    require(layout.get("BP-025", {}).get("reference") == "PI-U2D2-CABLE/GTM3", "BP-025 cable route changed")
    require("USB2AC50CM" in layout.get("BP-025", {}).get("mounting_basis", ""), "BP-025 lacks exact cable candidate")
    require(holds.get("CIH-010", {}).get("current_state") == "OPEN", "CIH-010 must remain an open physical/electrical hold")
    require("no received fit route retention electrical EMC thermal or application credit" in thermal.get("TS-015", {}).get("result", ""), "TS-015 fail-closed result changed")

    for group_name, group in (("interface", interface), ("trade", trade), ("sources", sources)):
        require(all(row.get("warning") == WARNING for row in group), f"{group_name} warning changed")
    for name, group in (("receiving", receiving), ("tests", tests)):
        require(all(row.get("state") == "NOT_EXECUTED" and row.get("authorization") == "NOT_AUTHORIZED" for row in group), f"{name} contains executed or authorized evidence")
        require(all(not row.get("actual") and not row.get("evidence_hash") for row in group), f"{name} contains invented result evidence")
        require(all(row.get("warning") == WARNING for row in group), f"{name} warning changed")

    require(any(row["stage"] == "POWERED_E1" for row in tests), "powered tests are not explicitly separated into E1")
    require(all(row["authorization"] == "NOT_AUTHORIZED" for row in tests if row["stage"] == "POWERED_E1"), "a powered cable test became authorized")
    require(any("no minimum bend radius" in row["limitations"] for row in sources), "unpublished bend limit caveat missing")
    require(any(row["candidate"] == "StarTech.com USB2AC50CM" and row["disposition"] == "PREFERRED EXACT CANDIDATE HOLD" for row in trade), "preferred trade candidate missing")

    for gate_id in ("EG-003", "EG-010", "EG-015", "EG-016", "EG-017"):
        require(gates.get(gate_id, {}).get("status") == "partial", f"{gate_id} must remain partial")
        require("check_hr_v0_u2d2_usb_cable_p01.py" in gates.get(gate_id, {}).get("evidence_location", ""), f"{gate_id} evidence path lacks R122 checker")

    electrical = next((item for item in metadata.get("current_products", []) if item.get("domain") == "electrical"), {})
    require("HR-V0-U2D2-USB-P0.1" in electrical.get("supporting_identifiers", []), "release metadata lacks R122 identifier")
    combined = doc + guide + "\n".join(str(value) for row in interface + trade + sources + receiving + tests for value in row.values())
    for token in ("HR-V0-U2D2-USB-P0.1", "USB2AC50CM", "0.5 m", "480 Mbps", "3.5 mm", "22/30 AWG", "aluminum-mylar foil with braid", "0 to 35", "NOT_EXECUTED", "NOT_AUTHORIZED", "zero functional-safety credit", "no-backfeed", "common-mode"):
        require(token.lower() in combined.lower(), f"controlled token missing: {token}")
    require("font:16px" in guide and "font-size:14px" in guide and "font-size:12px" in guide, "guide text floors are not explicit")
    require("data-mode=\"physical\"" in guide and "data-mode=\"electrical\"" in guide and "data-mode=\"controls\"" in guide, "interactive evidence filters missing")

    if failures:
        raise SystemExit("HR-V0 U2D2 USB cable P0.1 check failed:\n- " + "\n- ".join(failures))
    print("HR-V0 U2D2 USB cable P0.1 check passed: 14 interface rows, 4 trade rows, 4 primary sources, 18 blank receiving rows and 16 blank test rows")
    print("BOM-070 is an exact candidate hold only; EG-003/010/015/016/017 remain PARTIAL and all powered tests remain NOT_AUTHORIZED")
    print(WARNING)


if __name__ == "__main__":
    main()
