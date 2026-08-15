#!/usr/bin/env python3
"""Fail-closed checker for the R285 targeted-remesh disposition."""
import csv,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];FEATURE=ROOT/"mechanical/analysis/hr-v0-j2-c07-target-feature-identity-p0.1";REMESH=ROOT/"mechanical/analysis/hr-v0-j2-c07-targeted-remesh-p0.1";OUT=ROOT/"mechanical/analysis/hr-v0-j2-targeted-remesh-disposition-p0.1";REL=ROOT/"release/hr-v0/j2-targeted-remesh-disposition-p0.1";CFG=ROOT/"configuration/hr-v0-config-reconciliation-p0.49";CFGREL=ROOT/"release/hr-v0/configuration-reconciliation-p0.49"
def need(x,m):
    if not x:raise SystemExit(m)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def rows(p):
    with p.open(newline="",encoding="utf-8-sig") as s:return list(csv.DictReader(s))
def manifest(d):
    data=rows(d/"file-manifest.csv");actual=[p for p in d.rglob("*") if p.is_file() and p.name!="file-manifest.csv"];need(len(data)==len(actual),f"manifest count {d}");mapped={r["relative_path"]:r for r in data}
    for p in actual:r=p.relative_to(d).as_posix();need(r in mapped and mapped[r]["sha256"]==sha(p) and int(mapped[r]["bytes"])==p.stat().st_size,f"manifest {d.name}/{r}")
def parity(a,b):need({p.relative_to(a).as_posix():sha(p) for p in a.rglob("*") if p.is_file()}=={p.relative_to(b).as_posix():sha(p) for p in b.rglob("*") if p.is_file()},f"parity {a.name}")
def main():
    for d in (OUT,REL,CFG,CFGREL):need(d.is_dir(),f"missing {d}");manifest(d)
    parity(OUT,REL);parity(CFG,CFGREL);parity(FEATURE,ROOT/"release/hr-v0/j2-c07-target-feature-identity-p0.1");parity(REMESH,ROOT/"release/hr-v0/j2-c07-targeted-remesh-p0.1")
    fs=json.loads((FEATURE/"analysis-status.json").read_text());need(fs["surface_entities"]==12 and fs["boundary_curve_entities"]==46 and fs["feature_topology_gate"],"feature identity")
    rs=json.loads((REMESH/"analysis-status.json").read_text());need(rs["runs_executed"]==3 and rs["all_runs_pass"] and rs["raw_arrays_exactly_repeatable"] and rs["bounded_targeted_method_screen_pass"],"remesh result")
    need(not any(rs[k] for k in ("surface_deviation_from_brep_complete","exact_facet_map_complete","exact_zone_clipped_histograms_complete","full_domain_curved_jacobian_positivity_proven","load_boundary_preservation_complete","r279_c02_complete","r278_h02_closed","selected","safety_credit","capacity_credit","work_authority","fabrication_authorized","powered_testing_authorized","motion_authorized","energization_authorized")),"remesh boundary")
    variants=rows(REMESH/"variant-summary.csv");need(len(variants)==3 and {r["run_id"] for r in variants}=={"run-a","run-b-repeat","run-c-repeat"},"fresh runs");need(all(int(r["curved_wrong_or_zero_across_screens"])==0 and int(r["normalized_determinant_fail_across_screens"])==0 and r["mesh_repair_pass"]=="True" for r in variants),"sampled screens")
    status=json.loads((OUT/"analysis-status.json").read_text());need(status["identifier"]=="HR-V0-J2-TARGETED-REMESH-DISPOSITION-P0.1" and status["round"]=="R285","identity");need(status["exact_target_feature_identity_complete"] and status["targeted_remesh_three_run_repeatability_complete"] and status["bounded_sampled_jacobian_method_candidate_found"],"bounded advance")
    false=("surface_deviation_from_brep_complete","exact_facet_map_complete","exact_zone_clipped_histograms_complete","full_domain_curved_jacobian_positivity_proven","load_boundary_preservation_complete","r279_c02_complete","structural_solution_executed","mesh_convergence_complete","independent_numerical_acceptance_complete","r278_h02_closed","capacity_established","selected","safety_credit","procurement_authorized","fabrication_authorized","assembly_authorized","connection_authorized","powered_testing_authorized","motion_authorized","energization_authorized");need(not any(status[k] for k in false),"disposition boundary")
    need(len(rows(OUT/"finding-register.csv"))==8 and len(rows(OUT/"open-holds.csv"))==8 and len(rows(OUT/"acceptance-matrix.csv"))==8,"disposition tables")
    for r in rows(OUT/"exact-input-register.csv"):need(sha(ROOT/r["source_path"])==r["sha256"],f"input {r['source_path']}")
    cfg=json.loads((CFG/"package-status.json").read_text());need(cfg["identifier"]=="HR-V0-CONFIG-REC-P0.49" and cfg["round"]=="R285","config identity");need(cfg["current_records"]==75 and cfg["open_holds"]==408 and cfg["acceptance_rows"]==459,"config counts")
    need(cfg["bounded_sampled_jacobian_method_candidate_found"] and not any(cfg[k] for k in ("surface_deviation_from_brep_complete","exact_facet_map_complete","exact_zone_clipped_histograms_complete","full_domain_curved_jacobian_positivity_proven","load_boundary_preservation_complete","r279_c02_complete","r278_h02_closed","capacity_established","selected","safety_credit","fabrication_authorized","powered_testing_authorized","motion_authorized","energization_authorized")),"config boundary")
    for r in rows(CFG/"source-hash-register.csv"):need(sha(ROOT/r["source_path"])==r["sha256"],f"config source {r['source_path']}")
    page=(REL/"index.html").read_text();need(all(x in page for x in ("The targeted mesh repeats","Engineering closure does not","font-size:16px","overflow:auto","R279-C02","R278-H02")),"guide")
    need((ROOT/"docs/handoff-current.md").read_text().startswith("R285 targeted C07 remesh:"),"handoff");need((ROOT/"docs/review-ledger.md").read_text().count("| R285 | ")==1,"ledger");need("Two hundred eighty-five rounds are complete: R01-R285." in (ROOT/"README.md").read_text(),"README count")
    need((ROOT/"docs/reviews/2026-08-13-r285-independent-review-request.md").is_file() and (ROOT/"docs/reviews/2026-08-13-r285-validation-record.md").is_file(),"review docs")
    print("PASS: R285 targeted-remesh disposition synchronized; exact B-Rep/facet/load/full-domain/exact-zone/R279-C02/H02/capacity/all authority open")
if __name__=="__main__":main()
