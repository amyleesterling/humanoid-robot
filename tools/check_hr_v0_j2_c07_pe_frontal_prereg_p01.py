#!/usr/bin/env python3
"""Check the frozen R295 Frontal candidate."""
from __future__ import annotations
import csv, hashlib, json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"mechanical/analysis/hr-v0-j2-c07-pe-frontal-prereg-p0.1"
RELEASE=ROOT/"release/hr-v0/j2-c07-pe-frontal-prereg-p0.1"
GEN=ROOT/"tools/generate_hr_v0_j2_c07_pe_frontal_prereg_p01.py"
R288=ROOT/"mechanical/analysis/hr-v0-j2-c07-exact-zone-partition-p0.1/c07-exact-zone-fragmented.brep"
R293=ROOT/"mechanical/analysis/hr-v0-j2-c07-pe-topology-prereg-p0.1/frozen-pe-topology-protocol.json"
R294=ROOT/"mechanical/analysis/hr-v0-j2-c07-pe-topology-disposition-p0.1/next-method-boundary.json"
WARNING="PRELIMINARY - FRONTAL TETRAHEDRALIZATION PREREGISTRATION ONLY - NOT APPROVED FOR PROCUREMENT, QUOTATION, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION"
def sha(p:Path)->str:return hashlib.sha256(p.read_bytes()).hexdigest()
def fail(m:str)->None:raise SystemExit(f"R295 prereg check failed: {m}")
def rows(p:Path)->list[dict[str,str]]:
    with p.open(newline="",encoding="utf-8") as s:return list(csv.DictReader(s))
def main()->int:
    required={"README.md","analysis-status.json","execution-provenance.json","file-manifest.csv","frozen-frontal-protocol.json","inherited-target-register.csv"}
    if {p.name for p in OUT.iterdir()}!=required or {p.name for p in RELEASE.iterdir()}!=required:fail("file set")
    manifest=rows(OUT/"file-manifest.csv")
    if {r["relative_path"] for r in manifest}!=required-{"file-manifest.csv"}:fail("manifest")
    for r in manifest:
        p=OUT/r["relative_path"]
        if sha(p)!=r["sha256"] or p.stat().st_size!=int(r["bytes"]) or r["warning"]!=WARNING:fail(f"manifest {p.name}")
    for name in required:
        if sha(OUT/name)!=sha(RELEASE/name):fail(f"mirror {name}")
    protocol=json.loads((OUT/"frozen-frontal-protocol.json").read_text(encoding="utf-8"));status=json.loads((OUT/"analysis-status.json").read_text(encoding="utf-8"));prov=json.loads((OUT/"execution-provenance.json").read_text(encoding="utf-8"))
    if protocol["candidate_id"]!="R295-C07-PE-FRONTAL-V01" or protocol["linear_mesh_method"]["algorithm3d"]!=4:fail("candidate/algorithm")
    if protocol["linear_mesh_method"]["optimizer_sequence"]!=["Netgen"] or protocol["linear_mesh_method"]["relocate3d"]:fail("optimizer boundary")
    if protocol["r288_brep_sha256"]!=sha(R288) or protocol["r293_protocol_sha256"]!=sha(R293) or protocol["r294_method_boundary_sha256"]!=sha(R294):fail("input binding")
    if prov["generator_sha256"]!=sha(GEN):fail("generator binding")
    targets=rows(OUT/"inherited-target-register.csv")
    if sum(r["target_kind"]=="EXACT_FAILED_POCKET_VOLUME" for r in targets)!=4 or sum(r["target_kind"]=="SYMMETRY_CLOSED_EXACT_CYLINDER_FACE" for r in targets)!=6:fail("target counts")
    for key in ("mesh_executed","structural_solution_executed","r279_c02_complete","r278_h02_closed","capacity_credit","selected","safety_credit","work_authority"):
        if protocol[key] is not False or status[key] is not False:fail(f"fail-closed {key}")
    print("PASS: R295 Frontal candidate frozen before execution; exact CAD/fields/thresholds unchanged; mesh/structural/H02/capacity/all authority open");return 0
if __name__=="__main__":raise SystemExit(main())
