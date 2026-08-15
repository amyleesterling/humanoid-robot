#!/usr/bin/env python3
"""Fail-closed checks for R281 bounded J2 numerical backend evidence."""
from __future__ import annotations
import csv,hashlib,json,math
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"mechanical/analysis/hr-v0-j2-numerical-backend-p0.1";REL=ROOT/"release/hr-v0/j2-numerical-backend-p0.1"
C06=ROOT/"mechanical/analysis/hr-v0-j2-stop-iterative-solver-p0.1";C06R=ROOT/"release/hr-v0/j2-stop-iterative-solver-p0.1"
MQ=ROOT/"mechanical/analysis/hr-v0-j2-c07-mesh-quality-p0.1";MQR=ROOT/"release/hr-v0/j2-c07-mesh-quality-p0.1"
C07=ROOT/"mechanical/analysis/hr-v0-j2-c07-iterative-solver-p0.1";C07R=ROOT/"release/hr-v0/j2-c07-iterative-solver-p0.1"
CFG=ROOT/"configuration/hr-v0-config-reconciliation-p0.45";CFGR=ROOT/"release/hr-v0/configuration-reconciliation-p0.45"
WARNING="PRELIMINARY - NUMERICAL SOLVER FEASIBILITY ONLY - NOT APPROVED FOR PROCUREMENT, QUOTATION, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION"

def need(v,m):
    if not v:raise SystemExit(m)
def rows(p):
    with p.open(newline="",encoding="utf-8-sig") as s:return list(csv.DictReader(s))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def manifest(d):
    rec=rows(d/"file-manifest.csv");act=sorted(p for p in d.rglob("*") if p.is_file() and p.name!="file-manifest.csv");need(len(rec)==len(act),f"manifest count {d}");mapped={r["relative_path"]:r for r in rec}
    for p in act:
        rel=p.relative_to(d).as_posix();need(rel in mapped and mapped[rel]["sha256"]==sha(p) and int(mapped[rel]["bytes"])==p.stat().st_size,f"manifest drift {d}/{rel}")
def close(v,t):return math.isclose(float(v),t,rel_tol=1e-9,abs_tol=1e-12)
def main():
    for d in (OUT,REL,C06,C06R,MQ,MQR,C07,C07R,CFG,CFGR):need(d.is_dir(),f"missing {d}");manifest(d)
    st=json.loads((OUT/"analysis-status.json").read_text(encoding="utf-8"));need(st["identifier"]=="HR-V0-J2-NUMERICAL-BACKEND-P0.1" and st["round"]=="R281","identity")
    need(st["bounded_cases"]==3 and st["bounded_cases_pass"]==3 and st["numerical_backend_route_feasible"] is True,"route")
    need(st["c07_l0_minimum_sicn"]>=0.10 and st["c07_l0_fraction_below_sicn_0p20"]<=0.001,"quality")
    need(not any(st[k] for k in ("mesh_convergence_complete","r278_h02_closed","nonlinear_contact_complete","joined_joint_complete","selected","fabrication_authorized","powered_testing_authorized","motion_authorized","energization_authorized","safety_credit")),"authority")
    c06=rows(C06/"solver-result.csv")[0];need(c06["solution_order"]=="2" and c06["solution_dofs"]=="162702" and c06["iterations"]=="2754","C06 provenance");need(close(c06["relative_condensed_residual"],5.4575313727116744e-11) and close(c06["normalized_full_force_balance_error"],2.7138411183006767e-13),"C06 arithmetic")
    need(float(rows(C06/"initial-attempt-register.csv")[0]["postcomputed_relative_residual"])>1e-10,"C06 failure retention")
    mq=rows(MQ/"mesh-quality-register.csv");need(len(mq)==1 and mq[0]["variant"]=="DELAUNAY_NETGEN" and mq[0]["quality_gate"]=="PASS","mesh method")
    c07=rows(C07/"solver-results.csv");need(len(c07)==2 and all(r["bounded_solver_feasibility"]=="PASS" for r in c07),"C07 cases");need(all(float(r["relative_condensed_residual"])<=1e-10 and float(r["normalized_full_force_balance_error"])<=1e-8 for r in c07),"C07 residual")
    floor=next(r for r in c07 if "POCKET_FLOOR" in r["case_id"]);need(floor["true_residual_correction_passes"]=="1" and floor["true_residual_correction_iterations"]=="2226","correction")
    initial=rows(C07/"initial-attempt-register.csv");need(any("POCKET_FLOOR" in r["case_id"] and float(r["postcomputed_relative_residual"])>1e-10 for r in initial),"C07 failure retention")
    need(len(rows(OUT/"bounded-case-register.csv"))==3 and len(rows(OUT/"open-holds.csv"))==5,"integration rows")
    page=(REL/"index.html").read_text(encoding="utf-8")
    for token in (WARNING,"The P2 route is now computationally viable","H02 stays open","font:17px","font-size:16px","overflow:auto"):need(token in page,f"web {token}")
    cfg=json.loads((CFG/"package-status.json").read_text(encoding="utf-8"));need(cfg["identifier"]=="HR-V0-CONFIG-REC-P0.45" and cfg["round"]=="R281","config identity");need(cfg["current_records"]==64 and cfg["open_holds"]==376 and cfg["acceptance_rows"]==430,"config count");need(cfg["j2_bounded_p2_cases_passed"]==3 and cfg["j2_c07_mesh_quality_route_feasible"] is True and cfg["r278_h02_closed"] is False,"config evidence")
    for r in rows(CFG/"source-hash-register.csv"):need(sha(ROOT/r["source_path"])==r["sha256"],f"source hash {r['source_path']}")
    current_handoff=(ROOT/"docs/handoff-current.md").read_text(encoding="utf-8")
    current_readme=(ROOT/"README.md").read_text(encoding="utf-8")
    if current_handoff.startswith(("R282 J2 refinement erratum:", "R283 J2 execution architecture:", "R284 C07 curved-mesh development:", "R285 targeted C07 remesh:")) and any(text in current_readme for text in ("Two hundred eighty-two rounds are complete", "Two hundred eighty-three rounds are complete", "Two hundred eighty-four rounds are complete", "Two hundred eighty-five rounds are complete")):
        need((ROOT/"docs/review-ledger.md").read_text(encoding="utf-8").count("| R281 |")==1,"ledger")
        print("PASS: R281 residual-controlled P2/C07 mesh route is synchronized; R282 erratum is current and all work authority remains open")
        return 0
    need((ROOT/"docs/handoff-current.md").read_text(encoding="utf-8").startswith("R281 J2 numerical backend:"),"handoff");need((ROOT/"docs/review-ledger.md").read_text(encoding="utf-8").count("| R281 |")==1,"ledger");need("Two hundred eighty-one rounds are complete" in (ROOT/"README.md").read_text(encoding="utf-8"),"README")
    print("PASS: R281 residual-controlled P2/C07 mesh route is synchronized; multi-level convergence, H02 and all work authority remain open");return 0
if __name__=="__main__":raise SystemExit(main())
