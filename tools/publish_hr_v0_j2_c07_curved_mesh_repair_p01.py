#!/usr/bin/env python3
"""Publish bounded R283 C07 curved-mesh repair evidence."""
from __future__ import annotations
import csv,hashlib,json,shutil,sys
from pathlib import Path
import gmsh,numpy,scipy,skfem
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/"mechanical/analysis/hr-v0-j2-c07-curved-mesh-repair-p0.1";REL=ROOT/"release/hr-v0/j2-c07-curved-mesh-repair-p0.1"
IDENT="HR-V0-J2-C07-CURVED-MESH-REPAIR-P0.1";WARNING="PRELIMINARY - CURVED MESH METHOD EVIDENCE ONLY - NOT APPROVED FOR PROCUREMENT, QUOTATION, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION"
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def rows(p):
    with p.open(newline="",encoding="utf-8-sig") as s:return list(csv.DictReader(s))
def write_csv(p,rec):
    with p.open("w",newline="",encoding="utf-8") as s:w=csv.DictWriter(s,fieldnames=list(rec[0]),lineterminator="\n");w.writeheader();w.writerows(rec)
def manifest(d):
    rec=[{"relative_path":p.relative_to(d).as_posix(),"sha256":sha(p),"bytes":p.stat().st_size,"warning":WARNING} for p in sorted(d.rglob("*")) if p.is_file() and p.name!="file-manifest.csv"];write_csv(d/"file-manifest.csv",rec)
def main():
    tool=ROOT/"tools/generate_hr_v0_j2_c07_curved_mesh_repair_p01.py";base=ROOT/"tools/generate_hr_v0_j2_stop_refinement_execution_p01.py";step=ROOT/"cad/hr-v0/generated/arm-architecture-p0.13-pad-pocket-stop/parts/MV0-C07_J2_positive_fixed_catch_adapter.step"
    write_csv(OUT/"runtime-input-register.csv",[{"input":"baseline commit","value":"d36bb8d5979364c9fcf5a46101fcf79500c61f99","sha256":"N/A","warning":WARNING},{"input":step.relative_to(ROOT).as_posix(),"value":"exact STEP identity","sha256":sha(step),"warning":WARNING},{"input":tool.relative_to(ROOT).as_posix(),"value":"R283 generator","sha256":sha(tool),"warning":WARNING},{"input":base.relative_to(ROOT).as_posix(),"value":"shared OCC entity/local-field source","sha256":sha(base),"warning":WARNING},{"input":"Python runtime","value":sys.version.replace("\n"," "),"sha256":"N/A","warning":WARNING},{"input":"gmsh/numpy/scipy/skfem","value":f"{gmsh.__version__}/{numpy.__version__}/{scipy.__version__}/{skfem.__version__}","sha256":"N/A","warning":WARNING}])
    variants=rows(OUT/"variant-register.csv");attempts=rows(OUT/"failed-attempt-register.csv");passed=[r for r in variants if r["mesh_repair_pass"].lower()=="true"]
    status=json.loads((OUT/"analysis-status.json").read_text(encoding="utf-8"));status.update({"identifier":IDENT,"round":"R283","attempts_executed":len(variants),"failed_attempts":len(attempts),"promoted_variants":len(passed),"bounded_mesh_method_route_found":bool(passed),"geometry_preserving_curved_mesh_route_found":False,"v04_numerical_screen_observation":"linear SICN, curved determinant, element connectivity/orientation and OCC corner-membership screens pass; unique 1e-9 mm spatial corner bijection fails at 0.0863831 mm; no promotion","normalized_determinant_gate_scope":"1e-10 pre-registered bounded nonzero/conditioning floor; not R279-C02 or capacity","surface_deviation_from_brep_complete":False,"exact_facet_map_complete":False,"r279_c02_complete":False,"r278_h02_closed":False,"selected":False,"safety_credit":False,"capacity_credit":False,"work_authority":False});(OUT/"analysis-status.json").write_text(json.dumps(status,indent=2)+"\n",encoding="utf-8")
    (OUT/"README.md").write_text(f"# {IDENT}\n\n> **{WARNING}**\n\nR283 reruns V04 against the exact STEP SHA with retained raw evidence. Linear SICN, Q4/Q6/Q8 curved determinant, element connectivity/orientation and OCC corner-membership screens pass. The frozen unique 1e-9 mm spatial corner bijection fails: maximum nearest-corner displacement is 0.0863831 mm. V04 is rejected and no bounded route is promoted. This is not R279-C02, H02, capacity, selection, safety credit, or work authority.\n",encoding="utf-8")
    manifest(OUT)
    if REL.exists():shutil.rmtree(REL)
    shutil.copytree(OUT,REL);manifest(REL);print(json.dumps(status,indent=2));return 0
if __name__=="__main__":raise SystemExit(main())
