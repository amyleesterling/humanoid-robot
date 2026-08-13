#!/usr/bin/env python3
"""Normalize and manifest the already executed R307 numerical evidence."""
from __future__ import annotations
import csv, hashlib, json, shutil
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"mechanical/analysis/hr-v0-j2-c07-pe-cad-curving-mesh-p0.1"
RELEASE=ROOT/"release/hr-v0/j2-c07-pe-cad-curving-mesh-p0.1"
EXECUTOR=ROOT/"tools/generate_hr_v0_j2_c07_pe_cad_curving_mesh_p01.py"
IDENT="HR-V0-J2-C07-PE-CAD-CURVING-MESH-P0.1"
WARNING="PRELIMINARY - CAD-RESIDENT CONSTRAINED CURVING EVIDENCE ONLY - NOT APPROVED FOR PROCUREMENT, QUOTATION, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION"

def sha(path:Path)->str:return hashlib.sha256(path.read_bytes()).hexdigest()
def write_csv(path:Path,rows:list[dict[str,object]])->None:
    fields=[]
    for row in rows:
        for field in row:
            if field not in fields:fields.append(field)
    with path.open("w",newline="",encoding="utf-8") as stream:
        writer=csv.DictWriter(stream,fieldnames=fields,lineterminator="\n");writer.writeheader();writer.writerows(rows)

def main()->int:
    status_path=OUT/"analysis-status.json";status=json.loads(status_path.read_text(encoding="utf-8"))
    if not status["sampled_cad_curving_candidate_pass"] or status["exact_facet_revalidation_executed"]:
        raise RuntimeError("R307 numerical evidence state")
    status["high_order_optimizer"]="HighOrder"
    status["optimizer_scope"]="C07-MATRIX volume only; force=false; niter=1"
    status["publisher_sha256"]=sha(Path(__file__).resolve())
    status["warning"]=WARNING
    status_path.write_text(json.dumps(status,indent=2)+"\n",encoding="utf-8")
    provenance_path=OUT/"execution-provenance.json";provenance=json.loads(provenance_path.read_text(encoding="utf-8"))
    if provenance["generator_sha256"]!=sha(EXECUTOR):raise RuntimeError("execution generator drift")
    provenance["high_order_optimizer"]="HighOrder"
    provenance["publisher_path"]=Path(__file__).resolve().relative_to(ROOT).as_posix()
    provenance["publisher_sha256"]=sha(Path(__file__).resolve())
    provenance["warning"]=WARNING
    provenance_path.write_text(json.dumps(provenance,indent=2)+"\n",encoding="utf-8")
    manifest=[]
    for path in sorted(OUT.iterdir()):
        if path.is_file() and path.name!="file-manifest.csv":manifest.append({"relative_path":path.name,"sha256":sha(path),"bytes":path.stat().st_size,"warning":WARNING})
    write_csv(OUT/"file-manifest.csv",manifest)
    if RELEASE.exists():shutil.rmtree(RELEASE)
    RELEASE.parent.mkdir(parents=True,exist_ok=True);shutil.copytree(OUT,RELEASE)
    print(json.dumps(status,indent=2));return 0
if __name__=="__main__":raise SystemExit(main())
