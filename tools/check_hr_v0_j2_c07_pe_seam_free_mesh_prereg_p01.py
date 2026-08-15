#!/usr/bin/env python3
from __future__ import annotations
import csv,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/"mechanical/analysis/hr-v0-j2-c07-pe-seam-free-mesh-prereg-p0.1";RELEASE=ROOT/"release/hr-v0/j2-c07-pe-seam-free-mesh-prereg-p0.1";GEN=ROOT/"tools/generate_hr_v0_j2_c07_pe_seam_free_mesh_prereg_p01.py";R297=ROOT/"mechanical/analysis/hr-v0-j2-c07-pe-seam-free-partition-p0.1"
WARNING="PRELIMINARY - SEAM-FREE PE MESH PREREGISTRATION ONLY - NOT APPROVED FOR PROCUREMENT, QUOTATION, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION"
def sha(p:Path)->str:return hashlib.sha256(p.read_bytes()).hexdigest()
def fail(m:str)->None:raise SystemExit(f"R298 prereg check failed: {m}")
def rows(n:str):
    with (OUT/n).open(newline="",encoding="utf-8") as s:return list(csv.DictReader(s))
def main()->int:
    required={"README.md","analysis-status.json","exact-face-target-register.csv","execution-provenance.json","file-manifest.csv","frozen-seam-free-mesh-protocol.json"}
    if {p.name for p in OUT.iterdir()}!=required or {p.name for p in RELEASE.iterdir()}!=required:fail("file set")
    for r in rows("file-manifest.csv"):
        p=OUT/r["relative_path"]
        if sha(p)!=r["sha256"] or p.stat().st_size!=int(r["bytes"]):fail(f"manifest {p.name}")
    for n in required:
        if sha(OUT/n)!=sha(RELEASE/n):fail(f"mirror {n}")
    p=json.loads((OUT/"frozen-seam-free-mesh-protocol.json").read_text(encoding="utf-8"));s=json.loads((OUT/"analysis-status.json").read_text(encoding="utf-8"));v=json.loads((OUT/"execution-provenance.json").read_text(encoding="utf-8"))
    if p["candidate_id"]!="R298-C07-PE-SEAM-FREE-V01" or p["linear_mesh_method"]["algorithm3d"]!=4 or p["linear_mesh_method"]["optimizer_sequence"]!=["Netgen"]:fail("method")
    if p["r297_analysis_brep_sha256"]!=sha(R297/"c07-pe-seam-free-analysis-partition.brep") or p["r297_status_sha256"]!=sha(R297/"analysis-status.json") or v["generator_sha256"]!=sha(GEN):fail("provenance")
    if len(rows("exact-face-target-register.csv"))!=6:fail("face targets")
    for key in ("mesh_executed","structural_solution_executed","r279_c02_complete","r278_h02_closed","capacity_credit","selected","safety_credit","work_authority"):
        if p[key] is not False or s[key] is not False:fail(f"fail-closed {key}")
    print("PASS: R298 seam-free mesh candidate frozen before execution; physical CAD and thresholds unchanged; mesh/structural/H02/capacity/all authority open");return 0
if __name__=="__main__":raise SystemExit(main())
