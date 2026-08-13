#!/usr/bin/env python3
"""Publish R281 bounded P2 backend and C07 mesh-method feasibility evidence."""
from __future__ import annotations

import csv
import hashlib
import html
import json
import shutil
from pathlib import Path


ROOT=Path(__file__).resolve().parents[1]
C06=ROOT/"mechanical/analysis/hr-v0-j2-stop-iterative-solver-p0.1"
MQ=ROOT/"mechanical/analysis/hr-v0-j2-c07-mesh-quality-p0.1"
C07=ROOT/"mechanical/analysis/hr-v0-j2-c07-iterative-solver-p0.1"
OUT=ROOT/"mechanical/analysis/hr-v0-j2-numerical-backend-p0.1"
REL=ROOT/"release/hr-v0/j2-numerical-backend-p0.1"
SUBRELS=((C06,ROOT/"release/hr-v0/j2-stop-iterative-solver-p0.1"),(MQ,ROOT/"release/hr-v0/j2-c07-mesh-quality-p0.1"),(C07,ROOT/"release/hr-v0/j2-c07-iterative-solver-p0.1"))
CFG0=ROOT/"configuration/hr-v0-config-reconciliation-p0.44"
CFG=ROOT/"configuration/hr-v0-config-reconciliation-p0.45"
CFG_REL=ROOT/"release/hr-v0/configuration-reconciliation-p0.45"
IDENT="HR-V0-J2-NUMERICAL-BACKEND-P0.1"
CFG_IDENT="HR-V0-CONFIG-REC-P0.45"
WARNING="PRELIMINARY - NUMERICAL SOLVER FEASIBILITY ONLY - NOT APPROVED FOR PROCUREMENT, QUOTATION, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION"


def rows(path:Path)->list[dict[str,str]]:
    with path.open(newline="",encoding="utf-8-sig") as stream:return list(csv.DictReader(stream))


def write_csv(path:Path,records:list[dict[str,object]])->None:
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open("w",newline="",encoding="utf-8") as stream:
        writer=csv.DictWriter(stream,fieldnames=list(records[0]),lineterminator="\n");writer.writeheader();writer.writerows(records)


def sha(path:Path)->str:return hashlib.sha256(path.read_bytes()).hexdigest()


def manifest(directory:Path)->None:
    records=[{"relative_path":p.relative_to(directory).as_posix(),"sha256":sha(p),"bytes":p.stat().st_size,"warning":WARNING} for p in sorted(directory.rglob("*")) if p.is_file() and p.name!="file-manifest.csv"]
    write_csv(directory/"file-manifest.csv",records)


def table(records:list[dict[str,object]])->str:
    fields=list(records[0]);head="".join(f"<th>{html.escape(k.replace('_',' '))}</th>" for k in fields);body="".join("<tr>"+"".join(f"<td>{html.escape(str(r.get(k,'')))}</td>" for k in fields)+"</tr>" for r in records)
    return f"<div class='scroll'><table><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></div>"


def main()->int:
    for target in (OUT,REL,CFG,CFG_REL,*(target for _source,target in SUBRELS)):
        if target.exists():shutil.rmtree(target)
    OUT.mkdir(parents=True)
    c06=rows(C06/"solver-result.csv");mq=rows(MQ/"mesh-quality-register.csv");c07=rows(C07/"solver-results.csv")
    c06_status=json.loads((C06/"analysis-status.json").read_text(encoding="utf-8"));mq_status=json.loads((MQ/"analysis-status.json").read_text(encoding="utf-8"));c07_status=json.loads((C07/"analysis-status.json").read_text(encoding="utf-8"))
    if not c06_status["bounded_solver_feasibility_pass"] or not c07_status["mesh_quality_pass"] or not c07_status["bounded_solver_cases_pass"]:raise RuntimeError("bounded numerical route not demonstrated")
    cases=[
        {"case_id":"C06_EXACT_NORMAL_TOP","component":"C06","mesh_method":"Gmsh HXT/default optimization P2C","solution_dofs":c06[0]["solution_dofs"],"iterations":c06[0]["iterations"],"true_residual_corrections":0,"relative_residual":c06[0]["relative_condensed_residual"],"full_force_balance":c06[0]["normalized_full_force_balance_error"],"bounded_result":"PASS SOLVER FEASIBILITY ONLY","credit":"NO CONVERGENCE OR CAPACITY CREDIT","warning":WARNING},
        *[{"case_id":r["case_id"],"component":"C07","mesh_method":"Gmsh Delaunay + Netgen P2C","solution_dofs":r["solution_dofs"],"iterations":r["initial_iterations"],"true_residual_corrections":r["true_residual_correction_passes"],"relative_residual":r["relative_condensed_residual"],"full_force_balance":r["normalized_full_force_balance_error"],"bounded_result":"PASS SOLVER FEASIBILITY ONLY","credit":"NO CONVERGENCE OR CAPACITY CREDIT","warning":WARNING} for r in c07],
    ]
    write_csv(OUT/"bounded-case-register.csv",cases)
    failed_attempts=rows(C06/"initial-attempt-register.csv")+rows(C07/"initial-attempt-register.csv")
    write_csv(OUT/"true-residual-attempt-register.csv",failed_attempts)
    method=[{"method_id":"R281-M01","scope":"C06/C07 coarse P2 displacement feasibility","mesh":"exact OCC identity and local fields; straight-sided geometry","solver":"SciPy CG with Jacobi inverse diagonal","requested_rtol":"5e-11","acceptance":"postcomputed residual <=1e-10; full force balance <=1e-8; CG info=0","result":"PASS FOR THREE COARSE CASES","limitations":"no multi-level convergence; no curved P2 geometry; no contact/joined/dynamic/capacity credit","warning":WARNING},{"method_id":"R281-M02","scope":"C07 mesh quality","mesh":"Gmsh algorithm 1 Delaunay + Netgen optimization","solver":"N/A","requested_rtol":"N/A","acceptance":"min SICN >=0.10 and <=0.1% elements below 0.20","result":f"PASS L0: min {mq[0]['minimum_sicn']}; fraction {mq[0]['fraction_sicn_below_0p20']}","limitations":"single level; method not yet executed at L1-L3","warning":WARNING}]
    write_csv(OUT/"method-register.csv",method)
    holds=["Execute C06 and C07 L0-L3 with the bounded iterative method and exact accepted mesh method at every level","Add curved quadratic geometry or independently accepted geometry-order sensitivity before H02 closure","Report fixed zones, gauge-section resultants, moment balance, GCI/order and singularity trends required by R279","Independently verify iterative backend against a second solver/reference problem and accept residual-correction policy","Retain H03 nonlinear contact, H04 joined hardware/frame, dynamics, physical correlation and qualified capacity as separate open gates"]
    write_csv(OUT/"open-holds.csv",[{"hold_id":f"R281-H{i:02d}","hold":h,"state":"OPEN","closure_evidence":"NOT EXECUTED","release_effect":"BLOCKS R278-H02 AND P0.13 SELECTION/FABRICATION/MOTION","warning":WARNING} for i,h in enumerate(holds,1)])
    write_csv(OUT/"acceptance-matrix.csv",[{"acceptance_id":f"R281-ACC-{i:02d}","criterion":h,"execution_state":"NOT EXECUTED","result":"OPEN","evidence_uri":"","approver":"","warning":WARNING} for i,h in enumerate(holds,1)])
    status={"identifier":IDENT,"round":"R281","date":"2026-08-12","cad_identifier":"HR-V0-ARM-ARCH-P0.13-PAD-POCKET-STOP-CANDIDATE","bounded_cases":3,"bounded_cases_pass":3,"postcomputed_residual_gate":1e-10,"full_force_balance_gate":1e-8,"c07_mesh_method":"Gmsh Delaunay algorithm 1 plus Netgen optimization","c07_l0_minimum_sicn":float(mq[0]["minimum_sicn"]),"c07_l0_fraction_below_sicn_0p20":float(mq[0]["fraction_sicn_below_0p20"]),"numerical_backend_route_feasible":True,"mesh_convergence_complete":False,"r278_h02_closed":False,"nonlinear_contact_complete":False,"joined_joint_complete":False,"selected":False,"fabrication_authorized":False,"powered_testing_authorized":False,"motion_authorized":False,"energization_authorized":False,"safety_credit":False,"warning":WARNING}
    (OUT/"analysis-status.json").write_text(json.dumps(status,indent=2)+"\n",encoding="utf-8")
    page=f"""<!doctype html><html lang='en'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'><title>R281 J2 numerical backend</title><style>:root{{--navy:#082b55;--deep:#041a35;--gold:#f4b942;--paper:#f7fbff;--ink:#102a43;--line:#9ccfe8;--green:#147a4b}}*{{box-sizing:border-box}}body{{margin:0;background:var(--paper);color:var(--ink);font:17px/1.55 system-ui,sans-serif}}header{{background:linear-gradient(135deg,var(--deep),var(--navy));color:#fff;padding:clamp(30px,6vw,72px) 20px}}header>div,main{{max-width:1240px;margin:auto}}main{{padding:30px 20px 80px}}h1{{font-size:clamp(36px,6vw,66px);line-height:1.05}}h2{{font-size:clamp(26px,3vw,40px);color:var(--navy)}}.warning{{background:var(--gold);color:#17243a;border:3px solid #8a5b00;padding:15px 18px;font-weight:900}}.decision{{background:white;border:2px solid var(--line);border-left:10px solid var(--green);border-radius:15px;padding:20px;margin:22px 0}}.scroll{{overflow:auto;border:2px solid var(--line);border-radius:12px;background:white}}table{{border-collapse:collapse;width:100%;min-width:1050px}}th,td{{padding:13px 14px;text-align:left;vertical-align:top;border-bottom:1px solid var(--line);font-size:16px}}th{{background:var(--navy);color:white}}@media(max-width:620px){{body{{font-size:16px}}main{{padding-inline:14px}}}}</style></head><body><header><div><p class='warning'>{WARNING}</p><p>R281 &middot; {IDENT}</p><h1>The P2 route is now computationally viable.</h1><p>Three bounded coarse cases meet independently recomputed residual and full-force-balance gates. This unlocks refinement execution, not engineering capacity.</p></div></header><main><section class='decision'><h2>Backend feasibility passes; H02 stays open</h2><p>C06 and both C07 paths solve with quadratic displacement using residual-controlled CG. Delaunay plus Netgen repairs the C07 L0 quality failure. Multi-level convergence, curved geometry, contact, joints, dynamics and physical correlation remain unexecuted.</p></section><section><h2>Bounded cases</h2>{table(cases)}</section><section><h2>Method controls</h2>{table(method)}</section><section><h2>Failed attempts retained</h2>{table(failed_attempts)}</section><section><h2>Open holds</h2>{table(rows(OUT/'open-holds.csv'))}</section></main></body></html>"""
    (OUT/"README.md").write_text(f"# {IDENT}\n\n> **{WARNING}**\n\nR281 establishes a bounded iterative P2 and C07 mesh-quality route for later R279 execution. It does not close H02 or supply capacity/work authority.\n",encoding="utf-8");(OUT/"index.html").write_text(page,encoding="utf-8");manifest(OUT);shutil.copytree(OUT,REL);manifest(REL)
    for source,target in SUBRELS:shutil.copytree(source,target);manifest(source);manifest(target)

    shutil.copytree(CFG0,CFG);current=rows(CFG/"current-configuration-map.csv");current.append({"record_id":"CFG-64","role":"P0.13 J2 stop bounded iterative P2 and C07 mesh-method feasibility","identifier":IDENT,"source_path":"release/hr-v0/j2-numerical-backend-p0.1/analysis-status.json","configuration_state":"CURRENT NUMERICAL METHOD EVIDENCE - H02 OPEN / NO CAPACITY CREDIT","release_boundary":"L0-L3/GCI/curved geometry/independent solver verification plus H03/H04/dynamic/physical/qualified closure","warning":WARNING});write_csv(CFG/"current-configuration-map.csv",current)
    ch,ca=rows(CFG/"open-holds.csv"),rows(CFG/"acceptance-matrix.csv")
    for hold in rows(OUT/"open-holds.csv"):
        ch.append({"hold_id":f"HOLD-{len(ch)+1:03d}","hold":f"{IDENT}: {hold['hold']}","state":"NOT EXECUTED","closure_evidence":"controlled numerical/physical evidence and qualified acceptance","warning":WARNING});ca.append({"acceptance_id":f"ACC-{len(ca)+1:03d}","criterion":f"{IDENT}: {hold['hold']}","execution_state":"NOT EXECUTED","result":"OPEN","evidence_uri":"","approver":"","warning":WARNING})
    write_csv(CFG/"open-holds.csv",ch);write_csv(CFG/"acceptance-matrix.csv",ca);gates=rows(CFG/"gate-impact.csv")
    for gate in gates:
        if gate["gate_id"] in {"EG-005","EG-006"}:gate["evidence_added"]+=f"; {IDENT} bounded iterative P2/C07 quality route";gate["remaining_evidence"]+="; L0-L3/GCI/curved geometry/independent solver verification; H03/H04/dynamic/physical/qualified closure"
    write_csv(CFG/"gate-impact.csv",gates);cfg=json.loads((CFG/"package-status.json").read_text(encoding="utf-8"));cfg.update({"identifier":CFG_IDENT,"round":"R281","current_records":len(current),"open_holds":len(ch),"acceptance_rows":len(ca),"j2_numerical_backend":IDENT,"j2_bounded_p2_cases_passed":3,"j2_c07_mesh_quality_route_feasible":True,"r278_h02_closed":False,"fabrication_authorized":False,"powered_testing_authorized":False,"motion_authorized":False,"energization_authorized":False,"safety_credit":False});(CFG/"package-status.json").write_text(json.dumps(cfg,indent=2)+"\n",encoding="utf-8");(CFG/"README.md").write_text(f"# {CFG_IDENT}\n\n> **{WARNING}**\n\nR281 indexes bounded numerical method evidence. H02 and every work authority remain open.\n",encoding="utf-8");write_csv(CFG/"source-hash-register.csv",[{"source_path":r["source_path"],"sha256":sha(ROOT/r["source_path"]),"role":r["role"],"warning":WARNING} for r in current]);shutil.copy2(OUT/"index.html",CFG/"index.html");manifest(CFG);shutil.copytree(CFG,CFG_REL);manifest(CFG_REL)
    (ROOT/"docs/hr-v0-j2-numerical-backend-p0.1.md").write_text(f"# HR-V0 J2 numerical backend P0.1\n\n> **{WARNING}**\n\nR281 establishes a bounded iterative P2 route for C06 and both C07 load paths. All three coarse cases pass postcomputed residual <=1e-10 and full-force balance <=1e-8. Delaunay plus Netgen raises the C07 L0 minimum SICN to {mq[0]['minimum_sicn']} and passes the R279 quality gate. Failed true-residual attempts remain recorded.\n\nThis only makes the next convergence run computationally viable. H02, curved-geometry sensitivity, independent solver verification, H03/H04, dynamics and physical correlation remain open.\n\n[Interactive numerical guide](../release/hr-v0/j2-numerical-backend-p0.1/index.html)\n",encoding="utf-8");(ROOT/"docs/reviews/2026-08-12-r281-independent-review-request.md").write_text(f"# R281 independent review request\n\n> **{WARNING}**\n\nPlease review `{IDENT}` for SPD/CG applicability, Jacobi preconditioner, condensation, postcomputed residual policy, residual-correction solve, force balance, P2/straight-sided geometry disclosure, exact C07 method/quality metrics, failed-attempt retention and zero convergence/capacity/work credit.\n",encoding="utf-8")
    handoff=ROOT/"docs/handoff-current.md";old=handoff.read_text(encoding="utf-8")
    if not old.startswith("R281 J2 numerical backend:"):handoff.write_text(f"R281 J2 numerical backend: **`{IDENT}` establishes a bounded residual-controlled iterative P2 route for C06 and both C07 paths and a C07 mesh method passing SICN quality. This enables L0-L3 execution but does not close H02 or grant capacity/work credit.**\n\n"+old,encoding="utf-8")
    ledger=ROOT/"docs/review-ledger.md";text=ledger.read_text(encoding="utf-8").replace("Two hundred eighty rounds are complete (R01-R280).","Two hundred eighty-one rounds are complete (R01-R281).")
    if "| R281 |" not in text:text=text.rstrip()+f"\n| R281 | 2026-08-12 | Bounded iterative P2 and C07 mesh-method feasibility | Codex project-owned numerical-method execution; not independent or qualified review | R280 showed exact tags worked but direct P2 exhausted memory and C07 HXT L0 failed quality. | Residual-controlled Jacobi-CG passes C06 and both C07 coarse P2 cases; Delaunay+Netgen passes C07 L0 SICN. Failed true-residual attempts remain. This enables but does not execute L0-L3 convergence; H02/H03/H04 remain open. | `docs/hr-v0-j2-numerical-backend-p0.1.md`; `release/hr-v0/j2-numerical-backend-p0.1/`; `configuration/hr-v0-config-reconciliation-p0.45/` |\n"
    ledger.write_text(text,encoding="utf-8");readme=ROOT/"README.md";text=readme.read_text(encoding="utf-8");marker="## Start here\n\n";links="- [R281 bounded J2 numerical backend](docs/hr-v0-j2-numerical-backend-p0.1.md)\n- [R281 independent review request](docs/reviews/2026-08-12-r281-independent-review-request.md)\n- [Interactive R281 numerical guide](release/hr-v0/j2-numerical-backend-p0.1/index.html)\n- [Interactive configuration reconciliation P0.45](release/hr-v0/configuration-reconciliation-p0.45/index.html)\n"
    if links.splitlines()[0] not in text:text=text.replace(marker,marker+links)
    text=text.replace("Two hundred eighty rounds are complete: R01-R280.","Two hundred eighty-one rounds are complete: R01-R281.");readme.write_text(text,encoding="utf-8");import generate_hr_v0_collapse_envelope as generated_manifest;generated_manifest.write_generated_source_manifest();print(f"Published R281 {IDENT}; numerical route feasible, H02 and all work authority open");return 0


if __name__=="__main__":raise SystemExit(main())
