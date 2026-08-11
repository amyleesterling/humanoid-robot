#!/usr/bin/env python3
"""Synchronize release-candidate metadata to the R212 observation configuration."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "release/hr-v0/release-candidate.json"


def replace_one(values: list[str], old: str, new: str) -> None:
    if values.count(old) != 1:
        raise SystemExit(f"Expected exactly one {old!r} in release metadata")
    values[values.index(old)] = new


def main() -> None:
    data = json.loads(PATH.read_text(encoding="utf-8"))
    products = {row["domain"]: row for row in data["current_products"]}
    electrical = products["electrical"]
    if electrical["identifier"] != "Project Button Electrical V3-P1.15-CARRIER-CANDIDATE":
        raise SystemExit("P1.15 direct core identity changed unexpectedly")
    support = electrical["supporting_identifiers"]
    replace_one(support, "HR-V0-CONFIG-REC-P0.1", "HR-V0-CONFIG-REC-P0.2")
    replace_one(support, "HR-V0-RUNTIME-OBS-CARRIER-P0.2", "HR-V0-RUNTIME-OBS-CARRIER-P0.5")
    insert_at = support.index("HR-V0-RUNTIME-OBS-CARRIER-P0.5")
    for identifier in reversed([
        "V3-P1.17-OBSERVATION-P0.5-CANDIDATE",
    ]):
        if identifier not in support:
            support.insert(insert_at, identifier)
    insert_after = support.index("HR-V0-RUNTIME-OBS-CARRIER-P0.5") + 1
    for identifier in [
        "HR-V0-PI-OBS-CARRIER-P0.1",
        "HR-V0-OBSERVATION-FIELD-HARNESS-P0.1",
        "HR-V0-OBSERVATION-COMPUTE-HARNESS-P0.1",
    ]:
        if identifier not in support:
            support.insert(insert_after, identifier)
            insert_after += 1
    electrical["release_state"] = "carrier_integrated_p115_direct_core_with_parity_checked_p117_p05_observation_view_not_supplier_released_physical_evidence_absent"

    replace_one(products["bill_of_materials"]["supporting_identifiers"], "HR-V0-CONFIG-REC-P0.1", "HR-V0-CONFIG-REC-P0.2")
    replace_one(products["assembly"]["supporting_identifiers"], "HR-V0-CONFIG-REC-P0.1", "HR-V0-CONFIG-REC-P0.2")

    historical = data["historical_or_out_of_scope_products"]
    identifier = "V3-P1.16-OBSERVATION-CANDIDATE / HR-V0-RUNTIME-OBS-CARRIER-P0.2 through P0.4 / HR-V0-CONFIG-REC-P0.1"
    if not any(row.get("identifier") == identifier for row in historical):
        historical.append({
            "identifier": identifier,
            "disposition": "superseded observation and configuration candidates retained for audit; P1.17/P0.5/P0.2 reconciliation is current and remains unapproved for physical work",
        })
    PATH.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    print("Synchronized HR-V0-RC-P0.1 metadata to R212 observation configuration")
    print("PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION")


if __name__ == "__main__":
    main()
