#!/usr/bin/env python3
"""Generate R262 unsent JST/GAM custom-harness RFQ and config P0.26."""
from __future__ import annotations

import csv
import hashlib
import html
import json
import shutil
import zipfile
from pathlib import Path

from generate_hr_v0_bom_closure import classification


ROOT = Path(__file__).resolve().parents[1]
ID = "HR-V0-U2D2-JC1-HARNESS-RFQ-P0.1"
HID = "HR-V0-U2D2-JC1-HARNESS-P0.1"
CID = "HR-V0-CONFIG-REC-P0.26"
WARNING = "PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION"
OUT = ROOT / "procurement/hr-v0/u2d2-jc1-harness-rfq-p0.1"
REL = ROOT / "release/hr-v0/u2d2-jc1-harness-rfq-p0.1"
CFG0 = ROOT / "configuration/hr-v0-config-reconciliation-p0.25"
CFG = ROOT / "configuration/hr-v0-config-reconciliation-p0.26"
CFGR = ROOT / "release/hr-v0/configuration-reconciliation-p0.26"
BOM = ROOT / "bom/bom.csv"
CLOSURE = ROOT / "bom/hr-v0-bom-closure.csv"
RELEASE = ROOT / "release/hr-v0/release-candidate.json"
ZIP_NAME = f"{ID}-UNSENT.zip"
FIXED_ZIP_TIME = (2026, 8, 12, 0, 0, 0)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_csv(path: Path) -> tuple[list[dict[str, str]], list[str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        return list(reader), list(reader.fieldnames or [])


def write_csv(path: Path, fields: list[str], rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows({field: row.get(field, "") for field in fields} for row in rows)


def warned(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    return [row | {"warning": WARNING} for row in rows]


def manifest(directory: Path) -> None:
    files = sorted(path for path in directory.iterdir() if path.is_file() and path.name != "file-manifest.csv")
    write_csv(directory / "file-manifest.csv", ["path", "bytes", "sha256"], [
        {"path": path.name, "bytes": path.stat().st_size, "sha256": sha(path)} for path in files
    ])


def table(title: str, rows: list[dict[str, object]], fields: list[str]) -> str:
    head = "".join(f"<th>{html.escape(field.replace('_', ' ').title())}</th>" for field in fields)
    body = "".join("<tr>" + "".join(f"<td>{html.escape(str(row.get(field, '')))}</td>" for field in fields) + "</tr>" for row in rows)
    return f"<section><h2>{html.escape(title)}</h2><div class='scroll'><table><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></div></section>"


def package_rows() -> dict[str, tuple[list[str], list[dict[str, object]]]]:
    sources = [
        {"source_id":"SRC-01","organization":"JST Sales America","document":"EH connector product page","revision_or_date":"live page accessed 2026-08-12","url":"https://www.jst.com/products/crimp-style-connectors-wire-to-board-type/eh-connector/","controlled_fact":"EH is 2.5 mm pitch; 3 A at AWG 22; JST identifies its Guntersville division as a full-service custom cable/harness operation","not_proved":"acceptance of this exact harness, wire, length, twist, evidence or quantity"},
        {"source_id":"SRC-02","organization":"JST Guntersville Assembly Manufacturing","document":"EH 2.5 mm standard-lead catalog","revision_or_date":"live page accessed 2026-08-12","url":"https://gam-gec.com/crimp-and-poke-connectors/eh-2-5-mm-pitch/","controlled_fact":"standard double-ended SEH leads use AWG 22 UL1007 black wire in 2, 4, 6, 8, 10 and 12 inch inside lengths","not_proved":"500 mm custom length, two-color pair, housing population or project acceptance"},
        {"source_id":"SRC-03","organization":"JST Guntersville Assembly Manufacturing","document":"GAM-081 EH standard-lead drawing","revision_or_date":"drawing dated 2016-03-09, revision 1 dated 2018-07-02; live PDF accessed 2026-08-12","url":"https://gam-gec.com/wp-content/uploads/2018/10/GAM-081.pdf","controlled_fact":"ASEHSEH22K305 uses SEH-001T-P0.6, UL1007 22 AWG black and applicator processing; 304.8 +/- 5.0 mm nominal inside dimension and 316.2 +/- 5.0 mm overall screen","not_proved":"project finished-length datum equivalence or custom process acceptance"},
        {"source_id":"SRC-04","organization":"JST Guntersville Assembly Manufacturing","document":"custom assembly contact page","revision_or_date":"live page accessed 2026-08-12","url":"https://gam-gec.com/contact-us/","controlled_fact":"official US custom-assembly inquiry route accepts ZIP attachments and identifies sales/technical support in Guntersville, Alabama","not_proved":"quote, response, capacity, lead time, quality plan or order acceptance"},
        {"source_id":"SRC-05","organization":"JST Sales America","document":"FAQ - crimp specifications","revision_or_date":"live page accessed 2026-08-12","url":"https://www.jst.com/resources/faq/","controlled_fact":"JST directs users to Application Tools and Specifications for crimp height, strip length and tensile data and to contact JST when data is unavailable","not_proved":"numeric limits for SEH-001T-P0.6 with Belden 3051"},
        {"source_id":"SRC-06","organization":"JST","document":"EH connector catalog eEH.pdf","revision_or_date":"current catalog PDF accessed 2026-08-12","url":"https://www.jst-mfg.com/product/pdf/eng/eEH.pdf","controlled_fact":"SEH-001T-P0.6 accepts AWG 30-22 and 1.0-1.9 mm insulation OD; EHR-3 is the 3-circuit housing","not_proved":"specific conductor/process combination, workmanship or application release"},
        {"source_id":"SRC-07","organization":"Belden","document":"3051 technical data","revision_or_date":"Rev 0.118 dated 2026-06-30; accessed 2026-08-12","url":"https://www.belden.com/products/cable/electronic-wire-cable/lead-wire-hook-up-wire/3051","controlled_fact":"3051 is 22 AWG 7x30 tinned copper with nominal 1.6 mm OD; BK005 and WH005 are black and white 100 ft reels","not_proved":"GAM acceptance or JST crimp-process limits"},
        {"source_id":"SRC-08","organization":"ROBOTIS","document":"U2D2 e-Manual","revision_or_date":"live e-Manual accessed 2026-08-12","url":"https://emanual.robotis.com/docs/en/parts/interface/u2d2/","controlled_fact":"TTL cavities are 1 GND, 2 VDD and 3 DATA; U2D2 does not power DYNAMIXEL actuators","not_proved":"physical no-backfeed or finished-harness performance"},
    ]
    routes = [
        {"route_id":"ROUTE-01","candidate":"JST Guntersville Assembly Manufacturing custom harness","disposition":"PRIMARY UNSENT EVIDENCE/QUOTE ROUTE","reason":"manufacturer-controlled EH termination and custom harness capability; exact response still required","contact":"https://gam-gec.com/contact-us/; gam@jstus.com; technical support (256) 960-8668","external_action":"NOT SENT"},
        {"route_id":"ROUTE-02","candidate":"project crimp with JST YRS-260","disposition":"BACKUP HOLD","reason":"exact tool family is known but wire-specific numeric processing limits, calibration, coupons and qualified process remain absent","contact":"JST Application Tools and Specifications / technical support","external_action":"NOT REQUESTED"},
        {"route_id":"ROUTE-03","candidate":"catalog ASEHSEH22K305 leads","disposition":"REJECT AS COMPLETE HARNESS; COUPON OPTION ONLY","reason":"304.8 mm single black lead does not meet 500 mm finished two-color paired harness; no splices are allowed","contact":"https://gam-gec.com/product/asehseh22k305/","external_action":"NOT ORDERED"},
    ]
    requirements = [
        {"req_id":"RFQ-REQ-01","characteristic":"assembly","requirement":"one complete data/reference harness; quote one first article and five evaluation articles separately","acceptance_return":"provider quantity/MOQ/price/lead-time response","state":"REQUEST - NOT A PURCHASE"},
        {"req_id":"RFQ-REQ-02","characteristic":"end A","requirement":"JST EHR-3 housing; SEH-001T-P0.6 contacts only in cavities 1 and 3; cavity 2 physically empty","acceptance_return":"provider drawing and 100 percent population inspection","state":"EXACT REQUEST"},
        {"req_id":"RFQ-REQ-03","characteristic":"end B","requirement":"JST EHR-3 housing; SEH-001T-P0.6 contacts only in cavities 1 and 3; cavity 2 physically empty","acceptance_return":"provider drawing and 100 percent population inspection","state":"EXACT REQUEST"},
        {"req_id":"RFQ-REQ-04","characteristic":"connectivity","requirement":"A1-to-B1 GND; A3-to-B3 DATA; no other conductive path; no splice","acceptance_return":"100 percent continuity/isolation report with stated method and limits","state":"EXACT REQUEST"},
        {"req_id":"RFQ-REQ-05","characteristic":"wire","requirement":"requested Belden 3051 BK005 for cavity 1 and 3051 WH005 for cavity 3; identify any provider-proposed controlled equivalent before acceptance","acceptance_return":"exact manufacturer/order code, AWG, strand, material, insulation, OD and temperature rating","state":"CANDIDATE / SUBSTITUTE REQUIRES APPROVAL"},
        {"req_id":"RFQ-REQ-06","characteristic":"finished length","requirement":"500 +/- 5 mm unloaded centerline between rear wire-exit planes of assembled EHR-3 housings","acceptance_return":"provider drawing must reconcile this datum with its controlled inside/overall dimension scheme","state":"EXACT CANDIDATE HOLD"},
        {"req_id":"RFQ-REQ-07","characteristic":"pair lay","requirement":"25 +/- 5 mm per turn after termination; no shield or drain","acceptance_return":"provider capability/tolerance statement and measured first-article record","state":"EXACT CANDIDATE HOLD"},
        {"req_id":"RFQ-REQ-08","characteristic":"housing orientation","requirement":"cavity-number continuity controls; do not infer same/opposite visual orientation from an unnumbered view","acceptance_return":"numbered rear and mating-face views for both ends","state":"EXACT REQUEST"},
        {"req_id":"RFQ-REQ-09","characteristic":"strain/workmanship","requirement":"no nicked strands, insulation damage, exposed conductor outside accepted brush/bellmouth, connector load or bend below 15 mm stationary radius","acceptance_return":"provider workmanship standard and first-article inspection record","state":"QUALIFIED REVIEW REQUIRED"},
        {"req_id":"RFQ-REQ-10","characteristic":"traceability","requirement":"provider part number, drawing revision, work order/lot, component identities, tool/applicator identity and inspection status","acceptance_return":"certificate of conformance and traveler/inspection summary","state":"EXACT REQUEST"},
        {"req_id":"RFQ-REQ-11","characteristic":"process evidence","requirement":"controlled JST-compatible contact process for the accepted wire; no generic plier","acceptance_return":"numeric crimp/strip/pull limits or provider attestation to controlled JST specification plus process validation/sampling basis","state":"EVIDENCE REQUIRED"},
        {"req_id":"RFQ-REQ-12","characteristic":"label/packaging","requirement":"identify HAR-CTRL, END A U2D2 and END B JC1 without obscuring latch/bend zones; protect contacts/housings in shipment","acceptance_return":"proposed label material/placement and packaging method","state":"SELECTION REQUIRED"},
    ]
    questions = [
        {"question_id":f"Q-{i:02d}","question":question,"required_response":"written attributable response plus cited drawing/specification where applicable","state":"UNSENT"}
        for i, question in enumerate([
            "Will GAM quote one first article and five evaluation articles of the attached cavity-2-empty EHR-3 to EHR-3 harness?",
            "Can GAM manufacture the requested 500 +/- 5 mm finished datum, and how does that datum relate to GAM inside and overall dimensions?",
            "Can GAM use Belden 3051 BK005 and WH005; if not, what exact controlled black/white 22 AWG substitute is proposed?",
            "Does the proposed wire fall within the controlled SEH-001T-P0.6 conductor and insulation crimp ranges?",
            "Can GAM populate cavities 1 and 3 only and certify cavity 2 contains neither contact nor conductor at both ends?",
            "Can GAM produce and inspect a 25 +/- 5 mm pair lay without damaging the contact exits or violating bend limits?",
            "What provider part number and drawing revision would control the finished harness?",
            "What crimping machine/applicator/tool identity and controlled specification govern this wire/contact combination?",
            "Can GAM return numeric strip/crimp/pull limits, or instead a signed conformity statement to the controlled JST process and validation basis?",
            "What production sampling and destructive pull/cross-section evidence can accompany the first article without destructively testing shipped articles?",
            "What 100 percent continuity/isolation/population tests are performed and what method/limits/report can be supplied?",
            "Can GAM supply lot/work-order traceability and a certificate of conformance for housings, contacts, wire and processing?",
            "What workmanship standard, retention inspection, wire-exit support and damage criteria are used?",
            "What label materials/locations are available for HAR-CTRL, END A U2D2 and END B JC1?",
            "What packaging protects friction-lock housings and contacts during shipment?",
            "What are MOQ, first-article/nonrecurring charges, unit prices, lead time, quote validity and shipping terms to Boston, Massachusetts?",
            "Will custom harness material or process substitutions require written customer approval before manufacture?",
            "What additional application information does GAM require before accepting the build?",
        ], 1)
    ]
    evaluation = [
        {"evaluation_id":f"EV-{i:02d}","topic":topic,"required_evidence":evidence,"response":"","review_state":"NOT RECEIVED","reviewer":"","decision":"OPEN"}
        for i, (topic, evidence) in enumerate([
            ("provider identity/capability","attributable GAM response and controlled route"),
            ("provider part/drawing","unique part number, revision and complete numbered views"),
            ("component identity","EHR-3, SEH-001T-P0.6 and exact wire identities"),
            ("wire/contact compatibility","controlled conductor/insulation range and process confirmation"),
            ("finished dimension","provider datum reconciliation and tolerance acceptance"),
            ("cavity-2 omission","drawing plus 100 percent inspection method"),
            ("crimp process","tool/applicator, controlled specification and validation basis"),
            ("destructive process evidence","pull/cross-section/sample plan and results route"),
            ("electrical inspection","100 percent continuity/isolation method, limits and report"),
            ("pair lay/routing","manufacturing capability, tolerance and exit-strain control"),
            ("traceability/conformance","work order/lot, traveler summary and certificate"),
            ("commercial","MOQ, quantities, charges, price, lead time, validity and shipping"),
        ], 1)
    ]
    transmission = [
        {"transmission_id":"TX-01","recipient":"JST Guntersville Assembly Manufacturing","route":"https://gam-gec.com/contact-us/ / gam@jstus.com","attachment":ZIP_NAME,"attachment_sha256":"POPULATED AFTER GENERATION","authorization":"NOT AUTHORIZED","sent_at":"","sender":"","response_uri":"","state":"UNSENT"}
    ]
    holds = [
        {"hold_id":"R262-H01","scope":"transmission authority","state":"NOT AUTHORIZED","closure_evidence":"named sender and written authorization to transmit exact ZIP through official route"},
        {"hold_id":"R262-H02","scope":"provider technical response","state":"NOT RECEIVED","closure_evidence":"attributable GAM response to all eighteen questions"},
        {"hold_id":"R262-H03","scope":"provider part number and drawing","state":"SELECTION REQUIRED","closure_evidence":"unique custom assembly identity and accepted numbered drawing"},
        {"hold_id":"R262-H04","scope":"wire/contact process compatibility","state":"SELECTION REQUIRED","closure_evidence":"GAM acceptance of Belden wire or accepted exact substitute and controlled SEH process"},
        {"hold_id":"R262-H05","scope":"dimension datum and first article","state":"PHYSICAL EVIDENCE REQUIRED","closure_evidence":"provider datum reconciliation and received 500 +/- 5 mm first-article record"},
        {"hold_id":"R262-H06","scope":"crimp/process validation","state":"PHYSICAL EVIDENCE REQUIRED","closure_evidence":"controlled specification attestation, tool/applicator identity and accepted coupon/process evidence"},
        {"hold_id":"R262-H07","scope":"electrical and population inspection","state":"TEST REQUIRED","closure_evidence":"100 percent continuity/isolation/cavity-population results with accepted limits"},
        {"hold_id":"R262-H08","scope":"commercial and purchase decision","state":"SELECTION REQUIRED","closure_evidence":"attributable quote, comparison, budget/quantity decision and separate purchase authorization"},
        {"hold_id":"R262-H09","scope":"received route and system tests","state":"PHYSICAL EVIDENCE REQUIRED","closure_evidence":"installed fit, strain, separation, no-backfeed and waveform/error-rate evidence"},
        {"hold_id":"R262-H10","scope":"qualified review and work authority","state":"NOT EXECUTED","closure_evidence":"qualified electrical/controls acceptance and separate written authority for each physical stage"},
    ]
    acceptance = [
        {"acceptance_id":f"R262-ACC-{i:02d}","criterion":criterion,"execution_state":"NOT EXECUTED","result":"OPEN","evidence_uri":"","approver":""}
        for i, criterion in enumerate([
            "The controlled RFQ payload exactly matches the R261 cavity map and warning",
            "The primary route is JST/GAM custom assembly and remains UNSENT",
            "Catalog 304.8 mm single leads are rejected as the complete 500 mm two-conductor harness",
            "No splice or cavity-2 contact/conductor is permitted",
            "Provider drawing reconciles project finished length with provider inside/overall datums",
            "Exact accepted wire and SEH-001T-P0.6 process compatibility are documented",
            "Provider process evidence is attributable, configuration-bound and qualified-reviewed",
            "First-article population, length, lay, workmanship, continuity and isolation evidence passes",
            "Received system route, no-backfeed and waveform/error-rate evidence passes",
            "Commercial response is accepted through a separate purchase decision",
            "No external transmission or purchase has occurred in R262",
            "No fabrication, assembly, connection, powered test, motion, energization or safety credit is authorized",
        ], 1)
    ]
    return {
        "source-register.csv": (["source_id","organization","document","revision_or_date","url","controlled_fact","not_proved","warning"], warned(sources)),
        "supplier-route.csv": (["route_id","candidate","disposition","reason","contact","external_action","warning"], warned(routes)),
        "harness-requirement.csv": (["req_id","characteristic","requirement","acceptance_return","state","warning"], warned(requirements)),
        "provider-question-register.csv": (["question_id","question","required_response","state","warning"], warned(questions)),
        "response-evaluation.csv": (["evaluation_id","topic","required_evidence","response","review_state","reviewer","decision","warning"], warned(evaluation)),
        "transmission-register.csv": (["transmission_id","recipient","route","attachment","attachment_sha256","authorization","sent_at","sender","response_uri","state","warning"], warned(transmission)),
        "open-holds.csv": (["hold_id","scope","state","closure_evidence","warning"], warned(holds)),
        "acceptance-matrix.csv": (["acceptance_id","criterion","execution_state","result","evidence_uri","approver","warning"], warned(acceptance)),
    }


def svg() -> str:
    return f"""<svg xmlns='http://www.w3.org/2000/svg' width='1200' height='480' viewBox='0 0 1200 480' role='img' aria-labelledby='title desc'><title id='title'>HAR-CTRL cavity map</title><desc id='desc'>Two EHR-3 housings connect cavity 1 ground and cavity 3 data. Cavity 2 is empty at both ends.</desc><style>text{{font-family:system-ui,sans-serif;fill:#092f57}}.h{{font-size:28px;font-weight:800}}.t{{font-size:18px}}.n{{font-size:22px;font-weight:800}}.box{{fill:#dff3ff;stroke:#092f57;stroke-width:4}}.g{{stroke:#111;stroke-width:12}}.d{{stroke:#f3bd28;stroke-width:12}}.x{{stroke:#8d1721;stroke-width:5;stroke-dasharray:14 12}}</style><rect width='1200' height='480' fill='#f8fbfe'/><text x='40' y='48' class='h'>HAR-CTRL — numbered connectivity, not visual-orientation inference</text><rect x='70' y='100' width='230' height='280' rx='18' class='box'/><rect x='900' y='100' width='230' height='280' rx='18' class='box'/><text x='120' y='145' class='h'>END A · U2D2</text><text x='930' y='145' class='h'>END B · JC1</text><text x='100' y='220' class='n'>1 · GND</text><text x='100' y='285' class='n'>2 · EMPTY</text><text x='100' y='350' class='n'>3 · DATA</text><text x='930' y='220' class='n'>1 · CTRL_GND</text><text x='930' y='285' class='n'>2 · EMPTY</text><text x='930' y='350' class='n'>3 · DXL_DATA</text><line x1='300' y1='212' x2='900' y2='212' class='g'/><line x1='300' y1='342' x2='900' y2='342' class='d'/><line x1='300' y1='277' x2='900' y2='277' class='x'/><text x='430' y='198' class='t'>BLACK · 3051 BK005 · cavity 1 to 1</text><text x='430' y='330' class='t'>WHITE · 3051 WH005 · cavity 3 to 3</text><text x='428' y='270' class='t'>NO CONTACT · NO CONDUCTOR · NO SPLICE</text><text x='360' y='430' class='t'>500 +/- 5 mm project finished-datum candidate · provider datum reconciliation required</text></svg>"""


def request_message() -> str:
    return f"""Subject: UNSENT DRAFT - custom JST EH two-conductor harness technical/RFQ request

This message is a controlled draft and has not been sent.

Please review the attached {ID} package for a custom EHR-3 to EHR-3 evaluation harness. The requested assembly uses SEH-001T-P0.6 contacts in cavities 1 and 3 only, leaves cavity 2 physically empty at both ends, provides straight-through 1-to-1 and 3-to-3 connectivity, and contains no splice. The project finished-length candidate is 500 +/- 5 mm with a 25 +/- 5 mm pair lay.

Please quote one first article and five evaluation articles separately and return an attributable drawing, exact material identities, process-conformity evidence, inspection/test capabilities, MOQ, charges, unit prices and lead time. Belden 3051 BK005/WH005 is requested; identify any proposed substitute before acceptance. Please answer every row in provider-question-register.csv.

This request is for technical and commercial information only. It is not a purchase order, fabrication authorization, connection instruction or permission to energize hardware.

{WARNING}
"""


def guide(data: dict[str, tuple[list[str], list[dict[str, object]]]]) -> str:
    routes = data["supplier-route.csv"][1]
    reqs = data["harness-requirement.csv"][1]
    questions = data["provider-question-register.csv"][1]
    holds = data["open-holds.csv"][1]
    return f"""<!doctype html><html lang='en'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'><title>{ID}</title><style>:root{{--sky:#dff3ff;--blue:#092f57;--gold:#f3bd28;--ink:#102338;--paper:#f8fbfe;--line:#8eb9d8;--danger:#8d1721}}*{{box-sizing:border-box}}body{{margin:0;background:var(--paper);color:var(--ink);font:clamp(16px,1.15vw,19px)/1.55 system-ui,sans-serif}}header{{padding:clamp(24px,5vw,68px);background:linear-gradient(135deg,var(--sky),#fff);border-bottom:8px solid var(--gold)}}main{{max-width:1500px;margin:auto;padding:24px}}h1{{font-size:clamp(34px,5vw,70px);line-height:1.05;color:var(--blue)}}h2{{font-size:clamp(23px,2.3vw,34px);color:var(--blue)}}.warn{{background:#fff4c7;border:3px solid var(--gold);padding:16px;font-weight:800}}.cards{{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:16px;margin:24px 0}}.card,section{{background:#fff;border:2px solid var(--line);border-radius:14px;padding:18px;margin:18px 0}}.big{{font-size:2.2rem;font-weight:850;color:var(--blue)}}.state{{font-weight:850;color:var(--danger)}}object{{width:100%;min-height:420px;border:0}}.scroll{{overflow-x:auto}}table{{width:100%;border-collapse:collapse;min-width:980px;font-size:14px}}th,td{{text-align:left;vertical-align:top;padding:11px;border-bottom:1px solid #bed5e6;line-height:1.45}}th{{background:var(--blue);color:#fff;position:sticky;top:0}}a{{font-size:16px;font-weight:750;color:#075ea8}}@media(max-width:700px){{main{{padding:12px}}object{{min-height:300px}}table{{min-width:820px}}}}</style></head><body><header><p class='warn'>{WARNING}</p><h1>Ask the connector manufacturer to build it.</h1><p>R262 packages the exact R261 harness into a deterministic, unsent technical/RFQ bundle. It replaces guessed crimp data with an attributable manufacturer-response route.</p></header><main><div class='cards'><article class='card'><div class='big'>18</div><strong>provider questions</strong></article><article class='card'><div class='big'>12</div><strong>exact requirement rows</strong></article><article class='card'><div class='big'>1 + 5</div><strong>quote quantities, not an order</strong></article><article class='card'><div class='big'>UNSENT</div><strong>external state</strong></article></div><section><h2>Numbered harness view</h2><object type='image/svg+xml' data='assembly-definition.svg'>HAR-CTRL cavity map: 1-to-1 GND, cavity 2 empty, 3-to-3 DATA.</object><p class='state'>The catalog 12-inch single lead is not the complete project harness. No splice is permitted.</p></section>{table('Manufacturing routes', routes, ['route_id','candidate','disposition','reason','external_action'])}{table('Provider requirements', reqs, ['req_id','characteristic','requirement','acceptance_return','state'])}{table('Questions to answer', questions, ['question_id','question','required_response','state'])}{table('Open evidence', holds, ['hold_id','scope','state','closure_evidence'])}<section><h2>Controlled records</h2><p><a href='{ZIP_NAME}'>UNSENT ZIP</a> · <a href='request-message.txt'>draft message</a> · <a href='harness-requirement.csv'>requirements</a> · <a href='provider-question-register.csv'>questions</a> · <a href='response-evaluation.csv'>response evaluation</a> · <a href='transmission-register.csv'>transmission state</a> · <a href='open-holds.csv'>holds</a></p></section><p class='warn'>{WARNING}</p></main></body></html>"""


def make_zip(directory: Path) -> None:
    payload = ["request-message.txt", "assembly-definition.svg", "harness-requirement.csv", "provider-question-register.csv", "response-evaluation.csv"]
    internal = []
    for name in payload:
        path = directory / name
        internal.append({"path":name,"bytes":path.stat().st_size,"sha256":sha(path)})
    manifest_text = "path,bytes,sha256\n" + "".join(f"{r['path']},{r['bytes']},{r['sha256']}\n" for r in internal)
    control = json.dumps({"identifier":ID,"state":"UNSENT","purchase_order":False,"work_authority":False,"warning":WARNING}, indent=2) + "\n"
    with zipfile.ZipFile(directory / ZIP_NAME, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for name in payload:
            info = zipfile.ZipInfo(name, FIXED_ZIP_TIME)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, (directory / name).read_bytes())
        for name, content in (("PAYLOAD-MANIFEST.csv", manifest_text.encode()), ("PACKAGE-CONTROL.json", control.encode())):
            info = zipfile.ZipInfo(name, FIXED_ZIP_TIME)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, content)


def update_bom() -> None:
    rows, fields = read_csv(BOM)
    by_id = {row["item_id"]: row for row in rows}
    by_id["BOM-054"]["selection_basis"] = "Two EHR-3 housings are controlled internal content of BOM-061. R262 makes JST/GAM custom assembly the primary unsent inquiry route; separate housing purchase is prohibited if that route is later accepted. Provider part/drawing, received identity, population, retention and physical evidence remain open."
    by_id["BOM-055"]["selection_basis"] = "Four SEH-001T-P0.6 contacts are controlled internal content of BOM-061 cavities 1 and 3. R262 makes manufacturer-controlled termination the primary unsent inquiry route; separate contact/tool purchase is prohibited if accepted. Exact wire/process compatibility, crimp conformity, pull/section evidence, retention and received inspection remain open."
    by_id["BOM-061"]["selection_basis"] += " R262 adds a deterministic UNSENT JST/GAM custom-assembly RFQ and rejects catalog 304.8 mm single leads as the complete harness. Provider part/drawing, response, quote, process evidence, first article, purchase decision and every physical/system result remain open."
    write_csv(BOM, fields, sorted(rows, key=lambda row: int(row["item_id"].split("-")[1])))
    closure_fields = read_csv(CLOSURE)[1]
    write_csv(CLOSURE, closure_fields, [{"item_id": row["item_id"], **classification(row)} for row in rows])


def update_release() -> None:
    data = json.loads(RELEASE.read_text(encoding="utf-8"))
    for product in data["current_products"]:
        if product.get("domain") in {"electrical", "bill_of_materials", "assembly"}:
            for value in (ID, CID):
                if value not in product.get("supporting_identifiers", []):
                    product.setdefault("supporting_identifiers", []).append(value)
            product["configuration_reconciliation"] = CID
            product["u2d2_jc1_harness_rfq"] = ID
        if product.get("domain") == "bill_of_materials":
            product["release_state"] = "r262_108_group_bom_u2d2_jc1_manufacturer_rfq_ready_unsent_provider_response_quote_process_first_article_physical_qualified_and_authority_evidence_open_lot_a_purchase_blocker_no_complete_machine_procurement_release"
    RELEASE.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def update_config() -> None:
    shutil.copytree(CFG0, CFG)
    current, fields = read_csv(CFG / "current-configuration-map.csv")
    current.append({"record_id":"CFG-45","role":"U2D2-to-JC1 manufacturer-build technical/RFQ route","identifier":ID,"source_path":"release/hr-v0/u2d2-jc1-harness-rfq-p0.1/package-status.json","configuration_state":"CURRENT UNSENT RFQ - NO PURCHASE OR PHYSICAL AUTHORITY","release_boundary":"exact provider request and evaluation route ready; response, part/drawing, quote, process evidence, first article, system tests and authority open","warning":WARNING})
    write_csv(CFG / "current-configuration-map.csv", fields, current)
    supersession, fields = read_csv(CFG / "supersession-map.csv")
    supersession.append({"record_id":"SUP-38","prior_identifier":"HR-V0-CONFIG-REC-P0.25","current_or_required_successor":CID,"disposition":"SUPERSEDED BY R262 CONFIGURATION RECORD ONLY","use_authorized":"NO","warning":WARNING})
    write_csv(CFG / "supersession-map.csv", fields, supersession)
    gates, fields = read_csv(CFG / "gate-impact.csv")
    for row in gates:
        if row["gate_id"] in {"EG-002", "EG-003", "EG-015", "EG-018", "EG-020"}:
            row["evidence_added"] += f"; {ID} deterministic unsent manufacturer-build request and response-evaluation contract"
            row["remaining_evidence"] += "; authorized transmission; attributable provider response/quote; accepted drawing/process; first article; physical/system evidence; qualified acceptance"
    write_csv(CFG / "gate-impact.csv", fields, gates)
    holds, fields = read_csv(CFG / "open-holds.csv")
    for index, row in enumerate(package_rows()["open-holds.csv"][1], 166):
        holds.append({"hold_id":f"HOLD-{index:03d}","hold":f"{ID}: {row['scope']}","state":row["state"],"closure_evidence":row["closure_evidence"],"warning":WARNING})
    write_csv(CFG / "open-holds.csv", fields, holds)
    acceptance, fields = read_csv(CFG / "acceptance-matrix.csv")
    for index, row in enumerate(package_rows()["acceptance-matrix.csv"][1], 205):
        acceptance.append({"acceptance_id":f"ACC-{index:03d}","criterion":f"{ID}: {row['criterion']}","execution_state":"NOT EXECUTED","result":"OPEN","evidence_uri":"","approver":"","warning":WARNING})
    write_csv(CFG / "acceptance-matrix.csv", fields, acceptance)
    status = json.loads((CFG / "package-status.json").read_text(encoding="utf-8"))
    status.update({"identifier":CID,"round":"R262","date":"2026-08-12","current_records":45,"supersession_records":38,"bom_integration_records":29,"gate_records":11,"open_holds":len(holds),"acceptance_rows":len(acceptance),"u2d2_jc1_harness_rfq":ID})
    (CFG / "package-status.json").write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8")
    (CFG / "README.md").write_text(f"# {CID}\n\n> **{WARNING}**\n\nR262 adds {ID}: a deterministic, UNSENT manufacturer-build request for the R261 controller harness. Provider response, quote, process evidence, first article, purchase decision and all physical/system acceptance remain open. {len(holds)} holds and {len(acceptance)} blank acceptances remain.\n", encoding="utf-8")
    (CFG / "index.html").write_text((REL / "index.html").read_text(encoding="utf-8"), encoding="utf-8")
    source_rows = []
    for row in current:
        path = ROOT / row["source_path"]
        source_rows.append({"source_path":row["source_path"],"sha256":sha(path),"role":row["role"],"warning":WARNING})
    write_csv(CFG / "source-hash-register.csv", ["source_path","sha256","role","warning"], source_rows)
    manifest(CFG)
    shutil.copytree(CFG, CFGR)
    manifest(CFGR)


def main() -> None:
    for directory in (OUT, REL, CFG, CFGR):
        if directory.exists():
            shutil.rmtree(directory)
    update_bom()
    data = package_rows()
    OUT.mkdir(parents=True)
    for name, (fields, rows) in data.items():
        write_csv(OUT / name, fields, rows)
    (OUT / "assembly-definition.svg").write_text(svg(), encoding="utf-8")
    (OUT / "request-message.txt").write_text(request_message(), encoding="utf-8")
    (OUT / "README.md").write_text(f"# {ID}\n\n> **{WARNING}**\n\nR262 creates a deterministic, UNSENT JST/GAM technical/RFQ package for {HID}. It does not contact a provider, select a custom part, authorize a purchase or close physical evidence.\n", encoding="utf-8")
    make_zip(OUT)
    transmission, fields = read_csv(OUT / "transmission-register.csv")
    transmission[0]["attachment_sha256"] = sha(OUT / ZIP_NAME)
    write_csv(OUT / "transmission-register.csv", fields, transmission)
    status = {"identifier":ID,"round":"R262","date":"2026-08-12","parent_harness":HID,"source_records":8,"supplier_routes":3,"requirement_rows":12,"provider_questions":18,"response_evaluation_rows":12,"transmission_rows":1,"open_holds":10,"acceptance_rows":12,"payload_zip":ZIP_NAME,"payload_sha256":sha(OUT / ZIP_NAME),"manufacturer_build_route_defined":True,"external_transmission_authorized":False,"external_transmission_sent":False,"provider_response_received":False,"quote_received":False,"provider_selected":False,"purchase_authorized":False,"purchase_order_issued":False,"physical_article_exists":False,"physical_test_executed":False,"qualified_review_complete":False,"fabrication_authorized":False,"assembly_authorized":False,"connection_authorized":False,"powered_testing_authorized":False,"motion_authorized":False,"energization_authorized":False,"safety_credit":False,"warning":WARNING}
    (OUT / "package-status.json").write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8")
    (OUT / "index.html").write_text(guide(data), encoding="utf-8")
    manifest(OUT)
    shutil.copytree(OUT, REL)
    manifest(REL)
    update_release()
    update_config()
    print(f"Generated {ID}: deterministic UNSENT provider package; zero purchase/work authority")


if __name__ == "__main__":
    main()
