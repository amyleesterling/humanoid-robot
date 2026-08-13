#!/usr/bin/env python3
from __future__ import annotations
import csv,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/"mechanical/analysis/hr-v0-j2-c07-pe-constrained-curving-prereg-p0.1";RELEASE=ROOT/"release/hr-v0/j2-c07-pe-constrained-curving-prereg-p0.1";GEN=ROOT/"tools/generate_hr_v0_j2_c07_pe_constrained_curving_prereg_p01.py";R300=ROOT/"mechanical/analysis/hr-v0-j2-c07-pe-seam-free-jacobian-mesh-p0.1";R305=ROOT/"mechanical/analysis/hr-v0-j2-c07-pe-rail-jacobian-disposition-p0.1"
def sha(p:Path)->str:return hashlib.sha256(p.read_bytes()).hexdigest()
def fail(m:str)->None:raise SystemExit(f"R306 prereg check failed: {m}")
def main()->int:
    required={"README.md","acceptance-register.csv","analysis-status.json","execution-provenance.json","file-manifest.csv","frozen-constrained-curving-protocol.json","index.html"}
    if {p.name for p in OUT.iterdir()}!=required or {p.name for p in RELEASE.iterdir()}!=required:fail("file set")
    with (OUT/"file-manifest.csv").open(newline="",encoding="utf-8") as f:manifest=list(csv.DictReader(f))
    if {r["relative_path"] for r in manifest}!=required-{"file-manifest.csv"}:fail("manifest")
    for r in manifest:
        p=OUT/r["relative_path"]
        if sha(p)!=r["sha256"] or p.stat().st_size!=int(r["bytes"]):fail(f"manifest {p.name}")
    for n in required:
        if sha(OUT/n)!=sha(RELEASE/n):fail(f"mirror {n}")
    s=json.loads((OUT/"analysis-status.json").read_text());p=json.loads((OUT/"execution-provenance.json").read_text())
    if p["generator_sha256"]!=sha(GEN) or s["r300_status_sha256"]!=sha(R300/"analysis-status.json") or s["r305_status_sha256"]!=sha(R305/"analysis-status.json"):fail("binding")
    if s["operation"]!={"gmsh_method":"HighOrder","force":False,"niter":1,"dim_tags":"C07-MATRIX volume only","corner_mapping_tolerance_mm":0.1,"corner_restore_tolerance_mm":1e-12,"restore_every_pre-operation_linear_corner":True,"retain_optimized_midsides":True}:fail("operation")
    for key in ("mesh_executed","exact_facet_revalidation_executed","structural_solution_executed","r279_c02_complete","r278_h02_closed","capacity_credit","selected","safety_credit","work_authority"):
        if s[key] is not False:fail(key)
    html=(OUT/"index.html").read_text()
    if "font:17px" not in html or "font-size:16px" not in html or "overflow:auto" not in html:fail("legibility")
    print("PASS: R306 constrained HighOrder candidate preregistered once; mesh/facet/structural/H02/capacity/all authority open");return 0
if __name__=="__main__":raise SystemExit(main())
