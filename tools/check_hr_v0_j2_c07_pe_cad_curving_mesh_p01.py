#!/usr/bin/env python3
"""Independent consistency checker for the executed R307 package."""
from __future__ import annotations
import csv,gzip,hashlib,json
from pathlib import Path
import numpy as np
from hr_v0_mesh_raw_shards import LINEAR_KEYS,load_shards

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"mechanical/analysis/hr-v0-j2-c07-pe-cad-curving-mesh-p0.1";RELEASE=ROOT/"release/hr-v0/j2-c07-pe-cad-curving-mesh-p0.1"
R300=ROOT/"mechanical/analysis/hr-v0-j2-c07-pe-seam-free-jacobian-mesh-p0.1";R306=ROOT/"mechanical/analysis/hr-v0-j2-c07-pe-constrained-curving-mesh-p0.1"
EXECUTOR=ROOT/"tools/generate_hr_v0_j2_c07_pe_cad_curving_mesh_p01.py";PUBLISHER=ROOT/"tools/publish_hr_v0_j2_c07_pe_cad_curving_mesh_p01.py"
PREREG=ROOT/"mechanical/analysis/hr-v0-j2-c07-pe-cad-curving-prereg-p0.1/frozen-cad-curving-protocol.json"
R300_GEN=ROOT/"tools/generate_hr_v0_j2_c07_pe_seam_free_jacobian_mesh_p01.py";R298_GEN=ROOT/"tools/generate_hr_v0_j2_c07_pe_seam_free_mesh_p01.py";BASE_GEN=ROOT/"tools/generate_hr_v0_j2_c07_conformal_zone_mesh_p01.py"
def sha(path:Path)->str:return hashlib.sha256(path.read_bytes()).hexdigest()
def fail(message:str)->None:raise SystemExit(f"R307 check failed: {message}")
def rows(path:Path)->list[dict[str,str]]:
    with path.open(newline="",encoding="utf-8") as stream:return list(csv.DictReader(stream))
def main()->int:
    required={"README.md","actual-quadrature-jacobian-register.csv","analysis-status.json","bore-wall-field-resolution.csv","c07-conformal-zone-mesh.msh.gz","corner-restoration-evidence.npz","execution-provenance.json","file-manifest.csv","frozen-cad-curving-protocol.json","open-holds.csv","r300-reproduction-register.csv","raw-linear-mesh.npz","raw-tet10-mesh.npz","retained-pe-subzone-quality-inference.csv","seam-free-field-resolution.csv","sicn-histogram.csv","zone-quality-summary.csv","zone-volume-integration.csv"}
    if {p.name for p in OUT.iterdir()}!=required or {p.name for p in RELEASE.iterdir()}!=required:fail("file set")
    manifest=rows(OUT/"file-manifest.csv")
    if {row["relative_path"] for row in manifest}!=required-{"file-manifest.csv"}:fail("manifest set")
    for row in manifest:
        path=OUT/row["relative_path"]
        if sha(path)!=row["sha256"] or path.stat().st_size!=int(row["bytes"]):fail(f"manifest {path.name}")
    for name in required:
        if sha(OUT/name)!=sha(RELEASE/name):fail(f"mirror {name}")
    status=json.loads((OUT/"analysis-status.json").read_text(encoding="utf-8"));provenance=json.loads((OUT/"execution-provenance.json").read_text(encoding="utf-8"));protocol=json.loads(PREREG.read_text(encoding="utf-8"))
    if status["candidate_id"]!=protocol["candidate_id"] or status["preregistration_sha256"]!=sha(PREREG):fail("protocol binding")
    if status["r300_status_sha256"]!=sha(R300/"analysis-status.json") or status["r306_status_sha256"]!=sha(R306/"analysis-status.json"):fail("source status binding")
    if provenance["generator_sha256"]!=sha(EXECUTOR) or provenance["publisher_sha256"]!=sha(PUBLISHER):fail("local tool binding")
    if provenance["transitive_r300_generator_sha256"]!=sha(R300_GEN) or provenance["transitive_r298_generator_sha256"]!=sha(R298_GEN) or provenance["transitive_base_generator_sha256"]!=sha(BASE_GEN):fail("transitive tool binding")
    if provenance["high_order_optimizer"]!="HighOrder" or provenance["force"] is not False or provenance["niter"]!=1:fail("optimizer record")
    raw=load_shards(OUT);baseline=load_shards(R300)
    for key in LINEAR_KEYS:
        if not np.array_equal(raw[key],baseline[key]):fail(f"linear reproduction {key}")
    if not np.array_equal(raw["tet10_element_tags"],baseline["tet10_element_tags"]) or not np.array_equal(raw["tet10_connectivity"],baseline["tet10_connectivity"]):fail("Tet10 topology reproduction")
    with np.load(OUT/"corner-restoration-evidence.npz") as evidence:
        expected={"old_corner_tags","mapped_tet10_corner_tags","linear_corner_xyz","pre_restore_corner_xyz","restored_corner_xyz","initial_mapping_distance_mm","pre_restore_distance_mm","post_restore_distance_mm"}
        if set(evidence.files)!=expected:fail("corner evidence arrays")
        old=evidence["old_corner_tags"];mapped=evidence["mapped_tet10_corner_tags"];linear=evidence["linear_corner_xyz"];restored=evidence["restored_corner_xyz"]
        if len(old)!=status["vertices"] or len(np.unique(mapped))!=len(mapped):fail("corner bijection count")
        if float(np.max(evidence["initial_mapping_distance_mm"]))!=status["maximum_initial_corner_mapping_distance_mm"]:fail("initial mapping distance")
        if float(np.max(evidence["pre_restore_distance_mm"]))!=status["maximum_pre_restore_corner_movement_mm"]:fail("pre-restore distance")
        if float(np.max(evidence["post_restore_distance_mm"]))!=status["maximum_post_restore_corner_error_mm"] or not np.array_equal(linear,restored):fail("corner restoration")
        node_lookup={int(tag):raw["node_xyz"][index] for index,tag in enumerate(raw["node_tags"])}
        final=np.vstack([node_lookup[int(tag)] for tag in mapped])
        if not np.array_equal(final,restored):fail("corner evidence vs raw")
    jac=rows(OUT/"actual-quadrature-jacobian-register.csv")
    if {int(row["quadrature_order"]) for row in jac}!={4,6,8} or len(jac)!=63:fail("Jacobian coverage")
    jac_gate=all(int(row["wrong_or_zero_count"])==0 and int(row["normalized_floor_fail_count"])==0 for row in jac)
    if not jac_gate or any(row["full_reference_domain_positivity"]!="UNVERIFIED" for row in jac):fail("Jacobian gate/scope")
    quality=float(np.min(raw["linear_sicn"]))>=.10 and float(np.mean(raw["linear_sicn"]<.20))<=.001
    summaries=rows(OUT/"zone-quality-summary.csv");monitored=not any(row["zone_id"]!="C07-MATRIX" and row["monitored_min_0p20_gate"]!="PASS" for row in summaries)
    sampled=bool(quality and monitored and jac_gate and status["r300_linear_arrays_exact"] and status["r300_tet10_tags_and_connectivity_exact"] and status["corner_bijection_gate"] and status["element_connectivity_gate"] and status["maximum_post_restore_corner_error_mm"]<=1e-12)
    if not sampled or status["sampled_cad_curving_candidate_pass"]!=sampled:fail("sampled candidate derivation")
    digest=hashlib.sha256();count=0
    with gzip.open(OUT/"c07-conformal-zone-mesh.msh.gz","rb") as stream:
        while block:=stream.read(1024*1024):digest.update(block);count+=len(block)
    if digest.hexdigest()!=status["mesh_uncompressed_sha256"] or count!=status["mesh_uncompressed_bytes"]:fail("mesh gzip")
    for key in ("exact_facet_revalidation_executed","exact_facet_revalidation_pass","full_reference_domain_curved_jacobian_positive","r279_c02_complete","structural_solution_executed","mesh_convergence_complete","r278_h02_closed","capacity_credit","selected","safety_credit","procurement_authorized","fabrication_authorized","assembly_authorized","connection_authorized","powered_testing_authorized","motion_authorized","energization_authorized"):
        if status[key] is not False:fail(f"fail-closed {key}")
    print(f"PASS: R307 independently checked; exact R300 linear/topology reproduction; corners={len(old)}; Q4/Q6/Q8 failures=0; bounded sampled candidate=true; exact facet/R279-C02/H02/capacity/all authority open")
    return 0
if __name__=="__main__":raise SystemExit(main())
