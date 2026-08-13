#!/usr/bin/env python3
"""Fail-closed R284 constrained-high-order checker."""
import csv,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/"mechanical/analysis/hr-v0-j2-c07-constrained-high-order-p0.1";REL=ROOT/"release/hr-v0/j2-c07-constrained-high-order-p0.1"
WARNING="PRELIMINARY - CONSTRAINED HIGH-ORDER MESH METHOD EVIDENCE ONLY - NOT APPROVED FOR PROCUREMENT, QUOTATION, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION"
def need(v,m):
    if not v:raise SystemExit(m)
def rows(p):
    with p.open(newline="",encoding="utf-8-sig") as s:return list(csv.DictReader(s))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def manifest(d):
    r=rows(d/"file-manifest.csv");a=[p for p in d.rglob("*") if p.is_file() and p.name!="file-manifest.csv"];need(len(r)==len(a),"manifest count");m={x["relative_path"]:x for x in r}
    for p in a:x=m.get(p.relative_to(d).as_posix());need(x and x["sha256"]==sha(p) and int(x["bytes"])==p.stat().st_size,f"manifest {p}")
def normalized_warnings(d):
    for p in d.rglob("*.csv"):
        record=rows(p)
        if not record:continue
        need("warning" in record[0],f"warning column absent: {p}")
        need(all(x["warning"]==WARNING for x in record),f"warning mismatch: {p}")
def mirror():
    source={p.relative_to(OUT).as_posix():sha(p) for p in OUT.rglob("*") if p.is_file() and p.name!="file-manifest.csv"}
    release={p.relative_to(REL).as_posix():sha(p) for p in REL.rglob("*") if p.is_file() and p.name!="file-manifest.csv"}
    need(source==release,"source/release mirror mismatch")
def main():
    for d in (OUT,REL):need(d.is_dir(),f"missing {d}");manifest(d);normalized_warnings(d)
    mirror()
    st=json.loads((OUT/"analysis-status.json").read_text());need(st["identifier"]=="HR-V0-J2-C07-CONSTRAINED-HIGH-ORDER-P0.1" and st["round"]=="R284","identity");need(st["warning"]==WARNING,"status warning");need(st["bounded_constrained_high_order_method_pass"] and st["pre_restore_bijection_unique"] and st["post_restore_gate"] and st["optimized_midsides_retained"] and st["element_connectivity_gate"] and st["element_orientation_gate"] and st["occ_corner_membership_gate"] and st["linear_sicn_gate"] and st["curved_jacobian_gate"],"method gates");need(st["wrong_or_zero_total"]==0 and st["normalized_det_fail_total"]==0 and st["missing_edges"]==0,"counts")
    need(not any(st[k] for k in ("corner_restoration_curved_entity_conformity_revalidated","surface_deviation_from_brep_complete","exact_facet_map_complete","r279_c02_complete","r278_h02_closed","selected","safety_credit","capacity_credit","work_authority","fabrication_authorized","powered_testing_authorized","motion_authorized","energization_authorized")),"authority")
    generator=ROOT/"tools/generate_hr_v0_j2_c07_constrained_high_order_p01.py";base=ROOT/"tools/generate_hr_v0_j2_stop_refinement_execution_p01.py";need(st["generator_sha256"]==sha(generator) and st["transitive_base_sha256"]==sha(base),"source hashes");need(st["execution_options_sha256"]==sha(OUT/"execution-options.json") and st["runtime_input_register_sha256"]==sha(OUT/"runtime-input-register.csv"),"input hashes");options=json.loads((OUT/"execution-options.json").read_text());need(options["sampled_quadrature_orders"]==[4,6,8] and options["normalized_determinant_floor"]==1e-10 and options["high_order_optimizer"]=="HighOrder","options")
    raw=ROOT/st["raw_npz"];need(raw.is_file() and sha(raw)==st["raw_npz_sha256"],"raw");need(len(rows(OUT/"corner-correspondence.csv"))==8999 and len(rows(OUT/"element-identity.csv"))==35148 and len(rows(OUT/"occ-membership.csv"))==4 and len(rows(OUT/"edge-map.csv"))==50025 and len(rows(OUT/"jacobian-screens.csv"))==3 and len(rows(OUT/"runtime-input-register.csv"))==6,"evidence counts");need("finite samples" in (OUT/"README.md").read_text() and "not a proof" in st["jacobian_evidence_scope"],"finite wording");print("PASS: R284 bounded constrained-high-order C07 route synchronized; B-Rep/facet/R279-C02/H02/capacity/work authority remain open");return 0
if __name__=="__main__":raise SystemExit(main())
