#!/usr/bin/env python3
from __future__ import annotations
import csv,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/"mechanical/analysis/hr-v0-j2-c07-pe-cad-curving-prereg-p0.1";RELEASE=ROOT/"release/hr-v0/j2-c07-pe-cad-curving-prereg-p0.1";GEN=ROOT/"tools/generate_hr_v0_j2_c07_pe_cad_curving_prereg_p01.py";R297=ROOT/"mechanical/analysis/hr-v0-j2-c07-pe-seam-free-partition-p0.1";R300=ROOT/"mechanical/analysis/hr-v0-j2-c07-pe-seam-free-jacobian-mesh-p0.1";R306=ROOT/"mechanical/analysis/hr-v0-j2-c07-pe-constrained-curving-mesh-p0.1"
def sha(p:Path)->str:return hashlib.sha256(p.read_bytes()).hexdigest()
def fail(m:str)->None:raise SystemExit(f"R307 prereg check failed: {m}")
def main()->int:
    required={"README.md","acceptance-register.csv","analysis-status.json","execution-provenance.json","file-manifest.csv","frozen-cad-curving-protocol.json","index.html"}
    if {p.name for p in OUT.iterdir()}!=required or {p.name for p in RELEASE.iterdir()}!=required:fail("file set")
    with (OUT/"file-manifest.csv").open(newline="",encoding="utf-8") as f:m=list(csv.DictReader(f))
    if {r["relative_path"] for r in m}!=required-{"file-manifest.csv"}:fail("manifest")
    for r in m:
        p=OUT/r["relative_path"]
        if sha(p)!=r["sha256"] or p.stat().st_size!=int(r["bytes"]):fail(f"manifest {p.name}")
    for n in required:
        if sha(OUT/n)!=sha(RELEASE/n):fail(f"mirror {n}")
    s=json.loads((OUT/"analysis-status.json").read_text());p=json.loads((OUT/"execution-provenance.json").read_text())
    if p["generator_sha256"]!=sha(GEN) or s["source_analysis_brep_sha256"]!=sha(R297/"c07-pe-seam-free-analysis-partition.brep") or s["source_r300_status_sha256"]!=sha(R300/"analysis-status.json") or s["source_r306_status_sha256"]!=sha(R306/"analysis-status.json"):fail("binding")
    if s["physical_geometry_change"] is not False or "live R297 OCC" not in " ".join(s["execution_sequence"]):fail("method")
    for key in ("execution_started","execution_completed","exact_facet_revalidation_executed","full_reference_domain_curved_jacobian_positive","r279_c02_complete","structural_solution_executed","mesh_convergence_complete","r278_h02_closed","capacity_credit","selected","safety_credit","work_authority"):
        if s[key] is not False:fail(key)
    html=(OUT/"index.html").read_text()
    if "font:17px" not in html or "font-size:16px" not in html or "overflow:auto" not in html:fail("legibility")
    print("PASS: R307 CAD-resident constrained-curving candidate frozen once; execution/facet/full-domain/R279-C02/structural/H02/capacity/all authority open");return 0
if __name__=="__main__":raise SystemExit(main())
