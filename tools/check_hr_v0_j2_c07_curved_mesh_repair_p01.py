#!/usr/bin/env python3
"""Fail-closed checks for bounded R283 C07 curved mesh repair."""
import csv,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/"mechanical/analysis/hr-v0-j2-c07-curved-mesh-repair-p0.1";REL=ROOT/"release/hr-v0/j2-c07-curved-mesh-repair-p0.1"
def need(v,m):
    if not v:raise SystemExit(m)
def rows(p):
    with p.open(newline="",encoding="utf-8-sig") as s:return list(csv.DictReader(s))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def manifest(d):
    rec=rows(d/"file-manifest.csv");act=[p for p in d.rglob("*") if p.is_file() and p.name!="file-manifest.csv"];need(len(rec)==len(act),f"manifest count {d}");m={r["relative_path"]:r for r in rec}
    for p in act:r=m.get(p.relative_to(d).as_posix());need(r and r["sha256"]==sha(p) and int(r["bytes"])==p.stat().st_size,f"manifest drift {p}")
def main():
    for d in (OUT,REL):need(d.is_dir(),f"missing {d}");manifest(d)
    st=json.loads((OUT/"analysis-status.json").read_text());need(st["identifier"]=="HR-V0-J2-C07-CURVED-MESH-REPAIR-P0.1" and st["round"]=="R283","identity");need(st["attempts_executed"]==1 and st["failed_attempts"]==1 and st["promoted_variants"]==0,"attempts")
    need(not any(st[k] for k in ("bounded_mesh_method_route_found","geometry_preserving_curved_mesh_route_found","surface_deviation_from_brep_complete","exact_facet_map_complete","r279_c02_complete","r278_h02_closed","selected","safety_credit","capacity_credit","work_authority","fabrication_authorized","powered_testing_authorized","motion_authorized","energization_authorized")),"false gates")
    v=rows(OUT/"variant-register.csv");need(len(v)==1 and v[0]["variant"]=="V04_REFINED_HIGH_ORDER" and v[0]["mesh_repair_pass"].lower()=="false","V04");need(v[0]["linear_sicn_gate"]==v[0]["curved_jacobian_gate"]==v[0]["element_corner_connectivity_gate"]==v[0]["element_corner_orientation_gate"]==v[0]["occ_corner_membership_gate"]=="PASS","passing bounded screens");need(v[0]["corner_bijection_gate"]==v[0]["corner_identity_gate"]=="FAIL" and float(v[0]["corner_bijection_max_distance_mm"])>float(v[0]["corner_bijection_tolerance_mm"]),"bijection failure")
    raw=ROOT/v[0]["raw_npz"];edge=ROOT/v[0]["edge_map"];need(raw.is_file() and sha(raw)==v[0]["raw_npz_sha256"],"raw");need(edge.is_file() and sha(edge)==v[0]["edge_map_sha256"],"edge")
    for name,count in (("jacobian-screen-register.csv",3),("corner-bijection-v04_refined_high_order.csv",8999),("element-corner-identity-v04_refined_high_order.csv",35148),("occ-corner-membership-v04_refined_high_order.csv",4),("runtime-input-register.csv",6)):need(len(rows(OUT/name))==count,f"{name} count")
    need(len(rows(OUT/"failed-attempt-register.csv"))==1,"failed attempt");print("PASS: R283 V04 raw-evidence rerun synchronized; spatial corner bijection fails, no route promoted, R279-C02/H02/capacity/work authority open");return 0
if __name__=="__main__":raise SystemExit(main())
