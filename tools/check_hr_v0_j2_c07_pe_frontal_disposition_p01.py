#!/usr/bin/env python3
"""Check R296 disposition and the seam-free analysis-partition boundary."""
from __future__ import annotations
import csv,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/"mechanical/analysis/hr-v0-j2-c07-pe-frontal-disposition-p0.1";RELEASE=ROOT/"release/hr-v0/j2-c07-pe-frontal-disposition-p0.1";GEN=ROOT/"tools/generate_hr_v0_j2_c07_pe_frontal_disposition_p01.py"
WARNING="PRELIMINARY - FRONTAL TETRAHEDRALIZATION DISPOSITION ONLY - NOT APPROVED FOR PROCUREMENT, QUOTATION, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION"
def sha(p:Path)->str:return hashlib.sha256(p.read_bytes()).hexdigest()
def fail(m:str)->None:raise SystemExit(f"R296 disposition check failed: {m}")
def rows(name:str)->list[dict[str,str]]:
    with (OUT/name).open(newline="",encoding="utf-8") as s:return list(csv.DictReader(s))
def main()->int:
    required={"README.md","analysis-status.json","execution-provenance.json","file-manifest.csv","next-partition-boundary.json","pe-subzone-disposition.csv","r289-r295-method-comparison.csv"}
    if {p.name for p in OUT.iterdir()}!=required or {p.name for p in RELEASE.iterdir()}!=required:fail("file set")
    manifest=rows("file-manifest.csv")
    for r in manifest:
        p=OUT/r["relative_path"]
        if sha(p)!=r["sha256"] or p.stat().st_size!=int(r["bytes"]) or r["warning"]!=WARNING:fail(f"manifest {p.name}")
    if {r["relative_path"] for r in manifest}!=required-{"file-manifest.csv"}:fail("manifest membership")
    for n in required:
        if sha(OUT/n)!=sha(RELEASE/n):fail(f"mirror {n}")
    st=json.loads((OUT/"analysis-status.json").read_text(encoding="utf-8"));b=json.loads((OUT/"next-partition-boundary.json").read_text(encoding="utf-8"));p=json.loads((OUT/"execution-provenance.json").read_text(encoding="utf-8"))
    if p["generator_sha256"]!=sha(GEN):fail("generator")
    comp=rows("r289-r295-method-comparison.csv");zones=rows("pe-subzone-disposition.csv")
    if [r["run"] for r in comp]!=["R289","R291","R293","R295"] or any(int(r["failed_straight_zones"])!=4 for r in comp):fail("method invariance")
    if sum(r["kind"]=="STRAIGHT" and r["r295_gate"]=="FAIL" for r in zones)!=4 or sum(r["kind"]=="R2" and r["r295_gate"]=="PASS" for r in zones)!=4:fail("PE pattern")
    if b["physical_geometry_changed"] or not b["analysis_partition_internal_seams_changed"] or "fuse only the eight internal" not in b["required_next_analysis_partition"]:fail("partition boundary")
    for key in ("next_partition_executed","next_mesh_executed","structural_solution_executed","r279_c02_complete","r278_h02_closed","capacity_credit","selected","safety_credit","work_authority"):
        if st[key] is not False or b[key] is not False:fail(f"fail-closed {key}")
    print("PASS: R296 proves algorithm-invariant PE seam defect and freezes a seam-free analysis-only partition; physical CAD unchanged; mesh/structural/H02/capacity/all authority open");return 0
if __name__=="__main__":raise SystemExit(main())
