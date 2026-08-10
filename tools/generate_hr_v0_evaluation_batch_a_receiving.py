"""Generate the fail-closed unit-level Evaluation Batch A receiving campaign."""

from __future__ import annotations

import csv
import html
import json
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "bom" / "hr-v0-evaluation-batch-a.csv"
ACQ = ROOT / "procurement" / "hr-v0" / "evaluation-batch-a-acquisition-p0.1" / "line-register.csv"
OUT = ROOT / "tests" / "receiving" / "hr-v0-evaluation-batch-a-receiving-p0.1"
WEB = ROOT / "release" / "hr-v0" / "evaluation-batch-a-receiving-p0.1" / "index.html"
FORM = ROOT / "tests" / "forms" / "hr-v0-evaluation-batch-a-unit-receiving-template-p0.1.csv"
REVISION = "HR-V0-EVAL-BATCH-A-RCV-P0.1"
WARNING = "PRELIMINARY - NOT APPROVED FOR FABRICATION, CONNECTION, MOTION, OR ENERGIZATION"

STEPS = [
    ("RCV-00", "Authority and baseline", "Signed line/lot purchase authority, purchase record and exact candidate commit", "Approved line ID and ordered quantity reconcile; otherwise stop before opening", "authorization record; purchase record; commit"),
    ("RCV-01", "Shipment intake and quarantine", "Unopened shipment and quarantine location", "Shipment is segregated, labeled and cannot reach build stock", "intake photograph; quarantine-location record"),
    ("RCV-02", "Unopened packaging record", "Outer packaging, shipping label and packing record", "All sides and damage are recorded before opening", "container photographs; packing-record reference"),
    ("RCV-03", "Count and allocation", "Packing list and physical contents", "Quantity maps one-to-one to controlled unit IDs; surplus/substitutes remain quarantined", "count record; unit-allocation photograph"),
    ("RCV-04", "Identity capture", "Manufacturer, exact order code, model, serial and lot/date markings", "Exact identity is legible and matches the controlled expectation; ambiguity is a deviation", "nameplate and marking photographs; transcription"),
    ("RCV-05", "Visible-condition inspection", "Accessible surfaces, seals, connectors and terminals without connection", "No unaccepted damage, contamination, deformation or missing protective cap", "overview and detail photographs; condition record"),
    ("RCV-06", "Package-content inventory", "Manufacturer packing record and included loose contents", "Contents are counted and identified without inferring application suitability", "contents photograph; inventory record"),
    ("RCV-07", "Unpowered item-specific route", "Controlled receiving-route procedures listed for the evaluation line", "Only separately authorized unpowered observations are performed; no connector mating, source connection, encoder access or torque enable", "item-specific form references; instrument/calibration IDs where applicable"),
    ("RCV-08", "Evidence integrity", "All files, transcriptions and records for the unit", "Evidence manifest has immutable SHA-256 values and no missing required category", "completed evidence manifest; raw-file location"),
    ("RCV-09", "Independent identity check", "Expected identity, received identity, photographs and deviations", "A second named checker agrees or opens a nonconformance", "independent-check record; nonconformance ID if needed"),
    ("RCV-10", "Qualified disposition", "Completed receiving evidence and item-specific results", "Disposition is QUARANTINE, REJECT or ACCEPTED FOR NAMED UNPOWERED EVALUATION ONLY; never machine release", "qualified reviewer disposition and date"),
    ("RCV-11", "Storage and handoff", "Disposition label and controlled storage location", "Unit remains segregated; later use requires separate written procedure authorization", "final label photograph; storage-location record"),
]

EVIDENCE_CATEGORIES = [
    ("EV-01", "shipment_or_container", "Unopened shipment/container with record ID visible"),
    ("EV-02", "manufacturer_label_and_order_code", "Exact manufacturer/order-code label and lot/date marking"),
    ("EV-03", "unit_overview_with_scale", "Whole unit/article with unit ID and scale"),
    ("EV-04", "unit_identity_markings", "Model, serial, SKU and other accessible identity markings"),
    ("EV-05", "connector_or_terminal_view_unmated", "Accessible connector/terminal view without mating or connection"),
    ("EV-06", "included_contents_inventory", "Included loose contents laid out and counted"),
    ("EV-07", "damage_and_disposition", "Condition details and final quarantine/disposition label"),
]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    if not rows:
        raise ValueError(f"refusing to write empty CSV: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    source = read_csv(SOURCE)
    acquisition = read_csv(ACQ)
    if [row["batch_line"] for row in source] != [f"EVA-{index:03d}" for index in range(1, 18)]:
        raise AssertionError("Evaluation Batch A membership changed")
    if [row["line_id"] for row in acquisition] != [row["batch_line"] for row in source]:
        raise AssertionError("acquisition/source line parity changed")
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)
    WEB.parent.mkdir(parents=True, exist_ok=True)

    units: list[dict[str, str]] = []
    for src, acq in zip(source, acquisition):
        quantity = int(src["quantity"])
        for unit_index in range(1, quantity + 1):
            unit_id = f'{src["batch_line"]}-U{unit_index:02d}'
            units.append({
                "unit_id": unit_id,
                "line_id": src["batch_line"],
                "lot_id": acq["lot_id"],
                "parent_item_id": src["parent_item_id"],
                "manufacturer": src["manufacturer"],
                "expected_order_code": src["order_code"],
                "unit_index": str(unit_index),
                "line_quantity": str(quantity),
                "required_receiving_routes": src["receiving_route"],
                "evidence_directory": f'evidence/receiving/{unit_id}/',
                "quarantine_label_id": f'Q-{unit_id}',
                "received_order_code": "NOT EXECUTED",
                "serial_or_lot": "NOT EXECUTED",
                "authorization_state": "NOT AUTHORIZED",
                "order_state": "NOT ORDERED",
                "receiving_state": "NOT RECEIVED",
                "disposition": "QUARANTINE REQUIRED - NOT ACCEPTED",
                "connection_authorized": "NO",
                "motion_authorized": "NO",
                "energization_authorized": "NO",
                "warning": WARNING,
            })

    traveler: list[dict[str, str]] = []
    for unit in units:
        for step_id, name, required_input, acceptance, evidence in STEPS:
            traveler.append({
                "record_id": f'{unit["unit_id"]}-{step_id}',
                "unit_id": unit["unit_id"],
                "line_id": unit["line_id"],
                "lot_id": unit["lot_id"],
                "step_id": step_id,
                "step_name": name,
                "required_input": required_input,
                "acceptance_boundary": acceptance,
                "required_evidence": evidence,
                "executor": "SELECTION REQUIRED",
                "independent_witness": "SELECTION REQUIRED",
                "execution_state": "NOT EXECUTED",
                "result": "NOT EXECUTED",
                "evidence_uri": "NOT EXECUTED",
                "nonconformance_id": "NOT EXECUTED",
                "authorization_state": "NOT AUTHORIZED",
                "warning": WARNING,
            })

    evidence_rows: list[dict[str, str]] = []
    for unit in units:
        for category_id, category, instruction in EVIDENCE_CATEGORIES:
            evidence_rows.append({
                "evidence_id": f'{unit["unit_id"]}-{category_id}',
                "unit_id": unit["unit_id"],
                "line_id": unit["line_id"],
                "category": category,
                "capture_instruction": instruction,
                "expected_relative_path": f'{unit["evidence_directory"]}{category_id.lower()}-{category}.jpg',
                "captured_file": "NOT EXECUTED",
                "sha256": "NOT EXECUTED",
                "capture_time_utc": "NOT EXECUTED",
                "recorder": "SELECTION REQUIRED",
                "independent_check": "NOT EXECUTED",
                "state": "NOT EXECUTED",
                "warning": WARNING,
            })

    labels = [{
        "label_id": unit["quarantine_label_id"],
        "unit_id": unit["unit_id"],
        "line_id": unit["line_id"],
        "lot_id": unit["lot_id"],
        "expected_identity": f'{unit["manufacturer"]} {unit["expected_order_code"]}',
        "initial_state": "NOT RECEIVED - HOLD",
        "storage_location": "SELECTION REQUIRED",
        "received_date": "NOT EXECUTED",
        "inspector": "SELECTION REQUIRED",
        "disposition": "QUARANTINE - NO CONNECTION OR USE",
        "warning": WARNING,
    } for unit in units]

    write_csv(OUT / "receiving-unit-register.csv", units)
    write_csv(OUT / "receiving-traveler.csv", traveler)
    write_csv(OUT / "evidence-file-manifest-template.csv", evidence_rows)
    write_csv(OUT / "quarantine-label-register.csv", labels)
    write_csv(FORM, traveler)

    status = {
        "revision": REVISION,
        "source_batch": "EVALUATION-BATCH-A",
        "source_acquisition": "HR-V0-EVAL-BATCH-A-ACQ-P0.1",
        "line_count": 17,
        "physical_unit_count": 21,
        "traveler_step_count_per_unit": len(STEPS),
        "traveler_record_count": len(traveler),
        "evidence_category_count_per_unit": len(EVIDENCE_CATEGORIES),
        "evidence_placeholder_count": len(evidence_rows),
        "quarantine_label_count": len(labels),
        "authorized_unit_count": 0,
        "received_unit_count": 0,
        "executed_traveler_record_count": 0,
        "captured_evidence_count": 0,
        "accepted_for_machine_use_count": 0,
        "fabrication_authorized": False,
        "connection_authorized": False,
        "motion_authorized": False,
        "energization_authorized": False,
        "warning": WARNING,
    }
    (OUT / "package-status.json").write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8", newline="\n")

    lot_buttons = ''.join(f'<button data-lot="{lot}" aria-pressed="false">{lot}</button>' for lot in ("LOT-A", "LOT-B", "LOT-C", "LOT-D"))
    unit_rows = ''.join(
        f'<tr data-lot="{unit["lot_id"]}" data-search="{html.escape((unit["unit_id"] + " " + unit["manufacturer"] + " " + unit["expected_order_code"]).lower())}"><td>{unit["unit_id"]}</td><td>{unit["lot_id"]}</td><td>{html.escape(unit["manufacturer"])}</td><td>{html.escape(unit["expected_order_code"])}</td><td>{html.escape(unit["required_receiving_routes"])}</td><td>NOT RECEIVED</td></tr>'
        for unit in units
    )
    step_rows = ''.join(
        f'<tr><td>{step_id}</td><td>{html.escape(name)}</td><td>{html.escape(required_input)}</td><td>{html.escape(acceptance)}</td><td>NOT EXECUTED</td></tr>'
        for step_id, name, required_input, acceptance, _evidence in STEPS
    )
    label_cards = ''.join(
        f'<article class="label"><strong>{label["label_id"]}</strong><span>{label["unit_id"]} · {label["lot_id"]}</span><span>{html.escape(label["expected_identity"])}</span><b>NOT RECEIVED — HOLD</b><small>QUARANTINE · NO CONNECTION OR USE</small></article>'
        for label in labels
    )
    page = f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>HR-V0 Evaluation Batch A receiving</title><style>:root{{--sky:#78cff4;--navy:#082f58;--blue:#115e9b;--gold:#f3b61f;--paper:#f5faff;--hold:#fff2be}}*{{box-sizing:border-box}}body{{margin:0;color:var(--navy);font:clamp(16px,1.15vw,19px)/1.5 Arial,sans-serif;background:white}}header{{padding:clamp(1.5rem,5vw,4rem);background:linear-gradient(130deg,var(--sky),#edf9ff);border-bottom:7px solid var(--gold)}}h1{{font-size:clamp(2.1rem,5vw,4.5rem);line-height:1.04;max-width:18ch;margin:.3rem 0 1rem}}h2{{font-size:clamp(1.5rem,3vw,2.5rem);line-height:1.15}}main{{max-width:1480px;margin:auto;padding:2rem clamp(1rem,4vw,3.5rem)}}.warning{{padding:1rem;border:3px solid #b47c00;background:var(--hold);border-radius:.8rem;font-weight:800}}.summary{{font-size:clamp(1.15rem,2vw,1.55rem);max-width:62rem}}.stats{{display:grid;grid-template-columns:repeat(auto-fit,minmax(190px,1fr));gap:1rem;margin:2rem 0}}.stat{{border:3px solid var(--blue);border-radius:1rem;padding:1rem;background:var(--paper)}}.number{{font-size:clamp(2rem,4vw,3.3rem);font-weight:800}}button,input{{font:inherit;padding:.65rem .9rem;border:3px solid var(--blue);border-radius:.6rem;background:white;color:var(--navy);margin:.25rem}}button[aria-pressed="true"]{{background:var(--gold)}}input{{width:min(100%,32rem)}}.table-wrap{{overflow:auto;border:2px solid #8fb2ca;border-radius:.7rem;margin:1rem 0 2rem}}table{{width:100%;border-collapse:collapse;min-width:1080px}}th,td{{padding:.8rem;text-align:left;vertical-align:top;border-bottom:1px solid #b8ccd8}}th{{position:sticky;top:0;background:var(--navy);color:white}}.boundary{{border-left:7px solid var(--gold);padding-left:1rem;margin:2rem 0}}.labels{{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:.8rem}}.label{{border:3px solid var(--navy);padding:1rem;display:grid;gap:.35rem;background:white;break-inside:avoid}}.label strong{{font-size:1.25rem}}.label b{{background:var(--gold);padding:.35rem}}.label small{{font-size:14px;font-weight:700}}[hidden]{{display:none!important}}@media print{{header,.controls,.tables,.boundary,.stats{{display:none}}main{{max-width:none;padding:0}}.labels{{grid-template-columns:repeat(2,1fr)}}.label{{min-height:155px}}h2{{font-size:24px}}}}</style></head><body><header><div>{REVISION} · R146 · 2026-08-09</div><h1>Receive 21 evaluation units without losing identity</h1><div class="warning">{WARNING}. Zero units are authorized, ordered, received, connected, or accepted for machine use.</div></header><main><p class="summary">This campaign pre-identifies every physical unit in Evaluation Batch A, binds each to twelve receiving steps and seven evidence categories, and keeps every article in quarantine until a named disposition exists.</p><section class="stats"><div class="stat"><div class="number">21</div>pre-identified units</div><div class="stat"><div class="number">252</div>unit/step records</div><div class="stat"><div class="number">147</div>evidence placeholders</div><div class="stat"><div class="number">0</div>executed records</div></section><div class="boundary"><h2>Hard boundary</h2><p>Receiving is an identity and evidence operation. It is not installation or application acceptance. Do not mate connectors, connect any source, access encoders, enable torque, command motion, or remove quarantine based on this guide.</p></div><section class="controls"><h2>Find a unit</h2><input id="search" type="search" placeholder="Unit, manufacturer, model or order code"><div><button data-lot="ALL" aria-pressed="true">All 21</button>{lot_buttons}</div></section><section class="tables"><div class="table-wrap"><table><thead><tr><th>Unit</th><th>Lot</th><th>Maker</th><th>Expected identity</th><th>Required routes</th><th>State</th></tr></thead><tbody id="units">{unit_rows}</tbody></table></div><h2>Twelve required steps per unit</h2><div class="table-wrap"><table><thead><tr><th>Step</th><th>Operation</th><th>Required input</th><th>Acceptance boundary</th><th>State</th></tr></thead><tbody>{step_rows}</tbody></table></div></section><div class="boundary"><h2>Evidence rule</h2><p>Each unit has seven named evidence placeholders. Record the raw filename, SHA-256, UTC capture time and recorder. A missing or ambiguous identity remains quarantined and opens a deviation; it is never silently substituted.</p></div><h2>Printable quarantine labels</h2><p class="controls">Print only after confirming the controlled commit. Blank storage and inspector fields remain in the CSV register.</p><section class="labels">{label_cards}</section></main><script>const buttons=[...document.querySelectorAll('button[data-lot]')],rows=[...document.querySelectorAll('#units tr')],search=document.querySelector('#search');let lot='ALL';function filter(){{const q=search.value.trim().toLowerCase();rows.forEach(row=>row.hidden=(lot!=='ALL'&&row.dataset.lot!==lot)||(q&&!row.dataset.search.includes(q)))}}buttons.forEach(button=>button.addEventListener('click',()=>{{lot=button.dataset.lot;buttons.forEach(item=>item.setAttribute('aria-pressed',String(item===button)));filter()}}));search.addEventListener('input',filter);</script></body></html>'''
    WEB.write_text(page, encoding="utf-8", newline="\n")
    print(f"{REVISION}: 17 lines / 21 units / {len(traveler)} traveler records / {len(evidence_rows)} evidence placeholders")
    print("0 authorized / 0 ordered / 0 received / 0 executed")
    print(WARNING)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
