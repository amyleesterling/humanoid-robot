#!/usr/bin/env python3
"""Generate R257 Lot A inquiry P0.3 bound to R256 exact measurands."""
from __future__ import annotations

import html
import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import generate_hr_v0_lot_a_inquiry_p02 as old  # noqa: E402

ID = "HR-V0-LOT-A-INQUIRY-P0.3"
CID = "HR-V0-CONFIG-REC-P0.21"
WARNING = old.WARNING
OUT = ROOT / "procurement/hr-v0/lot-a-inquiry-p0.3"
REL = ROOT / "release/hr-v0/lot-a-inquiry-p0.3"
OLD = ROOT / "procurement/hr-v0/lot-a-inquiry-p0.2"
CFG0 = ROOT / "configuration/hr-v0-config-reconciliation-p0.20"
CFG = ROOT / "configuration/hr-v0-config-reconciliation-p0.21"
CFGR = ROOT / "release/hr-v0/configuration-reconciliation-p0.21"
MEAS = ROOT / "release/hr-v0/joint-measurement-definition-p0.1"


def remap(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    return [{key: value.replace("R255", "R257") if isinstance(value, str) else value for key, value in row.items() if key != "warning"} for row in rows]


def table(title: str, rows: list[dict[str, object]], fields: list[str], route: str = "") -> str:
    head = "".join(f"<th>{html.escape(field.replace('_', ' ').title())}</th>" for field in fields)
    body = "".join(f"<tr data-route='{html.escape(str(row.get(route, '')))}'>" + "".join(f"<td>{html.escape(str(row.get(field, '')))}</td>" for field in fields) + "</tr>" for row in rows)
    return f"<section><h2>{html.escape(title)}</h2><div class='scroll'><table><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></div></section>"


def guide(routes, attachments, questions, method_bids, characteristic_bids, evidence, gates) -> str:
    buttons = "".join(f"<button data-filter='{row['route_id']}'>{row['route_id']}</button>" for row in routes)
    return f"""<!doctype html><html lang='en'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'><title>{ID}</title><style>:root{{--sky:#dff3ff;--blue:#092f57;--gold:#f3bd28;--ink:#102338;--paper:#f8fbfe;--line:#8eb9d8}}*{{box-sizing:border-box}}body{{margin:0;background:var(--paper);color:var(--ink);font:clamp(16px,1.15vw,19px)/1.55 system-ui,sans-serif}}header{{padding:clamp(24px,5vw,68px);background:linear-gradient(135deg,var(--sky),#fff);border-bottom:8px solid var(--gold)}}main{{max-width:1500px;margin:auto;padding:24px}}h1{{font-size:clamp(34px,5vw,70px);line-height:1.05;color:var(--blue)}}h2{{font-size:clamp(24px,2.5vw,36px);color:var(--blue)}}.warn{{background:#fff4c7;border:3px solid var(--gold);padding:16px;font-weight:800}}.cards{{display:grid;grid-template-columns:repeat(auto-fit,minmax(210px,1fr));gap:14px;margin:22px 0}}.card,section{{background:#fff;border:2px solid var(--line);border-radius:14px;padding:18px;margin:18px 0}}.big{{font-size:2rem;font-weight:800;color:var(--blue)}}button{{font:inherit;font-weight:750;padding:10px 14px;margin:5px;border:2px solid var(--blue);border-radius:999px;background:#fff;color:var(--blue)}}button.active{{background:var(--blue);color:#fff}}.scroll{{overflow:auto}}table{{width:100%;border-collapse:collapse;min-width:980px;font-size:14px}}th,td{{text-align:left;vertical-align:top;padding:11px;border-bottom:1px solid #bed5e6;line-height:1.45}}th{{background:var(--blue);color:#fff;position:sticky;top:0}}a{{color:#075ea8;font-weight:750}}@media(max-width:700px){{main{{padding:12px}}}}</style></head><body><header><p class='warn'>{WARNING}</p><h1>Lot A inquiry P0.3</h1><p>Exact-feature metrology quote package. Nothing sent, ordered, selected, shipped or authorized.</p></header><main><div class='cards'><div class='card'><div class='big'>5</div>isolated routes</div><div class='card'><div class='big'>79</div>source features</div><div class='card'><div class='big'>18</div>characteristics per provider</div><div class='card'><div class='big'>0</div>responses or authorizations</div></div><section><h2>Exact measurement reference</h2><p><a href='../joint-measurement-definition-p0.1/index.html'>Open the R256 interactive feature and measurand guide</a>. CAD values remain nominal comparison aids, not received results or acceptance limits.</p></section><section><h2>Filter provider rows</h2><button class='active' data-filter='ALL'>All</button>{buttons}<p>Filtering changes only this review view; it cannot transmit anything.</p></section>{table('Inquiry routes',routes,['route_id','organization','official_route','purpose','selection_state'],'route_id')}{table('Controlled attachments',attachments,['attachment_id','path','recipient_scope','release_boundary'])}{table('Metrology questions',questions,['question_id','route_id','method_id','category','question','state'],'route_id')}{table('Method bid schedule',method_bids,['bid_id','route_id','method_id','requested_scope','bid_state'],'route_id')}{table('Per-characteristic bid schedule',characteristic_bids,['bid_id','route_id','characteristic_id','method_id','received_article_scope','bid_state','quoted_price'],'route_id')}{table('Required returned evidence',evidence,['evidence_id','route_id','required_record','acceptance_boundary','state'],'route_id')}{table('Decision gates',gates,['gate_id','decision','evidence_required','owner_role','state'])}<section><h2>Boundary</h2><p>Exact STEP files and derived feature records support reproducible quoting only. No provider may infer tolerances, thread functions, accepted datums, assembly authority or safety approval. Sender identity, reply address, received articles and every physical result remain absent.</p></section></main><script>const buttons=[...document.querySelectorAll('button[data-filter]')];buttons.forEach(button=>button.onclick=()=>{{buttons.forEach(item=>item.classList.remove('active'));button.classList.add('active');const filter=button.dataset.filter;document.querySelectorAll('tr[data-route]').forEach(row=>row.hidden=filter!=='ALL'&&row.dataset.route!==filter)}});</script></body></html>"""


def main() -> None:
    for directory in (OUT, REL, CFG, CFGR):
        if directory.exists():
            shutil.rmtree(directory)
    OUT.mkdir(parents=True)

    routes = remap(old.read_csv(OLD / "inquiry-route-register.csv")[0])
    for row in routes:
        row["route_state"] = row["route_state"].replace("2026-08-11", "2026-08-12")
    robotis = remap(old.read_csv(OLD / "robotis-question-register.csv")[0])
    questions = remap(old.read_csv(OLD / "metrology-question-register.csv")[0])
    for route in ("R257-RT-03", "R257-RT-04", "R257-RT-05"):
        questions.append({"question_id": f"R257-MQ-{route[-2:]}-G13", "route_id": route, "method_id": "ALL", "category": "SOURCE MATCH", "question": "Acknowledge the exact attachment hashes; describe how every received feature will be matched to the 79 source signatures and how missing, extra, inaccessible or nonmatching features will be reported without substitution.", "required_evidence": "Feature-match and discrepancy method", "state": "UNSENT / NOT RECEIVED"})
    method_bids = remap(old.read_csv(OLD / "method-bid-schedule.csv")[0])
    characteristics = old.read_csv(MEAS / "measurand-definition.csv")[0]
    characteristic_bids = []
    for route in ("R257-RT-03", "R257-RT-04", "R257-RT-05"):
        for row in characteristics:
            characteristic_bids.append({"bid_id": f"R257-CBID-{route[-2:]}-{row['characteristic_id'][-3:]}", "route_id": route, "characteristic_id": row["characteristic_id"], "method_id": row["method_id"], "received_article_scope": row["received_article_scope"], "feature_ids": row["feature_ids"], "requested_output": row["definition"], "bid_state": "NOT RECEIVED", "quoted_price": "", "lead_time": "", "technical_disposition": "NOT EXECUTED"})

    attachment_paths = [
        ("01", "docs/hr-v0-joint-stack-metrology-p0.2.md", "METROLOGY", "Five-method execution boundary"),
        ("02", "release/hr-v0/joint-stack-metrology-p0.2/method-register.csv", "METROLOGY", "Five unexecuted methods"),
        ("03", "release/hr-v0/joint-stack-metrology-p0.2/uncertainty-input-register.csv", "METROLOGY", "Blank uncertainty scaffold"),
        ("04", "docs/hr-v0-joint-measurement-definition-p0.1.md", "METROLOGY", "Exact feature/measurand interpretation boundary"),
        ("05", "release/hr-v0/joint-measurement-definition-p0.1/feature-register.csv", "METROLOGY", "79 exact CAD source features"),
        ("06", "release/hr-v0/joint-measurement-definition-p0.1/measurand-definition.csv", "METROLOGY", "18 unexecuted received characteristics"),
        ("07", "release/hr-v0/joint-measurement-definition-p0.1/transform-register.csv", "METROLOGY", "Three source-to-joint transforms"),
        ("08", "release/hr-v0/joint-measurement-definition-p0.1/hsi-closure-map.csv", "METROLOGY", "20 open HSI routes"),
        ("09", "release/hr-v0/joint-measurement-definition-p0.1/execution-result-template.csv", "METROLOGY", "Blank result/uncertainty/evidence fields"),
        ("10", "release/hr-v0/joint-measurement-definition-p0.1/axial-feature-index.svg", "METROLOGY", "Annotated nominal axial reference"),
        ("11", "release/hr-v0/joint-measurement-definition-p0.1/attachment-pattern-index.svg", "METROLOGY", "Annotated nominal pattern reference"),
        ("12", "cad/vendor/robotis/XMHD-540.N101.I101.STP", "METROLOGY", "Exact controlled XM540 source STEP"),
        ("13", "cad/vendor/robotis/FR13-H101K.stp", "METROLOGY", "Exact controlled H101 source STEP"),
        ("14", "cad/vendor/robotis/FR13-S102K.stp", "METROLOGY", "Exact controlled S102 source STEP"),
    ]
    attachments = [{"attachment_id": f"R257-AT-{number}", "path": path, "sha256": old.sha(ROOT / path), "recipient_scope": scope, "release_boundary": boundary} for number, path, scope, boundary in attachment_paths]

    message_robotis = (OLD / "UNSENT-robotis-request.md").read_text(encoding="utf-8").replace("R255", "R257")
    message_metro = f"""# UNSENT HR-V0 exact-feature metrology capability and quote request

> **{WARNING}**

Project Button requests an information-only response and separately itemized bid for `JSM2-M01..M05` and `R256-MZ-001..018`. The attached 79-feature register, transforms, annotated views and three exact STEP files define nominal reference surfaces. They do not define received conformance, tolerances, thread function, accepted datums or authorization.

Please return BID or NO BID for every method and every characteristic. Describe the feature-match, support, fit, residual, outlier, repetition, raw-data and uncertainty methods. Record every source/received mismatch without substituting another feature. No source, actuator cable, U2D2, encoder access, powered operation, motion or threaded assembly is permitted.

This is not an order or work authorization. Do not receive articles, design fixtures, subcontract work, incur cost or begin measurement without a later configuration-specific signed authorization. Sender identity and reply address are `SELECTION REQUIRED`.
"""
    (OUT / "UNSENT-robotis-request.md").write_text(message_robotis, encoding="utf-8")
    (OUT / "UNSENT-metrology-request.md").write_text(message_metro, encoding="utf-8")

    response_register = []
    for route in routes:
        route_id = route["route_id"]
        if route_id in {"R257-RT-01", "R257-RT-02"}:
            data = [dict(row, provider_response="", response_evidence_uri="", reviewer_disposition="NOT EXECUTED") for row in robotis if row["route_id"] == route_id]
            name = f"question-response-{route_id}.csv"
            old.write_csv(OUT / name, list(data[0]), data)
            response_register.append({"template_id": f"R257-RSP-{route_id[-2:]}-Q", "route_id": route_id, "template_type": "QUESTIONS", "path": name, "sha256": old.sha(OUT / name), "response_rows": len(data), "response_state": "BLANK / NOT RECEIVED"})
        else:
            data = [dict(row, provider_response="", response_evidence_uri="", reviewer_disposition="NOT EXECUTED") for row in questions if row["route_id"] == route_id]
            name = f"question-response-{route_id}.csv"
            old.write_csv(OUT / name, list(data[0]), data)
            response_register.append({"template_id": f"R257-RSP-{route_id[-2:]}-Q", "route_id": route_id, "template_type": "QUESTIONS", "path": name, "sha256": old.sha(OUT / name), "response_rows": len(data), "response_state": "BLANK / NOT RECEIVED"})
            bid_data = [row for row in characteristic_bids if row["route_id"] == route_id]
            bid_name = f"characteristic-bid-response-{route_id}.csv"
            old.write_csv(OUT / bid_name, list(bid_data[0]), bid_data)
            response_register.append({"template_id": f"R257-RSP-{route_id[-2:]}-C", "route_id": route_id, "template_type": "CHARACTERISTIC BID", "path": bid_name, "sha256": old.sha(OUT / bid_name), "response_rows": len(bid_data), "response_state": "BLANK / NOT RECEIVED"})

    transmittals = []
    for index, route in enumerate(routes, 1):
        route_id = route["route_id"]
        robotis_route = index <= 2
        message = "UNSENT-robotis-request.md" if robotis_route else "UNSENT-metrology-request.md"
        attachment_set = f"R257-RSP-{route_id[-2:]}-Q" if robotis_route else f"R257-AT-01..14 + R257-RSP-{route_id[-2:]}-Q/C + route-scoped method/characteristic bid rows"
        transmittals.append({"transmittal_id": f"R257-TX-{index:02d}", "route_id": route_id, "message_path": message, "message_sha256": old.sha(OUT / message), "attachment_set": attachment_set, "sender_identity": "SELECTION REQUIRED", "reply_address": "SELECTION REQUIRED", "send_authorization": "NOT AUTHORIZED", "sent_state": "NOT SENT"})

    evidence = remap(old.read_csv(OLD / "returned-evidence-register.csv")[0])
    evidence.extend([
        {"evidence_id": "R257-EV-19", "route_id": "METROLOGY", "required_record": "Exact attachment-hash acknowledgement and received/source feature-match report", "acceptance_boundary": "All 79 references addressed; mismatches explicit; no substitution", "state": "NOT RECEIVED"},
        {"evidence_id": "R257-EV-20", "route_id": "METROLOGY", "required_record": "Per-characteristic BID/NO BID and commercial/technical return", "acceptance_boundary": "All R256-MZ-001..018 answered separately by provider", "state": "NOT RECEIVED"},
    ])
    gates = remap(old.read_csv(OLD / "decision-gate.csv")[0])
    gates.append({"gate_id": "R257-GT-16", "decision": "Accept exact feature-match and per-characteristic bid", "evidence_required": "Complete 79-feature discrepancy method plus 18-row bid/technical response", "owner_role": "QUALIFIED MECHANICAL/METROLOGY REVIEWER", "state": "OPEN"})
    workflow = remap(old.read_csv(OLD / "workflow-register.csv")[0])
    workflow.append({"step_id": "R257-WF-15", "action": "Independently disposition 79-feature match and 18-characteristic scope before provider selection", "entry_gate": "GT-16", "output": "Characteristic-level accepted/rejected scope", "authorization": "NONE", "execution_state": "NOT EXECUTED"})
    acceptance = [{"acceptance_id": f"R257-ACC-{index:02d}", "criterion": gate["decision"], "execution_state": "NOT EXECUTED", "result": "OPEN", "evidence_uri": "", "approver": ""} for index, gate in enumerate(gates, 1)]
    sources = remap(old.read_csv(OLD / "source-register.csv")[0])
    for row in sources:
        if row["source_id"] in {"R257-SRC-04", "R257-SRC-05", "R257-SRC-07", "R257-SRC-08", "R257-SRC-09", "R257-SRC-10"}:
            row["revision_or_date"] = row["revision_or_date"].replace("2026-08-11", "2026-08-12")
    sources.extend([
        {"source_id": "R257-SRC-12", "authority": "Project Button", "title": "Joint measurement definition P0.1", "revision_or_date": "R256 / 2026-08-11", "path_or_url": "release/hr-v0/joint-measurement-definition-p0.1/package-status.json", "sha256": old.sha(MEAS / "package-status.json"), "controlled_fact": "79 source features; 18 unexecuted characteristics; zero physical evidence"},
        {"source_id": "R257-SRC-13", "authority": "Project Button", "title": "Lot A inquiry P0.2", "revision_or_date": "R255 / 2026-08-11", "path_or_url": "release/hr-v0/lot-a-inquiry-p0.2/package-status.json", "sha256": old.sha(ROOT / "release/hr-v0/lot-a-inquiry-p0.2/package-status.json"), "controlled_fact": "Superseded broad-scope inquiry baseline"},
    ])

    outputs = {
        "inquiry-route-register.csv": routes,
        "transmittal-register.csv": transmittals,
        "response-template-register.csv": response_register,
        "robotis-question-register.csv": robotis,
        "metrology-question-register.csv": questions,
        "method-bid-schedule.csv": method_bids,
        "characteristic-bid-schedule.csv": characteristic_bids,
        "attachment-manifest.csv": attachments,
        "returned-evidence-register.csv": evidence,
        "decision-gate.csv": gates,
        "workflow-register.csv": workflow,
        "acceptance-matrix.csv": acceptance,
        "source-register.csv": sources,
    }
    for name, data in outputs.items():
        old.write_csv(OUT / name, list(data[0]) + ["warning"], old.warned(data))
    status = {"identifier": ID, "round": "R257", "date": "2026-08-12", "inquiry_routes": 5, "unique_question_definitions": 45, "provider_attributed_metrology_question_rows": 99, "robotis_question_rows": 12, "method_bid_rows": 15, "characteristic_bid_rows": 54, "controlled_attachment_rows": 14, "source_bound_features": 79, "measurement_characteristics": 18, "returned_evidence_rows": 20, "decision_gates": 16, "workflow_steps": 15, "responses_received": 0, "transmissions_authorized": 0, "messages_sent": 0, "provider_selected": False, "purchase_authorized": False, "order_placed": False, "shipment_authorized": False, "work_authorized": False, "physical_articles_received": False, "qualified_review_complete": False, "assembly_authorized": False, "connection_authorized": False, "powered_testing_authorized": False, "motion_authorized": False, "energization_authorized": False, "safety_credit": False, "warning": WARNING}
    (OUT / "package-status.json").write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8")
    (OUT / "index.html").write_text(guide(routes, attachments, questions, method_bids, characteristic_bids, evidence, gates), encoding="utf-8")
    old.manifest(OUT)
    shutil.copytree(OUT, REL)
    old.manifest(REL)

    shutil.copytree(CFG0, CFG)
    current, fields = old.read_csv(CFG / "current-configuration-map.csv")
    current.append({"record_id": "CFG-40", "role": "Exact-feature Lot A supplier/metrology inquiry contract", "identifier": ID, "source_path": "release/hr-v0/lot-a-inquiry-p0.3/package-status.json", "configuration_state": "CURRENT CONTROLLED DRAFT - NOTHING SENT OR AUTHORIZED", "release_boundary": "79 source features and 18 characteristics bound to isolated provider returns", "warning": WARNING})
    old.write_csv(CFG / "current-configuration-map.csv", fields, current)
    supersession, fields = old.read_csv(CFG / "supersession-map.csv")
    supersession.extend([
        {"record_id": "SUP-32", "prior_identifier": "HR-V0-LOT-A-INQUIRY-P0.2", "current_or_required_successor": ID, "disposition": "SUPERSEDED FOR CURRENT INQUIRY USE; BROAD-SCOPE HISTORICAL PACKAGE RETAINED", "use_authorized": "NO", "warning": WARNING},
        {"record_id": "SUP-33", "prior_identifier": "HR-V0-CONFIG-REC-P0.20", "current_or_required_successor": CID, "disposition": "SUPERSEDED BY R257 CONFIGURATION RECORD ONLY", "use_authorized": "NO", "warning": WARNING},
    ])
    old.write_csv(CFG / "supersession-map.csv", fields, supersession)
    holds, fields = old.read_csv(CFG / "open-holds.csv")
    for index, gate in enumerate(gates, 110):
        holds.append({"hold_id": f"HOLD-{index:02d}", "hold": f"{ID}: {gate['decision']}", "state": "OPEN", "closure_evidence": gate["evidence_required"], "warning": WARNING})
    old.write_csv(CFG / "open-holds.csv", fields, holds)
    config_acceptance, fields = old.read_csv(CFG / "acceptance-matrix.csv")
    for index, row in enumerate(acceptance, 143):
        config_acceptance.append({"acceptance_id": f"ACC-{index:03d}", "criterion": f"{ID}: {row['criterion']}", "execution_state": "NOT EXECUTED", "result": "OPEN", "evidence_uri": "", "approver": "", "warning": WARNING})
    old.write_csv(CFG / "acceptance-matrix.csv", fields, config_acceptance)
    impacts, fields = old.read_csv(CFG / "gate-impact.csv")
    for row in impacts:
        if row["gate_id"] in {"EG-002", "EG-003", "EG-005", "EG-007"}:
            row["evidence_added"] += f"; {ID} exact-feature and characteristic-level inquiry route"
            row["remaining_evidence"] += "; authorized transmission; attributable returned bids; received feature match; accepted methods/uncertainty; executed results"
    old.write_csv(CFG / "gate-impact.csv", fields, impacts)
    hashes, fields = old.read_csv(CFG / "source-hash-register.csv")
    hashes.append({"source_path": "release/hr-v0/lot-a-inquiry-p0.3/package-status.json", "sha256": old.sha(REL / "package-status.json"), "role": "Exact-feature Lot A inquiry contract", "warning": WARNING})
    old.write_csv(CFG / "source-hash-register.csv", fields, hashes)
    config_status = json.loads((CFG / "package-status.json").read_text(encoding="utf-8"))
    config_status.update({"identifier": CID, "round": "R257", "date": "2026-08-12", "current_records": 40, "supersession_records": 33, "open_holds": 125, "acceptance_rows": 158, "lot_a_inquiry": ID, "joint_measurement_definition": "HR-V0-JOINT-MEAS-DEF-P0.1"})
    (CFG / "package-status.json").write_text(json.dumps(config_status, indent=2) + "\n", encoding="utf-8")
    (CFG / "README.md").write_text(f"# {CID}\n\n> **{WARNING}**\n\nR257 adds {ID} and supersedes P0.2 for current inquiry use. 125 holds and 158 unexecuted acceptances remain. Nothing is sent or authorized.\n", encoding="utf-8")
    (CFG / "index.html").write_text(guide(routes, attachments, questions, method_bids, characteristic_bids, evidence, gates), encoding="utf-8")
    old.manifest(CFG)
    shutil.copytree(CFG, CFGR)
    old.manifest(CFGR)
    print(f"Generated {ID}: 5 routes; 79 features; 18 characteristics/provider; zero sends/responses/authority")


if __name__ == "__main__":
    main()
