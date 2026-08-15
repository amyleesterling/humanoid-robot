#!/usr/bin/env python3
from __future__ import annotations
import csv,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/"mechanical/analysis/hr-v0-j2-c07-pe-rail-jacobian-prereg-p0.1";RELEASE=ROOT/"release/hr-v0/j2-c07-pe-rail-jacobian-prereg-p0.1";GEN=ROOT/"tools/generate_hr_v0_j2_c07_pe_rail_jacobian_prereg_p01.py";R297=ROOT/"mechanical/analysis/hr-v0-j2-c07-pe-seam-free-partition-p0.1/c07-pe-seam-free-analysis-partition.brep";R300=ROOT/"mechanical/analysis/hr-v0-j2-c07-pe-seam-free-jacobian-mesh-p0.1";R301=ROOT/"mechanical/analysis/hr-v0-j2-c07-pe-seam-free-jacobian-failure-localization-p0.1"
WARNING="PRELIMINARY - RAIL-TRANSITION JACOBIAN SUCCESSOR PREREGISTRATION ONLY - NOT APPROVED FOR PROCUREMENT, QUOTATION, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION"
def sha(p:Path)->str:return hashlib.sha256(p.read_bytes()).hexdigest()
def fail(m:str)->None:raise SystemExit(f"R302 prereg check failed: {m}")
def rows(n:str):
    with (OUT/n).open(newline="",encoding="utf-8") as s:return list(csv.DictReader(s))
def main()->int:
    required={"README.md","analysis-status.json","exact-rail-transition-target-register.csv","execution-provenance.json","file-manifest.csv","frozen-rail-jacobian-protocol.json","index.html"}
    if {p.name for p in OUT.iterdir()}!=required or {p.name for p in RELEASE.iterdir()}!=required:fail("file set")
    manifest=rows("file-manifest.csv")
    if {r["relative_path"] for r in manifest}!=required-{"file-manifest.csv"}:fail("manifest")
    for r in manifest:
        p=OUT/r["relative_path"]
        if sha(p)!=r["sha256"] or p.stat().st_size!=int(r["bytes"]):fail(f"manifest {p.name}")
    for n in required:
        if sha(OUT/n)!=sha(RELEASE/n):fail(f"mirror {n}")
    p=json.loads((OUT/"frozen-rail-jacobian-protocol.json").read_text(encoding="utf-8"));s=json.loads((OUT/"analysis-status.json").read_text(encoding="utf-8"));v=json.loads((OUT/"execution-provenance.json").read_text(encoding="utf-8"));targets=rows("exact-rail-transition-target-register.csv")
    if p["candidate_id"]!="R302-C07-PE-RAIL-JACOBIAN-V01" or len(targets)!=2 or len({r["geometric_signature_sha256"] for r in targets})!=2 or p["symmetry_closed_face_count"]!=2 or p["symmetry_rule"]!="X mirror only; candidate Z mirrors were enumerated and do not exist in the exact R297 topology":fail("targets")
    if p["r297_analysis_brep_sha256"]!=sha(R297) or p["r300_current_status_sha256"]!=sha(R300/"analysis-status.json") or p["r301_status_sha256"]!=sha(R301/"analysis-status.json") or v["generator_sha256"]!=sha(GEN):fail("provenance")
    for key in ("mesh_executed","structural_solution_executed","r279_c02_complete","r278_h02_closed","capacity_credit","selected","safety_credit","work_authority"):
        if p[key] is not False or s[key] is not False:fail(f"fail-closed {key}")
    h=(OUT/"index.html").read_text(encoding="utf-8")
    if "font:17px" not in h or "font-size:16px" not in h or "overflow:auto" not in h or WARNING not in h:fail("guide legibility/warning")
    print("PASS: R302 two-face X-mirrored rail-transition successor frozen; interactive guide legible; mesh/structural/H02/capacity/all authority open");return 0
if __name__=="__main__":raise SystemExit(main())
