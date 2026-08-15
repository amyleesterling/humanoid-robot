#!/usr/bin/env python3
"""Compare bounded C07 L0 mesh variants against the R279 quality gate."""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

import generate_hr_v0_j2_stop_refinement_execution_p01 as base


ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"mechanical/analysis/hr-v0-j2-c07-mesh-quality-p0.1"
IDENT="HR-V0-J2-C07-MESH-QUALITY-P0.1"
WARNING="PRELIMINARY - MESH QUALITY FEASIBILITY ONLY - NOT APPROVED FOR PROCUREMENT, QUOTATION, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION"
VARIANTS={
    "DELAUNAY_NETGEN":(1,"Netgen"),
    "DELAUNAY_RELOCATE":(1,"Relocate3D"),
    "FRONTAL_NETGEN":(4,"Netgen"),
    "HXT_NETGEN":(10,"Netgen"),
}


def rows(path:Path)->list[dict[str,str]]:
    if not path.exists():return []
    with path.open(newline="",encoding="utf-8-sig") as stream:return list(csv.DictReader(stream))


def write_csv(path:Path,records:list[dict[str,object]])->None:
    with path.open("w",newline="",encoding="utf-8") as stream:
        writer=csv.DictWriter(stream,fieldnames=list(records[0]),lineterminator="\n");writer.writeheader();writer.writerows(records)


def main()->int:
    parser=argparse.ArgumentParser();parser.add_argument("--variant",choices=tuple(VARIANTS),required=True);parser.add_argument("--reset",action="store_true");args=parser.parse_args()
    OUT.mkdir(parents=True,exist_ok=True);path=OUT/"mesh-quality-register.csv";records=[] if args.reset else rows(path)
    algorithm,optimize=VARIANTS[args.variant]
    _mesh,meta,_nodes,_samples,_entities=base.build_mesh("C07",base.LEVELS["L0"],algorithm3d=algorithm,optimize_method=optimize)
    quality_pass=float(meta["min_sicn"])>=0.10 and float(meta["fraction_sicn_below_0p20"])<=0.001
    record={"identifier":IDENT,"variant":args.variant,"algorithm3d":algorithm,"optimize_method":optimize,"vertices":meta["vertices"],"tetrahedra":meta["tetrahedra"],"minimum_sicn":meta["min_sicn"],"fraction_sicn_below_0p20":meta["fraction_sicn_below_0p20"],"mesh_seconds":meta["mesh_seconds"],"quality_gate":"PASS" if quality_pass else "FAIL","structural_solve_credit":"NONE","warning":WARNING}
    records=[r for r in records if r["variant"]!=args.variant];records.append(record);write_csv(path,records)
    status={"identifier":IDENT,"round":"R281-PROTOTYPE","variants_executed":sorted(r["variant"] for r in records),"passing_variants":sorted(r["variant"] for r in records if r["quality_gate"]=="PASS"),"mesh_quality_selection_complete":False,"structural_solve_complete":False,"r278_h02_closed":False,"selected":False,"fabrication_authorized":False,"powered_testing_authorized":False,"motion_authorized":False,"energization_authorized":False,"safety_credit":False,"warning":WARNING}
    (OUT/"analysis-status.json").write_text(json.dumps(status,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(record,indent=2));return 0


if __name__=="__main__":raise SystemExit(main())
