#!/usr/bin/env python3
from __future__ import annotations
import csv,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/"mechanical/analysis/hr-v0-j2-c07-pe-rail-jacobian-disposition-p0.1";RELEASE=ROOT/"release/hr-v0/j2-c07-pe-rail-jacobian-disposition-p0.1";GEN=ROOT/"tools/generate_hr_v0_j2_c07_pe_rail_jacobian_disposition_p01.py";R300=ROOT/"mechanical/analysis/hr-v0-j2-c07-pe-seam-free-jacobian-mesh-p0.1";R301=ROOT/"mechanical/analysis/hr-v0-j2-c07-pe-seam-free-jacobian-failure-localization-p0.1";R303=ROOT/"mechanical/analysis/hr-v0-j2-c07-pe-rail-jacobian-mesh-p0.1";R304=ROOT/"mechanical/analysis/hr-v0-j2-c07-pe-rail-jacobian-failure-localization-p0.1"
def sha(p:Path)->str:return hashlib.sha256(p.read_bytes()).hexdigest()
def rows(n:str):
    with (OUT/n).open(newline="",encoding="utf-8") as s:return list(csv.DictReader(s))
def fail(m:str)->None:raise SystemExit(f"R305 disposition check failed: {m}")
def main()->int:
    required={"README.md","analysis-status.json","execution-provenance.json","failed-element-geometry.csv","file-manifest.csv","r300-r303-comparison.csv"}
    if {p.name for p in OUT.iterdir()}!=required or {p.name for p in RELEASE.iterdir()}!=required:fail("file set")
    manifest=rows("file-manifest.csv")
    if {r["relative_path"] for r in manifest}!=required-{"file-manifest.csv"}:fail("manifest set")
    for r in manifest:
        p=OUT/r["relative_path"]
        if sha(p)!=r["sha256"] or p.stat().st_size!=int(r["bytes"]):fail(f"manifest {p.name}")
    for n in required:
        if sha(OUT/n)!=sha(RELEASE/n):fail(f"mirror {n}")
    s=json.loads((OUT/"analysis-status.json").read_text());p=json.loads((OUT/"execution-provenance.json").read_text());c=rows("r300-r303-comparison.csv");g=rows("failed-element-geometry.csv")
    expected={"r300_status_sha256":sha(R300/"analysis-status.json"),"r301_status_sha256":sha(R301/"analysis-status.json"),"r303_status_sha256":sha(R303/"analysis-status.json"),"r304_status_sha256":sha(R304/"analysis-status.json")}
    if p["generator_sha256"]!=sha(GEN) or any(s[k]!=v or p[k]!=v for k,v in expected.items()):fail("provenance")
    if len(c)!=4 or len(g)!=1 or not s["r303_face_refinement_rejected"] or not s["r300_restored_as_next_method_baseline"]:fail("disposition")
    if not (float(g[0]["minimum_corner_edge_mm"])<float(g[0]["maximum_corner_edge_mm"]) and float(g[0]["competing_surface_midside_gap_mm"])>0):fail("geometry")
    for key in ("next_mesh_executed","structural_solution_executed","r279_c02_complete","r278_h02_closed","capacity_credit","selected","safety_credit","work_authority"):
        if s[key] is not False:fail(key)
    print("PASS: R305 rejects R303 face refinement, restores R300 baseline, and keeps structural/H02/capacity/all authority open");return 0
if __name__=="__main__":raise SystemExit(main())
