#!/usr/bin/env python3
"""Synchronize R243 BOM, closure, gate and release metadata fail-closed."""
from __future__ import annotations

import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BOM = ROOT / "bom/bom.csv"
CLOSURE = ROOT / "bom/hr-v0-bom-closure.csv"
GATES = ROOT / "requirements/hr-v0-energization-gates.csv"
CANDIDATE = ROOT / "release/hr-v0/release-candidate.json"
FRAGMENT = "docs/hr-v0-p121-termination-p0.1.md; electrical/termination/hr-v0-p121-termination-p0.1/; release/hr-v0/p121-termination-p0.1/; configuration/hr-v0-config-reconciliation-p0.7/; requirements/hr-v0-gate-evidence-supplement-r243.csv; tools/check_hr_v0_p121_termination_p01.py"


def read(path: Path):
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        return list(reader), list(reader.fieldnames or [])


def write(path: Path, rows, fields) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def insert_after(values: list[str], anchor: str, additions: list[str]) -> None:
    position = values.index(anchor) + 1
    for value in additions:
        if value not in values:
            values.insert(position, value)
            position += 1


def main() -> None:
    bom, fields = read(BOM)
    if not any(row["item_id"] == "BOM-098" for row in bom):
        bom.append({
            "item_id":"BOM-098", "subsystem":"panel_p121_ferrule_materials", "manufacturer":"Phoenix Contact",
            "manufacturer_part_number":"AI 1,5 - 8 BK item 3200043, minimum pack 100; A 1,5 - 7 item 3200263, minimum pack 1000",
            "quantity":"2", "baseline_status":"exact_candidate_hold",
            "selection_basis":"R243 maps twelve item 3200043 insulated 8 mm ferrules to XD24/KWD endpoints and two item 3200263 uninsulated 7 mm ferrules to Pilz SR1/SRA1 A1 endpoints. Application quantities are not manufacturer order quantities. Terminal application acceptance, exact torque bits, tool calibration, received Belden/ferrule coupons, 40 N for 60 s pull evidence, installed retention/torque/continuity/isolation and qualified review remain open. No procurement, wiring, connection or energization is authorized",
        })
    if len(bom) != 98 or bom[-1]["item_id"] != "BOM-098":
        raise SystemExit("R243 BOM must contain 98 ordered groups ending at BOM-098")
    write(BOM, bom, fields)

    closure, fields = read(CLOSURE)
    if not any(row["item_id"] == "BOM-098" for row in closure):
        closure.append({
            "item_id":"BOM-098", "closure_class":"exact_candidate_hold", "order_code_state":"EXACT CANDIDATE",
            "quantity_state":"CANDIDATE QUANTITY ONLY", "primary_source_state":"CURRENT PRIMARY SOURCE RECORDED",
            "application_state":"SELECTION REQUIRED", "allowed_action":"HOLD",
            "closure_basis":"R243 controls exact two-format ferrule material candidates for fourteen P1.21 endpoints. Application quantities, order packs and primary tool candidates are explicit. Terminal application, exact bits, calibration, received coupons, pull/retention/torque, continuity/isolation, color convention, P1.21 acceptance and qualified release remain open. No procurement, assembly, wiring, connection or energization authority.",
        })
    if len(closure) != 98 or closure[-1]["item_id"] != "BOM-098":
        raise SystemExit("R243 closure register must contain 98 ordered groups ending at BOM-098")
    write(CLOSURE, closure, fields)

    gates, fields = read(GATES)
    targets = {"EG-002","EG-003","EG-004","EG-012","EG-015","EG-018","EG-020","EG-022"}
    touched = set()
    for row in gates:
        if row["gate_id"] in targets:
            if row["status"] != "partial":
                raise SystemExit(f"R243 may not promote {row['gate_id']}")
            if FRAGMENT not in row["evidence_location"]:
                row["evidence_location"] += "; " + FRAGMENT
            touched.add(row["gate_id"])
    if touched != targets:
        raise SystemExit("R243 gate set incomplete")
    write(GATES, gates, fields)

    candidate = json.loads(CANDIDATE.read_text(encoding="utf-8"))
    products = candidate["current_products"]
    electrical = next(product for product in products if product["domain"] == "electrical")
    insert_after(electrical["supporting_identifiers"], "HR-V0-CONFIG-REC-P0.6", ["HR-V0-P121-TERM-P0.1", "HR-V0-CONFIG-REC-P0.7"])
    electrical["release_state"] = "p115_current_p121_unaccepted_r243_exact_termination_candidates_only_received_application_calibration_physical_qualified_and_authority_open"
    electrical["configuration_reconciliation"] = "HR-V0-CONFIG-REC-P0.7"
    electrical["p121_termination_dossier"] = "HR-V0-P121-TERM-P0.1"
    electrical["p121_termination_summary"] = "14 endpoint candidates: 12 Phoenix 3200043 insulated 8 mm and 2 Phoenix 3200263 uninsulated 7 mm; exact primary tools held; received qualification, exact bits, installed evidence and acceptance open"
    bill = next(product for product in products if product["domain"] == "bill_of_materials")
    insert_after(bill["supporting_identifiers"], "HR-V0-CONFIG-REC-P0.6", ["HR-V0-P121-TERM-P0.1", "HR-V0-CONFIG-REC-P0.7"])
    bill["release_state"] = "r243_98_group_bom_with_exact_p121_ferrule_candidates_held_and_lot_a_purchase_blocker_no_complete_machine_procurement_release"
    bill["system_group_count"] = 98
    bill["configuration_reconciliation"] = "HR-V0-CONFIG-REC-P0.7"
    bill["p121_termination"] = "HR-V0-P121-TERM-P0.1"
    assembly = next(product for product in products if product["domain"] == "assembly")
    insert_after(assembly["supporting_identifiers"], "HR-V0-CONFIG-REC-P0.6", ["HR-V0-CONFIG-REC-P0.7"])
    CANDIDATE.write_text(json.dumps(candidate, indent=2) + "\n", encoding="utf-8", newline="\n")
    print("R243 synchronized: eight gates remain partial; 98 BOM groups; P1.15 current; P1.21 unaccepted; no work authority")


if __name__ == "__main__":
    main()
