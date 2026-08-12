#!/usr/bin/env python3
"""Compile accepted R248 physical properties into a canonical downstream bundle."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import re
import sys
from pathlib import Path

EX_CONFIG = 78
WARNING = "PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION"
EXPECTED = {("CFG-MP-01","J2"),("CFG-MP-02","J1"),("CFG-MP-03","J1"),("CFG-MP-03","J2"),("CFG-MP-04","J1"),("CFG-MP-04","J2")}
HASH = re.compile(r"^[0-9a-f]{64}$")


def number(row, key, *, positive=False):
    try: value=float(row[key])
    except (KeyError,TypeError,ValueError): raise ValueError(f"{row.get('configuration_id','?')}/{row.get('axis','?')}: missing numeric {key}")
    if not math.isfinite(value) or (value<=0 if positive else value<0): raise ValueError(f"{row.get('configuration_id','?')}/{row.get('axis','?')}: invalid {key}")
    return value


def compile_rows(rows, source_sha256):
    keyed={(r.get("configuration_id",""),r.get("axis","")):r for r in rows}
    if set(keyed)!=EXPECTED or len(rows)!=6: raise ValueError("exact six configuration/axis rows required")
    per_config={}
    canonical=[]
    for key in sorted(EXPECTED):
        row=keyed[key]
        if row.get("execution_state")!="EXECUTED" or row.get("acceptance")!="ACCEPTED": raise ValueError(f"{key}: not EXECUTED and ACCEPTED")
        config_hash=row.get("configuration_hash","").lower(); evidence_hash=row.get("measurement_manifest_sha256","").lower()
        if not HASH.fullmatch(config_hash) or not HASH.fullmatch(evidence_hash): raise ValueError(f"{key}: invalid configuration or evidence hash")
        if key[0] in per_config and per_config[key[0]]!=config_hash: raise ValueError(f"{key[0]}: axis rows use different configuration hashes")
        per_config[key[0]]=config_hash
        for field in ("accepted_by","acceptance_record_uri"):
            if not row.get(field,"").strip(): raise ValueError(f"{key}: missing {field}")
        values={
            "mass_kg":number(row,"accepted_mass_kg",positive=True),
            "expanded_uncertainty_mass_kg":number(row,"expanded_uncertainty_mass_kg"),
            "com_radius_m":number(row,"accepted_com_radius_m"),
            "expanded_uncertainty_com_radius_m":number(row,"expanded_uncertainty_com_radius_m"),
            "inertia_kg_m2":number(row,"accepted_inertia_kg_m2",positive=True),
            "expanded_uncertainty_inertia_kg_m2":number(row,"expanded_uncertainty_inertia_kg_m2"),
        }
        canonical.append({"configuration_id":key[0],"axis":key[1],"configuration_hash":config_hash,"measurement_manifest_sha256":evidence_hash,**values,"accepted_by":row["accepted_by"],"acceptance_record_uri":row["acceptance_record_uri"]})
    return {"schema":"hr-v0-accepted-moving-properties-v1","identifier":"HR-V0-ACCEPTED-PROP-BUNDLE-P0.1","source_contract":"HR-V0-MOVING-PROP-CLOSURE-P0.1","source_csv_sha256":source_sha256,"state":"ACCEPTED PHYSICAL PROPERTIES ONLY - DOWNSTREAM ANALYSES NOT YET ACCEPTED","properties":canonical,"procurement_authorized":False,"fabrication_authorized":False,"assembly_authorized":False,"connection_authorized":False,"powered_testing_authorized":False,"motion_authorized":False,"energization_authorized":False,"safety_credit":False,"warning":WARNING}


def main():
    parser=argparse.ArgumentParser(); parser.add_argument("input",type=Path); parser.add_argument("--output",type=Path)
    args=parser.parse_args()
    try:
        raw=args.input.read_bytes()
        with args.input.open(encoding="utf-8-sig",newline="") as handle: rows=list(csv.DictReader(handle))
        bundle=compile_rows(rows,hashlib.sha256(raw).hexdigest())
    except (OSError,ValueError) as exc:
        print(f"ACCEPTED PROPERTY BUNDLE NOT AVAILABLE: {exc}",file=sys.stderr); return EX_CONFIG
    text=json.dumps(bundle,indent=2,sort_keys=True)+"\n"
    if args.output: args.output.write_text(text,encoding="utf-8",newline="\n")
    else: print(text,end="")
    return 0


if __name__=="__main__": raise SystemExit(main())
