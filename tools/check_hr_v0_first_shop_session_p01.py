#!/usr/bin/env python3
"""Validate R251 minimum acquisition and unpowered shop session."""
import csv,hashlib,json
from pathlib import Path
R=Path(__file__).resolve().parents[1];S=R/"mechanical/metrology/hr-v0-first-shop-session-p0.1";O=R/"release/hr-v0/first-shop-session-p0.1";C=R/"configuration/hr-v0-config-reconciliation-p0.15";CO=R/"release/hr-v0/configuration-reconciliation-p0.15";W="PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION"
def rows(p):
    with p.open(encoding="utf-8-sig",newline="") as h:return list(csv.DictReader(h))
def sh(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def mf(d,f):
    rr=rows(d/"file-manifest.csv");a={p.relative_to(d).as_posix() for p in d.rglob("*") if p.is_file() and p.name!="file-manifest.csv"};f({x["path"] for x in rr}!=a,f"manifest {d}")
    for x in rr:p=d/x["path"];f(not p.is_file() or p.stat().st_size!=int(x["bytes"]) or sh(p)!=x["sha256"],f"hash {p}")
def main():
    e=[];f=lambda c,m:e.append(m) if c else None;cs={"source-binding.csv","six-article-register.csv","purchase-gate-snapshot.csv","supplier-question-snapshot.csv","session-traveler.csv","hold-point-snapshot.csv","instrument-readiness.csv","hsi-execution-register.csv","role-assignment-template.csv","evidence-location-plan.csv","stop-work-register.csv","open-holds.csv","acceptance-matrix.csv"};b=cs|{"README.md","package-status.json","file-manifest.csv"}
    f({p.name for p in S.iterdir() if p.is_file()}!=b,"source membership");f({p.name for p in O.iterdir() if p.is_file()}!=b|{"index.html"},"output membership");mf(S,f);mf(O,f)
    for n in b-{"file-manifest.csv"}:f((S/n).read_bytes()!=(O/n).read_bytes(),f"parity {n}")
    st=json.loads((O/"package-status.json").read_text());ex={"identifier":"HR-V0-FIRST-SHOP-SESSION-P0.1","round":"R251","articles":6,"purchase_gates":10,"supplier_questions":8,"operations":18,"hold_points":8,"instruments":6,"hsi_rows":20,"roles":7,"evidence_locations":9,"stop_conditions":10,"open_holds":12,"acceptance_rows":10,"warning":W}
    for k,v in ex.items():f(st.get(k)!=v,f"status {k}")
    for k in ("supplier_contacted","purchase_authorized","session_authorized","assembly_authorized","connection_authorized","powered_testing_authorized","motion_authorized","energization_authorized","safety_credit"):f(st.get(k) is not False,f"{k}")
    f(st.get("articles_received")!=0 or st.get("operations_executed")!=0 or st.get("hsi_accepted")!=0,"zero results")
    src=rows(O/"source-binding.csv");f(len(src)!=7,"source count")
    for x in src:p=R/x["path"];f(not p.is_file() or sh(p)!=x["sha256"],f"source hash {p}")
    checks=[("six-article-register.csv",6),("purchase-gate-snapshot.csv",10),("supplier-question-snapshot.csv",8),("session-traveler.csv",18),("hold-point-snapshot.csv",8),("instrument-readiness.csv",6),("hsi-execution-register.csv",20),("role-assignment-template.csv",7),("evidence-location-plan.csv",9),("stop-work-register.csv",10),("open-holds.csv",12),("acceptance-matrix.csv",10)]
    for n,c in checks:f(len(rows(O/n))!=c,f"{n} count")
    f(any(x["purchase_state"]!="NOT AUTHORIZED" or x["received_state"]!="NOT RECEIVED" for x in rows(O/"six-article-register.csv")),"articles blocked");f(any(x["current_state"]!="OPEN" or x["authority"]!="NONE" for x in rows(O/"purchase-gate-snapshot.csv")),"gates open");f(any(x["transmission_state"]!="UNSENT" or x["response"] for x in rows(O/"supplier-question-snapshot.csv")),"questions unsent");f(any(x["session_state"]!="NOT EXECUTED" or x["authorization_record"] or x["evidence_uri"] for x in rows(O/"session-traveler.csv")),"traveler blank");f(any(x["session_state"]!="OPEN" or x["signer"] for x in rows(O/"hold-point-snapshot.csv")),"holdpoints open");f(any(x["session_result"]!="NOT EXECUTED" or x["accepted_value"] or x["approver"] for x in rows(O/"hsi-execution-register.csv")),"HSI blank");f(any(x["person"]!="SELECTION REQUIRED" for x in rows(O/"role-assignment-template.csv")),"roles blank");f(any(x["exists"]!="FALSE" or x["content_hash"] for x in rows(O/"evidence-location-plan.csv")),"evidence blank")
    for n in cs:f(any(x.get("warning")!=W for x in rows(O/n)),f"warning {n}")
    p=(O/"index.html").read_text();
    for t in (W,"font:clamp(16px","font-size:14px","PURCHASE BLOCKED","SESSION NOT AUTHORIZED","ALL RESULTS BLANK"):f(t not in p,f"web {t}")
    cb={"README.md","current-configuration-map.csv","supersession-map.csv","bom-integration-map.csv","gate-impact.csv","open-holds.csv","acceptance-matrix.csv","package-status.json","source-hash-register.csv","file-manifest.csv"};f({p.name for p in C.iterdir() if p.is_file()}!=cb,"config");f({p.name for p in CO.iterdir() if p.is_file()}!=cb|{"index.html"},"config release");mf(C,f);mf(CO,f);cst=json.loads((CO/"package-status.json").read_text())
    for k,v in {"identifier":"HR-V0-CONFIG-REC-P0.15","round":"R251","current_records":35,"supersession_records":22,"open_holds":65,"acceptance_rows":97,"first_shop_session":"HR-V0-FIRST-SHOP-SESSION-P0.1"}.items():f(cst.get(k)!=v,f"config {k}")
    if e:print("R251 first-shop session: FAIL");[print("-",x) for x in e];return 1
    print("R251 first-shop session: PASS");print("6 articles; 10 purchase gates; 18 operations; 20 HSI rows; nothing authorized or executed");return 0
if __name__=="__main__":raise SystemExit(main())
