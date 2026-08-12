#!/usr/bin/env python3
"""Fail-closed checks for R267 Lot A alternate acquisition route."""
from __future__ import annotations

import csv
import hashlib
import json
import re
import sys
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"tools"))
import generate_hr_v0_lot_a_alternate_route_p01 as gen


def need(value: bool, message: str) -> None:
    if not value:
        raise SystemExit(message)


def rows(path: Path) -> list[dict[str,str]]:
    with path.open(newline="",encoding="utf-8-sig") as stream:
        return list(csv.DictReader(stream))


def check_manifest(directory: Path) -> None:
    listed = rows(directory/"file-manifest.csv")
    actual = sorted(p for p in directory.rglob("*") if p.is_file() and p.name != "file-manifest.csv")
    need(len(listed)==len(actual),f"manifest count {directory}")
    index = {r["relative_path"]:r for r in listed}
    for path in actual:
        rel = path.relative_to(directory).as_posix()
        need(rel in index,f"manifest member {rel}")
        need(index[rel]["sha256"]==hashlib.sha256(path.read_bytes()).hexdigest(),f"manifest hash {rel}")
        need(index[rel]["warning"]==gen.WARNING,f"manifest warning {rel}")


def main() -> None:
    for directory in (gen.OUT,gen.REL,gen.CFG,gen.CFGR):
        need(directory.exists(),f"missing {directory}")
        check_manifest(directory)
    sources = rows(gen.OUT/"official-source-verification.csv")
    need(len(sources)==8 and all(r["revision_or_date"].endswith(gen.DATE) or "accessed 2026-08-12" in r["revision_or_date"] for r in sources),"source dates")
    need("902-0137-000" in sources[0]["observed_fact"] and "ROBOTIS Inc" in sources[0]["observed_fact"] and "19 in stock" in sources[0]["observed_fact"],"DigiKey facts")
    need("902-0133-000" in sources[1]["observed_fact"] and "TTL 3-pin" in sources[1]["observed_fact"],"manufacturer identity split")
    routes = rows(gen.OUT/"route-comparison.csv")
    need(len(routes)==4,"route count")
    need(routes[0]["commercial_state"].startswith("CONDITIONALLY ADMISSIBLE"),"candidate route")
    need(routes[2]["commercial_state"].startswith("REJECTED") and routes[3]["commercial_state"].startswith("REJECTED"),"rejected routes")
    basket = rows(gen.OUT/"qualified-basket.csv")
    need(len(basket)==3 and sum(int(r["quantity"]) for r in basket)==6,"basket quantities")
    need(sum(Decimal(r["extended_visible_usd"]) for r in basket)==Decimal("1182.22"),"basket subtotal")
    need(basket[0]["manufacturer_part_number"]=="902-0137-000" and basket[0]["identity"]=="DYNAMIXEL XM540-W270-T","actuator identity")
    findings = rows(gen.OUT/"open-finding-register.csv")
    need(len(findings)==6 and all(r["state"]=="OPEN" for r in findings),"findings")
    gates = rows(gen.OUT/"readiness-gate.csv")
    need(len(gates)==12 and all(r["state"]!="CLOSED" for r in gates),"gates")
    inputs = rows(gen.OUT/"owner-input-template.csv")
    need(len(inputs)==12 and all(r["value"]=="" and r["state"]=="BLANK - NOT DECIDED" for r in inputs),"inputs")
    auth = rows(gen.OUT/"authorization-register.csv")
    need(len(auth)==6 and all(r["person"]==r["signature_reference"]==r["date"]=="" and r["decision"]=="NOT SIGNED / NO AUTHORITY" for r in auth),"authorization")
    need(len(rows(gen.OUT/"receipt-scope.csv"))==8,"scope")
    need(len(rows(gen.OUT/"stop-work-register.csv"))==10 and all(r["state"]=="ACTIVE" for r in rows(gen.OUT/"stop-work-register.csv")),"stops")
    accept = rows(gen.OUT/"acceptance-matrix.csv")
    need(len(accept)==12 and all(r["execution_state"]=="NOT EXECUTED" and r["result"]=="OPEN" for r in accept),"acceptance")
    for path in gen.OUT.glob("*.csv"):
        if path.name != "file-manifest.csv":
            need(all(r.get("warning")==gen.WARNING for r in rows(path)),f"warning {path.name}")
    status = json.loads((gen.OUT/"package-status.json").read_text(encoding="utf-8"))
    for key in ("supplier_contacted","cart_created","quote_created","checkout_started","draft_download_executed","purchase_authorized","purchase_executed","article_received","assembly_authorized","connection_authorized","powered_testing_authorized","motion_authorized","energization_authorized","safety_credit"):
        need(status[key] is False,f"authority {key}")
    hashes = json.loads((gen.OUT/"source-hash-register.json").read_text(encoding="utf-8"))
    need(len(hashes)==2 and all(re.fullmatch(r"[0-9a-f]{64}",v) for v in hashes.values()),"source hashes")
    for name in {p.name for p in gen.OUT.iterdir() if p.is_file()}-{"file-manifest.csv"}:
        need((gen.OUT/name).read_bytes()==(gen.REL/name).read_bytes(),f"release mirror {name}")
    page = (gen.REL/"index.html").read_text(encoding="utf-8")
    script = (gen.REL/"decision.js").read_text(encoding="utf-8")
    for token in ("font:clamp(16px","font-size:14px","not a checkout","$1,182.22","<script src='decision.js?v=r267'></script>",gen.WARNING):
        need(token in page,f"page {token}")
    for token in ("window.projectButtonCollectDraft=collect","authority_state:'NOT AUTHORIZED'","hr-v0-lot-a-alternate-route-draft.json"):
        need(token in script,f"script {token}")
    need("<form" not in page.lower() and "action=" not in page.lower(),"submission surface")
    need(not re.search(r"\b(fetch|XMLHttpRequest|WebSocket)\s*\(",page+script),"network API")
    cfg = json.loads((gen.CFG/"package-status.json").read_text(encoding="utf-8"))
    expected = {"identifier":gen.CID,"round":gen.ROUND,"current_records":48,"supersession_records":45,"bom_integration_records":30,"open_holds":234,"acceptance_rows":288,"lot_a_alternate_route":gen.ID}
    for key,value in expected.items():
        need(cfg.get(key)==value,f"config {key}")
    for key in ("physical_article_exists","physical_test_executed","qualified_review_complete","procurement_authorized","fabrication_authorized","assembly_authorized","connection_authorized","powered_testing_authorized","motion_authorized","energization_authorized","safety_credit"):
        need(cfg.get(key) is False,f"config authority {key}")
    current = rows(gen.CFG/"current-configuration-map.csv")
    need(len(current)==48 and current[-1]["identifier"]==gen.ID,"current config")
    supers = rows(gen.CFG/"supersession-map.csv")
    need(len(supers)==45 and supers[-1]["current_or_required_successor"]==gen.CID,"supersession")
    release = json.loads(gen.RELEASE.read_text(encoding="utf-8"))
    for product in release["current_products"]:
        if product.get("domain") in {"electrical","mechanical","bill_of_materials","commissioning","assembly"}:
            need(product.get("configuration_reconciliation")==gen.CID,f"release config {product.get('domain')}")
        if product.get("domain") in {"mechanical","bill_of_materials","assembly"}:
            need(product.get("lot_a_alternate_route")==gen.ID,f"release package {product.get('domain')}")
    for path,token in {ROOT/"README.md":"R267",ROOT/"docs/handoff-current.md":gen.ID,ROOT/"docs/review-ledger.md":"lot-a-alternate-route-p0.1"}.items():
        need(token in path.read_text(encoding="utf-8"),f"narrative {path.name}")
    need("No Sol R12 blocker closes" in (ROOT/"docs/reviews/2026-08-12-sol-r12-post-r267-status.md").read_text(encoding="utf-8"),"Sol boundary")
    print("R267 Lot A alternate acquisition-route checks: PASS")
    print("4 routes / 6 articles / $1,182.22 visible / 12 gates / 0 authority")
    print(gen.WARNING)


if __name__ == "__main__":
    main()
