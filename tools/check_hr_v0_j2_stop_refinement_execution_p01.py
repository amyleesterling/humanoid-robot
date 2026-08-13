#!/usr/bin/env python3
"""Fail-closed checks for R280 bounded J2 refinement execution."""
from __future__ import annotations

import csv
import hashlib
import json
import math
from pathlib import Path


ROOT=Path(__file__).resolve().parents[1]
SRC=ROOT/"mechanical/analysis/hr-v0-j2-stop-refinement-execution-p0.1"
REL=ROOT/"release/hr-v0/j2-stop-refinement-execution-p0.1"
CFG=ROOT/"configuration/hr-v0-config-reconciliation-p0.44"
CFG_REL=ROOT/"release/hr-v0/configuration-reconciliation-p0.44"
WARNING="PRELIMINARY - SCRATCH NUMERICAL EVIDENCE ONLY - NOT APPROVED FOR PROCUREMENT, QUOTATION, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION"


def need(value:bool,message:str)->None:
    if not value:raise SystemExit(message)


def rows(path:Path)->list[dict[str,str]]:
    with path.open(newline="",encoding="utf-8-sig") as stream:return list(csv.DictReader(stream))


def sha(path:Path)->str:return hashlib.sha256(path.read_bytes()).hexdigest()


def check_manifest(directory:Path)->None:
    records=rows(directory/"file-manifest.csv");actual=sorted(p for p in directory.rglob("*") if p.is_file() and p.name!="file-manifest.csv")
    need(len(records)==len(actual),f"manifest count {directory}");mapped={r["relative_path"]:r for r in records}
    for path in actual:
        rel=path.relative_to(directory).as_posix();need(rel in mapped and mapped[rel]["sha256"]==sha(path) and int(mapped[rel]["bytes"])==path.stat().st_size,f"manifest drift {directory}/{rel}")


def close(value:float,target:float,tol:float=1e-8)->bool:return math.isclose(value,target,rel_tol=tol,abs_tol=tol)


def main()->int:
    for directory in (SRC,REL,CFG,CFG_REL):need(directory.is_dir(),f"missing {directory}");check_manifest(directory)
    status=json.loads((SRC/"execution-status.json").read_text(encoding="utf-8"))
    need(status["identifier"]=="HR-V0-J2-STOP-REFINEMENT-EXECUTION-P0.1" and status["round"]=="R279-PROTOTYPE","identity")
    need(status["mesh_executions"]==["C06:L0","C06:P2C","C07:L0"],"mesh executions")
    need(status["case_executions"]==["C06:L0:P1:C06_EXACT_NORMAL_TOP"],"case execution")
    need(status["direct_p2_attempts_interrupted_for_resources"]==2 and len(status["mesh_quality_rejections"])==1 and status["mesh_quality_rejections"][0].startswith("C07:L0"),"failure evidence")
    need(not any(status[k] for k in ("mesh_convergence_complete","r278_h02_closed","nonlinear_contact_complete","joined_joint_complete","selected","fabrication_authorized","powered_testing_authorized","motion_authorized","energization_authorized","safety_credit")),"authority")
    mesh=rows(SRC/"mesh-register.csv");need(len(mesh)==3,"mesh rows")
    mapped={(r["part"],r["level"]):r for r in mesh}
    need((int(mapped[("C06","P2C")]["vertices"]),int(mapped[("C06","P2C")]["tetrahedra"]),int(mapped[("C06","P2C")]["p2_dofs_if_solved"]))==(8027,33102,162702),"coarse mesh")
    need((int(mapped[("C06","L0")]["vertices"]),int(mapped[("C06","L0")]["tetrahedra"]),int(mapped[("C06","L0")]["p2_dofs_if_solved"]))==(40399,197167,884739),"C06 mesh")
    need((int(mapped[("C07","L0")]["vertices"]),int(mapped[("C07","L0")]["tetrahedra"]),int(mapped[("C07","L0")]["p2_dofs_if_solved"]))==(54204,252751,1161459),"C07 mesh")
    need(float(mapped[("C07","L0")]["min_sicn"])<0.10,"C07 quality rejection")
    case=rows(SRC/"case-results.csv");need(len(case)==1 and case[0]["solution_order"]=="1" and case[0]["solution_dofs"]=="121197","case provenance")
    need(close(float(case[0]["normalized_force_balance_error"]),4.9633679897436804e-14) and close(float(case[0]["strain_energy_n_mm"]),0.4002779523587397),"P1 diagnostic arithmetic")
    need(case[0]["convergence_accepted"]=="False" and case[0]["selection_or_release_effect"]=="NONE","P1 credit")
    attempts=rows(SRC/"attempt-register.csv");need(len(attempts)==2 and all(r["result"].endswith("NO STRUCTURAL RESULT") and r["convergence_or_release_credit"]=="NONE" for r in attempts),"attempt boundary")
    need(len(rows(SRC/"open-holds.csv"))==5 and len(rows(SRC/"acceptance-matrix.csv"))==5,"holds")
    page=(REL/"index.html").read_text(encoding="utf-8")
    for token in (WARNING,"The exact mesh path works. The current solver path does not.","R278-H02 remains open","font:17px","font-size:16px","overflow:auto"):
        need(token in page,f"web token {token}")
    cfg=json.loads((CFG/"package-status.json").read_text(encoding="utf-8"))
    need(cfg["identifier"]=="HR-V0-CONFIG-REC-P0.44" and cfg["round"]=="R280","config identity")
    need(cfg["current_records"]==63 and cfg["open_holds"]==371 and cfg["acceptance_rows"]==425,"config count")
    need(cfg["j2_refinement_execution"]==status["identifier"] and cfg["j2_refinement_meshes"]==3 and cfg["j2_refinement_cases"]==1 and cfg["j2_direct_p2_results"]==0 and cfg["r278_h02_closed"] is False,"config evidence")
    for record in rows(CFG/"source-hash-register.csv"):need(sha(ROOT/record["source_path"])==record["sha256"],f"source hash {record['source_path']}")
    need((ROOT/"docs/handoff-current.md").read_text(encoding="utf-8").startswith(("R280 J2 refinement execution feasibility:","R281 J2 numerical backend:","R282 J2 refinement erratum:","R283 J2 execution architecture:")),"handoff")
    need((ROOT/"docs/review-ledger.md").read_text(encoding="utf-8").count("| R280 |")==1,"ledger")
    need(any(text in (ROOT/"README.md").read_text(encoding="utf-8") for text in ("Two hundred eighty rounds are complete","Two hundred eighty-one rounds are complete","Two hundred eighty-two rounds are complete","Two hundred eighty-three rounds are complete")),"README")
    print("PASS: R280 exact local-mesh feasibility evidence is synchronized; P2 produced no results, C07 quality fails, H02 and all work authority remain open")
    return 0


if __name__=="__main__":raise SystemExit(main())
