#!/usr/bin/env python3
"""Preregister the exact R308 facet/B-Rep/load evaluation of R307."""
from __future__ import annotations
import csv,hashlib,json,shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
R307=ROOT/"mechanical/analysis/hr-v0-j2-c07-pe-cad-curving-mesh-p0.1";R307_PROTOCOL=ROOT/"mechanical/analysis/hr-v0-j2-c07-pe-cad-curving-prereg-p0.1/frozen-cad-curving-protocol.json"
EVALUATOR=ROOT/"tools/generate_hr_v0_j2_c07_brep_facet_load_p01.py";EXECUTOR=ROOT/"tools/generate_hr_v0_j2_c07_pe_cad_curving_facet_p01.py"
OUT=ROOT/"mechanical/analysis/hr-v0-j2-c07-pe-cad-curving-facet-prereg-p0.1";RELEASE=ROOT/"release/hr-v0/j2-c07-pe-cad-curving-facet-prereg-p0.1"
IDENT="HR-V0-J2-C07-PE-CAD-CURVING-FACET-PREREG-P0.1";WARNING="PRELIMINARY - R307 EXACT FACET/B-REP/LOAD REVALIDATION PREREGISTRATION ONLY - NOT APPROVED FOR PROCUREMENT, QUOTATION, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION"
def sha(path:Path)->str:return hashlib.sha256(path.read_bytes()).hexdigest()
def write_csv(path:Path,rows:list[dict[str,object]])->None:
    fields=[]
    for row in rows:
        for field in row:
            if field not in fields:fields.append(field)
    with path.open("w",newline="",encoding="utf-8") as stream:w=csv.DictWriter(stream,fieldnames=fields,lineterminator="\n");w.writeheader();w.writerows(rows)
def main()->int:
    status=json.loads((R307/"analysis-status.json").read_text(encoding="utf-8"));source_protocol=json.loads(R307_PROTOCOL.read_text(encoding="utf-8"))
    if not status["sampled_cad_curving_candidate_pass"] or status["exact_facet_revalidation_executed"]:raise RuntimeError("R307 source state")
    if OUT.exists():shutil.rmtree(OUT)
    OUT.mkdir(parents=True)
    protocol={"identifier":IDENT,"round":"R308-PREREG","date":"2026-08-13","candidate_id":"R308-C07-R307-EXACT-FACET-BREP-LOAD-V01","source_r307_status_sha256":sha(R307/"analysis-status.json"),"source_r307_raw_linear_sha256":sha(R307/"raw-linear-mesh.npz"),"source_r307_raw_tet10_sha256":sha(R307/"raw-tet10-mesh.npz"),"source_r307_protocol_sha256":sha(R307_PROTOCOL),"transitive_evaluator_sha256":sha(EVALUATOR),"executor_sha256":sha(EXECUTOR),"execution":"one evaluation only; no mesh, geometry, tolerance, clipping, quadrature, load or threshold tuning","acceptance":source_protocol["acceptance"],"exact_facet_revalidation_executed":False,"r279_c02_complete":False,"structural_solution_executed":False,"r278_h02_closed":False,"capacity_credit":False,"safety_credit":False,"work_authority":False,"warning":WARNING}
    (OUT/"frozen-protocol.json").write_text(json.dumps(protocol,indent=2)+"\n",encoding="utf-8")
    (OUT/"analysis-status.json").write_text(json.dumps(protocol,indent=2)+"\n",encoding="utf-8")
    (OUT/"README.md").write_text(f"# {IDENT}\n\n**{WARNING}**\n\nR308 freezes one exact exterior-facet/B-Rep/load evaluation of the retained R307 candidate. It does not remesh or alter CAD. Passing this gate still does not prove full-reference-domain positivity, structural convergence, capacity, physical validation, or work authority.\n",encoding="utf-8")
    manifest=[]
    for path in sorted(OUT.iterdir()):manifest.append({"relative_path":path.name,"sha256":sha(path),"bytes":path.stat().st_size,"warning":WARNING})
    write_csv(OUT/"file-manifest.csv",manifest)
    if RELEASE.exists():shutil.rmtree(RELEASE)
    RELEASE.parent.mkdir(parents=True,exist_ok=True);shutil.copytree(OUT,RELEASE);print(json.dumps(protocol,indent=2));return 0
if __name__=="__main__":raise SystemExit(main())
