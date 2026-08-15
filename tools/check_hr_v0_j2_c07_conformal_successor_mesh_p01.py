#!/usr/bin/env python3
"""Checker for the single preregistered R291 successor mesh execution."""
from __future__ import annotations
import csv, gzip, hashlib, json
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"mechanical/analysis/hr-v0-j2-c07-conformal-successor-mesh-p0.1"
RELEASE=ROOT/"release/hr-v0/j2-c07-conformal-successor-mesh-p0.1"
GEN=ROOT/"tools/generate_hr_v0_j2_c07_conformal_successor_mesh_p01.py"
BASE=ROOT/"tools/generate_hr_v0_j2_c07_conformal_zone_mesh_p01.py"
PREREG=ROOT/"mechanical/analysis/hr-v0-j2-c07-conformal-successor-prereg-p0.1/frozen-successor-protocol.json"
WARNING="PRELIMINARY - PREREGISTERED CONFORMAL SUCCESSOR MESH EVIDENCE ONLY - NOT APPROVED FOR PROCUREMENT, QUOTATION, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION"
def sha(p:Path)->str:return hashlib.sha256(p.read_bytes()).hexdigest()
def fail(m:str)->None:raise SystemExit(f"R291 successor mesh check failed: {m}")
def rows(name:str)->list[dict[str,str]]:
    with (OUT/name).open(newline="",encoding="utf-8") as s:return list(csv.DictReader(s))
def main()->int:
    required={"README.md","actual-quadrature-jacobian-register.csv","analysis-status.json","c07-conformal-zone-mesh.msh.gz","execution-provenance.json","failed-baseline-register.csv","file-manifest.csv","frozen-successor-protocol.json","open-holds.csv","raw-conformal-zone-mesh.npz","sicn-histogram.csv","successor-field-resolution.csv","zone-quality-summary.csv","zone-volume-integration.csv"}
    if {p.name for p in OUT.iterdir()}!=required or {p.name for p in RELEASE.iterdir()}!=required:fail("file set drift")
    manifest=rows("file-manifest.csv")
    if {r["relative_path"] for r in manifest}!=required-{"file-manifest.csv"}:fail("manifest membership")
    for r in manifest:
        p=OUT/r["relative_path"]
        if sha(p)!=r["sha256"] or p.stat().st_size!=int(r["bytes"]):fail(f"manifest drift {p}")
    for name in required:
        if sha(OUT/name)!=sha(RELEASE/name):fail(f"mirror drift {name}")
    status=json.loads((OUT/"analysis-status.json").read_text(encoding="utf-8"));provenance=json.loads((OUT/"execution-provenance.json").read_text(encoding="utf-8"))
    if status["identifier"]!="HR-V0-J2-C07-CONFORMAL-SUCCESSOR-MESH-P0.1" or status["round"]!="R291":fail("identity drift")
    if not status["single_preregistered_execution_complete"] or not status["thresholds_unchanged"]:fail("execution/threshold state")
    if status["preregistration_sha256"]!=sha(PREREG) or sha(OUT/"frozen-successor-protocol.json")!=sha(PREREG):fail("prereg binding")
    if provenance["generator_sha256"]!=sha(GEN) or provenance["transitive_r289_generator_sha256"]!=sha(BASE):fail("generator provenance")
    resolved=rows("successor-field-resolution.csv")
    if sum(r["target_kind"]=="EXACT_FAILED_POCKET_VOLUME" for r in resolved)!=4 or sum(r["target_kind"]=="EXACT_CYLINDER_FACE" for r in resolved)!=6:fail("target resolution count")
    if any(r["resolution_gate"]!="PASS" for r in resolved):fail("target resolution failure")
    raw=np.load(OUT/"raw-conformal-zone-mesh.npz");sicn=raw["linear_sicn"]
    if len(sicn)!=status["linear_tetrahedra"] or abs(float(np.min(sicn))-status["global_sicn_minimum"])>1e-14:fail("raw quality drift")
    summaries=rows("zone-quality-summary.csv");hist=rows("sicn-histogram.csv")
    if len(summaries)!=28 or len({r["zone_id"] for r in summaries})!=28:fail("zone summary identity")
    for s in summaries:
        z=[r for r in hist if r["scope"]=="EXACT_ZONE" and r["zone_id"]==s["zone_id"]]
        if len(z)!=10 or sum(int(r["count"]) for r in z)!=int(s["tetrahedra"]):fail(f"zone histogram {s['zone_id']}")
    jac=rows("actual-quadrature-jacobian-register.csv")
    derived_jac=all(int(r["wrong_or_zero_count"])==0 and int(r["normalized_floor_fail_count"])==0 for r in jac)
    if status["actual_quadrature_signed_jacobian_gate"]!=derived_jac:fail("Jacobian derivation")
    derived_c02=bool(status["global_sicn_gate"] and status["monitored_zone_minimum_gate"] and derived_jac)
    if status["r279_c02_complete"]!=derived_c02:fail("R279-C02 derivation")
    digest=hashlib.sha256();count=0
    with gzip.open(OUT/"c07-conformal-zone-mesh.msh.gz","rb") as s:
        while True:
            b=s.read(1024*1024)
            if not b:break
            digest.update(b);count+=len(b)
    if digest.hexdigest()!=status["mesh_uncompressed_sha256"] or count!=status["mesh_uncompressed_bytes"]:fail("gzip reproduction")
    for key in ("full_reference_domain_curved_jacobian_positive","structural_solution_executed","mesh_convergence_complete","r278_h02_closed","capacity_credit","selected","safety_credit","procurement_authorized","fabrication_authorized","assembly_authorized","connection_authorized","powered_testing_authorized","motion_authorized","energization_authorized"):
        if status[key] is not False:fail(f"fail-closed state {key}")
    print(f"PASS: R291 successor synchronized; tets={len(sicn)} global={status['global_sicn_gate']} monitored={status['monitored_zone_minimum_gate']} jacobian={derived_jac} R279-C02={derived_c02}; structural/H02/capacity/all authority open")
    return 0
if __name__=="__main__":raise SystemExit(main())
