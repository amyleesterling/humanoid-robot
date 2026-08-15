#!/usr/bin/env python3
"""Fail-closed checks for R279 J2 stop refinement protocol."""
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path


ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"mechanical/analysis/hr-v0-j2-stop-refinement-protocol-p0.1"
REL=ROOT/"release/hr-v0/j2-stop-refinement-protocol-p0.1"
CFG=ROOT/"configuration/hr-v0-config-reconciliation-p0.43"
CFG_REL=ROOT/"release/hr-v0/configuration-reconciliation-p0.43"
WARNING="PRELIMINARY - NOT APPROVED FOR PROCUREMENT, QUOTATION, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION"


def need(value: bool, message: str) -> None:
    if not value: raise SystemExit(message)


def rows(path: Path) -> list[dict[str,str]]:
    with path.open(newline="",encoding="utf-8-sig") as stream: return list(csv.DictReader(stream))


def sha(path: Path) -> str: return hashlib.sha256(path.read_bytes()).hexdigest()


def check_manifest(directory: Path) -> None:
    records=rows(directory/"file-manifest.csv")
    actual=sorted(p for p in directory.rglob("*") if p.is_file() and p.name!="file-manifest.csv")
    need(len(records)==len(actual),f"manifest count {directory}")
    mapped={r["relative_path"]:r for r in records}
    for path in actual:
        rel=path.relative_to(directory).as_posix()
        need(rel in mapped and mapped[rel]["sha256"]==sha(path) and int(mapped[rel]["bytes"])==path.stat().st_size,f"manifest drift {directory}/{rel}")


def main() -> int:
    for directory in (OUT,REL,CFG,CFG_REL): need(directory.is_dir(),f"missing {directory}"); check_manifest(directory)
    status=json.loads((OUT/"analysis-status.json").read_text(encoding="utf-8"))
    need(status["identifier"]=="HR-V0-J2-STOP-REFINEMENT-PROTOCOL-P0.1" and status["round"]=="R279","identity")
    need(status["r278_metrics_audited"]==18 and status["r278_metrics_over_5_percent"]==13,"audit count")
    need(status["protocol_zones"]==7 and status["mesh_levels"]==4 and status["acceptance_criteria"]==10,"protocol count")
    need(status["mesh_refinement_hold_closed"] is False and status["execution_complete"] is False,"false closure")
    need(not any(status[k] for k in ("selected","fabrication_authorized","powered_testing_authorized","motion_authorized","energization_authorized","safety_credit")),"authority")
    audit=rows(OUT/"r278-instability-audit.csv")
    need(len(audit)==18 and sum(r["diagnostic"]=="NOT STABLE" for r in audit)==13,"audit rows")
    need(max(float(r["last_pair_relative_change"]) for r in audit)>0.18,"instability lost")
    mesh=rows(OUT/"mesh-plan.csv")
    need([float(r["pocket_max_mm"]) for r in mesh]==[0.26,0.18,0.13,0.09],"pocket mesh plan")
    need(all(float(r["growth_max"])<=1.4 for r in mesh),"growth plan")
    zones=rows(OUT/"physical-zone-register.csv")
    need({r["zone_id"] for r in zones}=={"C06-RR-PROFILE","C06-RR-STEP","C06-GAUGE","C07-PE-STRAIGHTS/CORNERS","C07-PF","C07-GAUGE","H1-H4/E1-E2"},"zone identity")
    criteria=rows(OUT/"acceptance-criteria.csv")
    need(len(criteria)==10 and any("GCI95" in r["acceptance"] for r in criteria) and any("P2" in r["acceptance"] for r in criteria),"criteria")
    need(all(r["capacity_use"].startswith("PROHIBITED") for r in rows(OUT/"singularity-register.csv")),"singularity capacity boundary")
    need(len(rows(OUT/"open-holds.csv"))==4 and len(rows(OUT/"acceptance-matrix.csv"))==4,"holds")
    page=(REL/"index.html").read_text(encoding="utf-8")
    for token in (WARNING,"A coarse mesh is not convergence","13 of 18","R278-H02 remains open","font:17px","font-size:16px","overflow:auto"):
        need(token in page,f"web token {token}")
    cfg=json.loads((CFG/"package-status.json").read_text(encoding="utf-8"))
    need(cfg["identifier"]=="HR-V0-CONFIG-REC-P0.43" and cfg["round"]=="R279","config identity")
    need(cfg["current_records"]==62 and cfg["open_holds"]==366 and cfg["acceptance_rows"]==420,"config counts")
    need(cfg["j2_refinement_protocol"]==status["identifier"] and cfg["j2_refinement_protocol_executed"] is False and cfg["r278_h02_closed"] is False,"config boundary")
    for record in rows(CFG/"source-hash-register.csv"): need(sha(ROOT/record["source_path"])==record["sha256"],f"source hash {record['source_path']}")
    need((ROOT/"docs/handoff-current.md").read_text(encoding="utf-8").startswith(("R279 J2 convergence protocol:","R280 J2 refinement execution feasibility:","R281 J2 numerical backend:","R282 J2 refinement erratum:","R283 J2 execution architecture:","R284 C07 curved-mesh development:", "R285 targeted C07 remesh:")),"handoff")
    need((ROOT/"docs/review-ledger.md").read_text(encoding="utf-8").count("| R279 |")==1,"ledger")
    need(any(text in (ROOT/"README.md").read_text(encoding="utf-8") for text in ("Two hundred seventy-nine rounds are complete","Two hundred eighty rounds are complete","Two hundred eighty-one rounds are complete","Two hundred eighty-two rounds are complete","Two hundred eighty-three rounds are complete","Two hundred eighty-four rounds are complete", "Two hundred eighty-five rounds are complete")),"README")
    print("PASS: R279 exact local convergence protocol is synchronized and unexecuted; R278-H02 and all work authority remain open")
    return 0


if __name__=="__main__": raise SystemExit(main())
