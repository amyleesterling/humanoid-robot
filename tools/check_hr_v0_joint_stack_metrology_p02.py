#!/usr/bin/env python3
"""Fail-closed R254 joint-stack metrology P0.2 checker."""
from __future__ import annotations

import csv
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "test-fixtures/hr-v0/joint-stack-metrology-p0.2"
REL = ROOT / "release/hr-v0/joint-stack-metrology-p0.2"
CFG = ROOT / "configuration/hr-v0-config-reconciliation-p0.18"
CFGR = ROOT / "release/hr-v0/configuration-reconciliation-p0.18"
WARNING = "PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION"


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check_manifest(directory: Path, errors: list[str]) -> None:
    for row in rows(directory/"file-manifest.csv"):
        path = directory/row["path"]
        if not path.is_file() or str(path.stat().st_size) != row["bytes"] or sha(path) != row["sha256"]:
            errors.append(f"manifest mismatch: {path}")


def main() -> int:
    errors: list[str] = []
    for directory in (OUT,REL,CFG,CFGR):
        if not directory.is_dir(): errors.append(f"missing {directory}")
        else: check_manifest(directory,errors)
    if errors: return fail(errors)
    methods = rows(OUT/"method-register.csv")
    appl = rows(OUT/"fixture-applicability.csv")
    hsi = rows(OUT/"hsi-method-map.csv")
    uncertainty = rows(OUT/"uncertainty-input-register.csv")
    holds = rows(OUT/"hold-point-register.csv")
    ops = rows(OUT/"operation-sequence.csv")
    acc = rows(OUT/"acceptance-matrix.csv")
    phases = rows(OUT/"phase-gate-register.csv")
    status = json.loads((OUT/"package-status.json").read_text(encoding="utf-8"))
    if len(methods)!=5 or any(r["execution_state"]!="NOT EXECUTED" for r in methods): errors.append("five blank methods changed")
    expected = ["NOT APPLICABLE","CONDITIONAL SUPPORT CANDIDATE ONLY","CONDITIONAL FIXED-DATUM CANDIDATE ONLY","NOT ACCEPTABLE AS SOLE FIXTURE","NOT APPLICABLE"]
    if [r["p02_fixture_disposition"] for r in appl] != expected or any(r["use_authorized"]!="NO" for r in appl): errors.append("P0.2 limited applicability changed")
    if len(hsi)!=20 or [r["hsi_id"] for r in hsi] != [f"HSI-{i:03d}" for i in range(1,21)] or any(r["state"]!="OPEN" for r in hsi): errors.append("20-row HSI routing changed")
    numeric = ("numeric_input","distribution","divisor","sensitivity","standard_uncertainty")
    if len(uncertainty)!=40 or any(r["state"]!="SELECTION REQUIRED" or any(r[k] for k in numeric) for r in uncertainty): errors.append("40 uncertainty inputs are not blank/fail-closed")
    if len(holds)!=12 or any(r["state"]!="OPEN" for r in holds): errors.append("12 hold points changed")
    if len(ops)!=22 or any(r["authorization"]!="NONE" or r["execution_state"]!="NOT EXECUTED" for r in ops): errors.append("22 operations changed/promoted")
    if len(acc)!=12 or any(r["execution_state"]!="NOT EXECUTED" or r["result"]!="OPEN" or r["evidence_uri"] or r["approver"] for r in acc): errors.append("12 blank acceptances changed")
    if len(phases)!=5 or any(r["authorization_state"]!="NOT AUTHORIZED" or r["execution_state"]!="NOT EXECUTED" for r in phases): errors.append("phase authorization changed")
    false_keys=("physical_articles_received","threaded_assembly_authorized","fixture_use_authorized","qualified_review_complete","procurement_authorized","fabrication_authorized","assembly_authorized","connection_authorized","powered_testing_authorized","motion_authorized","energization_authorized","safety_credit")
    if status.get("identifier")!="HR-V0-JOINT-MET-P0.2" or status.get("operations_executed")!=0 or status.get("authorizations_granted")!=0 or any(status.get(k) is not False for k in false_keys) or status.get("warning")!=WARNING: errors.append("package status was promoted")
    cfg_status=json.loads((CFG/"package-status.json").read_text(encoding="utf-8"))
    if any((cfg_status.get("identifier")!="HR-V0-CONFIG-REC-P0.18",cfg_status.get("current_records")!=37,cfg_status.get("supersession_records")!=27,cfg_status.get("open_holds")!=82,cfg_status.get("acceptance_rows")!=115)): errors.append("configuration P0.18 counts changed")
    current=rows(CFG/"current-configuration-map.csv"); supers=rows(CFG/"supersession-map.csv")
    if "HR-V0-JOINT-MET-P0.2" not in [r["identifier"] for r in current] or not any(r["prior_identifier"]=="HR-V0-JOINT-MET-P0.1" for r in supers): errors.append("metrology supersession/configuration binding missing")
    for path in (OUT/"HR-V0_joint-stack-metrology-guide.html",REL/"index.html",CFG/"index.html",CFGR/"index.html"):
        text=path.read_text(encoding="utf-8")
        for token in (WARNING,"font:clamp(16px","font-size:14px","Five task-specific methods","Zero executed measurements"):
            if token not in text: errors.append(f"{path} omits {token}")
    return fail(errors) if errors else success()


def fail(errors: list[str]) -> int:
    print("R254 joint-stack metrology P0.2: FAIL",file=sys.stderr)
    for e in errors: print(f"- {e}",file=sys.stderr)
    return 1


def success() -> int:
    print("R254 joint-stack metrology P0.2: PASS")
    print("5 task methods; 20 HSI routes; 40 blank uncertainty inputs; 0 authorizations/results")
    print(WARNING)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
