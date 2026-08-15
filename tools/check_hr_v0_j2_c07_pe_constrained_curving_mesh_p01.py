#!/usr/bin/env python3
from __future__ import annotations
import csv,gzip,hashlib,json
from pathlib import Path
import numpy as np
from hr_v0_mesh_raw_shards import load_shards
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/"mechanical/analysis/hr-v0-j2-c07-pe-constrained-curving-mesh-p0.1";RELEASE=ROOT/"release/hr-v0/j2-c07-pe-constrained-curving-mesh-p0.1";GEN=ROOT/"tools/generate_hr_v0_j2_c07_pe_constrained_curving_mesh_p01.py";R300=ROOT/"mechanical/analysis/hr-v0-j2-c07-pe-seam-free-jacobian-mesh-p0.1";PREREG=ROOT/"mechanical/analysis/hr-v0-j2-c07-pe-constrained-curving-prereg-p0.1/frozen-constrained-curving-protocol.json"
def sha(p:Path)->str:return hashlib.sha256(p.read_bytes()).hexdigest()
def fail(m:str)->None:raise SystemExit(f"R306 mesh check failed: {m}")
def rows(n:str):
    with (OUT/n).open(newline="",encoding="utf-8") as s:return list(csv.DictReader(s))
def main()->int:
    attempt_required={"README.md","analysis-status.json","attempt-register.csv","execution-provenance.json","file-manifest.csv","open-holds.csv"}
    if OUT.exists() and (OUT/"analysis-status.json").exists():
        attempt_status=json.loads((OUT/"analysis-status.json").read_text())
        if attempt_status.get("controlled_stop") is True:
            if {p.name for p in OUT.iterdir()}!=attempt_required or {p.name for p in RELEASE.iterdir()}!=attempt_required:fail("attempt file set")
            manifest=rows("file-manifest.csv")
            if {r["relative_path"] for r in manifest}!=attempt_required-{"file-manifest.csv"}:fail("attempt manifest")
            for r in manifest:
                pth=OUT/r["relative_path"]
                if sha(pth)!=r["sha256"] or pth.stat().st_size!=int(r["bytes"]):fail(f"attempt manifest {pth.name}")
            for name in attempt_required:
                if sha(OUT/name)!=sha(RELEASE/name):fail(f"attempt mirror {name}")
            attempt=rows("attempt-register.csv")
            if len(attempt)!=1 or attempt[0]["result"]!="CONTROLLED STOP - NO NUMERICAL RESULT" or attempt[0]["temporary_decompressed_mesh_removed"]!="True":fail("attempt register")
            if attempt_status["execution_completed"] is not False or attempt_status["numerical_result_available"] is not False:fail("attempt result boundary")
            for key in ("sampled_constrained_curving_candidate_pass","exact_facet_revalidation_executed","full_reference_domain_curved_jacobian_positive","r279_c02_complete","structural_solution_executed","mesh_convergence_complete","r278_h02_closed","capacity_credit","selected","safety_credit","procurement_authorized","fabrication_authorized","assembly_authorized","connection_authorized","powered_testing_authorized","motion_authorized","energization_authorized"):
                if attempt_status[key] is not False:fail(f"attempt {key}")
            print("PASS: R306 controlled-stop attempt retained; no numerical result, facet/full-domain/R279-C02/structural/H02/capacity/all authority open");return 0
    required={"README.md","actual-quadrature-jacobian-register.csv","analysis-status.json","c07-constrained-curving.msh.gz","corner-restoration-evidence.npz","execution-provenance.json","file-manifest.csv","open-holds.csv","raw-linear-mesh.npz","raw-tet10-mesh.npz","retained-pe-subzone-quality-inference.csv","sicn-histogram.csv","zone-quality-summary.csv","zone-volume-integration.csv"}
    if {p.name for p in OUT.iterdir()}!=required or {p.name for p in RELEASE.iterdir()}!=required:fail("file set")
    manifest=rows("file-manifest.csv")
    if {r["relative_path"] for r in manifest}!=required-{"file-manifest.csv"}:fail("manifest")
    for r in manifest:
        p=OUT/r["relative_path"]
        if sha(p)!=r["sha256"] or p.stat().st_size!=int(r["bytes"]):fail(f"manifest {p.name}")
    for n in required:
        if sha(OUT/n)!=sha(RELEASE/n):fail(f"mirror {n}")
    s=json.loads((OUT/"analysis-status.json").read_text());p=json.loads((OUT/"execution-provenance.json").read_text());protocol=json.loads(PREREG.read_text())
    if p["generator_sha256"]!=sha(GEN) or s["preregistration_sha256"]!=sha(PREREG) or s["candidate_id"]!=protocol["candidate_id"] or s["r300_status_sha256"]!=sha(R300/"analysis-status.json"):fail("binding")
    base=load_shards(R300);new=load_shards(OUT)
    for key in ("linear_node_tags","linear_node_xyz","linear_element_tags","linear_tet4_connectivity","linear_sicn","element_zone_code","tet10_element_tags","tet10_connectivity"):
        if not np.array_equal(base[key],new[key]):fail(f"unchanged array {key}")
    with np.load(OUT/"corner-restoration-evidence.npz") as e:
        if float(np.max(e["post_restore_distance_mm"]))!=s["maximum_post_restore_corner_error_mm"] or not np.array_equal(e["corner_pre_xyz"],e["corner_restored_xyz"]):fail("corner restoration")
    jac=rows("actual-quadrature-jacobian-register.csv");jacgate=all(int(r["wrong_or_zero_count"])==0 and int(r["normalized_floor_fail_count"])==0 for r in jac)
    if {int(r["quadrature_order"]) for r in jac}!={4,6,8} or any(r["full_reference_domain_positivity"]!="UNVERIFIED" for r in jac):fail("Jacobian scope")
    candidate=bool(s["corner_restore_gate"] and s["element_connectivity_gate"] and jacgate)
    if s["actual_quadrature_signed_jacobian_gate"]!=jacgate or s["sampled_constrained_curving_candidate_pass"]!=candidate:fail("gate derivation")
    digest=hashlib.sha256();count=0
    with gzip.open(OUT/"c07-constrained-curving.msh.gz","rb") as z:
        while True:
            b=z.read(1024*1024)
            if not b:break
            digest.update(b);count+=len(b)
    if digest.hexdigest()!=s["mesh_uncompressed_sha256"] or count!=s["mesh_uncompressed_bytes"]:fail("mesh gzip")
    for key in ("exact_facet_revalidation_executed","exact_facet_revalidation_pass","full_reference_domain_curved_jacobian_positive","r279_c02_complete","structural_solution_executed","mesh_convergence_complete","r278_h02_closed","capacity_credit","selected","safety_credit","procurement_authorized","fabrication_authorized","assembly_authorized","connection_authorized","powered_testing_authorized","motion_authorized","energization_authorized"):
        if s[key] is not False:fail(key)
    print(f"PASS: R306 synchronized; corners={s['corner_restore_gate']} connectivity={s['element_connectivity_gate']} sampled_jacobian={jacgate}; facet/full-domain/R279-C02/structural/H02/capacity/all authority open");return 0
if __name__=="__main__":raise SystemExit(main())
