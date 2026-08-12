#!/usr/bin/env python3
"""Generate R267 Lot A alternate acquisition-route qualification."""
from __future__ import annotations

import csv
import hashlib
import html
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ID = "HR-V0-LOT-A-ALT-ROUTE-P0.1"
CID = "HR-V0-CONFIG-REC-P0.31"
ROUND = "R267"
DATE = "2026-08-12"
DESIGN_BASE = "94dc15fcbd5c82db29d265dcf2440e55398df536"
WARNING = "PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION"
OUT = ROOT / "procurement/hr-v0/lot-a-alternate-route-p0.1"
REL = ROOT / "release/hr-v0/lot-a-alternate-route-p0.1"
CFG0 = ROOT / "configuration/hr-v0-config-reconciliation-p0.30"
CFG = ROOT / "configuration/hr-v0-config-reconciliation-p0.31"
CFGR = ROOT / "release/hr-v0/configuration-reconciliation-p0.31"
PRIOR = ROOT / "procurement/hr-v0/lot-a-decision-capsule-p0.1"
RELEASE = ROOT / "release/hr-v0/release-candidate.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def warned(row: dict[str, object]) -> dict[str, object]:
    return {**row, "warning": WARNING}


def write_csv(path: Path, fields: list[str], records: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows({field: row.get(field, "") for field in fields} for row in records)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as stream:
        return list(csv.DictReader(stream))


def manifest(directory: Path) -> None:
    records = []
    for path in sorted(p for p in directory.rglob("*") if p.is_file() and p.name != "file-manifest.csv"):
        records.append(warned({"relative_path": path.relative_to(directory).as_posix(), "sha256": sha(path), "bytes": path.stat().st_size}))
    write_csv(directory / "file-manifest.csv", ["relative_path", "sha256", "bytes", "warning"], records)


def package_rows() -> dict[str, tuple[list[str], list[dict[str, object]]]]:
    sources = [
        warned({"source_id":"R267-SRC-01","organization":"DigiKey Marketplace","title":"ROBOTIS 902-0137-000","revision_or_date":"live page; accessed 2026-08-12","url":"https://www.digikey.com/en/products/detail/robotis/902-0137-000/12349044","observed_fact":"manufacturer ROBOTIS; manufacturer product number 902-0137-000; description XM540-W270-T; DigiKey number 2700-902-0137-000-ND; 19 in stock; $482.89 each; marketplace product; page says approximately 7 days from ROBOTIS Inc","boundary":"dynamic page observation only; no units reserved, cart created, quote obtained, seller contract accepted or shipment identity received"}),
        warned({"source_id":"R267-SRC-02","organization":"ROBOTIS Japan","title":"XM540-W270 official e-Shop","revision_or_date":"live page; accessed 2026-08-12","url":"https://e-shop.robotis.co.jp/product.php?id=43","observed_fact":"XM540-W270-T is part 902-0137-000, JAN 8809052935160 and TTL 3-pin; -R is separately 902-0133-000 and RS-485 4-pin","boundary":"manufacturer identity evidence only; Japan inventory and price are not a US allocation or acquisition route"}),
        warned({"source_id":"R267-SRC-03","organization":"ROBOTIS","title":"XM540-W270-T/R e-Manual","revision_or_date":"live page; no revision shown; accessed 2026-08-12","url":"https://emanual.robotis.com/docs/en/dxl/x/xm540-w270/","observed_fact":"manufacturer distinguishes -T TTL and -R RS-485 variants","boundary":"does not reserve stock or prove received article identity"}),
        warned({"source_id":"R267-SRC-04","organization":"ROBOTIS US","title":"DYNAMIXEL XM540-W270-T","revision_or_date":"live page; no revision shown; accessed 2026-08-12","url":"https://www.robotis.us/dynamixel-xm540-w270-t/","observed_fact":"title, SKU 902-0137-000 and communication field describe -T/TTL while package table names -R; $482.89; stock field blank","boundary":"direct-store route remains held on the same-page contradiction and absent numeric allocation"}),
        warned({"source_id":"R267-SRC-05","organization":"RobotShop","title":"ROBOTIS DYNAMIXEL XM540-W270-T Smart Servo Actuator","revision_or_date":"live page; accessed 2026-08-12","url":"https://www.robotshop.com/products/robotis-dynamixel-xm540-w270-t-smart-servo-actuator","observed_fact":"manufacturer number 902-0137-000; $482.89; only 1 unit left","boundary":"cannot cover required quantity two at observed stock; seller/fulfillment authorization not independently established here"}),
        warned({"source_id":"R267-SRC-06","organization":"Trossen Robotics","title":"DYNAMIXEL XM540-W270-T Robot Actuator","revision_or_date":"live page/search result; accessed 2026-08-12","url":"https://store.trossenrobotics.com/products/dynamixel-xm540-w270-t-robot-actuator-2","observed_fact":"$419.90 and out of stock; page requests sales contact for order timing","boundary":"not an available route; no contact was made and no lead time or allocation was inferred"}),
        warned({"source_id":"R267-SRC-07","organization":"ROBOTIS US","title":"FR13-H101K Set","revision_or_date":"live page; no revision shown; accessed 2026-08-12","url":"https://robotis.us/fr13-h101k-set/","observed_fact":"SKU 903-0270-300; $76.71; stock field blank","boundary":"no allocation inferred"}),
        warned({"source_id":"R267-SRC-08","organization":"ROBOTIS US","title":"FR13-S102K Set","revision_or_date":"live page; no revision shown; accessed 2026-08-12","url":"https://www.robotis.us/fr13-s102k-set/","observed_fact":"SKU 903-0269-300; $31.51; Current Stock 94","boundary":"displayed count is not a reservation or allocation"}),
    ]
    routes = [
        warned({"route_id":"R267-ROUTE-01","seller_surface":"DigiKey Marketplace","supplier_or_fulfiller":"ROBOTIS Inc (as displayed)","scope":"2 x 902-0137-000 actuator only","identity_evidence":"EXACT PART/MODEL BINDING DISPLAYED","quantity_evidence":"19 IN STOCK DISPLAYED","commercial_state":"CONDITIONALLY ADMISSIBLE FOR DATED CART/QUOTE EVALUATION ONLY","disposition_basis":"exact -T identity and required quantity are displayed; all dynamic and contractual facts remain unaccepted"}),
        warned({"route_id":"R267-ROUTE-02","seller_surface":"ROBOTIS US direct","supplier_or_fulfiller":"ROBOTIS Inc","scope":"2 x actuator plus 4 x frame sets","identity_evidence":"ACTUATOR PAGE CONTRADICTORY","quantity_evidence":"TWO BLANK STOCK FIELDS; ONE UNRESERVED COUNT","commercial_state":"HOLD","disposition_basis":"does not close actuator shipment identity or allocation"}),
        warned({"route_id":"R267-ROUTE-03","seller_surface":"RobotShop","supplier_or_fulfiller":"NOT ESTABLISHED","scope":"actuator only","identity_evidence":"EXACT PART/MODEL DISPLAYED","quantity_evidence":"ONLY 1 UNIT LEFT","commercial_state":"REJECTED FOR CURRENT TWO-UNIT LOT","disposition_basis":"observed quantity cannot cover requirement"}),
        warned({"route_id":"R267-ROUTE-04","seller_surface":"Trossen Robotics","supplier_or_fulfiller":"NOT ESTABLISHED","scope":"actuator only","identity_evidence":"EXACT MODEL DISPLAYED","quantity_evidence":"OUT OF STOCK","commercial_state":"REJECTED FOR CURRENT LOT","disposition_basis":"no observed availability and no sales contact authorized"}),
    ]
    basket = [
        warned({"line_id":"R267-LINE-01","seller_surface":"DigiKey Marketplace","supplier_or_fulfiller":"ROBOTIS Inc (as displayed)","manufacturer_part_number":"902-0137-000","identity":"DYNAMIXEL XM540-W270-T","quantity":2,"unit_price_usd_visible":"482.89","extended_visible_usd":"965.78","allocation":"NOT RESERVED","state":"HOLD - DATED CART/QUOTE AND OWNER DECISION REQUIRED"}),
        warned({"line_id":"R267-LINE-02","seller_surface":"ROBOTIS US","supplier_or_fulfiller":"ROBOTIS Inc","manufacturer_part_number":"903-0270-300","identity":"FR13-H101K Set","quantity":2,"unit_price_usd_visible":"76.71","extended_visible_usd":"153.42","allocation":"NOT PROVED","state":"HOLD - ALLOCATION AND OWNER DECISION REQUIRED"}),
        warned({"line_id":"R267-LINE-03","seller_surface":"ROBOTIS US","supplier_or_fulfiller":"ROBOTIS Inc","manufacturer_part_number":"903-0269-300","identity":"FR13-S102K Set","quantity":2,"unit_price_usd_visible":"31.51","extended_visible_usd":"63.02","allocation":"NOT RESERVED","state":"HOLD - ALLOCATION AND OWNER DECISION REQUIRED"}),
    ]
    findings = [
        warned({"finding_id":"R267-F-01","severity":"MAJOR","subject":"split commercial route","evidence":"actuators would use DigiKey Marketplace while frame sets remain ROBOTIS US direct","required_closure":"dated cart/quote records naming each seller and fulfiller plus accepted split-route traceability","state":"OPEN"}),
        warned({"finding_id":"R267-F-02","severity":"MAJOR","subject":"dynamic allocation","evidence":"displayed stock counts are not reservations and H101 exposes no numeric stock","required_closure":"dated cart/quote allocation for all six articles","state":"OPEN"}),
        warned({"finding_id":"R267-F-03","severity":"MAJOR","subject":"landed cost","evidence":"$1,182.22 visible subtotal excludes separate shipping, Massachusetts tax status, marketplace charges, fees and price changes","required_closure":"complete landed-cost record for the exact Boston-area ship-to and accepted maximum spend","state":"OPEN"}),
        warned({"finding_id":"R267-F-04","severity":"MAJOR","subject":"received identity","evidence":"commercial pages do not prove the labels, connector population or model register of delivered articles","required_closure":"quarantined receiving inspection against 902-0137-000, -T, TTL/3-pin and later controlled model readback","state":"OPEN"}),
        warned({"finding_id":"R267-F-05","severity":"MAJOR","subject":"terms and authority","evidence":"no cart, quote, terms acceptance, purchaser, payment authority, receiver, ship-to or maximum spend exists","required_closure":"separately signed program-owner receipt/quarantine-only decision and accepted commercial record","state":"OPEN"}),
        warned({"finding_id":"R267-F-06","severity":"MINOR","subject":"seller authorization wording","evidence":"DigiKey labels the listing marketplace and references fully authorized partners, and says shipment from ROBOTIS Inc; no blanket distributor contract was independently reviewed","required_closure":"retain claim at page-display level or obtain attributable seller/manufacturer confirmation","state":"OPEN"}),
    ]
    gate_specs = [
        ("R267-G-01","Accept DigiKey marketplace actuator route","OPEN","dated cart/quote showing DigiKey seller surface and ROBOTIS Inc fulfiller"),
        ("R267-G-02","Confirm two exact 902-0137-000 units allocated","OPEN","dated allocation naming XM540-W270-T and quantity two"),
        ("R267-G-03","Confirm four exact frame-set articles allocated","OPEN","dated allocation for two 903-0270-300 and two 903-0269-300"),
        ("R267-G-04","Close both sellers, shipping, tax, fees and expiration","OPEN","complete split-route landed-cost record"),
        ("R267-G-05","Set numerical maximum spend","OPEN","signed program-owner value"),
        ("R267-G-06","Freeze exact Boston-area ship-to","OPEN","signed controlled address reference"),
        ("R267-G-07","Name adult purchaser, payment authority and receiver","OPEN","signed role assignments"),
        ("R267-G-08","Bind design baseline and exact line identities","PARTIALLY ADDRESSED - FORMAL ACCEPTANCE OPEN",f"accepted decision citing {DESIGN_BASE} and R267-LINE-01..03"),
        ("R267-G-09","Accept no-substitution and no-backorder rules","OPEN","signed rule and cart/quote without alternates"),
        ("R267-G-10","Limit authority to receipt and quarantine","OPEN","signed scope excluding assembly, connection, power and use"),
        ("R267-G-11","Prepare serialized receiving evidence","OPEN","controlled label/photo/packing/model-readback/deviation locations"),
        ("R267-G-12","Qualify received actuator identity","OPEN","received label and connector inspection; controlled model readback only under a later separately released test"),
    ]
    gates = [warned({"gate_id":a,"decision":b,"state":c,"required_evidence":d}) for a,b,c,d in gate_specs]
    input_specs = [
        ("owner_decision","approve / decline / defer"),("maximum_spend_usd","numeric including contingency"),("digikey_cart_or_quote_id","dated identifier"),("robotis_cart_or_quote_id","dated identifier"),("commercial_expiration","date/time"),("ship_to_reference","controlled reference; do not expose full address publicly"),("receiving_owner","adult name/reference"),("quarantine_location","controlled location"),("purchaser","adult name/reference"),("payment_authority","adult name/reference"),("tax_status","taxable / accepted exemption"),("signed_decision_uri","signed artifact reference"),
    ]
    inputs = [warned({"input_id":f"R267-IN-{i:02d}","field":field,"value":"","required_content":need,"state":"BLANK - NOT DECIDED"}) for i,(field,need) in enumerate(input_specs,1)]
    roles = ["program owner","purchaser","payment authority","receiving owner","independent configuration reviewer","qualified mechanical reviewer"]
    auth = [warned({"role":role,"person":"","signature_reference":"","date":"","decision":"NOT SIGNED / NO AUTHORITY"}) for role in roles]
    scope_specs = [
        ("SCOPE-01","create dated carts/quotes for evaluation","NOT AUTHORIZED"),("SCOPE-02","purchase exact R267-LINE-01..03 quantities","NOT AUTHORIZED"),("SCOPE-03","receive sealed articles","NOT AUTHORIZED"),("SCOPE-04","photograph labels and packing records","NOT AUTHORIZED"),("SCOPE-05","quarantine received articles","NOT AUTHORIZED"),("SCOPE-06","open packages for controlled receiving inspection","NOT AUTHORIZED"),("SCOPE-07","assemble or connect any article","PROHIBITED BY THIS PACKAGE"),("SCOPE-08","powered test, motion or energization","PROHIBITED BY THIS PACKAGE"),
    ]
    scopes = [warned({"scope_id":a,"activity":b,"state":c}) for a,b,c in scope_specs]
    stop_specs = [
        ("STOP-01","any listing, seller, fulfiller, model or manufacturer number differs"),("STOP-02","quantity two is not allocatable for any required line"),("STOP-03","a cart or quote contains substitution, backorder or unknown revision"),("STOP-04","shipping, tax, marketplace charges, fees or expiration are absent"),("STOP-05","maximum spend is blank or exceeded"),("STOP-06","ship-to, purchaser, payment authority, receiver or quarantine location is absent"),("STOP-07","candidate commit, package hash or line identity differs"),("STOP-08","scope would include assembly, cable connection, power, motion or use"),("STOP-09","any required signature or acceptance is absent"),("STOP-10","a received article is damaged, opened, mislabeled, wrong-protocol or inconsistent"),
    ]
    stops = [warned({"stop_id":a,"condition":b,"mandatory_action":"STOP; do not purchase/use; record deviation and obtain written disposition","state":"ACTIVE"}) for a,b in stop_specs]
    accept = [warned({"acceptance_id":f"R267-ACC-{i:02d}","criterion":g[1],"execution_state":"NOT EXECUTED","result":"OPEN","evidence_uri":"","approver":""}) for i,g in enumerate(gate_specs,1)]
    binding = [
        warned({"binding_id":"R267-BIND-01","subject":"design baseline","value":DESIGN_BASE,"state":"RECORDED - FORMAL ACCEPTANCE OPEN"}),
        warned({"binding_id":"R267-BIND-02","subject":"prior decision capsule","value":"HR-V0-LOT-A-DECISION-CAP-P0.1","state":"SOURCE EVIDENCE; ROUTE DECISION SUPERSEDED BY THIS QUALIFICATION"}),
        warned({"binding_id":"R267-BIND-03","subject":"actuator route","value":"DigiKey 2700-902-0137-000-ND / manufacturer 902-0137-000 / ROBOTIS Inc fulfiller as displayed","state":"CONDITIONALLY ADMISSIBLE FOR QUOTE EVALUATION ONLY"}),
        warned({"binding_id":"R267-BIND-04","subject":"current configuration input","value":"HR-V0-CONFIG-REC-P0.30","state":"HASH BOUND"}),
    ]
    return {
        "official-source-verification.csv":(["source_id","organization","title","revision_or_date","url","observed_fact","boundary","warning"],sources),
        "route-comparison.csv":(["route_id","seller_surface","supplier_or_fulfiller","scope","identity_evidence","quantity_evidence","commercial_state","disposition_basis","warning"],routes),
        "qualified-basket.csv":(["line_id","seller_surface","supplier_or_fulfiller","manufacturer_part_number","identity","quantity","unit_price_usd_visible","extended_visible_usd","allocation","state","warning"],basket),
        "open-finding-register.csv":(["finding_id","severity","subject","evidence","required_closure","state","warning"],findings),
        "readiness-gate.csv":(["gate_id","decision","state","required_evidence","warning"],gates),
        "owner-input-template.csv":(["input_id","field","value","required_content","state","warning"],inputs),
        "authorization-register.csv":(["role","person","signature_reference","date","decision","warning"],auth),
        "receipt-scope.csv":(["scope_id","activity","state","warning"],scopes),
        "stop-work-register.csv":(["stop_id","condition","mandatory_action","state","warning"],stops),
        "acceptance-matrix.csv":(["acceptance_id","criterion","execution_state","result","evidence_uri","approver","warning"],accept),
        "configuration-binding.csv":(["binding_id","subject","value","state","warning"],binding),
    }


def interactive(data: dict[str, tuple[list[str], list[dict[str, object]]]]) -> tuple[str, str]:
    routes = data["route-comparison.csv"][1]
    basket = data["qualified-basket.csv"][1]
    gates = data["readiness-gate.csv"][1]
    inputs = data["owner-input-template.csv"][1]
    route_cards = "".join(f"<article><h3>{r['route_id']}: {html.escape(str(r['seller_surface']))}</h3><p><strong>{html.escape(str(r['commercial_state']))}</strong></p><p>{html.escape(str(r['scope']))}</p><p>{html.escape(str(r['identity_evidence']))}; {html.escape(str(r['quantity_evidence']))}</p><p>{html.escape(str(r['disposition_basis']))}</p></article>" for r in routes)
    basket_rows = "".join(f"<tr><td>{r['line_id']}</td><td>{html.escape(str(r['seller_surface']))}</td><td>{r['quantity']} x {html.escape(str(r['identity']))}</td><td>{r['manufacturer_part_number']}</td><td>${r['extended_visible_usd']}</td><td>{html.escape(str(r['state']))}</td></tr>" for r in basket)
    gate_rows = "".join(f"<tr><td>{r['gate_id']}</td><td>{html.escape(str(r['decision']))}</td><td>{html.escape(str(r['state']))}</td><td>{html.escape(str(r['required_evidence']))}</td></tr>" for r in gates)
    input_rows = "".join(f"<label>{html.escape(str(r['field']).replace('_',' ').title())}<span>{html.escape(str(r['required_content']))}</span><input id='{r['field']}' autocomplete='off'></label>" for r in inputs)
    css = ":root{--sky:#dff3ff;--blue:#092f57;--gold:#f3bd28;--paper:#f7fbff;--ink:#102338;--line:#8bb7d6;--danger:#851b25}*{box-sizing:border-box}body{margin:0;background:var(--paper);color:var(--ink);font:clamp(16px,1.2vw,19px)/1.5 system-ui,sans-serif}header{padding:clamp(24px,5vw,60px);background:linear-gradient(135deg,var(--sky),white);border-bottom:8px solid var(--gold)}main{max-width:1450px;margin:auto;padding:24px}h1{font-size:clamp(34px,5vw,66px);line-height:1.05;color:var(--blue)}h2{font-size:clamp(25px,2.5vw,38px);color:var(--blue)}h3{font-size:22px;color:var(--blue)}.warn{background:#fff4c7;border:3px solid var(--gold);padding:16px;font-weight:850}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(300px,100%),1fr));gap:16px}article,section{background:white;border:2px solid var(--line);border-radius:14px;padding:18px;margin:16px 0}.state{color:var(--danger);font-weight:800}.scroll{overflow-x:auto}table{width:100%;min-width:980px;border-collapse:collapse;font-size:14px}th,td{padding:11px;border-bottom:1px solid #bfd8e8;text-align:left;vertical-align:top}th{background:var(--blue);color:white}label{display:block;font-weight:800}label span{display:block;font-size:14px;font-weight:400;margin:4px 0}input{width:100%;font:16px/1.35 system-ui;padding:10px;border:2px solid #7199b7;border-radius:8px}button{font:800 16px/1.2 system-ui;padding:12px 16px;border:2px solid var(--blue);border-radius:9px;background:white;color:var(--blue);margin:5px}button.primary{background:var(--gold);color:#17253a}@media(max-width:700px){main{padding:12px}header{padding:24px 16px}table{min-width:900px}}"
    page = f"""<!doctype html><html lang='en'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'><title>{ID}</title><style>{css}</style></head><body><header><p class='warn'>{WARNING}</p><h1>A qualified route candidate, not a checkout.</h1><p>The exact actuator identity is clearer on the candidate marketplace route. Allocation, landed cost, authority and received identity remain open.</p></header><main><section><h2>Route comparison</h2><div class='grid'>{route_cards}</div></section><section><h2>Candidate split basket</h2><p>Six articles. Visible subtotal: <strong>$1,182.22</strong>. No cart, quote, reservation or authority exists.</p><div class='scroll'><table><thead><tr><th>Line</th><th>Seller surface</th><th>Article</th><th>Manufacturer number</th><th>Visible extension</th><th>State</th></tr></thead><tbody>{basket_rows}</tbody></table></div></section><section><h2>Unclosed gates</h2><div class='scroll'><table><thead><tr><th>Gate</th><th>Decision</th><th>State</th><th>Required evidence</th></tr></thead><tbody>{gate_rows}</tbody></table></div></section><section><h2>Unsaved draft inputs</h2><p>Entries stay in this browser. Exporting a draft is not approval and does not submit or purchase anything.</p><div class='grid'>{input_rows}</div><button class='primary' id='download'>Download draft JSON</button><button id='clear'>Clear unsaved inputs</button><p id='count' class='state'>0 / {len(inputs)} draft inputs filled</p></section><p class='warn'>{WARNING}</p></main><script src='decision.js?v=r267'></script></body></html>"""
    schema = [{"field":r["field"],"state":"BLANK - NOT DECIDED"} for r in inputs]
    script = f"(()=>{{const routeSchema={json.dumps(schema,separators=(',',':'))};function collect(){{return{{package:'{ID}',design_base:'{DESIGN_BASE}',authority_state:'NOT AUTHORIZED',warning:{json.dumps(WARNING)},inputs:routeSchema.map(r=>({{...r,value:document.getElementById(r.field).value}}))}}}}function count(){{document.getElementById('count').textContent=collect().inputs.filter(r=>r.value!=='').length+' / '+routeSchema.length+' draft inputs filled'}}document.addEventListener('input',count);document.getElementById('download').onclick=()=>{{const a=document.createElement('a');a.href=URL.createObjectURL(new Blob([JSON.stringify(collect(),null,2)],{{type:'application/json'}}));a.download='hr-v0-lot-a-alternate-route-draft.json';a.click();setTimeout(()=>URL.revokeObjectURL(a.href),1000)}};document.getElementById('clear').onclick=()=>{{if(confirm('Clear every unsaved draft input?'))location.reload()}};window.projectButtonCollectDraft=collect;}})();\n"
    return page, script


def update_config(data: dict[str, tuple[list[str], list[dict[str, object]]]]) -> None:
    shutil.copytree(CFG0, CFG)
    current = read_csv(CFG / "current-configuration-map.csv")
    current.append(warned({"record_id":"CFG-48","role":"Lot A alternate acquisition-route qualification","identifier":ID,"source_path":"release/hr-v0/lot-a-alternate-route-p0.1/package-status.json","configuration_state":"CURRENT ROUTE QUALIFICATION - NO PURCHASE AUTHORITY","release_boundary":"commercial page observations only; cart/quote, owner decision, receipt and physical evidence remain open"}))
    write_csv(CFG / "current-configuration-map.csv", list(current[0]), current)
    supers = read_csv(CFG / "supersession-map.csv")
    supers.append(warned({"record_id":"SUP-45","prior_identifier":"HR-V0-CONFIG-REC-P0.30","current_or_required_successor":CID,"disposition":"superseded for current package indexing; R266 remains source evidence","use_authorized":"NO"}))
    write_csv(CFG / "supersession-map.csv", list(supers[0]), supers)
    holds = read_csv(CFG / "open-holds.csv")
    for row in data["readiness-gate.csv"][1]:
        holds.append(warned({"hold_id":f"HOLD-{len(holds)+1:02d}","hold":f"{ID}: {row['decision']}","state":row["state"],"closure_evidence":row["required_evidence"]}))
    write_csv(CFG / "open-holds.csv", list(holds[0]), holds)
    accept = read_csv(CFG / "acceptance-matrix.csv")
    for row in data["acceptance-matrix.csv"][1]:
        accept.append(warned({"acceptance_id":f"ACC-{len(accept)+1:03d}","criterion":f"{ID}: {row['criterion']}","execution_state":"NOT EXECUTED","result":"OPEN","evidence_uri":"","approver":""}))
    write_csv(CFG / "acceptance-matrix.csv", list(accept[0]), accept)
    impacts = read_csv(CFG / "gate-impact.csv")
    for row in impacts:
        if row["gate_id"] in {"EG-002","EG-003","EG-005"}:
            row["evidence_added"] += f"; {ID} exact actuator marketplace route comparison and split-basket hold"
            row["remaining_evidence"] += "; dated carts/quotes and allocation for both sellers; signed owner roles/spend/scope; received quarantine and identity evidence"
    write_csv(CFG / "gate-impact.csv", list(impacts[0]), impacts)
    status = json.loads((CFG / "package-status.json").read_text(encoding="utf-8"))
    status.update({"identifier":CID,"round":ROUND,"date":DATE,"system_bom_groups":109,"current_records":48,"supersession_records":45,"bom_integration_records":30,"gate_records":11,"open_holds":len(holds),"acceptance_rows":len(accept),"lot_a_alternate_route":ID})
    for key in ("physical_article_exists","physical_test_executed","qualified_review_complete","procurement_authorized","fabrication_authorized","assembly_authorized","connection_authorized","powered_testing_authorized","motion_authorized","energization_authorized","safety_credit"):
        status[key] = False
    (CFG / "package-status.json").write_text(json.dumps(status,indent=2)+"\n",encoding="utf-8")
    (CFG / "README.md").write_text(f"# {CID}\n\n> **{WARNING}**\n\nR267 adds {ID}. The exact actuator marketplace route is conditionally admissible for dated cart/quote evaluation only. It authorizes no contact, cart, checkout, purchase, receipt or physical work. {len(holds)} holds and {len(accept)} blank acceptances remain.\n",encoding="utf-8")
    shutil.copy2(REL / "index.html", CFG / "index.html")
    shutil.copy2(REL / "decision.js", CFG / "decision.js")
    hashes = []
    for row in current:
        path = ROOT / row["source_path"]
        hashes.append(warned({"source_path":row["source_path"],"sha256":sha(path),"role":row["role"]}))
    write_csv(CFG / "source-hash-register.csv", ["source_path","sha256","role","warning"], hashes)
    manifest(CFG)
    shutil.copytree(CFG, CFGR)
    manifest(CFGR)


def update_release() -> None:
    data = json.loads(RELEASE.read_text(encoding="utf-8"))
    for product in data["current_products"]:
        if product.get("domain") in {"electrical","mechanical","bill_of_materials","commissioning","assembly"}:
            product["configuration_reconciliation"] = CID
        if product.get("domain") in {"mechanical","bill_of_materials","assembly"}:
            for value in (ID,CID):
                if value not in product.get("supporting_identifiers",[]):
                    product.setdefault("supporting_identifiers",[]).append(value)
            product["lot_a_alternate_route"] = ID
    RELEASE.write_text(json.dumps(data,indent=2)+"\n",encoding="utf-8")


def docs() -> None:
    (ROOT / "docs/hr-v0-lot-a-alternate-route-p0.1.md").write_text(f"""# HR-V0 Lot A alternate acquisition route P0.1

> **{WARNING}**

R267 qualifies one actuator-only commercial route for **dated cart/quote evaluation**, not purchase. DigiKey Marketplace displays manufacturer part `902-0137-000` as `XM540-W270-T`, quantity 19, $482.89 each, and shipment from ROBOTIS Inc. The official ROBOTIS Japan e-Shop independently distinguishes `902-0137-000` / `-T` / TTL 3-pin from `902-0133-000` / `-R` / RS-485 4-pin.

The candidate basket uses DigiKey Marketplace for two actuators and ROBOTIS US for two H101 plus two S102 frame sets. Its visible subtotal remains **$1,182.22**. This is a split commercial route: no cart, quote, allocation, shipping, tax, fees, terms acceptance, purchaser, receiver, payment authority, signature or received article exists. RobotShop is rejected for the current two-unit lot because it displays one unit; Trossen is rejected because it displays out of stock. The ROBOTIS US direct actuator route remains held on its T/R page contradiction.

Primary evidence: [DigiKey marketplace listing](https://www.digikey.com/en/products/detail/robotis/902-0137-000/12349044), [ROBOTIS Japan e-Shop](https://e-shop.robotis.co.jp/product.php?id=43), [ROBOTIS e-Manual](https://emanual.robotis.com/docs/en/dxl/x/xm540-w270/), [ROBOTIS US actuator page](https://www.robotis.us/dynamixel-xm540-w270-t/), [RobotShop](https://www.robotshop.com/products/robotis-dynamixel-xm540-w270-t-smart-servo-actuator), [Trossen](https://store.trossenrobotics.com/products/dynamixel-xm540-w270-t-robot-actuator-2), [H101](https://robotis.us/fr13-h101k-set/) and [S102](https://www.robotis.us/fr13-s102k-set/).

Interactive guide: [release package](../release/hr-v0/lot-a-alternate-route-p0.1/index.html).
""",encoding="utf-8")
    (ROOT / "docs/reviews/2026-08-12-r267-validation-record.md").write_text(f"""# R267 validation record

> **{WARNING}**

`{ID}` records eight current source checks, four compared routes, three exact basket lines, six open findings, twelve gates, twelve blank owner inputs, six blank signatures, eight scope rows, ten active stop conditions and twelve blank acceptances. The visible arithmetic remains `2 x 482.89 + 2 x 76.71 + 2 x 31.51 = 1,182.22 USD`. No seller was contacted, no cart/quote was created, no checkout or download was activated, and no purchase, receipt or physical work is claimed.

The DigiKey route is conditionally admissible only because its page explicitly binds the exact manufacturer number to the `-T` model and displays fulfillment from ROBOTIS Inc. This is not a claim that dynamic stock is reserved, that commercial terms are accepted, or that the received identity is proven. No Sol R12 blocker receives qualified closure.

Automated validation passed 208 non-native repository checks and 19 KiCad-native checks. The dedicated R267 checker and `node --check` of the external decision script passed. Browser QA at the effective 1280 x 720 viewport confirmed 16 px body/input text, 14 px table text, no page-level horizontal overflow, legible unclipped content and a draft counter transition from 0/12 to 1/12 after one dummy `defer` entry; the input was cleared back to 0/12 and no download was activated. The browser evaluation sandbox does not expose page globals or handler properties, so successful counter behavior is the runtime evidence. Narrow-mobile visual QA remains unverified in this environment; responsive CSS and internal table scrolling were inspected from source.

The staged master release manifest covers 6,466 package files. No physical article, executed test, qualified approval or energization authority is claimed.
""",encoding="utf-8")
    (ROOT / "docs/reviews/2026-08-12-r267-independent-review-request.md").write_text(f"""# R267 independent review request

> **{WARNING}**

Reopen all eight linked sources. Verify each exact model, manufacturer number, seller/fulfiller wording, displayed stock, price, route disposition and subtotal. Challenge the use of DigiKey Marketplace as a route candidate and confirm that no distributor authorization broader than the displayed page wording is claimed. Audit every gate, blank field, stop, source hash, configuration count and browser behavior. Report BLOCKER / MAJOR / MINOR findings with exact file/row references. Do not contact sellers, create carts, authorize purchase or infer received identity.
""",encoding="utf-8")
    (ROOT / "docs/reviews/2026-08-12-sol-r12-post-r267-status.md").write_text(f"""# Sol R12 status after R267

> **{WARNING}**

R267 is a project-owned commercial route qualification, not a new independent review. It supplies a clearer route-level identity chain for the two XM540-W270-T candidates but does not create a cart, allocation, authority, receipt or physical evidence. The frame-kit route, landed cost, roles, scope and receiving qualification remain open.

No Sol R12 blocker closes. HR-V0 remains not build-ready and energization remains prohibited.
""",encoding="utf-8")


def update_narrative() -> None:
    readme = ROOT / "README.md"
    text = readme.read_text(encoding="utf-8")
    marker = "## Start here\n\n"
    links = "- [R267 Lot A alternate acquisition route](docs/hr-v0-lot-a-alternate-route-p0.1.md)\n- [Interactive R267 route guide](release/hr-v0/lot-a-alternate-route-p0.1/index.html)\n- [Interactive configuration reconciliation P0.31](release/hr-v0/configuration-reconciliation-p0.31/index.html)\n- [R267 independent review request](docs/reviews/2026-08-12-r267-independent-review-request.md)\n- [Sol R12 status after R267](docs/reviews/2026-08-12-sol-r12-post-r267-status.md)\n"
    if links.splitlines()[0] not in text:
        text = text.replace(marker, marker + links, 1)
    readme.write_text(text,encoding="utf-8")
    handoff = ROOT / "docs/handoff-current.md"
    h = handoff.read_text(encoding="utf-8")
    block = f"R267 Lot A alternate route: **`{ID}` qualifies DigiKey Marketplace / displayed ROBOTIS Inc fulfillment for dated quote evaluation of two exact `902-0137-000` / `XM540-W270-T` actuators. RobotShop cannot cover quantity two, Trossen is out of stock, and ROBOTIS US direct remains held on its T/R contradiction. The split basket remains $1,182.22 visible before shipping, tax and fees. `{CID}` carries 48 current records, 45 supersessions, 30 BOM integrations, 234 holds and 288 blank acceptances. No contact, cart, quote, checkout, purchase, receipt or authority exists. No Sol R12 blocker closes and energization remains prohibited.**\n\n"
    if not h.startswith("R267 Lot A alternate route:"):
        handoff.write_text(block+h,encoding="utf-8")
    ledger = ROOT / "docs/review-ledger.md"
    l = ledger.read_text(encoding="utf-8")
    row = f"| R267 | 2026-08-12 | Lot A alternate acquisition-route qualification | Codex procurement/configuration pass; not independent and nothing purchased | R266 decision capsule and current seller/manufacturer pages | Qualified DigiKey Marketplace / displayed ROBOTIS Inc fulfillment for dated quote evaluation of exact 902-0137-000 actuators; rejected RobotShop on quantity and Trossen on stock; retained split-route, allocation, landed-cost, authority and receiving holds. | `docs/hr-v0-lot-a-alternate-route-p0.1.md`; `procurement/hr-v0/lot-a-alternate-route-p0.1/`; `release/hr-v0/lot-a-alternate-route-p0.1/`; `configuration/hr-v0-config-reconciliation-p0.31/` |\n"
    if "| R267 |" not in l:
        l = l.replace("\nTwo hundred sixty-six rounds are complete", f"\n{row}\nTwo hundred sixty-seven rounds are complete", 1).replace("(R01-R266)","(R01-R267)",1)
    ledger.write_text(l,encoding="utf-8")


def main() -> None:
    for path in (PRIOR / "package-status.json", CFG0 / "package-status.json", RELEASE):
        if not path.exists():
            raise FileNotFoundError(path)
    for directory in (OUT,REL,CFG,CFGR):
        if directory.exists():
            shutil.rmtree(directory)
    data = package_rows()
    OUT.mkdir(parents=True)
    for name,(fields,records) in data.items():
        write_csv(OUT/name,fields,records)
    source_hashes = {"prior_decision_capsule":sha(PRIOR/"package-status.json"),"configuration_input":sha(CFG0/"package-status.json")}
    (OUT / "source-hash-register.json").write_text(json.dumps(source_hashes,indent=2)+"\n",encoding="utf-8")
    status = {"identifier":ID,"round":ROUND,"date":DATE,"design_base_commit":DESIGN_BASE,"official_and_commercial_sources_checked":8,"routes_compared":4,"basket_lines":3,"physical_units":6,"visible_subtotal_usd":"1182.22","open_findings":6,"decision_gates":12,"blank_owner_inputs":12,"blank_signatures":6,"active_stop_conditions":10,"acceptance_rows":12,"supplier_contacted":False,"cart_created":False,"quote_created":False,"checkout_started":False,"draft_download_executed":False,"purchase_authorized":False,"purchase_executed":False,"article_received":False,"assembly_authorized":False,"connection_authorized":False,"powered_testing_authorized":False,"motion_authorized":False,"energization_authorized":False,"safety_credit":False,"source_hashes":source_hashes,"warning":WARNING}
    (OUT / "package-status.json").write_text(json.dumps(status,indent=2)+"\n",encoding="utf-8")
    (OUT / "README.md").write_text(f"# {ID}\n\n> **{WARNING}**\n\nR267 qualifies an exact-identity actuator route for dated cart/quote evaluation only. It contacts nobody, creates no cart or quote, orders nothing and grants no authority.\n",encoding="utf-8")
    manifest(OUT)
    shutil.copytree(OUT,REL)
    page,script = interactive(data)
    (REL / "index.html").write_text(page,encoding="utf-8")
    (REL / "decision.js").write_text(script,encoding="utf-8")
    manifest(REL)
    update_release()
    update_config(data)
    docs()
    update_narrative()
    print(f"Generated {ID}: 4 routes / 6 articles / $1,182.22 visible / 0 authority")
    print(WARNING)


if __name__ == "__main__":
    main()
