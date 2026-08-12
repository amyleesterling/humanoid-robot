#!/usr/bin/env python3
"""Fail-closed R255 Lot A inquiry checker."""
import csv,hashlib,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/"procurement/hr-v0/lot-a-inquiry-p0.2";REL=ROOT/"release/hr-v0/lot-a-inquiry-p0.2";CFG=ROOT/"configuration/hr-v0-config-reconciliation-p0.19";CFGR=ROOT/"release/hr-v0/configuration-reconciliation-p0.19"
WARNING="PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION"
def rows(p):
    with p.open(encoding="utf-8-sig",newline="") as f:return list(csv.DictReader(f))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def mf(d,e):
    for r in rows(d/"file-manifest.csv"):
      p=d/r["path"]
      if not p.is_file() or str(p.stat().st_size)!=r["bytes"] or sha(p)!=r["sha256"]:e.append(f"manifest mismatch: {p}")
def main():
    e=[]
    for d in (OUT,REL,CFG,CFGR):
      if not d.is_dir():e.append(f"missing {d}")
      else:mf(d,e)
    if e:return fail(e)
    routes=rows(OUT/"inquiry-route-register.csv");tx=rows(OUT/"transmittal-register.csv");rsp=rows(OUT/"response-template-register.csv");rq=rows(OUT/"robotis-question-register.csv");mq=rows(OUT/"metrology-question-register.csv");bids=rows(OUT/"method-bid-schedule.csv");ev=rows(OUT/"returned-evidence-register.csv");g=rows(OUT/"decision-gate.csv");wf=rows(OUT/"workflow-register.csv");acc=rows(OUT/"acceptance-matrix.csv");att=rows(OUT/"attachment-manifest.csv")
    if len(routes)!=5 or any("NOT" not in r["selection_state"] for r in routes):e.append("five held routes changed")
    if len(tx)!=5 or any(r["send_authorization"]!="NOT AUTHORIZED" or r["sent_state"]!="NOT SENT" or r["sender_identity"]!="SELECTION REQUIRED" or r["reply_address"]!="SELECTION REQUIRED" for r in tx):e.append("transmission fail-closed state changed")
    if len(rq)!=12 or any(r["state"]!="UNSENT / NOT RECEIVED" for r in rq):e.append("ROBOTIS questions changed")
    if len(mq)!=96 or len({(r["method_id"],r["category"],r["question"]) for r in mq})!=32 or any(r["state"]!="UNSENT / NOT RECEIVED" for r in mq):e.append("32 unique / 96 provider-attributed metrology questions changed")
    if len(bids)!=15 or any(r["bid_state"]!="NOT RECEIVED" or r["technical_disposition"]!="NOT EXECUTED" for r in bids):e.append("bid schedule changed")
    if len(ev)!=18 or any(r["state"]!="NOT RECEIVED" for r in ev):e.append("returned evidence changed")
    if len(g)!=15 or any(r["state"]!="OPEN" for r in g):e.append("decision gates changed")
    if len(wf)!=14 or any(r["authorization"]!="NONE" or r["execution_state"]!="NOT EXECUTED" for r in wf):e.append("workflow promoted")
    if len(acc)!=15 or any(r["execution_state"]!="NOT EXECUTED" or r["result"]!="OPEN" or r["evidence_uri"] or r["approver"] for r in acc):e.append("acceptance changed")
    if len(att)!=4 or any(sha(ROOT/r["path"])!=r["sha256"] for r in att):e.append("attachment bindings stale")
    if len(rsp)!=5 or sorted(int(r["response_rows"]) for r in rsp)!=[4,8,32,32,32] or any(r["response_state"]!="BLANK / NOT RECEIVED" or sha(OUT/r["path"])!=r["sha256"] for r in rsp):e.append("recipient-specific response templates changed")
    for r in rsp:
      data=rows(OUT/r["path"])
      if any(x["route_id"]!=r["route_id"] or x["provider_response"] or x["response_evidence_uri"] or x["reviewer_disposition"]!="NOT EXECUTED" for x in data):e.append(f"response template not blank/route-scoped: {r['template_id']}")
    for r in tx:
      if sha(OUT/r["message_path"])!=r["message_sha256"]:e.append(f"message hash stale: {r['transmittal_id']}")
    s=json.loads((OUT/"package-status.json").read_text(encoding="utf-8"));false=("provider_selected","purchase_authorized","order_placed","shipment_authorized","work_authorized","physical_articles_received","qualified_review_complete","assembly_authorized","connection_authorized","powered_testing_authorized","motion_authorized","energization_authorized","safety_credit")
    if s.get("identifier")!="HR-V0-LOT-A-INQUIRY-P0.2" or s.get("responses_received")!=0 or s.get("messages_sent")!=0 or s.get("transmissions_authorized")!=0 or any(s.get(k) is not False for k in false) or s.get("warning")!=WARNING:e.append("package status promoted")
    cs=json.loads((CFG/"package-status.json").read_text(encoding="utf-8"))
    if (cs.get("identifier"),cs.get("current_records"),cs.get("supersession_records"),cs.get("open_holds"),cs.get("acceptance_rows")) != ("HR-V0-CONFIG-REC-P0.19",38,30,97,130):e.append("configuration P0.19 counts changed")
    current=rows(CFG/"current-configuration-map.csv");sup=rows(CFG/"supersession-map.csv")
    if "HR-V0-LOT-A-INQUIRY-P0.2" not in [r["identifier"] for r in current] or not {"HR-V0-LOT-A-SRC-P0.1","HR-V0-EVAL-ACQ-P0.1"}.issubset({r["prior_identifier"] for r in sup}):e.append("configuration/supersession binding missing")
    for p in (OUT/"index.html",REL/"index.html",CFG/"index.html",CFGR/"index.html"):
      t=p.read_text(encoding="utf-8")
      for x in (WARNING,"font:clamp(16px","font-size:14px","Nothing sent. Nothing ordered.","0</div>send or purchase authorizations"):
        if x not in t:e.append(f"{p} omits {x}")
    return fail(e) if e else success()
def fail(e):
    print("R255 Lot A inquiry P0.2: FAIL",file=sys.stderr)
    for x in e:print(f"- {x}",file=sys.stderr)
    return 1
def success():
    print("R255 Lot A inquiry P0.2: PASS");print("5 routes; 12 ROBOTIS + 96 provider-attributed metrology rows; 0 sends/responses/authorizations");print(WARNING);return 0
if __name__=="__main__":raise SystemExit(main())
