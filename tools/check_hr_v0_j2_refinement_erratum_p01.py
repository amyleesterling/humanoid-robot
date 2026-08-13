#!/usr/bin/env python3
"""Fail-closed checks for R282 J2 refinement erratum."""
from __future__ import annotations
import csv,hashlib,json,math
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"mechanical/analysis/hr-v0-j2-refinement-erratum-p0.1";REL=ROOT/"release/hr-v0/j2-refinement-erratum-p0.1"
CURVED=ROOT/"mechanical/analysis/hr-v0-j2-curved-tet10-prototype-p0.1";CURVEDR=ROOT/"release/hr-v0/j2-curved-tet10-prototype-p0.1"
XCHK=ROOT/"mechanical/analysis/hr-v0-j2-backend-crosscheck-p0.1";XCHKR=ROOT/"release/hr-v0/j2-backend-crosscheck-p0.1"
CFG=ROOT/"configuration/hr-v0-config-reconciliation-p0.46";CFGR=ROOT/"release/hr-v0/configuration-reconciliation-p0.46"
R281=ROOT/"mechanical/analysis/hr-v0-j2-numerical-backend-p0.1";R281R=ROOT/"release/hr-v0/j2-numerical-backend-p0.1"
def need(v,m):
    if not v:raise SystemExit(m)
def rows(p):
    with p.open(newline="",encoding="utf-8-sig") as s:return list(csv.DictReader(s))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def manifest(d):
    rec=rows(d/"file-manifest.csv");actual=sorted(p for p in d.rglob("*") if p.is_file() and p.name!="file-manifest.csv");need(len(rec)==len(actual),f"manifest count {d}");mapped={r["relative_path"]:r for r in rec}
    for p in actual:
        rel=p.relative_to(d).as_posix();need(rel in mapped and mapped[rel]["sha256"]==sha(p) and int(mapped[rel]["bytes"])==p.stat().st_size,f"manifest drift {d}/{rel}")
def close(v,t):return math.isclose(float(v),t,rel_tol=1e-8,abs_tol=1e-15)
def main():
    for d in (OUT,REL,CURVED,CURVEDR,XCHK,XCHKR,CFG,CFGR):need(d.is_dir(),f"missing {d}");manifest(d)
    for d in (R281,R281R):need(d.is_dir(),f"missing immutable historical {d}")
    st=json.loads((OUT/"analysis-status.json").read_text(encoding="utf-8"));need(st["identifier"]=="HR-V0-J2-REFINEMENT-ERRATUM-P0.1" and st["round"]=="R282","identity")
    need(st["backend_direct_cg_crosscheck_pass"] and st["affine_patch_test_pass"] and st["c06_curved_import_screen_pass"] and not st["c07_curved_import_screen_pass"],"method disposition")
    forbidden=("monolithic_l0_l3_executed","r281_acc_04_independently_accepted","curved_geometry_order_sensitivity_complete","exact_zone_execution_complete","raw_convergence_evidence_complete","mesh_convergence_complete","r278_h02_closed","nonlinear_contact_complete","joined_joint_complete","selected","capacity_established","fabrication_authorized","powered_testing_authorized","motion_authorized","energization_authorized","safety_credit")
    need(not any(st[k] for k in forbidden),"false gates")
    freeze=rows(OUT/"protocol-freeze-register.csv");need(len(freeze)==6,"freeze rows");gci=next(r for r in freeze if r["control_id"]=="R282-F05")["frozen_definition"];need(all(t in gci for t in ("coarse c=L1","r_cm=h_c/h_m>1","dc_m/dm_f","GCI_cm","GCI_mf","GCI_cm/(r_mf^p*GCI_mf)")),"GCI convention")
    need("geometrically clipped" in next(r for r in freeze if r["control_id"]=="R282-F04")["acceptance"],"clipped h")
    zones=rows(OUT/"exact-zone-register.csv");need(len(zones)==5 and all(r["centroid_or_sample_substitute"]=="PROHIBITED" for r in zones),"zones")
    need(len(rows(OUT/"execution-architecture.csv"))==4 and len(rows(OUT/"open-holds.csv"))==6,"architecture/holds")
    curved=json.loads((CURVED/"analysis-status.json").read_text(encoding="utf-8"));need(len(curved["parts"])==2 and curved["both_import_screens_pass"] is False,"curved status")
    c06=next(r for r in curved["parts"] if r["part"]=="C06");c07=next(r for r in curved["parts"] if r["part"]=="C07");need(c06["mapped_edge_dofs"]==c06["global_edges"] and c06["curved_wrong_or_zero_jacobian_count"]=="0","C06 curved");need(c07["mapped_edge_dofs"]==c07["global_edges"] and c07["curved_wrong_or_zero_jacobian_count"]=="18" and float(c07["curved_signed_jacobian_min"])<0,"C07 fail")
    x=json.loads((XCHK/"analysis-status.json").read_text(encoding="utf-8"));need(x["backend_crosscheck_pass"] and x["affine_patch_test_pass"] and not x["r281_acc_04_closed"],"backend")
    need(close(x["solution_relative_l2_difference"],7.382440192865555e-13),"solver agreement");patch=rows(XCHK/"affine-patch-register.csv");need(len(patch)==2 and max(float(r["relative_dof_error"]) for r in patch)<1e-11,"patch")
    need(st["historical_baseline_commit"]=="f271cbe4fb25ae70044103e88fce7fcfea976dea" and st["historical_r281_artifacts_mutated"] is False,"historical baseline")
    need(sha(R281/"analysis-status.json")=="2bd6684a87771ed21a79085c8f0e7a521caa85a09e8add84773586014585a366","manifest-bound R281 working-byte hash")
    need(sha(R281/"method-register.csv")=="d6bdfe770ebd62d6f53263c209cd10109bdefdc86b8aa6d7451cf8b886874461","immutable R281 method hash")
    historical_attempt=ROOT/"mechanical/analysis/hr-v0-j2-c07-iterative-solver-p0.1/initial-attempt-register.csv";need(sha(historical_attempt)=="bf4b24a6d0d4833b19340afa3417024ba8d7a3bcb8e21ed516dfea8dc2827a5b","immutable C07 attempts hash")
    attempts=rows(historical_attempt);need(len({r["attempt_id"] for r in attempts})==1,"historical duplicate retained")
    errata=rows(OUT/"historical-errata-register.csv");need(len(errata)==4 and all(r["historical_baseline_commit"]==st["historical_baseline_commit"] for r in errata),"errata binding")
    need("two global SICN screens" in errata[0]["correction"] and "non-unique" in errata[1]["correction"] and "linear geometry" in errata[2]["correction"] and "explicit CRLF checkout rules" in errata[3]["correction"],"errata substance")
    cfg=json.loads((CFG/"package-status.json").read_text(encoding="utf-8"));need(cfg["identifier"]=="HR-V0-CONFIG-REC-P0.46" and cfg["round"]=="R282" and cfg["current_records"]==65 and cfg["open_holds"]==382 and cfg["acceptance_rows"]==436,"config")
    need(not cfg["j2_c07_curved_import_screen_pass"] and not cfg["r281_acc_04_independently_accepted"] and not cfg["r278_h02_closed"],"config gates")
    for r in rows(CFG/"source-hash-register.csv"):need(sha(ROOT/r["source_path"])==r["sha256"],f"source hash {r['source_path']}")
    page=(REL/"index.html").read_text(encoding="utf-8");need(all(t in page for t in ("H02 remains open","18 wrong-orientation","What R281 got wrong","two global SICN screens","font:17px","font-size:16px","overflow:auto")),"web");need(page.count("PRELIMINARY - PROTOCOL CORRECTION") == 1,"single web warning")
    need((ROOT/"docs/handoff-current.md").read_text(encoding="utf-8").startswith(("R282 J2 refinement erratum:","R283 J2 execution architecture:","R284 C07 curved-mesh development:")),"handoff");need((ROOT/"docs/review-ledger.md").read_text(encoding="utf-8").count("| R282 |")==1,"ledger");need(any(t in (ROOT/"README.md").read_text(encoding="utf-8") for t in ("Two hundred eighty-two rounds are complete","Two hundred eighty-three rounds are complete","Two hundred eighty-four rounds are complete")),"README")
    print("PASS: R282 protocol correction and bounded method evidence are synchronized; C07 curved screen, H02, capacity and all work authority remain open");return 0
if __name__=="__main__":raise SystemExit(main())
