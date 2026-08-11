#!/usr/bin/env python3
"""Synchronize R223 panel placement/configuration evidence without promoting gates."""

from __future__ import annotations

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GATES = ROOT / "requirements/hr-v0-energization-gates.csv"
CANDIDATE = ROOT / "release/hr-v0/release-candidate.json"
FRAGMENT = "docs/hr-v0-panel-node-placement-p0.1.md; electrical/panel/hr-v0-control-panel-p0.7-node-placement/; release/hr-v0/panel-node-placement-p0.1/; configuration/hr-v0-config-reconciliation-p0.4/; requirements/hr-v0-gate-evidence-supplement-r223.csv; tools/check_hr_v0_panel_node_placement_p01.py"


def insert_after(values: list[str], anchor: str, additions: list[str]) -> None:
    position = values.index(anchor) + 1
    for value in additions:
        if value not in values:
            values.insert(position, value)
            position += 1


def main() -> int:
    with GATES.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        gate_rows, fields = list(reader), list(reader.fieldnames or [])
    targets = {"EG-002", "EG-003", "EG-004", "EG-010", "EG-014", "EG-015", "EG-018", "EG-020"}
    touched = set()
    for row in gate_rows:
        if row["gate_id"] in targets:
            if row["status"] != "partial":
                raise SystemExit(f"R223 may not promote {row['gate_id']}")
            if FRAGMENT not in row["evidence_location"]:
                row["evidence_location"] += "; " + FRAGMENT
            touched.add(row["gate_id"])
    if touched != targets:
        raise SystemExit("R223 gate set incomplete")
    with GATES.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(gate_rows)

    candidate = json.loads(CANDIDATE.read_text(encoding="utf-8"))
    electrical = next(item for item in candidate["current_products"] if item["domain"] == "electrical")
    insert_after(electrical["supporting_identifiers"], "HR-V0-PANEL-P2P-P0.1", ["HR-V0-PANEL-NODE-PLACEMENT-P0.1", "HR-V0-CONFIG-REC-P0.4"])
    electrical["control_panel_node_placement_candidate"] = "HR-V0-PANEL-NODE-PLACEMENT-P0.1"
    electrical["configuration_reconciliation"] = "HR-V0-CONFIG-REC-P0.4"
    electrical["release_state"] = "p115_current_p118_topology_unaccepted_r223_nodes_placed_catalog_only_lengths_terminations_protection_physical_evidence_and_work_authority_absent"
    bill = next(item for item in candidate["current_products"] if item["domain"] == "bill_of_materials")
    insert_after(bill["supporting_identifiers"], "HR-V0-CONFIG-REC-P0.3", ["HR-V0-PANEL-NODE-PLACEMENT-P0.1", "HR-V0-CONFIG-REC-P0.4"])
    bill["system_group_count"] = 95
    bill["configuration_reconciliation"] = "HR-V0-CONFIG-REC-P0.4"
    bill["release_state"] = "95_group_covered_bom_with_r223_panel_nodes_and_accessory_hold_no_complete_machine_procurement_release"
    assembly = next(item for item in candidate["current_products"] if item["domain"] == "assembly")
    insert_after(assembly["supporting_identifiers"], "HR-V0-CONFIG-REC-P0.3", ["HR-V0-CONFIG-REC-P0.4"])
    CANDIDATE.write_text(json.dumps(candidate, indent=2) + "\n", encoding="utf-8", newline="\n")
    print("R223 synchronized; eight gates remain partial; P1.15 remains current; zero physical/work authority")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
