#!/usr/bin/env python3
"""Check the single preregistered R295 Frontal mesh execution."""
from __future__ import annotations
import csv,gzip,hashlib,json
from pathlib import Path
import numpy as np
from hr_v0_mesh_raw_shards import load_shards

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"mechanical/analysis/hr-v0-j2-c07-pe-frontal-mesh-p0.1";RELEASE=ROOT/"release/hr-v0/j2-c07-pe-frontal-mesh-p0.1"
GEN=ROOT/"tools/generate_hr_v0_j2_c07_pe_frontal_mesh_p01.py";PRIOR=ROOT/"tools/generate_hr_v0_j2_c07_conformal_successor_mesh_p01.py";BASE=ROOT/"tools/generate_hr_v0_j2_c07_conformal_zone_mesh_p01.py"
PREREG=ROOT/"mechanical/analysis/hr-v0-j2-c07-pe-frontal-prereg-p0.1/frozen-frontal-protocol.json";R293=ROOT/"mechanical/analysis/hr-v0-j2-c07-pe-topology-mesh-p0.1/analysis-status.json";R293_PROVENANCE=R293.parent/"execution-provenance.json"
WARNING="PRELIMINARY - PREREGISTERED FRONTAL TETRAHEDRALIZATION EVIDENCE ONLY - NOT APPROVED FOR PROCUREMENT, QUOTATION, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION"
MIGRATION=ROOT/"tools/migrate_hr_v0_mesh_raw_to_shards_p01.py";SHARD_HELPER=ROOT/"tools/hr_v0_mesh_raw_shards.py"
def sha(p:Path)->str:return hashlib.sha256(p.read_bytes()).hexdigest()
def fail(m:str)->None:raise SystemExit(f"R295 Frontal mesh check failed: {m}")
def rows(name:str)->list[dict[str,str]]:
    with (OUT/name).open(newline="",encoding="utf-8") as s:return list(csv.DictReader(s))
def main()->int:
    required={"README.md","actual-quadrature-jacobian-register.csv","analysis-status.json","c07-conformal-zone-mesh.msh.gz","execution-provenance.json","file-manifest.csv","frozen-frontal-protocol.json","method-baseline-register.csv","method-execution-register.csv","open-holds.csv","raw-linear-mesh.npz","raw-tet10-mesh.npz","sicn-histogram.csv","successor-field-resolution.csv","zone-quality-summary.csv","zone-volume-integration.csv"}
    if {p.name for p in OUT.iterdir()}!=required or {p.name for p in RELEASE.iterdir()}!=required:fail("file set")
    manifest=rows("file-manifest.csv")
    if {r["relative_path"] for r in manifest}!=required-{"file-manifest.csv"}:fail("manifest membership")
    for r in manifest:
        p=OUT/r["relative_path"]
        if sha(p)!=r["sha256"] or p.stat().st_size!=int(r["bytes"]) or r["warning"]!=WARNING:fail(f"manifest {p.name}")
    for name in required:
        if sha(OUT/name)!=sha(RELEASE/name):fail(f"mirror {name}")
    st=json.loads((OUT/"analysis-status.json").read_text(encoding="utf-8"));prov=json.loads((OUT/"execution-provenance.json").read_text(encoding="utf-8"));protocol=json.loads(PREREG.read_text(encoding="utf-8"))
    if st["candidate_id"]!=protocol["candidate_id"] or st["algorithm3d"]!=4 or st["algorithm_name"]!="Frontal":fail("candidate/algorithm")
    if st["linear_optimizer_sequence"]!=["Netgen"] or st["relocate3d"] or st["high_order_optimizer"]!="NONE":fail("optimizer state")
    r293_provenance=json.loads(R293_PROVENANCE.read_text(encoding="utf-8"))
    if st["preregistration_sha256"]!=sha(PREREG) or st["r293_baseline_status_sha256"]!=r293_provenance["pre_raw_shard_migration_status_sha256"]:fail("input binding")
    if prov["generator_sha256"]!=sha(GEN) or prov["transitive_r291_generator_sha256"]!=sha(PRIOR) or prov["transitive_r289_generator_sha256"]!=sha(BASE):fail("generator binding")
    method=rows("method-execution-register.csv")
    if len(method)!=1 or int(method[0]["algorithm3d"])!=4 or method[0]["linear_optimizer"]!="Netgen" or method[0]["relocate3d"]!="False":fail("method record")
    if prov["raw_shard_migration_generator_sha256"]!=sha(MIGRATION) or prov["raw_shard_helper_sha256"]!=sha(SHARD_HELPER):fail("raw shard provenance")
    raw=load_shards(OUT);sicn=raw["linear_sicn"]
    if len(sicn)!=st["linear_tetrahedra"] or abs(float(np.min(sicn))-st["global_sicn_minimum"])>1e-14:fail("raw quality")
    global_gate=float(np.min(sicn))>=.10 and float(np.mean(sicn<.20))<=.001
    if st["global_sicn_gate"]!=global_gate:fail("global derivation")
    summaries=rows("zone-quality-summary.csv");hist=rows("sicn-histogram.csv")
    if len(summaries)!=28 or len({r["zone_id"] for r in summaries})!=28:fail("zone summary")
    for s in summaries:
        z=[r for r in hist if r["scope"]=="EXACT_ZONE" and r["zone_id"]==s["zone_id"]]
        if len(z)!=10 or sum(int(r["count"]) for r in z)!=int(s["tetrahedra"]):fail(f"zone histogram {s['zone_id']}")
    monitored=not any(r["zone_id"]!="C07-MATRIX" and r["monitored_min_0p20_gate"]!="PASS" for r in summaries)
    if st["monitored_zone_minimum_gate"]!=monitored:fail("monitored derivation")
    jac=rows("actual-quadrature-jacobian-register.csv");jac_gate=all(int(r["wrong_or_zero_count"])==0 and int(r["normalized_floor_fail_count"])==0 for r in jac)
    if st["actual_quadrature_signed_jacobian_gate"]!=jac_gate or {int(r["quadrature_order"]) for r in jac}!={4,6,8}:fail("Jacobian derivation")
    if any(r["full_reference_domain_positivity"]!="UNVERIFIED" for r in jac):fail("full-domain overclaim")
    c02=bool(global_gate and monitored and jac_gate)
    if st["r279_c02_complete"]!=c02:fail("R279-C02 derivation")
    digest=hashlib.sha256();count=0
    with gzip.open(OUT/"c07-conformal-zone-mesh.msh.gz","rb") as s:
        while True:
            b=s.read(1024*1024)
            if not b:break
            digest.update(b);count+=len(b)
    if digest.hexdigest()!=st["mesh_uncompressed_sha256"] or count!=st["mesh_uncompressed_bytes"]:fail("gzip reproduction")
    for key in ("full_reference_domain_curved_jacobian_positive","structural_solution_executed","mesh_convergence_complete","r278_h02_closed","capacity_credit","selected","safety_credit","procurement_authorized","fabrication_authorized","assembly_authorized","connection_authorized","powered_testing_authorized","motion_authorized","energization_authorized"):
        if st[key] is not False:fail(f"fail-closed {key}")
    print(f"PASS: R295 Frontal execution synchronized; tets={len(sicn)} global={global_gate} monitored={monitored} jacobian={jac_gate} R279-C02={c02}; structural/H02/capacity/all authority open");return 0
if __name__=="__main__":raise SystemExit(main())
