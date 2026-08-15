#!/usr/bin/env python3
"""Synchronize R241 gate/configuration metadata without promoting authority."""
from __future__ import annotations
import csv, json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
GATES=ROOT/"requirements/hr-v0-energization-gates.csv"
CANDIDATE=ROOT/"release/hr-v0/release-candidate.json"
FRAGMENT="docs/hr-v0-p121-segregation-hardware-p0.1.md; electrical/routing/hr-v0-p121-segregation-hardware-p0.1/; release/hr-v0/p121-segregation-hardware-p0.1/; configuration/hr-v0-config-reconciliation-p0.5/; requirements/hr-v0-gate-evidence-supplement-r241.csv; tools/check_hr_v0_p121_segregation_hardware_p01.py"

def insert_after(values,anchor,additions):
    position=values.index(anchor)+1
    for value in additions:
        if value not in values: values.insert(position,value);position+=1

def main():
    with GATES.open(encoding="utf-8-sig",newline="") as h:
        reader=csv.DictReader(h); rows=list(reader); fields=list(reader.fieldnames or [])
    targets={"EG-002","EG-003","EG-004","EG-012","EG-018","EG-020","EG-022"}; touched=set()
    for row in rows:
        if row["gate_id"] in targets:
            if row["status"]!="partial":raise SystemExit(f"R241 may not promote {row['gate_id']}")
            if FRAGMENT not in row["evidence_location"]:row["evidence_location"]+="; "+FRAGMENT
            touched.add(row["gate_id"])
    if touched!=targets:raise SystemExit("R241 gate set incomplete")
    with GATES.open("w",encoding="utf-8",newline="") as h:
        writer=csv.DictWriter(h,fieldnames=fields,lineterminator="\n");writer.writeheader();writer.writerows(rows)
    candidate=json.loads(CANDIDATE.read_text(encoding="utf-8")); products=candidate["current_products"]
    electrical=next(p for p in products if p["domain"]=="electrical")
    insert_after(electrical["supporting_identifiers"],"HR-V0-P121-ROUTING-P0.1",["HR-V0-P121-SEGREGATION-HW-P0.1","HR-V0-CONFIG-REC-P0.5"])
    electrical["release_state"]="p115_current_p118_p119_p120_p121_unaccepted_r241_exact_duct_candidate_junction_conductor_fill_physical_qualified_and_authority_open"
    electrical["configuration_reconciliation"]="HR-V0-CONFIG-REC-P0.5"
    electrical["p121_segregation_hardware_dossier"]="HR-V0-P121-SEGREGATION-HW-P0.1"
    electrical["p121_segregation_hardware_summary"]="Phoenix Contact 3240187 exact 25 x 25 x 2000 mm planning candidate; 369.8 mm WD5 envelope; 7 logical conductors; junction, fill, physical and qualified evidence open; no safety credit or route release"
    bill=next(p for p in products if p["domain"]=="bill_of_materials")
    insert_after(bill["supporting_identifiers"],"HR-V0-CONFIG-REC-P0.4",["HR-V0-P121-SEGREGATION-HW-P0.1","HR-V0-CONFIG-REC-P0.5"])
    bill["release_state"]="r241_96_group_bom_with_exact_duct_candidate_held_and_lot_a_purchase_blocker_no_complete_machine_procurement_release"
    bill["system_group_count"]=96;bill["configuration_reconciliation"]="HR-V0-CONFIG-REC-P0.5";bill["p121_segregation_hardware"]="HR-V0-P121-SEGREGATION-HW-P0.1"
    assembly=next(p for p in products if p["domain"]=="assembly")
    insert_after(assembly["supporting_identifiers"],"HR-V0-CONFIG-REC-P0.4",["HR-V0-CONFIG-REC-P0.5"])
    CANDIDATE.write_text(json.dumps(candidate,indent=2)+"\n",encoding="utf-8",newline="\n")
    print("R241 synchronized: seven gates remain partial; 96 BOM groups; P1.15 current; P1.21 unaccepted; no work authority")
if __name__=="__main__":main()
