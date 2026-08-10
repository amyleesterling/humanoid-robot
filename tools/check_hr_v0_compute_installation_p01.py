#!/usr/bin/env python3
"""Fail-closed consistency checks for HR-V0-COMPUTE-INSTALL-P0.1 / HR-V0-CP-P0.6."""

from __future__ import annotations

import csv
import json
import xml.etree.ElementTree as ET
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

    layout = rows(PANEL / "backplate-layout.csv")
    panel_bom = rows(PANEL / "panel-bom.csv")
    thermal = rows(PANEL / "thermal-space-screen.csv")
    holds = rows(PANEL / "compute-installation-holds.csv")
    receiving = rows(ROOT / "tests" / "forms" / "hr-v0-compute-installation-receiving-template-p0.1.csv")
    system_bom = {row["item_id"]: row for row in rows(ROOT / "bom" / "bom.csv")}
    closure = {row["item_id"]: row for row in rows(ROOT / "bom" / "hr-v0-bom-closure.csv")}
    gates = {row["gate_id"]: row for row in rows(ROOT / "requirements" / "hr-v0-energization-gates.csv")}
    metadata = json.loads((ROOT / "release" / "hr-v0" / "release-candidate.json").read_text(encoding="utf-8"))
    doc = (ROOT / "docs" / "hr-v0-control-panel-p0.6.md").read_text(encoding="utf-8")
    guide = (ROOT / "release" / "hr-v0" / "compute-installation-p0.1" / "index.html").read_text(encoding="utf-8")

    require(len(layout) == 26, "P0.6 layout must contain 26 planning envelopes")
    require(len(panel_bom) == 34, "P0.6 panel BOM must contain 34 rows after R122 cable hold")
    require(len(thermal) == 15, "thermal/space screen must contain 15 rows")
    require(len(holds) == 16, "compute installation must retain 16 explicit holds")
    require(len(receiving) == 20, "receiving template must contain 20 rows")

    boundary = next((row for row in layout if row["layout_id"] == "BP-001"), {})
    require(boundary.get("reference") == "BP1" and boundary.get("width_mm") == "533.4" and boundary.get("height_mm") == "685.8", "18P2721 boundary changed")
    max_x = float(boundary.get("width_mm", 0))
    max_y = float(boundary.get("height_mm", 0))
    for row in layout:
        x, y = float(row["x_mm"]), float(row["y_mm"])
        width, height = float(row["width_mm"]), float(row["height_mm"])
        require(x >= 0 and y >= 0 and x + width <= max_x + 1e-9 and y + height <= max_y + 1e-9, f"{row['layout_id']} leaves nominal panel boundary")
        require(row["warning"] == WARNING, f"{row['layout_id']} warning changed")

    by_ref = {row["reference"]: row for row in layout}
    require(by_ref.get("CCASE1", {}).get("width_mm") == "90.5" and by_ref.get("CCASE1", {}).get("height_mm") == "87", "PI5-CASE-D plan envelope changed")
    require(float(by_ref["CCASE1"]["x_mm"]) > 423.8, "compute case crossed WD2 segregation boundary")
    require(by_ref.get("U2D2/GTM1", {}).get("width_mm") == "63.5", "U2D2 retention base envelope changed")
    require({"DR4", "CCASE1", "U2D2/GTM1", "PSU3-CABLE/GTM2", "PI-U2D2-CABLE/GTM3", "OPEN-LOWER-ZONE"}.issubset(by_ref), "compute/reserve allocations missing")

    parts = {row["reference"]: row for row in panel_bom}
    expected = {
        "ENC1": "PJ302410RT", "BP1": "18P2721", "CCASE1": "PI5-CASE-D; SKU 26087",
        "PI1": "SC1112", "COOL1": "SC1148", "U2D2": "902-0132-000",
        "GTM1/GTM2/GTM3": "GTM500C2; article 130-95000",
        "GT1/GT2/GT3": "GT.50X80C2; article 854-44353", "PSU3": "SC1158",
        "PI-U2D2-CABLE": "USB2AC50CM",
    }
    for ref, part_number in expected.items():
        require(parts.get(ref, {}).get("manufacturer_part_number") == part_number, f"{ref} exact candidate identity changed")
    require(all(row["warning"] == WARNING for row in panel_bom + thermal + holds), "panel warning changed")
    require(all(row["state"] == "NOT_EXECUTED" and row["authorization"] == "NOT_AUTHORIZED" and not row["actual"] and not row["evidence_hash"] for row in receiving), "receiving template contains executed or authorized evidence")

    expected_bom = {
        "BOM-058": "PJ302410RT enclosure plus 18P2721 white-steel inner panel",
        "BOM-080": "PI5-CASE-D; SKU 26087",
        "BOM-081": "GTM500C2; article 130-95000",
        "BOM-082": "GT.50X80C2; article 854-44353",
    }
    for item_id, part_number in expected_bom.items():
        require(system_bom.get(item_id, {}).get("manufacturer_part_number") == part_number, f"{item_id} system BOM identity changed")
        require(closure.get(item_id, {}).get("closure_class") == "exact_candidate_hold" and closure.get(item_id, {}).get("allowed_action") == "HOLD", f"{item_id} is not a fail-closed exact candidate")
    require(system_bom.get("BOM-070", {}).get("manufacturer_part_number") == "USB2AC50CM", "BOM-070 exact cable identity changed")
    require(system_bom.get("BOM-070", {}).get("baseline_status") == "exact_candidate_hold", "BOM-070 must remain an exact candidate hold")
    require(closure.get("BOM-070", {}).get("closure_class") == "exact_candidate_hold" and closure.get("BOM-070", {}).get("allowed_action") == "HOLD", "BOM-070 closure must remain fail-closed")

    for gate_id in ("EG-003", "EG-010", "EG-017"):
        require(gates.get(gate_id, {}).get("status") == "partial", f"{gate_id} must remain partial")
        require("check_hr_v0_compute_installation_p01.py" in gates[gate_id]["evidence_location"], f"{gate_id} evidence is not synchronized")
    electrical = next((item for item in metadata.get("current_products", []) if item.get("domain") == "electrical"), {})
    require("HR-V0-CP-P0.6" in electrical.get("supporting_identifiers", []), "release metadata lacks P0.6")
    require("HR-V0-COMPUTE-INSTALL-P0.1" in electrical.get("supporting_identifiers", []), "release metadata lacks compute-install identifier")

    try:
        ET.parse(PANEL / "panel-layout.svg")
    except Exception as exc:  # pragma: no cover - diagnostic path
        failures.append(f"panel-layout.svg does not parse: {exc}")
    combined = doc + guide + "\n".join(str(value) for row in panel_bom + thermal + holds + receiving for value in row.values())
    for token in ("HR-V0-CP-P0.6", "HR-V0-COMPUTE-INSTALL-P0.1", "PJ302410RT", "18P2721", "PI5-CASE-D", "26087", "902-0132-000", "GTM500C2", "854-44353", "BOM-070", "SELECTION REQUIRED", "NOT_EXECUTED", "NOT_AUTHORIZED", "zero functional-safety credit"):
        require(token.lower() in combined.lower(), f"required controlled token missing: {token}")
    require("font:16px" in guide and "font-size:14px" in guide and "font-size:12px" in guide, "guide text floors are not explicit")
    require("data-mode=\"compute\"" in guide and "data-mode=\"holds\"" in guide, "guide filters missing")

    if failures:
        raise SystemExit("HR-V0 compute-installation check failed:\n- " + "\n- ".join(failures))
    print("HR-V0 compute-installation P0.1 check passed: 26 bounded planning envelopes, 34 panel BOM rows, 16 fail-closed holds and 20 unexecuted receiving rows")
    print("BOM-070 is an exact held cable candidate only; EG-003, EG-010 and EG-017 remain PARTIAL")
    print(WARNING)


if __name__ == "__main__":
    main()
