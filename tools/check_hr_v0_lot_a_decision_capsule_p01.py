#!/usr/bin/env python3
"""Fail-closed checks for R266 Lot A decision capsule."""
from __future__ import annotations

import csv
import hashlib
import json
import re
import sys
from decimal import Decimal
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"tools"))
import generate_hr_v0_lot_a_decision_capsule_p01 as gen


def need(value: bool, message: str) -> None:
    if not value: raise SystemExit(message)


def rows(path: Path) -> list[dict[str,str]]:
    with path.open(newline="",encoding="utf-8-sig") as stream: return list(csv.DictReader(stream))


def check_manifest(directory: Path) -> None:
    manifest=rows(directory/"file-manifest.csv")
    actual=sorted(p for p in directory.rglob("*") if p.is_file() and p.name!="file-manifest.csv")
    need(len(manifest)==len(actual),f"manifest count {directory}")
    index={r["relative_path"]:r for r in manifest}
    for path in actual:
        rel=path.relative_to(directory).as_posix()
        need(rel in index,f"manifest member {rel}")
        need(index[rel]["sha256"]==hashlib.sha256(path.read_bytes()).hexdigest(),f"manifest hash {rel}")
        need(index[rel]["warning"]==gen.WARNING,f"manifest warning {rel}")


def main() -> None:
    for path in (gen.OUT,gen.REL,gen.CFG,gen.CFGR): need(path.exists(),f"missing {path}")
    for directory in (gen.OUT,gen.REL,gen.CFG,gen.CFGR): check_manifest(directory)
    items=rows(gen.OUT/"item-decision-register.csv")
    need(len(items)==3 and sum(int(r["quantity"]) for r in items)==6,"item quantities")
    subtotal=sum(Decimal(r["extended_visible_usd"]) for r in items)
    need(subtotal==Decimal("1182.22"),"subtotal")
    need(items[0]["order_code"]=="902-0137-000" and items[0]["decision_state"].startswith("BLOCKED"),"XM540 line")
    sources=rows(gen.OUT/"official-source-verification.csv")
    need(len(sources)==4 and all(r["revision_or_date"].endswith(gen.DATE) for r in sources),"source dates")
    need("package table names -R" in sources[0]["observed_fact"] and "contradiction persists" in sources[0]["boundary"],"T/R contradiction")
    findings=rows(gen.OUT/"open-finding-register.csv")
    need(len(findings)==4 and all(r["state"]=="OPEN" for r in findings) and findings[0]["severity"]=="BLOCKER","findings")
    gates=rows(gen.OUT/"readiness-gate.csv")
    need(len(gates)==12 and sum(r["state"].startswith("PARTIALLY") for r in gates)==1 and all(r["state"]!="CLOSED" for r in gates),"gates")
    inputs=rows(gen.OUT/"owner-input-template.csv")
    need(len(inputs)==12 and all(r["value"]=="" and r["state"]=="BLANK - NOT DECIDED" for r in inputs),"owner inputs")
    auth=rows(gen.OUT/"authorization-register.csv")
    need(len(auth)==6 and all(r["person"]==r["signature_reference"]==r["date"]=="" and r["decision"]=="NOT SIGNED / NO AUTHORITY" for r in auth),"authorization")
    scope=rows(gen.OUT/"receipt-scope.csv")
    need(len(scope)==8 and all("AUTHORIZED" not in r["state"] or r["state"].startswith("NOT AUTHORIZED") for r in scope),"scope")
    stops=rows(gen.OUT/"stop-work-register.csv")
    need(len(stops)==10 and all(r["state"]=="ACTIVE" for r in stops),"stops")
    accept=rows(gen.OUT/"acceptance-matrix.csv")
    need(len(accept)==12 and all(r["execution_state"]=="NOT EXECUTED" and r["result"]=="OPEN" for r in accept),"acceptance")
    for path in gen.OUT.glob("*.csv"):
        if path.name!="file-manifest.csv": need(all(r.get("warning")==gen.WARNING for r in rows(path)),f"warning {path.name}")
    status=json.loads((gen.OUT/"package-status.json").read_text(encoding="utf-8"))
    need(status["design_base_commit"]==gen.DESIGN_BASE and status["visible_subtotal_usd"]=="1182.22","status identity")
    for key in ("supplier_contacted","cart_created","checkout_started","draft_download_executed","purchase_authorized","purchase_executed","article_received","assembly_authorized","connection_authorized","powered_testing_authorized","motion_authorized","energization_authorized","safety_credit"): need(status[key] is False,f"authority {key}")
    hashes=json.loads((gen.OUT/"source-hash-register.json").read_text(encoding="utf-8"))
    need(len(hashes)==5 and all(re.fullmatch(r"[0-9a-f]{64}",v) for v in hashes.values()),"source hashes")
    common={p.name for p in gen.OUT.iterdir() if p.is_file()}
    for name in common-{"file-manifest.csv"}: need((gen.OUT/name).read_bytes()==(gen.REL/name).read_bytes(),f"release mirror {name}")
    page=(gen.REL/"index.html").read_text(encoding="utf-8")
    script=(gen.REL/"decision.js").read_text(encoding="utf-8")
    for token in ("font:clamp(16px","font-size:14px","transmits nothing","places no order","$1,182.22","<script src='decision.js'></script>",gen.WARNING): need(token in page,f"page {token}")
    for token in ("window.projectButtonCollectDraft=collect","authority_state:'NOT AUTHORIZED'","Download draft JSON" if False else "hr-v0-lot-a-draft-decision.json"): need(token in script,f"script {token}")
    need("<script>" not in page and "<form" not in page.lower() and "action=" not in page.lower(),"submission surface")
    need(not re.search(r"\b(fetch|XMLHttpRequest|WebSocket)\s*\(",page+script),"network API")
    cfg=json.loads((gen.CFG/"package-status.json").read_text(encoding="utf-8"))
    expected={"identifier":gen.CID,"round":gen.ROUND,"current_records":47,"supersession_records":44,"bom_integration_records":30,"open_holds":222,"acceptance_rows":276,"lot_a_decision_capsule":gen.ID}
    for key,value in expected.items(): need(cfg.get(key)==value,f"config {key}")
    for key in ("physical_article_exists","physical_test_executed","qualified_review_complete","procurement_authorized","fabrication_authorized","assembly_authorized","connection_authorized","powered_testing_authorized","motion_authorized","energization_authorized","safety_credit"): need(cfg.get(key) is False,f"config authority {key}")
    current=rows(gen.CFG/"current-configuration-map.csv")
    need(len(current)==47 and current[-1]["identifier"]==gen.ID,"current config")
    supers=rows(gen.CFG/"supersession-map.csv")
    need(len(supers)==44 and supers[-1]["prior_identifier"]=="HR-V0-CONFIG-REC-P0.29" and supers[-1]["current_or_required_successor"]==gen.CID,"supersession")
    need((gen.CFG/"decision.js").read_bytes()==(gen.REL/"decision.js").read_bytes(),"config script mirror")
    release=json.loads(gen.RELEASE.read_text(encoding="utf-8"))
    for product in release["current_products"]:
        if product.get("domain") in {"electrical","mechanical","bill_of_materials","commissioning","assembly"}: need(product.get("configuration_reconciliation") in {gen.CID,"HR-V0-CONFIG-REC-P0.31"},f"release config {product.get('domain')}")
        if product.get("domain") in {"mechanical","bill_of_materials","assembly"}: need(product.get("lot_a_decision_capsule")==gen.ID and gen.ID in product.get("supporting_identifiers",[]) and gen.CID in product.get("supporting_identifiers",[]),f"release package {product.get('domain')}")
    narrative_tokens={ROOT/"README.md":"R266",ROOT/"docs/handoff-current.md":gen.ID,ROOT/"docs/review-ledger.md":"lot-a-decision-capsule-p0.1"}
    for path,token in narrative_tokens.items():
        content=path.read_text(encoding="utf-8"); need("R266" in content and token in content,f"narrative {path.name}")
    need("No Sol R12 blocker closes" in (ROOT/"docs/reviews/2026-08-12-sol-r12-post-r266-status.md").read_text(encoding="utf-8"),"Sol boundary")
    print("R266 Lot A decision capsule checks: PASS")
    print("6 articles / $1,182.22 visible / 12 gates / 0 authority")
    print(gen.WARNING)


if __name__=="__main__": main()
