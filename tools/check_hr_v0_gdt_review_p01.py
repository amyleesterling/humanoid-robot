#!/usr/bin/env python3
"""Validate R250 review-only datum/GD&T proposal."""
import csv,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];SRC=ROOT/"mechanical/drawings/hr-v0-gdt-review-p0.1";REL=ROOT/"release/hr-v0/gdt-review-p0.1";CFG=ROOT/"configuration/hr-v0-config-reconciliation-p0.14";CFGR=ROOT/"release/hr-v0/configuration-reconciliation-p0.14";W="PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION"
def rows(p):
    with p.open(encoding="utf-8-sig",newline="") as h:return list(csv.DictReader(h))
def sh(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def mf(d,f):
    rs=rows(d/"file-manifest.csv");a={p.relative_to(d).as_posix() for p in d.rglob("*") if p.is_file() and p.name!="file-manifest.csv"};f({r["path"] for r in rs}!=a,f"manifest membership {d}")
    for r in rs:
        p=d/r["path"];f(not p.is_file() or p.stat().st_size!=int(r["bytes"]) or sh(p)!=r["sha256"],f"manifest hash {p}")
def main():
    es=[];f=lambda c,m:es.append(m) if c else None;csvs={"datum-reference-frame-proposal.csv","feature-control-proposal.csv","inspection-uncertainty-allocation.csv","source-register.csv","qualified-review-checklist.csv","open-holds.csv","acceptance-matrix.csv"};base=csvs|{"README.md","package-status.json","file-manifest.csv"}
    f({p.name for p in SRC.iterdir() if p.is_file()}!=base,"source membership");f({p.name for p in REL.iterdir() if p.is_file()}!=base|{"index.html"},"release membership");mf(SRC,f);mf(REL,f)
    for n in base-{"file-manifest.csv"}:f((SRC/n).read_bytes()!=(REL/n).read_bytes(),f"parity {n}")
    s=json.loads((REL/"package-status.json").read_text());ex={"identifier":"HR-V0-GDT-REVIEW-P0.1","round":"R250","parts":5,"datum_proposals":5,"feature_control_proposals":20,"uncertainty_rows":15,"review_questions":12,"open_holds":12,"acceptance_rows":10,"warning":W}
    for k,v in ex.items():f(s.get(k)!=v,f"status {k}")
    for k in ("drawing_geometry_changed","formal_gdt_released","qualified_review_complete","procurement_authorized","fabrication_authorized","assembly_authorized","connection_authorized","powered_testing_authorized","motion_authorized","energization_authorized","safety_credit"):f(s.get(k) is not False,f"{k} false")
    parts={"MV0-C01","MV0-C04","MV0-C05","MV0-C06","MV0-C07"};d=rows(REL/"datum-reference-frame-proposal.csv");f(len(d)!=5 or {r["part_id"] for r in d}!=parts or any(r["proposal_state"]!="PROPOSED - QUALIFIED DISPOSITION REQUIRED" or r["fabrication_authorized"]!="FALSE" for r in d),"datum proposals")
    fc=rows(REL/"feature-control-proposal.csv");f(len(fc)!=20 or {r["part_id"] for r in fc}!=parts or any(r["released"]!="NO" or r["standard_interpretation"]!="QUALIFIED REVIEW REQUIRED" for r in fc),"FCF proposals")
    u=rows(REL/"inspection-uncertainty-allocation.csv");f(len(u)!=15 or any(r["maximum_expanded_uncertainty"]!="SELECTION REQUIRED BEFORE FAI" or r["method_validation"]!="NOT EXECUTED" for r in u),"uncertainty boundary")
    src=rows(REL/"source-register.csv");f(len(src)!=4 or not any("Y14.5" in r["source"] for r in src) or not any("Technical Note 1297" in r["source"] for r in src),"sources")
    f(len(rows(REL/"qualified-review-checklist.csv"))!=12 or any(r["state"]!="NOT EXECUTED" or r["response"] or r["reviewer"] for r in rows(REL/"qualified-review-checklist.csv")),"blank review")
    f(len(rows(REL/"open-holds.csv"))!=12 or any(r["state"]!="OPEN" for r in rows(REL/"open-holds.csv")),"holds");f(len(rows(REL/"acceptance-matrix.csv"))!=10 or any(r["result"]!="OPEN" for r in rows(REL/"acceptance-matrix.csv")),"acceptance")
    for n in csvs:f(any(r.get("warning")!=W for r in rows(REL/n)),f"warning {n}")
    p=(REL/"index.html").read_text();
    for t in (W,"font:clamp(16px","font-size:14px","FORMAL GD&T NOT RELEASED","DRAWING GEOMETRY UNCHANGED"):f(t not in p,f"web {t}")
    cb={"README.md","current-configuration-map.csv","supersession-map.csv","bom-integration-map.csv","gate-impact.csv","open-holds.csv","acceptance-matrix.csv","package-status.json","source-hash-register.csv","file-manifest.csv"};f({p.name for p in CFG.iterdir() if p.is_file()}!=cb,"config membership");f({p.name for p in CFGR.iterdir() if p.is_file()}!=cb|{"index.html"},"config release membership");mf(CFG,f);mf(CFGR,f)
    cs=json.loads((CFGR/"package-status.json").read_text());
    for k,v in {"identifier":"HR-V0-CONFIG-REC-P0.14","round":"R250","current_records":34,"supersession_records":21,"open_holds":60,"acceptance_rows":89,"gdt_review":"HR-V0-GDT-REVIEW-P0.1"}.items():f(cs.get(k)!=v,f"config {k}")
    cur=rows(CFGR/"current-configuration-map.csv");f(len(cur)!=34 or cur[-1]["identifier"]!="HR-V0-GDT-REVIEW-P0.1","config records")
    for r in rows(CFGR/"source-hash-register.csv"):
        p=ROOT/r["source_path"];f(not p.is_file() or sh(p)!=r["sha256"],f"config hash {p}")
    if es:print("R250 GD&T review: FAIL");[print("-",x) for x in es];return 1
    print("R250 GD&T review: PASS");print("5 datum proposals; 20 FCF proposals; formal release false; geometry unchanged");return 0
if __name__=="__main__":raise SystemExit(main())
