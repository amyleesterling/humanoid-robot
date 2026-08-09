#!/usr/bin/env python3
"""Fail-closed consistency checks for HR-V0-COMPUTE-SEL-P0.1."""

from __future__ import annotations

import csv
import json
from pathlib import Path

from generate_hr_v0_electrical_v3 import REV, sheets

ROOT = Path(__file__).resolve().parents[1]
WARNING = "PRELIMINARY - NOT APPROVED FOR PROCUREMENT FABRICATION OR ENERGIZATION"


def read_csv(relative: str) -> list[dict[str, str]]:
    with (ROOT / relative).open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def main() -> None:
    failures: list[str] = []

    def require(condition: bool, message: str) -> None:
        if not condition:
            failures.append(message)

    sources = read_csv("electrical/vendor/raspberry-pi/compute-r119/source-manifest-p0.1.csv")
    selection = read_csv("bom/hr-v0-compute-selection-p0.1.csv")
    interfaces = read_csv("electrical/interfaces/hr-v0-compute-power-selection-p0.1.csv")
    receiving = read_csv("tests/forms/hr-v0-compute-receiving-template-p0.1.csv")
    bom = {row["item_id"]: row for row in read_csv("bom/bom.csv")}
    closure = {row["item_id"]: row for row in read_csv("bom/hr-v0-bom-closure.csv")}
    gates = {row["gate_id"]: row for row in read_csv("requirements/hr-v0-energization-gates.csv")}
    guide = (ROOT / "release/hr-v0/compute-selection-p0.1/index.html").read_text(encoding="utf-8")
    doc = (ROOT / "docs/hr-v0-compute-selection-p0.1.md").read_text(encoding="utf-8")
    metadata = json.loads((ROOT / "release/hr-v0/release-candidate.json").read_text(encoding="utf-8"))
    components = {component.ref: component for sheet in sheets() for component in sheet.components}

    require(REV == "V3-P1.14", "current electrical revision is not V3-P1.14")
    require(len(sources) == 7 and len(selection) == 2 and len(interfaces) == 12 and len(receiving) == 16, "controlled row counts changed")
    require({row["exact_candidate"] for row in selection} == {
        "Raspberry Pi 5 8GB RAM - Unit only; SC1112",
        "Raspberry Pi 27W USB-C Power Supply; US Type A; black; SC1158",
    }, "candidate identity set changed")
    require("SC1112" in bom.get("BOM-001", {}).get("manufacturer_part_number", "") and "SC1158" in bom.get("BOM-002", {}).get("manufacturer_part_number", ""), "system BOM identities are not synchronized")
    for item_id in ("BOM-001", "BOM-002"):
        row = closure.get(item_id, {})
        require(row.get("closure_class") == "exact_candidate_hold" and row.get("allowed_action") == "HOLD" and row.get("application_state") == "SELECTION REQUIRED", f"{item_id} is not fail-closed")
    require("SC1112" in components["PI1"].value and "SC1158" in components["PSU3"].value, "KiCad model identities are not synchronized")
    require(all(row.get("state") == "NOT_EXECUTED" and row.get("authorization") == "NOT_AUTHORIZED" and not row.get("actual") and not row.get("evidence_hash") for row in receiving), "receiving form contains an executed or authorized result")
    require(sum(row["state"] == "EXACT_CANDIDATE" for row in interfaces) == 2 and sum(row["state"] == "OPEN" for row in interfaces) == 9 and sum(row["state"] == "PARTIAL" for row in interfaces) == 1, "interface state counts changed")
    require(all(row.get("warning") == WARNING for row in sources + selection + interfaces + receiving), "warning missing from a controlled CSV row")
    require(gates.get("EG-003", {}).get("status") == "partial" and gates.get("EG-010", {}).get("status") == "partial", "compute work improperly closed an energization gate")
    require("hr-v0-compute-selection-p0.1.csv" in gates["EG-003"]["evidence_location"] and "hr-v0-compute-power-selection-p0.1.csv" in gates["EG-010"]["evidence_location"], "gate evidence is not synchronized")
    electrical = next((item for item in metadata.get("current_products", []) if item.get("domain") == "electrical"), {})
    require(electrical.get("identifier") == "Project Button Electrical V3-P1.14" and "HR-V0-COMPUTE-SEL-P0.1" in electrical.get("supporting_identifiers", []), "release metadata is not synchronized")
    combined = doc + guide + "\n".join(str(value) for row in sources + selection + interfaces + receiving for value in row.values())
    for token in ("SC1112", "SC1158", "zero functional-safety credit", "SELECTION REQUIRED", "NOT APPROVED", "NOT_EXECUTED", "NOT_AUTHORIZED"):
        require(token.lower() in combined.lower(), f"required fail-closed token missing: {token}")
    require("font-size:16px" in guide and "font-size:14px" in guide and "font-size:12px" in guide, "guide text floors are not explicit")

    if failures:
        raise SystemExit("HR-V0 compute selection check failed:\n- " + "\n- ".join(failures))
    print("HR-V0 compute selection check passed: SC1112 and SC1158 exact candidates; 12 interface records; 16 unexecuted receiving rows")
    print("EG-003 and EG-010 remain PARTIAL; no purchase, connection, test or energization authority")
    print(WARNING)


if __name__ == "__main__":
    main()
