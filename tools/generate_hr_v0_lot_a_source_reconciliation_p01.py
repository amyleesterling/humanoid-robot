#!/usr/bin/env python3
"""Generate the R237 Lot A source-reconciliation and purchase-gate package."""

from __future__ import annotations

import csv
import hashlib
import html
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUTS = (
    ROOT / "procurement/hr-v0/lot-a-source-reconciliation-p0.1",
    ROOT / "release/hr-v0/lot-a-source-reconciliation-p0.1",
)
IDENTIFIER = "HR-V0-LOT-A-SRC-P0.1"
WARNING = "PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION"
DATE = "2026-08-11"


def warned(record: dict[str, str]) -> dict[str, str]:
    return {**record, "warning": WARNING}


ITEMS = [
    warned({"item_id": "LOT-A-001", "evaluation_lines": "EVA-002;EVA-003", "manufacturer": "ROBOTIS", "requested_identity": "DYNAMIXEL XM540-W270-T", "order_code": "902-0137-000", "quantity": "2", "unit_price_usd_visible": "482.89", "extended_visible_usd": "965.78", "stock_evidence": "NO NUMERIC STOCK VALUE EXPOSED", "decision_state": "PURCHASE BLOCKED - VARIANT CLARIFICATION REQUIRED"}),
    warned({"item_id": "LOT-A-002", "evaluation_lines": "EVA-011;EVA-012", "manufacturer": "ROBOTIS", "requested_identity": "FR13-H101K Set", "order_code": "903-0270-300", "quantity": "2", "unit_price_usd_visible": "76.71", "extended_visible_usd": "153.42", "stock_evidence": "NO NUMERIC STOCK VALUE EXPOSED", "decision_state": "HOLD - ALLOCATION AND LOT AUTHORIZATION REQUIRED"}),
    warned({"item_id": "LOT-A-003", "evaluation_lines": "EVA-013", "manufacturer": "ROBOTIS", "requested_identity": "FR13-S102K Set", "order_code": "903-0269-300", "quantity": "2", "unit_price_usd_visible": "31.51", "extended_visible_usd": "63.02", "stock_evidence": "PAGE DISPLAYED CURRENT STOCK 94 AT ACCESS TIME; CART ALLOCATION NOT PROVED", "decision_state": "HOLD - LOT AUTHORIZATION REQUIRED"}),
]

SOURCES = [
    warned({"source_id": "LAS-001", "organization": "ROBOTIS US", "title": "DYNAMIXEL XM540-W270-T", "revision_or_date": "no revision shown; accessed 2026-08-11", "url": "https://www.robotis.us/dynamixel-xm540-w270-t/", "controlled_use": "title, SKU, price, visible stock field, package contents and seller contact route"}),
    warned({"source_id": "LAS-002", "organization": "ROBOTIS US", "title": "FR13-H101K Set", "revision_or_date": "no revision shown; accessed 2026-08-11", "url": "https://robotis.us/fr13-h101k-set/", "controlled_use": "SKU, price, visible stock field, compatibility and package contents"}),
    warned({"source_id": "LAS-003", "organization": "ROBOTIS US", "title": "FR13-S102K Set", "revision_or_date": "no revision shown; accessed 2026-08-11", "url": "https://www.robotis.us/fr13-s102k-set/", "controlled_use": "SKU, price, visible stock value, compatibility and package contents"}),
    warned({"source_id": "LAS-004", "organization": "ROBOTIS", "title": "XH540-W270-T/R e-Manual", "revision_or_date": "live e-Manual; accessed 2026-08-11", "url": "https://emanual.robotis.com/docs/en/dxl/x/xh540-w270/", "controlled_use": "separate TTL/RS-485 connector identities, assembly cautions and official frame drawing routes"}),
]

FACTS = [
    warned({"fact_id": "LAF-001", "source_id": "LAS-001", "subject": "product title", "observed_fact": "DYNAMIXEL XM540-W270-T", "interpretation_boundary": "Does not override contradictory package-content text"}),
    warned({"fact_id": "LAF-002", "source_id": "LAS-001", "subject": "SKU", "observed_fact": "902-0137-000", "interpretation_boundary": "SKU-to-variant shipment identity requires seller confirmation"}),
    warned({"fact_id": "LAF-003", "source_id": "LAS-001", "subject": "visible price", "observed_fact": "$482.89 each", "interpretation_boundary": "Excludes shipping, tax, fees and allocation"}),
    warned({"fact_id": "LAF-004", "source_id": "LAS-001", "subject": "communication", "observed_fact": "Page states TTL", "interpretation_boundary": "Received label and later model readback remain required"}),
    warned({"fact_id": "LAF-005", "source_id": "LAS-001", "subject": "package contents", "observed_fact": "Package table names XM540-W270-R", "interpretation_boundary": "Contradicts title/TTL request; no inference permitted"}),
    warned({"fact_id": "LAF-006", "source_id": "LAS-001", "subject": "stock", "observed_fact": "Current Stock field rendered without a numeric value", "interpretation_boundary": "Blank is neither in-stock nor zero-stock evidence"}),
    warned({"fact_id": "LAF-007", "source_id": "LAS-002", "subject": "H101 identity and price", "observed_fact": "SKU 903-0270-300; $76.71 each", "interpretation_boundary": "Shipping, tax, fees and allocation excluded"}),
    warned({"fact_id": "LAF-008", "source_id": "LAS-002", "subject": "H101 compatibility", "observed_fact": "Hinge frame and idler set for X540 series", "interpretation_boundary": "Received fit and temporary-assembly method remain unverified"}),
    warned({"fact_id": "LAF-009", "source_id": "LAS-002", "subject": "H101 stock", "observed_fact": "Current Stock field rendered without a numeric value", "interpretation_boundary": "Blank is neither in-stock nor zero-stock evidence"}),
    warned({"fact_id": "LAF-010", "source_id": "LAS-003", "subject": "S102 identity and price", "observed_fact": "SKU 903-0269-300; $31.51 each", "interpretation_boundary": "Shipping, tax, fees and allocation excluded"}),
    warned({"fact_id": "LAF-011", "source_id": "LAS-003", "subject": "S102 stock", "observed_fact": "Current Stock 94 displayed", "interpretation_boundary": "Access-time page value does not reserve two units"}),
    warned({"fact_id": "LAF-012", "source_id": "LAS-003", "subject": "S102 compatibility", "observed_fact": "Bottom side frame set for X540 series", "interpretation_boundary": "Received fit and temporary-assembly method remain unverified"}),
    warned({"fact_id": "LAF-013", "source_id": "LAS-004", "subject": "assembly precaution", "observed_fact": "Align thrust washer/index; use idler and spacer rings; verify screw length against mounting depth", "interpretation_boundary": "No Project Button temporary torque or assembly authorization is established"}),
]

ANOMALIES = [
    warned({"anomaly_id": "LAA-001", "severity": "BLOCKER", "item_id": "LOT-A-001", "observation": "The official sales page title and TTL field specify XM540-W270-T while its package-content table names XM540-W270-R.", "prohibited_inference": "Do not assume the shipped communication variant from the title, SKU, image or package table.", "closure_evidence": "Written ROBOTIS US confirmation tying SKU 902-0137-000 to the exact shipped -T article and corrected/current package contents; then received label plus later controlled model/protocol readback.", "state": "OPEN"}),
    warned({"anomaly_id": "LAA-002", "severity": "MAJOR", "item_id": "LOT-A-001", "observation": "The XM540 page exposes no numeric stock value.", "prohibited_inference": "Do not report in stock or out of stock.", "closure_evidence": "Dated cart or written allocated-stock confirmation for two exact -T units.", "state": "OPEN"}),
    warned({"anomaly_id": "LAA-003", "severity": "MAJOR", "item_id": "LOT-A-002", "observation": "The H101 page exposes no numeric stock value.", "prohibited_inference": "Do not report in stock or out of stock.", "closure_evidence": "Dated cart or written allocated-stock confirmation for two exact kits.", "state": "OPEN"}),
    warned({"anomaly_id": "LAA-004", "severity": "MAJOR", "item_id": "LOT-A", "observation": "The $1,182.22 visible subtotal excludes shipping, Massachusetts tax or exemption, fees and price/stock changes.", "prohibited_inference": "Do not treat the visible subtotal as a maximum spend or landed cost.", "closure_evidence": "Dated seller cart or quote to the selected ship-to address plus accepted tax status and maximum-spend authorization.", "state": "OPEN"}),
]

QUESTIONS = [
    warned({"question_id": "LAQ-001", "recipient": "ROBOTIS US sales/support", "question": "Does SKU 902-0137-000 currently ship an XM540-W270-T (TTL), despite the product page package table naming XM540-W270-R?", "required_response": "Written SKU-to-model-to-communication binding", "state": "UNSENT"}),
    warned({"question_id": "LAQ-002", "recipient": "ROBOTIS US sales/support", "question": "What exact model label, hardware revision and included cables will ship for two units of SKU 902-0137-000?", "required_response": "Written contents/revision list", "state": "UNSENT"}),
    warned({"question_id": "LAQ-003", "recipient": "ROBOTIS US sales/support", "question": "Are two exact SKU 902-0137-000 units allocated and what is the lead time?", "required_response": "Dated allocation and lead-time statement", "state": "UNSENT"}),
    warned({"question_id": "LAQ-004", "recipient": "ROBOTIS US sales/support", "question": "Are two FR13-H101K SKU 903-0270-300 kits allocated and what is the lead time?", "required_response": "Dated allocation and lead-time statement", "state": "UNSENT"}),
    warned({"question_id": "LAQ-005", "recipient": "ROBOTIS US sales/support", "question": "Are two FR13-S102K SKU 903-0269-300 kits allocated and what is the lead time?", "required_response": "Dated allocation and lead-time statement", "state": "UNSENT"}),
    warned({"question_id": "LAQ-006", "recipient": "ROBOTIS US sales/support", "question": "Will all six articles ship new with manufacturer labels, traceable packing records and the page-listed hardware contents?", "required_response": "Written condition and contents confirmation", "state": "UNSENT"}),
    warned({"question_id": "LAQ-007", "recipient": "ROBOTIS US sales/support", "question": "Provide a dated Boston-area cart or quote including shipping, tax treatment, fees and quote expiration.", "required_response": "Dated complete-cost record", "state": "UNSENT"}),
    warned({"question_id": "LAQ-008", "recipient": "ROBOTIS technical support", "question": "Is there a manufacturer-published temporary assembly torque/reuse instruction for the received X540/H101/S102 screw stack?", "required_response": "Official document reference or explicit statement that no value is supplied", "state": "UNSENT"}),
]

GATES = [
    ("LAG-001", "Resolve the -T/-R sales-page contradiction", "LAQ-001/002 accepted written response", "OPEN"),
    ("LAG-002", "Confirm allocated stock for all six articles", "LAQ-003/004/005 dated response or exact cart", "OPEN"),
    ("LAG-003", "Freeze exact seller and cart/quote", "ROBOTIS US dated cart/quote identity", "OPEN"),
    ("LAG-004", "Close complete landed-cost basis", "shipping, tax/exemption, fees and expiration", "OPEN"),
    ("LAG-005", "Set a maximum spend", "program-owner numerical authorization", "OPEN"),
    ("LAG-006", "Freeze ship-to and receiving owner", "named Boston-area address and adult receiving owner", "OPEN"),
    ("LAG-007", "Freeze candidate commit and line identities", "clean commit and manifest recorded in authorization", "OPEN"),
    ("LAG-008", "Accept no-substitution rule", "written rejection of -R or alternate frames without new review", "OPEN"),
    ("LAG-009", "Approve receipt/quarantine-only scope", "signed authorization excludes assembly, power and use", "OPEN"),
    ("LAG-010", "Prepare receiving evidence locations", "serialized photo, label, lot, contents and discrepancy records", "OPEN"),
]
DECISION_GATES = [warned({"gate_id": a, "decision": b, "evidence_required": c, "state": d}) for a, b, c, d in GATES]

RECEIVING = [
    warned({"record_id": f"LAR-{i:03d}", "article_scope": scope, "required_observation": observation, "result": "NOT_EXECUTED", "evidence_uri": "NOT_EXECUTED", "disposition": "NOT_ACCEPTED"})
    for i, (scope, observation) in enumerate([
        ("shipment", "sealed package and packing-list identity before opening"),
        ("two actuator cartons", "SKU 902-0137-000 and exact XM540-W270-T labels; any -R is quarantined"),
        ("two actuators", "serial, hardware revision, case/connector condition and individual photographs"),
        ("two actuator kits", "page-listed horns, three cable types, fasteners and spacer rings inventoried separately"),
        ("two H101 cartons", "SKU 903-0270-300 and exact kit labels"),
        ("two H101 kits", "hinge frame, idler set, all fastener quantities and ten spacer rings per kit"),
        ("two S102 cartons", "SKU 903-0269-300 and exact kit labels"),
        ("two S102 kits", "side frame, all fastener quantities and ten spacer rings per kit"),
        ("all six articles", "mass recorded without accepting commerce shipping weight as article mass"),
        ("all loose hardware", "kept segregated by serialized article allocation; no thread engagement"),
        ("discrepancies", "quarantine and nonconformance record; no substitution acceptance"),
        ("lot close", "hash-bound evidence index and qualified receiving disposition"),
    ], 1)
]


def write_csv(path: Path, records: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(records[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(records)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_text_lf(path: Path, value: str) -> None:
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(value)


def page() -> str:
    item_cards = "".join(f'<article><span>{html.escape(r["item_id"])}</span><h3>{html.escape(r["requested_identity"])}</h3><p><strong>{r["quantity"]} × ${r["unit_price_usd_visible"]}</strong> · SKU {r["order_code"]}</p><p>{html.escape(r["stock_evidence"])}</p><p class="state">{html.escape(r["decision_state"])}</p></article>' for r in ITEMS)
    anomaly_rows = "".join(f'<tr><td>{r["anomaly_id"]}<br><strong>{r["severity"]}</strong></td><td>{html.escape(r["observation"])}</td><td>{html.escape(r["closure_evidence"])}</td><td>{r["state"]}</td></tr>' for r in ANOMALIES)
    question_rows = "".join(f'<tr data-row><td>{r["question_id"]}</td><td>{html.escape(r["question"])}</td><td>{html.escape(r["required_response"])}</td><td>{r["state"]}</td></tr>' for r in QUESTIONS)
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>HR-V0 Lot A source reconciliation</title><style>:root{{--navy:#082f58;--blue:#1268a8;--sky:#dff3ff;--gold:#f3b61f;--paper:#f7fbff;--line:#8bbbd8;--red:#8d1c1c}}*{{box-sizing:border-box}}body{{margin:0;background:var(--paper);color:var(--navy);font:clamp(16px,1.15vw,19px)/1.5 system-ui,sans-serif}}header{{padding:clamp(24px,5vw,64px);background:linear-gradient(135deg,var(--navy),#0d68a7);color:white;border-bottom:7px solid var(--gold)}}main{{max-width:1320px;margin:auto;padding:28px 18px 64px}}h1{{font-size:clamp(36px,5vw,68px);line-height:1.04;max-width:18ch}}h2{{font-size:clamp(26px,3vw,40px)}}h3{{font-size:21px}}.warning{{background:#fff2bd;color:#3c2b00;border:3px solid var(--gold);padding:16px;font-weight:850}}.verdict{{font-size:clamp(20px,2vw,28px);background:white;border-left:8px solid var(--red);padding:20px;margin:28px 0}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(270px,100%),1fr));gap:14px}}article{{background:white;border:2px solid var(--line);border-radius:12px;padding:18px}}article span{{font-size:14px;font-weight:850;background:var(--sky);padding:5px 8px;border-radius:6px}}.state{{color:var(--red);font-weight:850}}label,input{{font-size:16px}}input{{width:100%;padding:11px;border:2px solid var(--blue);border-radius:8px;margin:8px 0 14px}}.scroll{{overflow:auto;border:2px solid var(--line);border-radius:10px;background:white}}table{{border-collapse:collapse;width:100%;min-width:920px}}th,td{{padding:12px;border-bottom:1px solid var(--line);text-align:left;vertical-align:top}}th{{background:var(--navy);color:white}}a{{color:#075b9c;font-weight:750}}footer{{padding:24px;background:var(--navy);color:white}}@media(max-width:600px){{header,main{{padding:20px 14px}}}}</style></head><body><header><div class="warning">{WARNING}</div><p>{IDENTIFIER} · R237 · {DATE}</p><h1>Six articles unlock the next measurements. One source contradiction blocks the order.</h1><p>Receipt-and-quarantine-only decision surface for the two HR-V0 joint stacks.</p></header><main><div class="verdict"><strong>Current verdict:</strong> do not order Lot A yet. The official XM540 sales page asks for the TTL <code>-T</code> product but names an RS-485 <code>-R</code> unit in its package table. Written SKU-to-variant confirmation is required.</div><section class="grid">{item_cards}</section><h2>Price boundary</h2><p>The visible official-page subtotal is <strong>$1,182.22</strong> for six articles. It is not landed cost and not a spending authorization. Shipping, Massachusetts tax or exemption, fees, allocation and price validity remain open.</p><h2>Four source anomalies</h2><div class="scroll"><table><thead><tr><th>ID / severity</th><th>Observed</th><th>Evidence required</th><th>State</th></tr></thead><tbody>{anomaly_rows}</tbody></table></div><h2>Eight unsent supplier questions</h2><label for="filter">Filter questions</label><input id="filter" type="search" placeholder="Variant, stock, quote, torque…"><div class="scroll"><table><thead><tr><th>ID</th><th>Question</th><th>Required response</th><th>State</th></tr></thead><tbody id="questions">{question_rows}</tbody></table></div><h2>Machine-readable packet</h2><p><a href="item-register.csv">Items</a> · <a href="source-fact-register.csv">Facts</a> · <a href="anomaly-register.csv">Anomalies</a> · <a href="supplier-question-register.csv">Questions</a> · <a href="decision-gate.csv">Decision gates</a> · <a href="receiving-acceptance-template.csv">Receiving template</a> · <a href="package-status.json">Status</a></p><div class="warning">If later authorized, scope is purchase, receipt, quarantine, inventory and unpowered loose-part measurement only. No thread engagement, assembly, cable connection, power, encoder access, motion or energization.</div></main><footer>{WARNING}</footer><script>const f=document.querySelector('#filter'),rows=[...document.querySelectorAll('[data-row]')];f.addEventListener('input',()=>{{const q=f.value.toLowerCase();rows.forEach(r=>r.hidden=!r.textContent.toLowerCase().includes(q))}});</script></body></html>'''


def build(directory: Path) -> None:
    directory.mkdir(parents=True, exist_ok=True)
    write_csv(directory / "item-register.csv", ITEMS)
    write_csv(directory / "source-register.csv", SOURCES)
    write_csv(directory / "source-fact-register.csv", FACTS)
    write_csv(directory / "anomaly-register.csv", ANOMALIES)
    write_csv(directory / "supplier-question-register.csv", QUESTIONS)
    write_csv(directory / "decision-gate.csv", DECISION_GATES)
    write_csv(directory / "receiving-acceptance-template.csv", RECEIVING)
    status = {
        "identifier": IDENTIFIER, "round": "R237", "date": DATE,
        "unique_item_count": 3, "physical_unit_count": 6,
        "official_page_visible_subtotal_usd": "1182.22",
        "source_fact_count": 13, "open_anomaly_count": 4,
        "blocker_count": 1, "unsent_question_count": 8,
        "open_decision_gate_count": 10, "unexecuted_receiving_record_count": 12,
        "purchase_authorized": False, "article_received": False,
        "assembly_authorized": False, "connection_authorized": False,
        "powered_testing_authorized": False, "motion_authorized": False,
        "energization_authorized": False, "safety_credit": False,
        "warning": WARNING,
    }
    write_text_lf(directory / "package-status.json", json.dumps(status, indent=2) + "\n")
    write_text_lf(directory / "README.md", f"# {IDENTIFIER}\n\n> **{WARNING}**\n\nR237 controls the six-article Lot A source state and exposes the official sales-page `-T`/`-R` contradiction as a purchase blocker. All eight questions are unsent, all ten decision gates are open and all twelve receiving records are unexecuted. The visible $1,182.22 subtotal is not landed cost or authority.\n")
    write_text_lf(directory / "index.html", page())
    files = sorted(path for path in directory.iterdir() if path.is_file() and path.name != "file-manifest.csv")
    write_csv(directory / "file-manifest.csv", [{"path": path.name, "bytes": str(path.stat().st_size), "sha256": digest(path)} for path in files])


def main() -> None:
    for directory in OUTS:
        build(directory)
    print(f"{IDENTIFIER}: 6 units / $1,182.22 visible subtotal / 1 blocker / 8 unsent questions / 0 authority")
    print(WARNING)


if __name__ == "__main__":
    main()
