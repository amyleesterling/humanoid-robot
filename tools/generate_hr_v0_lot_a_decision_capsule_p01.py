#!/usr/bin/env python3
"""Generate R266 Lot A owner-decision capsule without granting purchase authority."""
from __future__ import annotations

import csv
import hashlib
import html
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ID = "HR-V0-LOT-A-DECISION-CAP-P0.1"
CID = "HR-V0-CONFIG-REC-P0.30"
ROUND = "R266"
DATE = "2026-08-12"
DESIGN_BASE = "94dc15fcbd5c82db29d265dcf2440e55398df536"
WARNING = "PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION"
OUT = ROOT / "procurement/hr-v0/lot-a-decision-capsule-p0.1"
REL = ROOT / "release/hr-v0/lot-a-decision-capsule-p0.1"
SOURCE = ROOT / "procurement/hr-v0/lot-a-source-reconciliation-p0.1"
TX = ROOT / "procurement/hr-v0/lot-a-transmission-bundles-p0.1"
CFG0 = ROOT / "configuration/hr-v0-config-reconciliation-p0.29"
CFG = ROOT / "configuration/hr-v0-config-reconciliation-p0.30"
CFGR = ROOT / "release/hr-v0/configuration-reconciliation-p0.30"
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
    rows = []
    for path in sorted(p for p in directory.rglob("*") if p.is_file() and p.name != "file-manifest.csv"):
        rows.append({"relative_path": path.relative_to(directory).as_posix(), "sha256": sha(path), "bytes": path.stat().st_size, "warning": WARNING})
    write_csv(directory / "file-manifest.csv", ["relative_path", "sha256", "bytes", "warning"], rows)


def package_rows() -> dict[str, tuple[list[str], list[dict[str, object]]]]:
    sources = [
        warned({"source_id":"R266-SRC-01","organization":"ROBOTIS US","title":"DYNAMIXEL XM540-W270-T","revision_or_date":"no revision shown; accessed 2026-08-12","url":"https://www.robotis.us/dynamixel-xm540-w270-t/","observed_fact":"title -T; SKU 902-0137-000; $482.89; TTL; stock field blank; package table names -R","boundary":"identity contradiction persists; no shipment identity or allocation inferred"}),
        warned({"source_id":"R266-SRC-02","organization":"ROBOTIS US","title":"FR13-H101K Set","revision_or_date":"no revision shown; accessed 2026-08-12","url":"https://robotis.us/fr13-h101k-set/","observed_fact":"SKU 903-0270-300; $76.71; stock field blank; X540 hinge/idler set","boundary":"blank stock is neither available nor unavailable evidence"}),
        warned({"source_id":"R266-SRC-03","organization":"ROBOTIS US","title":"FR13-S102K Set","revision_or_date":"no revision shown; accessed 2026-08-12","url":"https://www.robotis.us/fr13-s102k-set/","observed_fact":"SKU 903-0269-300; $31.51; Current Stock 94; X540 side-frame set","boundary":"page value does not reserve or allocate two units"}),
        warned({"source_id":"R266-SRC-04","organization":"ROBOTIS","title":"XM540-W270-T/R e-Manual","revision_or_date":"live page; no revision shown; accessed 2026-08-12","url":"https://emanual.robotis.com/docs/en/dxl/x/xm540-w270/","observed_fact":"manufacturer distinguishes T TTL and R RS-485 variants","boundary":"does not resolve what SKU 902-0137-000 will ship"}),
    ]
    items = [
        warned({"item_id":"LOT-A-001","identity":"DYNAMIXEL XM540-W270-T","order_code":"902-0137-000","quantity":2,"unit_price_usd_visible":"482.89","extended_visible_usd":"965.78","stock_observation":"NO NUMERIC VALUE","allocation":"NOT PROVED","decision_state":"BLOCKED - WRITTEN T/R IDENTITY AND ALLOCATION REQUIRED"}),
        warned({"item_id":"LOT-A-002","identity":"FR13-H101K Set","order_code":"903-0270-300","quantity":2,"unit_price_usd_visible":"76.71","extended_visible_usd":"153.42","stock_observation":"NO NUMERIC VALUE","allocation":"NOT PROVED","decision_state":"HOLD - ALLOCATION AND OWNER DECISION REQUIRED"}),
        warned({"item_id":"LOT-A-003","identity":"FR13-S102K Set","order_code":"903-0269-300","quantity":2,"unit_price_usd_visible":"31.51","extended_visible_usd":"63.02","stock_observation":"94 DISPLAYED AT ACCESS TIME","allocation":"NOT PROVED","decision_state":"HOLD - ALLOCATION AND OWNER DECISION REQUIRED"}),
    ]
    contradictions = [
        warned({"finding_id":"R266-F-01","severity":"BLOCKER","subject":"XM540 shipment identity","evidence":"same official seller page says -T/TTL but package table says -R","required_closure":"attributable written ROBOTIS SKU-to-model/protocol/contents response plus received label and later controlled model readback","state":"OPEN"}),
        warned({"finding_id":"R266-F-02","severity":"MAJOR","subject":"allocation","evidence":"two required pages expose blank numeric stock and one page shows an unreserved count","required_closure":"dated cart or written allocation for all six exact articles","state":"OPEN"}),
        warned({"finding_id":"R266-F-03","severity":"MAJOR","subject":"landed cost","evidence":"$1,182.22 visible subtotal excludes shipping, Massachusetts tax status, fees and changes","required_closure":"dated cart/quote to selected ship-to plus accepted maximum spend","state":"OPEN"}),
        warned({"finding_id":"R266-F-04","severity":"MAJOR","subject":"authority","evidence":"no named purchaser, receiver, payment authority, ship-to, signed scope or maximum spend","required_closure":"separately signed program-owner receipt/quarantine-only purchase decision","state":"OPEN"}),
    ]
    gate_specs = [
        ("R266-G-01","Resolve exact XM540 -T/-R shipment identity","OPEN","accepted R257-RQ-01/02 response and received identity"),
        ("R266-G-02","Confirm allocation of all six exact articles","OPEN","dated cart or attributable seller allocation"),
        ("R266-G-03","Freeze seller and cart/quote identity","OPEN","dated ROBOTIS US cart or quote"),
        ("R266-G-04","Close shipping, tax/exemption, fees and expiration","OPEN","complete landed-cost record"),
        ("R266-G-05","Set numerical maximum spend","OPEN","signed program-owner value"),
        ("R266-G-06","Freeze exact Boston-area ship-to","OPEN","signed address record; repository copy may be redacted"),
        ("R266-G-07","Name adult receiving owner and quarantine location","OPEN","signed identity and location"),
        ("R266-G-08","Bind design baseline and exact line identities","PARTIALLY ADDRESSED - FORMAL ACCEPTANCE OPEN",f"accepted decision citing {DESIGN_BASE} and LOT-A-001..003"),
        ("R266-G-09","Accept no-substitution rule","OPEN","signed rejection of alternates without new review"),
        ("R266-G-10","Limit scope to receipt and quarantine","OPEN","signed scope excluding assembly, connection, power and use"),
        ("R266-G-11","Prepare serialized evidence storage","OPEN","controlled photo/label/packing/discrepancy locations"),
        ("R266-G-12","Name purchaser and payment authority","OPEN","signed adult identities and payment route"),
    ]
    gates = [warned({"gate_id":a,"decision":b,"state":c,"required_evidence":d}) for a,b,c,d in gate_specs]
    input_specs = [
        ("owner_decision","approve / decline / defer"),("maximum_spend_usd","numeric including contingency"),("seller_legal_name","exact seller"),("quote_or_cart_id","dated identifier"),("quote_expiration","date/time"),("ship_to_reference","controlled reference; avoid exposing full address in public repo"),("receiving_owner","adult name/reference"),("quarantine_location","controlled location"),("purchaser","adult name/reference"),("payment_authority","adult name/reference"),("tax_status","taxable / accepted exemption"),("signed_decision_uri","signed artifact reference"),
    ]
    owner_inputs = [warned({"input_id":f"R266-IN-{i:02d}","field":field,"value":"","required_content":need,"state":"BLANK - NOT DECIDED"}) for i,(field,need) in enumerate(input_specs,1)]
    auth_roles = ["program owner","purchaser","payment authority","receiving owner","independent configuration reviewer","qualified mechanical reviewer"]
    auth = [warned({"role":role,"person":"","signature_reference":"","date":"","decision":"NOT SIGNED / NO AUTHORITY"}) for role in auth_roles]
    scope = [
        ("SCOPE-01","purchase exact LOT-A-001..003 quantities","NOT AUTHORIZED"),("SCOPE-02","receive sealed articles","NOT AUTHORIZED"),("SCOPE-03","photograph labels and packing records","NOT AUTHORIZED"),("SCOPE-04","quarantine received articles","NOT AUTHORIZED"),("SCOPE-05","open packages for controlled receiving inspection","NOT AUTHORIZED"),("SCOPE-06","assemble or thread hardware","PROHIBITED BY THIS CAPSULE"),("SCOPE-07","connect any cable or power source","PROHIBITED BY THIS CAPSULE"),("SCOPE-08","powered test, motion or energization","PROHIBITED BY THIS CAPSULE"),
    ]
    receipt_scope = [warned({"scope_id":a,"activity":b,"state":c}) for a,b,c in scope]
    stops = [
        ("STOP-01","the -T/-R identity contradiction lacks attributable written closure"),("STOP-02","any exact line, quantity or order code differs"),("STOP-03","the cart or quote is undated, expired or omits shipping/tax/fees"),("STOP-04","maximum spend is blank or exceeded"),("STOP-05","ship-to, adult receiver or quarantine location is absent"),("STOP-06","seller proposes substitution, split identity or unknown revision"),("STOP-07","candidate commit or item hashes do not match"),("STOP-08","scope would include assembly, cable connection, power, motion or use"),("STOP-09","any signer, role or decision is missing"),("STOP-10","an article arrives damaged, opened, mislabeled or inconsistent"),
    ]
    stop_rows = [warned({"stop_id":a,"condition":b,"mandatory_action":"STOP; do not purchase/use; record deviation and obtain written disposition","state":"ACTIVE"}) for a,b in stops]
    accept = [warned({"acceptance_id":f"R266-ACC-{i:02d}","criterion":g[1],"execution_state":"NOT EXECUTED","result":"OPEN","evidence_uri":"","approver":""}) for i,g in enumerate(gate_specs,1)]
    binding = [
        warned({"binding_id":"R266-BIND-01","subject":"design baseline","value":DESIGN_BASE,"state":"RECORDED - FORMAL ACCEPTANCE OPEN"}),
        warned({"binding_id":"R266-BIND-02","subject":"source package","value":"HR-V0-LOT-A-SRC-P0.1","state":"HASH BOUND"}),
        warned({"binding_id":"R266-BIND-03","subject":"unsent transmission package","value":"HR-V0-LOT-A-TX-BUNDLE-P0.1","state":"HASH BOUND / NOT AUTHORIZED / NOT SENT"}),
        warned({"binding_id":"R266-BIND-04","subject":"current configuration input","value":"HR-V0-CONFIG-REC-P0.29","state":"HASH BOUND"}),
    ]
    return {
        "official-source-verification.csv":(["source_id","organization","title","revision_or_date","url","observed_fact","boundary","warning"],sources),
        "item-decision-register.csv":(["item_id","identity","order_code","quantity","unit_price_usd_visible","extended_visible_usd","stock_observation","allocation","decision_state","warning"],items),
        "open-finding-register.csv":(["finding_id","severity","subject","evidence","required_closure","state","warning"],contradictions),
        "readiness-gate.csv":(["gate_id","decision","state","required_evidence","warning"],gates),
        "owner-input-template.csv":(["input_id","field","value","required_content","state","warning"],owner_inputs),
        "authorization-register.csv":(["role","person","signature_reference","date","decision","warning"],auth),
        "receipt-scope.csv":(["scope_id","activity","state","warning"],receipt_scope),
        "stop-work-register.csv":(["stop_id","condition","mandatory_action","state","warning"],stop_rows),
        "acceptance-matrix.csv":(["acceptance_id","criterion","execution_state","result","evidence_uri","approver","warning"],accept),
        "configuration-binding.csv":(["binding_id","subject","value","state","warning"],binding),
    }


def interactive_parts(data: dict[str, tuple[list[str], list[dict[str, object]]]]) -> tuple[str,str]:
    items=data["item-decision-register.csv"][1]
    gates=data["readiness-gate.csv"][1]
    inputs=data["owner-input-template.csv"][1]
    item_cards="".join(f"<article><h3>{html.escape(str(r['item_id']))}</h3><p><strong>{html.escape(str(r['quantity']))} x {html.escape(str(r['identity']))}</strong></p><p>Order code {html.escape(str(r['order_code']))}</p><p>${html.escape(str(r['extended_visible_usd']))} visible extended price</p><p class='state'>{html.escape(str(r['decision_state']))}</p></article>" for r in items)
    gate_rows="".join(f"<tr><td><code>{r['gate_id']}</code></td><td>{html.escape(str(r['decision']))}</td><td>{html.escape(str(r['state']))}</td><td>{html.escape(str(r['required_evidence']))}</td></tr>" for r in gates)
    input_rows="".join(f"<label>{html.escape(str(r['field']).replace('_',' ').title())}<span>{html.escape(str(r['required_content']))}</span><input id='{r['field']}' type='text' autocomplete='off'></label>" for r in inputs)
    page=f"""<!doctype html><html lang='en'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'><title>{ID}</title><style>:root{{--sky:#dff3ff;--blue:#092f57;--gold:#f3bd28;--paper:#f7fbff;--ink:#102338;--line:#8bb7d6;--danger:#851b25}}*{{box-sizing:border-box}}body{{margin:0;background:var(--paper);color:var(--ink);font:clamp(16px,1.2vw,19px)/1.5 system-ui,sans-serif}}header{{padding:clamp(24px,5vw,60px);background:linear-gradient(135deg,var(--sky),white);border-bottom:8px solid var(--gold)}}main{{max-width:1450px;margin:auto;padding:24px}}h1{{font-size:clamp(34px,5vw,66px);line-height:1.05;color:var(--blue)}}h2{{font-size:clamp(25px,2.5vw,38px);color:var(--blue)}}h3{{font-size:22px;color:var(--blue)}}.warn{{background:#fff4c7;border:3px solid var(--gold);padding:16px;font-weight:850}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(280px,100%),1fr));gap:16px}}article,section{{background:white;border:2px solid var(--line);border-radius:14px;padding:18px;margin:16px 0}}.state{{color:var(--danger);font-weight:800}}.scroll{{overflow-x:auto}}table{{width:100%;min-width:980px;border-collapse:collapse;font-size:14px}}th,td{{padding:11px;border-bottom:1px solid #bfd8e8;text-align:left;vertical-align:top}}th{{background:var(--blue);color:white}}label{{display:block;font-weight:800}}label span{{display:block;font-size:14px;font-weight:400;margin:4px 0}}input{{width:100%;font:16px/1.35 system-ui;padding:10px;border:2px solid #7199b7;border-radius:8px}}button{{font:800 16px/1.2 system-ui;padding:12px 16px;border:2px solid var(--blue);border-radius:9px;background:white;color:var(--blue);margin:5px}}button.primary{{background:var(--gold);color:#17253a}}code{{font-size:14px}}@media(max-width:700px){{main{{padding:12px}}header{{padding:24px 16px}}table{{min-width:900px}}}}</style></head><body><header><p class='warn'>{WARNING}</p><h1>A decision surface, not a checkout.</h1><p>This local-only page transmits nothing, places no order, creates no signature, and grants no authority.</p></header><main><section><h2>Exact evaluation lot</h2><p>Six articles. Current official-page visible subtotal: <strong>$1,182.22</strong>. Shipping, Massachusetts tax status, fees, allocation and quote expiry remain open.</p><div class='grid'>{item_cards}</div></section><section><h2>Unclosed gates</h2><div class='scroll'><table><thead><tr><th>Gate</th><th>Decision</th><th>State</th><th>Required evidence</th></tr></thead><tbody>{gate_rows}</tbody></table></div></section><section><h2>Unsaved draft inputs</h2><p>Filling this page is not approval. Exported data remains a draft until a separately controlled signed decision is accepted.</p><div class='grid'>{input_rows}</div><button class='primary' id='download'>Download draft JSON</button><button id='clear'>Clear unsaved inputs</button><p id='count' class='state'>0 / {len(inputs)} draft inputs filled</p></section><p class='warn'>{WARNING}</p></main><script src='decision.js'></script></body></html>"""
    schema=[{"field":r["field"],"state":"BLANK - NOT DECIDED"} for r in inputs]
    script=f"""const schema={json.dumps(schema,separators=(',',':'))};function collect(){{return{{package:'{ID}',design_base:'{DESIGN_BASE}',authority_state:'NOT AUTHORIZED',warning:{json.dumps(WARNING)},inputs:schema.map(r=>({{...r,value:document.getElementById(r.field).value}}))}}}}function count(){{document.getElementById('count').textContent=collect().inputs.filter(r=>r.value!=='').length+' / '+schema.length+' draft inputs filled'}}document.addEventListener('input',count);function downloadDraft(){{const data=JSON.stringify(collect(),null,2),a=document.createElement('a');a.href=URL.createObjectURL(new Blob([data],{{type:'application/json'}}));a.download='hr-v0-lot-a-draft-decision.json';a.click();setTimeout(()=>URL.revokeObjectURL(a.href),1000)}}document.getElementById('download').onclick=downloadDraft;document.getElementById('clear').onclick=()=>{{if(confirm('Clear every unsaved draft input?'))location.reload()}};window.projectButtonCollectDraft=collect;\n"""
    return page,script


def update_release() -> None:
    data=json.loads(RELEASE.read_text(encoding="utf-8"))
    for product in data["current_products"]:
        if product.get("domain") in {"electrical","mechanical","bill_of_materials","commissioning","assembly"}:
            product["configuration_reconciliation"]=CID
        if product.get("domain") in {"mechanical","bill_of_materials","assembly"}:
            for value in (ID,CID):
                if value not in product.get("supporting_identifiers",[]): product.setdefault("supporting_identifiers",[]).append(value)
            product["lot_a_decision_capsule"]=ID
    RELEASE.write_text(json.dumps(data,indent=2)+"\n",encoding="utf-8")


def update_config(data: dict[str, tuple[list[str], list[dict[str, object]]]]) -> None:
    shutil.copytree(CFG0,CFG)
    current=read_csv(CFG/"current-configuration-map.csv")
    current.append(warned({"record_id":"CFG-47","role":"Lot A local-only owner decision capsule","identifier":ID,"source_path":"release/hr-v0/lot-a-decision-capsule-p0.1/package-status.json","configuration_state":"CURRENT DRAFT DECISION SURFACE - NO PURCHASE AUTHORITY"}))
    write_csv(CFG/"current-configuration-map.csv",list(current[0]),current)
    supers=read_csv(CFG/"supersession-map.csv")
    supers.append(warned({"record_id":"SUP-44","prior_identifier":"HR-V0-CONFIG-REC-P0.29","current_or_required_successor":CID,"scope":"configuration reconciliation only","disposition":"superseded for current package indexing; prior engineering identities remain controlled"}))
    write_csv(CFG/"supersession-map.csv",list(supers[0]),supers)
    holds=read_csv(CFG/"open-holds.csv")
    for i,row in enumerate(data["readiness-gate.csv"][1],1): holds.append(warned({"hold_id":f"HOLD-{len(holds)+1:02d}","scope":f"{ID}: {row['decision']}","state":row["state"],"closure_evidence":row["required_evidence"]}))
    write_csv(CFG/"open-holds.csv",list(holds[0]),holds)
    accept=read_csv(CFG/"acceptance-matrix.csv")
    for row in data["acceptance-matrix.csv"][1]: accept.append(warned({"acceptance_id":f"ACC-{len(accept)+1:03d}","criterion":f"{ID}: {row['criterion']}","execution_state":"NOT EXECUTED","result":"OPEN","evidence_uri":"","approver":""}))
    write_csv(CFG/"acceptance-matrix.csv",list(accept[0]),accept)
    gates=read_csv(CFG/"gate-impact.csv")
    for row in gates:
        if row["gate_id"] in {"EG-002","EG-003","EG-005"}:
            row["evidence_added"] += f"; {ID} current official-page snapshot and local-only decision capsule"
            row["remaining_evidence"] += "; attributable seller identity/allocation/quote response; signed maximum-spend/ship-to/receiver/purchaser decision; received quarantine evidence"
    write_csv(CFG/"gate-impact.csv",list(gates[0]),gates)
    status=json.loads((CFG/"package-status.json").read_text(encoding="utf-8"))
    status.update({"identifier":CID,"round":ROUND,"date":DATE,"warning":WARNING,"system_bom_groups":109,"current_records":47,"supersession_records":44,"bom_integration_records":30,"gate_records":11,"open_holds":len(holds),"acceptance_rows":len(accept),"lot_a_decision_capsule":ID})
    for key in ("physical_article_exists","physical_test_executed","qualified_review_complete","procurement_authorized","fabrication_authorized","assembly_authorized","connection_authorized","powered_testing_authorized","motion_authorized","energization_authorized","safety_credit"): status[key]=False
    (CFG/"package-status.json").write_text(json.dumps(status,indent=2)+"\n",encoding="utf-8")
    (CFG/"README.md").write_text(f"# {CID}\n\n> **{WARNING}**\n\nR266 adds {ID}, a local-only blank decision surface. It records current primary-page facts and authorizes no contact, cart, checkout, purchase or receipt. {len(holds)} holds and {len(accept)} blank acceptances remain.\n",encoding="utf-8")
    for name in ("index.html","decision.js"):
        shutil.copy2(REL/name,CFG/name)
    hashes=[]
    for row in current:
        path=ROOT/row["source_path"]
        hashes.append(warned({"source_path":row["source_path"],"sha256":sha(path),"role":row["role"]}))
    write_csv(CFG/"source-hash-register.csv",["source_path","sha256","role","warning"],hashes)
    manifest(CFG)
    shutil.copytree(CFG,CFGR)
    manifest(CFGR)


def docs() -> None:
    (ROOT/"docs/hr-v0-lot-a-decision-capsule-p0.1.md").write_text(f"""# HR-V0 Lot A decision capsule P0.1

> **{WARNING}**

R266 rechecks the three official ROBOTIS US product pages on 2026-08-12 and binds the six-article Lot A decision to design baseline `{DESIGN_BASE}`. The visible subtotal remains $1,182.22. The XM540 page still contradicts itself: its title, SKU and communication field describe the `-T`/TTL product while the package table names `-R`. Two pages expose no numeric stock; the S102 page displays 94 but does not reserve two units.

The local interactive page captures twelve unsaved draft fields and can export draft JSON only after a user action. It transmits nothing, performs no checkout, produces no signature and grants no authority. Twelve gates, four findings and all signatures remain open.

Primary sources: [XM540-W270-T](https://www.robotis.us/dynamixel-xm540-w270-t/), [FR13-H101K](https://robotis.us/fr13-h101k-set/), [FR13-S102K](https://www.robotis.us/fr13-s102k-set/), and [XM540 e-Manual](https://emanual.robotis.com/docs/en/dxl/x/xm540-w270/).

Interactive guide: [release package](../release/hr-v0/lot-a-decision-capsule-p0.1/index.html).
""",encoding="utf-8")
    (ROOT/"docs/reviews/2026-08-12-r266-validation-record.md").write_text(f"""# R266 validation record

> **{WARNING}**

`{ID}` records four current primary-source checks, three exact item lines, four open findings, twelve decision gates, twelve blank owner inputs, six blank signatures, eight scope rows, ten active stop conditions and twelve blank acceptances. The $1,182.22 arithmetic is `2 x 482.89 + 2 x 76.71 + 2 x 31.51`; it excludes shipping, tax, fees and allocation. No supplier was contacted, no cart was created, no download was activated, and no purchase or physical work is claimed.

Automated validation passed 207 non-native repository checks and 19 KiCad-native checks. The dedicated R266 checker and `node --check` of the external decision script passed. Browser QA at the effective 1280 x 720 viewport confirmed 16 px body/input text, 14 px table text, no page-level horizontal overflow, no script errors, and a draft counter change from 0/12 to 1/12 after one dummy `defer` entry. No download was activated. Narrow-mobile visual QA remains unverified because the browser viewport override did not apply in this environment; the static CSS breakpoint and internal table scrolling were inspected only from source.

The staged master release manifest passed with 6,402 package files. No Sol R12 blocker receives qualified closure.
""",encoding="utf-8")
    (ROOT/"docs/reviews/2026-08-12-r266-independent-review-request.md").write_text(f"""# R266 independent review request

> **{WARNING}**

Independently reopen all four official sources and verify the identities, order codes, prices, stock observations, subtotal arithmetic and persistent `-T`/`-R` contradiction. Audit every gate, blank field, scope boundary, stop condition, source hash, configuration count and interactive behavior. Confirm the page transmits nothing and cannot create purchase authority. Report BLOCKER / MAJOR / MINOR findings with exact file/row references. Do not contact a seller, create a cart, authorize purchase or infer received identity.
""",encoding="utf-8")
    (ROOT/"docs/reviews/2026-08-12-sol-r12-post-r266-status.md").write_text(f"""# Sol R12 status after R266

> **{WARNING}**

R266 is a project-owned commercial-decision correction, not a new independent review. It narrows the evidence gap between the existing Lot A source/inquiry packages and a future program-owner purchase decision, while retaining every missing seller response, allocation, landed cost, signature, received article and qualified review.

No Sol R12 blocker closes. HR-V0 remains not build-ready and energization remains prohibited.
""",encoding="utf-8")


def update_narrative() -> None:
    readme=ROOT/"README.md"
    text=readme.read_text(encoding="utf-8")
    marker="## Start here\n\n"
    links="- [R266 Lot A decision capsule](docs/hr-v0-lot-a-decision-capsule-p0.1.md)\n- [Interactive R266 draft decision guide](release/hr-v0/lot-a-decision-capsule-p0.1/index.html)\n- [Interactive configuration reconciliation P0.30](release/hr-v0/configuration-reconciliation-p0.30/index.html)\n- [R266 independent review request](docs/reviews/2026-08-12-r266-independent-review-request.md)\n- [Sol R12 status after R266](docs/reviews/2026-08-12-sol-r12-post-r266-status.md)\n"
    if links.splitlines()[0] not in text: text=text.replace(marker,marker+links,1)
    readme.write_text(text,encoding="utf-8")
    handoff=ROOT/"docs/handoff-current.md"
    h=handoff.read_text(encoding="utf-8")
    block=f"R266 Lot A decision capsule: **`{ID}` rechecks the official ROBOTIS US pages and preserves the $1,182.22 six-article visible subtotal while exposing the still-current XM540 `-T`/`-R` contradiction, blank XM540/H101 stock fields and unreserved S102 count. The local-only page has twelve blank draft inputs, twelve open/partial gates, six blank signatures and ten active stops. `{CID}` carries 47 current records, 44 supersessions, 30 BOM integrations, 222 holds and 276 blank acceptances. No contact, cart, checkout, download, purchase, receipt or authority exists. No Sol R12 blocker closes and energization remains prohibited.**\n\n"
    if not h.startswith("R266 Lot A decision capsule:"): handoff.write_text(block+h,encoding="utf-8")
    ledger=ROOT/"docs/review-ledger.md"
    l=ledger.read_text(encoding="utf-8")
    row=f"| R266 | 2026-08-12 | Lot A current-source and owner-decision capsule | Codex procurement/configuration pass; not independent and nothing purchased | R237/R257/R258 Lot A source and unsent inquiry chain plus R265 configuration | Rechecked the official ROBOTIS US pages, retained the unresolved XM540 T/R contradiction, and issued a local-only twelve-field draft decision surface. Six articles and the $1,182.22 visible subtotal remain unallocated; all authority is blank/false. | `docs/hr-v0-lot-a-decision-capsule-p0.1.md`; `procurement/hr-v0/lot-a-decision-capsule-p0.1/`; `release/hr-v0/lot-a-decision-capsule-p0.1/`; `configuration/hr-v0-config-reconciliation-p0.30/` |\n"
    if "| R266 |" not in l: l=l.replace("\nTwo hundred sixty-five rounds are complete",f"\n{row}\nTwo hundred sixty-six rounds are complete",1).replace("(R01-R265)","(R01-R266)",1)
    ledger.write_text(l,encoding="utf-8")


def main() -> None:
    required=[SOURCE/"item-register.csv",SOURCE/"anomaly-register.csv",SOURCE/"decision-gate.csv",TX/"package-status.json",CFG0/"package-status.json",RELEASE]
    for path in required:
        if not path.exists(): raise FileNotFoundError(path)
    for directory in (OUT,REL,CFG,CFGR):
        if directory.exists(): shutil.rmtree(directory)
    data=package_rows()
    OUT.mkdir(parents=True)
    for name,(fields,records) in data.items(): write_csv(OUT/name,fields,records)
    local_sources={"lot_a_items":SOURCE/"item-register.csv","lot_a_anomalies":SOURCE/"anomaly-register.csv","lot_a_gates":SOURCE/"decision-gate.csv","transmission_status":TX/"package-status.json","configuration_input":CFG0/"package-status.json"}
    source_hashes={key:sha(path) for key,path in local_sources.items()}
    (OUT/"source-hash-register.json").write_text(json.dumps(source_hashes,indent=2)+"\n",encoding="utf-8")
    status={"identifier":ID,"round":ROUND,"date":DATE,"design_base_commit":DESIGN_BASE,"official_sources_checked":4,"item_lines":3,"physical_units":6,"visible_subtotal_usd":"1182.22","open_findings":4,"decision_gates":12,"blank_owner_inputs":12,"blank_signatures":6,"active_stop_conditions":10,"acceptance_rows":12,"supplier_contacted":False,"cart_created":False,"checkout_started":False,"draft_download_executed":False,"purchase_authorized":False,"purchase_executed":False,"article_received":False,"assembly_authorized":False,"connection_authorized":False,"powered_testing_authorized":False,"motion_authorized":False,"energization_authorized":False,"safety_credit":False,"source_hashes":source_hashes,"warning":WARNING}
    (OUT/"package-status.json").write_text(json.dumps(status,indent=2)+"\n",encoding="utf-8")
    (OUT/"README.md").write_text(f"# {ID}\n\n> **{WARNING}**\n\nR266 is a current-source, local-only draft decision capsule. It contacts nobody, orders nothing and grants no authority.\n",encoding="utf-8")
    manifest(OUT)
    shutil.copytree(OUT,REL)
    page,script=interactive_parts(data)
    (REL/"index.html").write_text(page,encoding="utf-8")
    (REL/"decision.js").write_text(script,encoding="utf-8")
    manifest(REL)
    update_release()
    update_config(data)
    docs()
    update_narrative()
    print(f"Generated {ID}: 6 articles / $1,182.22 visible / 12 gates / 0 authority")
    print(WARNING)


if __name__ == "__main__": main()
