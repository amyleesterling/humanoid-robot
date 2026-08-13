#!/usr/bin/env python3
from __future__ import annotations
import csv,gzip,hashlib,json
from pathlib import Path
import numpy as np
from hr_v0_mesh_raw_shards import load_shards
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/"mechanical/analysis/hr-v0-j2-c07-pe-seam-free-mesh-p0.1";RELEASE=ROOT/"release/hr-v0/j2-c07-pe-seam-free-mesh-p0.1";GEN=ROOT/"tools/generate_hr_v0_j2_c07_pe_seam_free_mesh_p01.py";BASE=ROOT/"tools/generate_hr_v0_j2_c07_conformal_zone_mesh_p01.py";PREREG=ROOT/"mechanical/analysis/hr-v0-j2-c07-pe-seam-free-mesh-prereg-p0.1/frozen-seam-free-mesh-protocol.json";R297=ROOT/"mechanical/analysis/hr-v0-j2-c07-pe-seam-free-partition-p0.1"
WARNING="PRELIMINARY - PREREGISTERED SEAM-FREE PE MESH EVIDENCE ONLY - NOT APPROVED FOR PROCUREMENT, QUOTATION, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION"
MIGRATION=ROOT/"tools/migrate_hr_v0_mesh_raw_to_shards_p01.py";SHARD_HELPER=ROOT/"tools/hr_v0_mesh_raw_shards.py"
def sha(p:Path)->str:return hashlib.sha256(p.read_bytes()).hexdigest()
def fail(m:str)->None:raise SystemExit(f"R298 seam-free mesh check failed: {m}")
def rows(n:str):
    with (OUT/n).open(newline="",encoding="utf-8") as s:return list(csv.DictReader(s))
def main()->int:
    required={"README.md","actual-quadrature-jacobian-register.csv","analysis-status.json","c07-conformal-zone-mesh.msh.gz","execution-provenance.json","file-manifest.csv","frozen-seam-free-mesh-protocol.json","open-holds.csv","raw-linear-mesh.npz","raw-tet10-mesh.npz","retained-pe-subzone-quality-inference.csv","seam-free-field-resolution.csv","sicn-histogram.csv","zone-quality-summary.csv","zone-volume-integration.csv"}
    if {p.name for p in OUT.iterdir()}!=required or {p.name for p in RELEASE.iterdir()}!=required:fail("file set")
    manifest=rows("file-manifest.csv")
    if {r["relative_path"] for r in manifest}!=required-{"file-manifest.csv"}:fail("manifest")
    for r in manifest:
        p=OUT/r["relative_path"]
        if sha(p)!=r["sha256"] or p.stat().st_size!=int(r["bytes"]):fail(f"manifest {p.name}")
    for n in required:
        if sha(OUT/n)!=sha(RELEASE/n):fail(f"mirror {n}")
    st=json.loads((OUT/"analysis-status.json").read_text(encoding="utf-8"));prov=json.loads((OUT/"execution-provenance.json").read_text(encoding="utf-8"));protocol=json.loads(PREREG.read_text(encoding="utf-8"))
    if st["candidate_id"]!=protocol["candidate_id"] or st["preregistration_sha256"]!=sha(PREREG):fail("prereg binding")
    if st["r297_analysis_brep_sha256"]!=sha(R297/"c07-pe-seam-free-analysis-partition.brep") or st["r297_classification_brep_sha256"]!=sha(R297/"c07-pe-eight-subzone-classification.brep"):fail("R297 binding")
    if prov["generator_sha256"]!=sha(GEN) or prov["transitive_r289_generator_sha256"]!=sha(BASE):fail("generator binding")
    if st["algorithm3d"]!=4 or st["linear_optimizer_sequence"]!=["Netgen"] or st["relocate3d"]:fail("method")
    if prov["raw_shard_migration_generator_sha256"]!=sha(MIGRATION) or prov["raw_shard_helper_sha256"]!=sha(SHARD_HELPER):fail("raw shard provenance")
    raw=load_shards(OUT);q=raw["linear_sicn"]
    if len(q)!=st["linear_tetrahedra"] or abs(float(np.min(q))-st["global_sicn_minimum"])>1e-14:fail("raw quality")
    global_gate=float(np.min(q))>=.10 and float(np.mean(q<.20))<=.001
    summaries=rows("zone-quality-summary.csv");hist=rows("sicn-histogram.csv")
    if len(summaries)!=21 or len({r["zone_id"] for r in summaries})!=21:fail("zone count")
    for s in summaries:
        z=[r for r in hist if r["scope"]=="EXACT_ZONE" and r["zone_id"]==s["zone_id"]]
        if len(z)!=10 or sum(int(r["count"]) for r in z)!=int(s["tetrahedra"]):fail(f"hist {s['zone_id']}")
    monitored=not any(r["zone_id"]!="C07-MATRIX" and r["monitored_min_0p20_gate"]!="PASS" for r in summaries)
    fused=[r for r in summaries if r["zone_id"]=="C07-PE-FUSED"]
    if len(fused)!=1:fail("fused zone")
    fused_gate=float(fused[0]["minimum_sicn"])>=.20
    if st["fused_pe_quality_gate"]!=fused_gate or st["retained_pe_subzone_quality_floor_proven"]!=fused_gate:fail("fused inference")
    inference=rows("retained-pe-subzone-quality-inference.csv")
    if len(inference)!=8 or any((r["conservative_inference_gate"]=="PASS")!=fused_gate for r in inference):fail("subzone inference")
    jac=rows("actual-quadrature-jacobian-register.csv");jac_gate=all(int(r["wrong_or_zero_count"])==0 and int(r["normalized_floor_fail_count"])==0 for r in jac)
    if any(r["full_reference_domain_positivity"]!="UNVERIFIED" for r in jac):fail("full domain overclaim")
    c02=bool(global_gate and monitored and jac_gate)
    if st["global_sicn_gate"]!=global_gate or st["monitored_zone_minimum_gate"]!=monitored or st["actual_quadrature_signed_jacobian_gate"]!=jac_gate or st["r279_c02_complete"]!=c02:fail("gate derivation")
    digest=hashlib.sha256();count=0
    with gzip.open(OUT/"c07-conformal-zone-mesh.msh.gz","rb") as s:
        while True:
            b=s.read(1024*1024)
            if not b:break
            digest.update(b);count+=len(b)
    if digest.hexdigest()!=st["mesh_uncompressed_sha256"] or count!=st["mesh_uncompressed_bytes"]:fail("gzip")
    for key in ("full_reference_domain_curved_jacobian_positive","structural_solution_executed","mesh_convergence_complete","r278_h02_closed","capacity_credit","selected","safety_credit","procurement_authorized","fabrication_authorized","assembly_authorized","connection_authorized","powered_testing_authorized","motion_authorized","energization_authorized"):
        if st[key] is not False:fail(f"fail-closed {key}")
    print(f"PASS: R298 seam-free mesh synchronized; tets={len(q)} global={global_gate} fused/subzones={fused_gate} monitored={monitored} jacobian={jac_gate} R279-C02={c02}; structural/H02/capacity/all authority open");return 0
if __name__=="__main__":raise SystemExit(main())
