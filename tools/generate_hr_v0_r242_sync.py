#!/usr/bin/env python3
"""Synchronize R242 BOM, gate and release metadata without promoting authority."""
from __future__ import annotations
import csv, json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
BOM=ROOT/"bom/bom.csv"
GATES=ROOT/"requirements/hr-v0-energization-gates.csv"
CANDIDATE=ROOT/"release/hr-v0/release-candidate.json"
FRAGMENT="docs/hr-v0-p121-conductor-fill-p0.1.md; electrical/routing/hr-v0-p121-conductor-fill-p0.1/; release/hr-v0/p121-conductor-fill-p0.1/; configuration/hr-v0-config-reconciliation-p0.6/; requirements/hr-v0-gate-evidence-supplement-r242.csv; tools/check_hr_v0_p121_conductor_fill_p01.py"

def read(path):
    with path.open(encoding="utf-8-sig",newline="") as h:
        reader=csv.DictReader(h); return list(reader),list(reader.fieldnames or [])
def write(path,rows,fields):
    with path.open("w",encoding="utf-8",newline="") as h:
        writer=csv.DictWriter(h,fieldnames=fields,lineterminator="\n");writer.writeheader();writer.writerows(rows)
def insert_after(values,anchor,additions):
    position=values.index(anchor)+1
    for value in additions:
        if value not in values:values.insert(position,value);position+=1

def main():
    bom,fields=read(BOM)
    if not any(r["item_id"]=="BOM-097" for r in bom):
        bom.append({
            "item_id":"BOM-097","subsystem":"panel_p121_stationary_control_conductor","manufacturer":"Belden",
            "manufacturer_part_number":"3057 BL005","quantity":"1","baseline_status":"exact_candidate_hold",
            "selection_basis":"R242 assigns one exact active 100 ft blue 16 AWG candidate reel to the seven stationary P1.21 WD5/WD2 conductors. The 6.72325 m route-centerline sum is geometry only. Qualified Boston/US color convention, the red XD24/blue XD0 identification conflict, received identity/DCR, cut lengths, ferrules/tools, strip/torque/pull, F24/fault coordination, complete WD2 occupancy, bend/junction, thermal, installed evidence and qualified review remain open. No procurement, cutting, wiring, connection or energization is authorized"
        })
    if len(bom)!=97 or bom[-1]["item_id"]!="BOM-097":raise SystemExit("R242 BOM must contain 97 ordered groups ending at BOM-097")
    write(BOM,bom,fields)

    gates,fields=read(GATES); targets={"EG-002","EG-003","EG-004","EG-010","EG-012","EG-015","EG-018","EG-020","EG-022"}; touched=set()
    for row in gates:
        if row["gate_id"] in targets:
            if row["status"]!="partial":raise SystemExit(f"R242 may not promote {row['gate_id']}")
            if FRAGMENT not in row["evidence_location"]:row["evidence_location"]+="; "+FRAGMENT
            touched.add(row["gate_id"])
    if touched!=targets:raise SystemExit("R242 gate set incomplete")
    write(GATES,gates,fields)

    candidate=json.loads(CANDIDATE.read_text(encoding="utf-8")); products=candidate["current_products"]
    electrical=next(p for p in products if p["domain"]=="electrical")
    insert_after(electrical["supporting_identifiers"],"HR-V0-CONFIG-REC-P0.5",["HR-V0-P121-CONDUCTOR-FILL-P0.1","HR-V0-CONFIG-REC-P0.6"])
    electrical["release_state"]="p115_current_p118_p119_p120_p121_unaccepted_r242_exact_conductor_candidate_geometry_fill_only_color_dcr_cut_protection_thermal_physical_qualified_and_authority_open"
    electrical["configuration_reconciliation"]="HR-V0-CONFIG-REC-P0.6"
    electrical["p121_conductor_fill_dossier"]="HR-V0-P121-CONDUCTOR-FILL-P0.1"
    electrical["p121_conductor_fill_summary"]="Belden 3057 BL005 exact held 16 AWG candidate for 7 routes; WD5 8.89 percent and WD2 enumerated maximum 2.66 percent geometry screens; total fill, color, DCR, cuts, protection, thermal, physical and qualified evidence open"
    bill=next(p for p in products if p["domain"]=="bill_of_materials")
    insert_after(bill["supporting_identifiers"],"HR-V0-CONFIG-REC-P0.5",["HR-V0-P121-CONDUCTOR-FILL-P0.1","HR-V0-CONFIG-REC-P0.6"])
    bill["release_state"]="r242_97_group_bom_with_exact_duct_and_p121_conductor_candidates_held_and_lot_a_purchase_blocker_no_complete_machine_procurement_release"
    bill["system_group_count"]=97;bill["configuration_reconciliation"]="HR-V0-CONFIG-REC-P0.6";bill["p121_conductor_fill"]="HR-V0-P121-CONDUCTOR-FILL-P0.1"
    assembly=next(p for p in products if p["domain"]=="assembly")
    insert_after(assembly["supporting_identifiers"],"HR-V0-CONFIG-REC-P0.5",["HR-V0-CONFIG-REC-P0.6"])
    CANDIDATE.write_text(json.dumps(candidate,indent=2)+"\n",encoding="utf-8",newline="\n")
    print("R242 synchronized: nine gates remain partial; 97 BOM groups; P1.15 current; P1.21 unaccepted; no work authority")
if __name__=="__main__":main()
