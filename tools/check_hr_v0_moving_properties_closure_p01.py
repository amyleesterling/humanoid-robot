#!/usr/bin/env python3
"""Validate R248 moving-properties contract and P0.12 reconciliation."""
from __future__ import annotations

import csv
import hashlib
import importlib.util
import json
import math
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SRC=ROOT/"mechanical/metrology/hr-v0-moving-properties-closure-p0.1"
REL=ROOT/"release/hr-v0/moving-properties-closure-p0.1"
CFG=ROOT/"configuration/hr-v0-config-reconciliation-p0.12"
CFG_REL=ROOT/"release/hr-v0/configuration-reconciliation-p0.12"
WARNING="PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION"


def rows(path):
    with path.open(encoding="utf-8-sig",newline="") as handle: return list(csv.DictReader(handle))


def digest(path): return hashlib.sha256(path.read_bytes()).hexdigest()


def check_manifest(directory,fail):
    records=rows(directory/"file-manifest.csv")
    actual={p.relative_to(directory).as_posix() for p in directory.rglob("*") if p.is_file() and p.name!="file-manifest.csv"}
    fail({r["path"] for r in records}!=actual,f"manifest membership: {directory}")
    for record in records:
        path=directory/record["path"]
        fail(not path.is_file() or path.stat().st_size!=int(record["bytes"]) or digest(path)!=record["sha256"],f"manifest hash: {path}")


def main():
    errors=[]
    fail=lambda condition,message: errors.append(message) if condition else None
    csv_names={"ledger-coverage.csv","measurement-configuration.csv","instrument-register.csv","loose-mass-result-template.csv","mass-repeat-template.csv","assembly-mass-closure-template.csv","reaction-com-template.csv","pendulum-calibration-template.csv","inertia-result-template.csv","uncertainty-budget-template.csv","calculation-contract.csv","source-register.csv","open-holds.csv","acceptance-matrix.csv"}
    common=csv_names|{"README.md","package-status.json","file-manifest.csv"}
    fail(not SRC.is_dir() or {p.name for p in SRC.iterdir() if p.is_file()}!=common,"source membership")
    fail(not REL.is_dir() or {p.name for p in REL.iterdir() if p.is_file()}!=common|{"index.html"},"release membership")
    check_manifest(SRC,fail); check_manifest(REL,fail)
    for name in common-{"file-manifest.csv"}: fail((SRC/name).read_bytes()!=(REL/name).read_bytes(),f"source/release parity: {name}")
    status=json.loads((REL/"package-status.json").read_text(encoding="utf-8"))
    expected={"identifier":"HR-V0-MOVING-PROP-CLOSURE-P0.1","round":"R248","state":"BLANK EXECUTION CONTRACT","ledger_rows":17,"configurations":4,"mass_repeat_rows":170,"com_rows":8,"pendulum_calibration_rows":4,"inertia_rows":6,"open_holds":12,"acceptance_rows":10,"physical_measurements":0,"accepted_properties":0,"warning":WARNING}
    for key,value in expected.items(): fail(status.get(key)!=value,f"status {key}")
    for key in ("b010_closed","r247_h11_closed","procurement_authorized","fabrication_authorized","assembly_authorized","connection_authorized","powered_testing_authorized","motion_authorized","energization_authorized","safety_credit"):
        fail(status.get(key) is not False,f"{key} must be false")
    ledger=rows(ROOT/"bom/hr-v0-moving-mass-ledger.csv"); coverage=rows(REL/"ledger-coverage.csv")
    fail(len(ledger)!=17 or len(coverage)!=17,"17-row ledger coverage")
    fail({r["mass_id"] for r in ledger}!={r["ledger_id"] for r in coverage},"ledger ID coverage")
    fail(any(r["execution_state"]!="NOT EXECUTED" or r["accepted_result"] or r["evidence_uri"] for r in coverage),"coverage must stay blank")
    checks=[("measurement-configuration.csv",4),("instrument-register.csv",6),("loose-mass-result-template.csv",17),("mass-repeat-template.csv",170),("assembly-mass-closure-template.csv",4),("reaction-com-template.csv",8),("pendulum-calibration-template.csv",4),("inertia-result-template.csv",6),("uncertainty-budget-template.csv",17),("calculation-contract.csv",6),("source-register.csv",4),("open-holds.csv",12),("acceptance-matrix.csv",10)]
    for name,count in checks: fail(len(rows(REL/name))!=count,f"{name}: expected {count}")
    for name in csv_names:
        data=rows(REL/name)
        fail(any(r.get("warning")!=WARNING for r in data),f"warning: {name}")
    for name in ("loose-mass-result-template.csv","assembly-mass-closure-template.csv","reaction-com-template.csv","pendulum-calibration-template.csv","inertia-result-template.csv"):
        fail(any(r.get("execution_state")!="NOT EXECUTED" for r in rows(REL/name)),f"unexecuted template: {name}")
    fail(any(r.get("state")!="NOT EXECUTED" for r in rows(REL/"mass-repeat-template.csv")),"unexecuted template: mass-repeat-template.csv")
    fail(any(r["mean_mass_g"] or r["expanded_uncertainty_g"] or r["raw_repeat_uri"] for r in rows(REL/"loose-mass-result-template.csv")),"mass result fields must be blank")
    fail(any(r["reaction_a_N"] or r["reaction_b_N"] or r["calculated_com_mm"] for r in rows(REL/"reaction-com-template.csv")),"COM fields must be blank")
    fail(any(r["fitted_K"] or r["calculated_inertia_kg_m2"] for r in rows(REL/"inertia-result-template.csv")),"inertia fields must be blank")
    fail(any(r["state"]!="OPEN" for r in rows(REL/"open-holds.csv")),"holds must be open")
    fail(any(r["result"]!="OPEN" or r["execution_state"]!="NOT EXECUTED" for r in rows(REL/"acceptance-matrix.csv")),"acceptances must be open")
    sources={r["source_id"]:r for r in rows(REL/"source-register.csv")}
    fail(set(sources)!={"SRC-01","SRC-02","SRC-03","SRC-04"},"primary source register")
    fail("NIST.IR.6969-2019" not in sources["SRC-01"]["url_or_path"] or "ntrs.nasa.gov" not in sources["SRC-03"]["url_or_path"],"NIST/NASA source URLs")
    page=(REL/"index.html").read_text(encoding="utf-8")
    for token in (WARNING,"font:clamp(16px","font-size:14px","BLANK EXECUTION CONTRACT","B-010 AND R247-H11 REMAIN OPEN","ledger-coverage.csv"):
        fail(token not in page,f"web token: {token}")

    spec=importlib.util.spec_from_file_location("moving_calc",ROOT/"tools/calculate_hr_v0_moving_properties_p01.py")
    mod=importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
    base={"execution_state":"EXECUTED","acceptance":"ACCEPTED"}
    c=dict(base,support_a_coordinate_mm="0",support_b_coordinate_mm="1000",reaction_a_N="70",reaction_b_N="30",independent_mass_kg=str(100/9.80665))
    out=mod.com(c); fail(not math.isclose(out["calculated_com_mm"],300,abs_tol=1e-10),"synthetic COM formula")
    cal1=dict(base,pendulum_mass_kg="1",body_mass_kg="1",known_body_inertia_kg_m2="0.1",mean_period_s="2")
    cal2=dict(base,pendulum_mass_kg="1",body_mass_kg="2",known_body_inertia_kg_m2="0.5",mean_period_s="3")
    article=dict(base,article_mass_kg="1.5",mean_period_s="2.5")
    try: inertia=mod.inertia(cal1,cal2,article)
    except ValueError as exc: fail(True,f"synthetic inertia formula: {exc}"); inertia={}
    fail(not inertia or inertia.get("fitted_K",0)<=0 or inertia.get("calculated_inertia_kg_m2",0)<=0,"synthetic calibrated inertia result")
    try: mod.com(dict(c,execution_state="NOT EXECUTED")); fail(True,"calculator accepted unexecuted COM")
    except ValueError: pass

    cfg_common={"README.md","current-configuration-map.csv","supersession-map.csv","bom-integration-map.csv","gate-impact.csv","open-holds.csv","acceptance-matrix.csv","package-status.json","source-hash-register.csv","file-manifest.csv"}
    fail({p.name for p in CFG.iterdir() if p.is_file()}!=cfg_common,"config membership")
    fail({p.name for p in CFG_REL.iterdir() if p.is_file()}!=cfg_common|{"index.html"},"config release membership")
    check_manifest(CFG,fail); check_manifest(CFG_REL,fail)
    cfg=json.loads((CFG_REL/"package-status.json").read_text(encoding="utf-8"))
    for key,value in {"identifier":"HR-V0-CONFIG-REC-P0.12","round":"R248","current_records":32,"supersession_records":19,"open_holds":50,"acceptance_rows":73,"moving_properties_closure":"HR-V0-MOVING-PROP-CLOSURE-P0.1"}.items(): fail(cfg.get(key)!=value,f"config {key}")
    current=rows(CFG_REL/"current-configuration-map.csv")
    fail(len(current)!=32 or current[-1]["identifier"]!="HR-V0-MOVING-PROP-CLOSURE-P0.1","32 config records")
    hashes=rows(CFG_REL/"source-hash-register.csv"); fail(len(hashes)!=32,"32 source hashes")
    for record in hashes:
        path=ROOT/record["source_path"]
        if record["source_path"] in {"bom/bom.csv","release/hr-v0/release-candidate.json"}: fail(len(record["sha256"])!=64,f"historical mutable-source hash format: {record['source_path']}")
        else: fail(not path.is_file() or digest(path)!=record["sha256"],f"config source hash: {record['source_path']}")
    impacts={r["gate_id"]:r for r in rows(CFG_REL/"gate-impact.csv")}
    for gate in ("EG-005","EG-006"):
        fail("HR-V0-MOVING-PROP-CLOSURE-P0.1" not in impacts[gate]["evidence_added"] or impacts[gate]["gate_closed"]!="NO",f"gate impact {gate}")
    if errors:
        print("HR-V0 R248 moving-properties closure package: FAIL")
        for error in errors: print("-",error)
        return 1
    print("HR-V0 R248 moving-properties closure package: PASS")
    print("17 ledger rows; 170 blank mass repeats; 8 COM rows; 4 calibrations; 6 inertia rows; 0 physical results")
    print("B-010, R247-H11, motion and energization remain open")
    return 0


if __name__=="__main__": raise SystemExit(main())
