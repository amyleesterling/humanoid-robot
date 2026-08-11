#!/usr/bin/env python3
"""Synchronize R244 gate and release metadata fail-closed."""
from __future__ import annotations

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GATES = ROOT / "requirements/hr-v0-energization-gates.csv"
CANDIDATE = ROOT / "release/hr-v0/release-candidate.json"
IDENT = "HR-V0-P121-DCR-DROP-P0.1"
CFG = "HR-V0-CONFIG-REC-P0.8"
FRAGMENT = "docs/hr-v0-p121-dcr-drop-p0.1.md; electrical/routing/hr-v0-p121-dcr-drop-p0.1/; release/hr-v0/p121-dcr-drop-p0.1/; configuration/hr-v0-config-reconciliation-p0.8/; requirements/hr-v0-gate-evidence-supplement-r244.csv; tools/check_hr_v0_p121_dcr_drop_p01.py"

def read(path: Path):
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle); return list(reader), list(reader.fieldnames or [])

def write(path: Path, rows, fields):
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n"); writer.writeheader(); writer.writerows(rows)

def insert_after(values: list[str], anchor: str, additions: list[str]) -> None:
    position = values.index(anchor) + 1
    for value in additions:
        if value not in values: values.insert(position, value); position += 1

def main() -> None:
    gates, fields = read(GATES)
    targets = {"EG-002","EG-003","EG-004","EG-012","EG-015","EG-018","EG-020","EG-022"}; touched = set()
    for row in gates:
        if row["gate_id"] in targets:
            if row["status"] != "partial": raise SystemExit(f"R244 may not promote {row['gate_id']}")
            if FRAGMENT not in row["evidence_location"]: row["evidence_location"] += "; " + FRAGMENT
            touched.add(row["gate_id"])
    if touched != targets: raise SystemExit("R244 gate set incomplete")
    write(GATES, gates, fields)
    candidate = json.loads(CANDIDATE.read_text(encoding="utf-8")); products = candidate["current_products"]
    electrical = next(p for p in products if p["domain"] == "electrical")
    insert_after(electrical["supporting_identifiers"], "HR-V0-CONFIG-REC-P0.7", [IDENT, CFG])
    electrical["release_state"] = "p115_current_p121_unaccepted_r244_nominal_dcr_drop_and_bit_disposition_only_received_complete_circuit_physical_qualified_and_authority_open"
    electrical["configuration_reconciliation"] = CFG
    electrical["p121_dcr_drop_dossier"] = IDENT
    electrical["p121_dcr_drop_summary"] = "manufacturer-nominal 4.4 ohm/1000 ft at 20 C; four one-way centerline conductor-only numeric screens; received DCR/cuts/complete circuit and exact bits open"
    bill = next(p for p in products if p["domain"] == "bill_of_materials")
    insert_after(bill["supporting_identifiers"], "HR-V0-CONFIG-REC-P0.7", [CFG])
    bill["release_state"] = "r244_98_group_bom_unchanged_with_nominal_dcr_drop_evidence_exact_p121_ferrule_candidates_held_and_lot_a_purchase_blocker_no_complete_machine_procurement_release"
    bill["configuration_reconciliation"] = CFG
    assembly = next(p for p in products if p["domain"] == "assembly")
    insert_after(assembly["supporting_identifiers"], "HR-V0-CONFIG-REC-P0.7", [CFG])
    CANDIDATE.write_text(json.dumps(candidate, indent=2) + "\n", encoding="utf-8", newline="\n")
    print("R244 synchronized: eight gates remain partial; 98 BOM groups unchanged; P1.15 current; P1.21 unaccepted")

if __name__ == "__main__": main()
