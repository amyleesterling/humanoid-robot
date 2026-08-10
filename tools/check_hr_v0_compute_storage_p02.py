#!/usr/bin/env python3
"""Fail-closed checks for HR-V0-COMPUTE-STORAGE-P0.2."""

from __future__ import annotations

import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PART = "SDCIT2/64GBSP"
IDENTIFIER = "HR-V0-COMPUTE-STORAGE-P0.2"
WARNING = "PRELIMINARY - NOT APPROVED FOR PROCUREMENT INSTALLATION IMAGING CONNECTION POWERED TEST OR ENERGIZATION"


def read_csv(relative: str) -> list[dict[str, str]]:
    with (ROOT / relative).open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def main() -> None:
    failures: list[str] = []

    def require(condition: bool, message: str) -> None:
        if not condition:
            failures.append(message)

    sources = read_csv("electrical/vendor/kingston/storage-r170/source-manifest-p0.1.csv")
    candidate = read_csv("bom/hr-v0-compute-storage-p0.2.csv")
    interfaces = read_csv("electrical/interfaces/hr-v0-compute-storage-p0.2.csv")
    holds = read_csv("electrical/interfaces/hr-v0-compute-storage-holds-p0.2.csv")
    receiving = read_csv("tests/forms/hr-v0-compute-storage-receiving-template-p0.2.csv")
    supplement = read_csv("requirements/hr-v0-gate-evidence-supplement-r170.csv")
    bom = {row["item_id"]: row for row in read_csv("bom/bom.csv")}
    closure = {row["item_id"]: row for row in read_csv("bom/hr-v0-bom-closure.csv")}
    gates = {row["gate_id"]: row for row in read_csv("requirements/hr-v0-energization-gates.csv")}
    doc = (ROOT / "docs/hr-v0-compute-storage-p0.2.md").read_text(encoding="utf-8")
    guide = (ROOT / "release/hr-v0/compute-storage-p0.2/index.html").read_text(encoding="utf-8")
    metadata = json.loads((ROOT / "release/hr-v0/release-candidate.json").read_text(encoding="utf-8"))

    require(len(sources) == 3, "source manifest must contain three current primary records")
    require(len(candidate) == 1, "candidate register must contain one line")
    require(len(interfaces) == 13, "interface register must contain thirteen lines")
    require(len(holds) == 12, "hold register must contain twelve lines")
    require(len(receiving) == 10, "receiving template must contain ten lines")
    require(len(supplement) == 3 and {row["gate_id"] for row in supplement} == {"EG-002", "EG-003", "EG-017"}, "gate supplement changed")

    item = candidate[0]
    require(item["item_id"] == "BOM-064" and item["reference"] == "STORE1", "candidate is not bound to STORE1/BOM-064")
    require(item["manufacturer"] == "Kingston Technology" and item["part_number"] == PART, "exact Kingston identity changed")
    require(item["quantity"] == "1" and item["capacity"] == "64 GB", "candidate quantity or capacity changed")
    require(item["candidate_state"] == "EXACT_CANDIDATE" and item["application_state"] == "HOLD" and item["allowed_action"] == "HOLD", "candidate is not fail-closed")

    system_item = bom.get("BOM-064", {})
    require(system_item.get("manufacturer") == "Kingston Technology", "BOM-064 manufacturer is not synchronized")
    require(system_item.get("manufacturer_part_number") == PART, "BOM-064 exact part number is not synchronized")
    require(system_item.get("baseline_status") == "exact_candidate_hold", "BOM-064 baseline state is not an exact-candidate hold")
    require(closure.get("BOM-064", {}).get("closure_class") == "exact_candidate_hold", "BOM-064 closure class is not exact_candidate_hold")
    require(closure.get("BOM-064", {}).get("allowed_action") == "HOLD", "BOM-064 improperly authorizes action")

    kingston = next((row for row in sources if row["source_id"] == "KNG170-SRC-001"), {})
    require(PART in kingston.get("controlled_fact", ""), "Kingston source does not control the exact part number")
    require("MKD-02122026" in kingston.get("revision_or_date", "") and "subject to change" in kingston.get("revision_or_date", ""), "Kingston source revision/boundary is incomplete")
    require("not allocated to the 64 GB part" in kingston.get("boundary", ""), "capacity-specific TBW boundary missing")
    require(any("RP-008348-DS-4" in row["revision_or_date"] for row in sources), "Raspberry Pi 5 source revision missing")

    require({row["state"] for row in interfaces} == {"EXACT_CANDIDATE", "PARTIAL", "OPEN", "PINNED_NOT_EXECUTED"}, "interface evidence states changed")
    require(sum(row["state"] == "EXACT_CANDIDATE" for row in interfaces) == 1, "exact interface count changed")
    require(sum(row["state"] == "OPEN" for row in interfaces) == 6, "open interface count changed")
    require(sum(row["state"] == "PARTIAL" for row in interfaces) == 5, "partial interface count changed")
    require(sum(row["state"] == "PINNED_NOT_EXECUTED" for row in interfaces) == 1, "pinned image boundary missing")
    require(all(row["current_state"] == "OPEN" for row in holds), "a physical/application hold is not open")
    require(all(row["authorization"] == "NOT_AUTHORIZED" and row["state"] == "NOT_EXECUTED" and not row["actual_result"] and not row["evidence_hash"] for row in receiving), "receiving template contains executed or authorized evidence")

    for gate_id in ("EG-002", "EG-003", "EG-005", "EG-010", "EG-017", "EG-021", "EG-022", "EG-027"):
        require(gates.get(gate_id, {}).get("status") in {"partial", "open"}, f"{gate_id} was improperly closed")
    require(all(row["disposition"] == "REMAINS PARTIAL" for row in supplement), "gate supplement improperly advances a gate")

    products = metadata.get("current_products", [])
    electrical = next((item for item in products if item.get("domain") == "electrical"), {})
    bill = next((item for item in products if item.get("domain") == "bill_of_materials"), {})
    require(IDENTIFIER in electrical.get("supporting_identifiers", []), "electrical metadata lacks storage identifier")
    require(IDENTIFIER in bill.get("supporting_identifiers", []), "BOM metadata lacks storage identifier")

    combined = doc + guide + "\n".join(str(value) for row in sources + candidate + interfaces + holds + receiving for value in row.values())
    for token in (PART, "64 GB", "power-failure protection", "30K P/E", "not approved", "zero functional-safety credit", "twelve holds"):
        require(token.lower() in combined.lower(), f"required token missing: {token}")
    require("3840 TBW" in combined and "not" in combined.lower(), "TBW non-allocation boundary missing")
    require("font:16px" in guide and "font-size:16px" in guide and "font-size:14px" in guide, "guide text floors are not explicit")
    require(guide.count("data-filter=") == 4 and guide.count("data-kind=") == 4, "guide filter/card structure changed")

    warnings = sources + candidate + interfaces + holds + receiving
    require(all(row["warning"] == WARNING for row in warnings), "controlled CSV warning missing or changed")

    if failures:
        raise SystemExit("HR-V0 compute-storage P0.2 check failed:\n- " + "\n- ".join(failures))
    print("HR-V0 compute-storage P0.2 check passed: exact Kingston 64 GB candidate, 13 interfaces, 12 open holds, 10 unexecuted receiving checks")
    print("BOM-064 remains HOLD; no media has been purchased, received, inserted, imaged, booted or power-loss tested")
    print(WARNING)


if __name__ == "__main__":
    main()
