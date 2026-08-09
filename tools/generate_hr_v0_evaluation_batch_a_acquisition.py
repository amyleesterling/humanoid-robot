"""Generate the complete fail-closed Evaluation Batch A acquisition packet."""

from __future__ import annotations

import csv
import html
import json
import shutil
from decimal import Decimal
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "bom" / "hr-v0-evaluation-batch-a.csv"
OUT = ROOT / "procurement" / "hr-v0" / "evaluation-batch-a-acquisition-p0.1"
FORM = ROOT / "tests" / "forms" / "hr-v0-evaluation-batch-a-authorization-template.csv"
REVISION = "HR-V0-EVAL-BATCH-A-ACQ-P0.1"
WARNING = (
    "PRELIMINARY - EVALUATION ACQUISITION DECISION ONLY - NOT APPROVED FOR "
    "FABRICATION, CONNECTION, MOTION, OR ENERGIZATION"
)


LOTS = {
    "EVA-001": "LOT-B",
    "EVA-002": "LOT-A",
    "EVA-003": "LOT-A",
    "EVA-004": "LOT-B",
    "EVA-005": "LOT-C",
    "EVA-006": "LOT-C",
    "EVA-007": "LOT-C",
    "EVA-008": "LOT-C",
    "EVA-009": "LOT-C",
    "EVA-010": "LOT-B",
    "EVA-011": "LOT-A",
    "EVA-012": "LOT-A",
    "EVA-013": "LOT-A",
    "EVA-014": "LOT-C",
    "EVA-015": "LOT-C",
    "EVA-016": "LOT-D",
    "EVA-017": "LOT-D",
}

# Official manufacturer-page snapshots rechecked 2026-08-09.  Absence from this
# map means a current manufacturer price was not exposed and a written quote is
# required; it never means zero cost.
PRICES = {
    "EVA-001": Decimal("36.92"),
    "EVA-002": Decimal("482.89"),
    "EVA-003": Decimal("482.89"),
    "EVA-004": Decimal("310.39"),
    "EVA-010": Decimal("314.76"),
    "EVA-011": Decimal("76.71"),
    "EVA-012": Decimal("76.71"),
    "EVA-013": Decimal("31.51"),
    "EVA-014": Decimal("20.44"),
}

LOT_NAMES = {
    "LOT-A": "Joint-stack metrology articles",
    "LOT-B": "Bench mechatronics and gripper articles",
    "LOT-C": "Safety and control evaluation articles",
    "LOT-D": "External power-source evaluation articles",
}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    if not rows:
        raise ValueError(f"refusing to write empty CSV: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    source_rows = read_csv(SOURCE)
    if [row["batch_line"] for row in source_rows] != [f"EVA-{i:03d}" for i in range(1, 18)]:
        raise AssertionError("Evaluation Batch A membership/order changed")
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)

    lines: list[dict[str, str]] = []
    for row in source_rows:
        line_id = row["batch_line"]
        quantity = int(row["quantity"])
        unit = PRICES.get(line_id)
        known = unit * quantity if unit is not None else Decimal("0")
        lines.append(
            {
                "line_id": line_id,
                "lot_id": LOTS[line_id],
                "parent_item_id": row["parent_item_id"],
                "manufacturer": row["manufacturer"],
                "order_code": row["order_code"],
                "quantity": str(quantity),
                "unit_price_usd": f"{unit:.2f}" if unit is not None else "QUOTE REQUIRED",
                "extended_known_usd": f"{known:.2f}",
                "price_state": "OFFICIAL WEB SNAPSHOT" if unit is not None else "QUOTE REQUIRED - NO CURRENT MANUFACTURER PRICE EXPOSED",
                "official_source": row["primary_source"],
                "source_access": "official record rechecked 2026-08-09",
                "availability_state": "WRITTEN STOCK/ALLOCATION CONFIRMATION REQUIRED",
                "receiving_route": row["receiving_route"],
                "permitted_use_if_later_approved": "Receive, quarantine, identify, inventory, photograph and execute only the separately authorized unpowered receiving/evaluation procedure",
                "prohibited_use": "Production use; fabrication release; wiring; source connection; encoder access; torque enable; motion; child access; energization",
                "authorization_state": "NOT AUTHORIZED",
                "order_state": "NOT ORDERED",
                "evidence_state": "NOT RECEIVED",
                "warning": WARNING,
            }
        )

    lot_rows: list[dict[str, str]] = []
    authorization_rows: list[dict[str, str]] = []
    for lot_id, name in LOT_NAMES.items():
        members = [row for row in lines if row["lot_id"] == lot_id]
        known = sum(Decimal(row["extended_known_usd"]) for row in members)
        quote_count = sum(row["unit_price_usd"] == "QUOTE REQUIRED" for row in members)
        lot_rows.append(
            {
                "lot_id": lot_id,
                "lot_name": name,
                "line_ids": ";".join(row["line_id"] for row in members),
                "line_count": str(len(members)),
                "physical_unit_count": str(sum(int(row["quantity"]) for row in members)),
                "known_price_floor_usd": f"{known:.2f}",
                "quote_required_line_count": str(quote_count),
                "total_cost_state": "INCOMPLETE - SHIPPING TAX FEES AND QUOTE-REQUIRED LINES EXCLUDED",
                "decision_state": "NOT AUTHORIZED",
                "warning": WARNING,
            }
        )
        authorization_rows.append(
            {
                "authorization_id": f"EBAA-{lot_id[-1]}",
                "lot_id": lot_id,
                "line_ids": ";".join(row["line_id"] for row in members),
                "program_owner_decision": "NOT AUTHORIZED",
                "maximum_authorized_usd": "NOT AUTHORIZED",
                "current_cart_or_quote_uri": "NOT EXECUTED",
                "quote_expiration": "NOT EXECUTED",
                "seller_identity_verified_by": "SELECTION REQUIRED",
                "ship_to": "SELECTION REQUIRED",
                "receiving_owner": "SELECTION REQUIRED",
                "approver_name": "SELECTION REQUIRED",
                "approver_signature_date": "NOT EXECUTED",
                "purchase_order_or_receipt": "NOT EXECUTED",
                "warning": WARNING,
            }
        )

    source_register: list[dict[str, str]] = []
    seen: set[str] = set()
    for row in source_rows:
        url = row["primary_source"]
        if url in seen:
            continue
        seen.add(url)
        matching = [line["line_id"] for line in lines if line["official_source"] == url]
        source_register.append(
            {
                "source_id": f"EBAS-{len(source_register) + 1:03d}",
                "line_ids": ";".join(matching),
                "authority": row["manufacturer"],
                "order_code": row["order_code"],
                "url": url,
                "revision_or_access": "official record rechecked 2026-08-09",
                "controlled_fact": "Exact manufacturer/order-code identity and current product-record presence; price only where the line register says OFFICIAL WEB SNAPSHOT",
                "boundary": "Page presence is not allocated stock, total landed cost, application acceptance, received identity or selection approval",
            }
        )

    write_csv(OUT / "line-register.csv", lines)
    write_csv(OUT / "lot-register.csv", lot_rows)
    write_csv(OUT / "purchase-authorization-register.csv", authorization_rows)
    write_csv(OUT / "source-register.csv", source_register)
    write_csv(
        FORM,
        [
            {
                "authorization_id": "NOT-AUTHORIZED",
                "revision": REVISION,
                "source_commit": "NOT EXECUTED",
                "approved_lot_ids": "NOT AUTHORIZED",
                "approved_line_ids": "NOT AUTHORIZED",
                "maximum_spend_usd": "NOT AUTHORIZED",
                "seller_and_quote": "NOT EXECUTED",
                "quote_expiration": "NOT EXECUTED",
                "ship_to": "SELECTION REQUIRED",
                "receiving_owner": "SELECTION REQUIRED",
                "permitted_use": "NOT AUTHORIZED",
                "program_owner_name": "SELECTION REQUIRED",
                "program_owner_signature": "NOT EXECUTED",
                "approval_date": "NOT EXECUTED",
                "purchase_order": "NOT EXECUTED",
                "decision": "NOT AUTHORIZED",
                "warning": WARNING,
            }
        ],
    )

    known_total = sum(Decimal(row["extended_known_usd"]) for row in lines)
    quote_lines = sum(row["unit_price_usd"] == "QUOTE REQUIRED" for row in lines)
    if known_total != Decimal("1864.73") or quote_lines != 8:
        raise AssertionError("current price-floor arithmetic changed")
    status = {
        "revision": REVISION,
        "source_batch": "EVALUATION-BATCH-A",
        "line_count": 17,
        "physical_unit_count": 21,
        "lot_count": 4,
        "official_web_known_price_floor_usd": "1864.73",
        "quote_required_line_count": 8,
        "shipping_tax_fees_included": False,
        "purchase_authorized": False,
        "order_placed": False,
        "physical_evidence_received": False,
        "fabrication_authorized": False,
        "connection_authorized": False,
        "motion_authorized": False,
        "energization_authorized": False,
        "warning": WARNING,
    }
    (OUT / "package-status.json").write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8", newline="\n")

    lot_cards = "".join(
        f'<article class="card" data-lot="{row["lot_id"]}"><div class="eyebrow">{row["lot_id"]}</div><h2>{html.escape(row["lot_name"])}</h2><p>{row["line_count"]} lines / {row["physical_unit_count"]} physical units</p><p>Known price floor: <strong>${row["known_price_floor_usd"]}</strong></p><p>Quote-required lines: <strong>{row["quote_required_line_count"]}</strong></p><span class="badge">NOT AUTHORIZED</span></article>'
        for row in lot_rows
    )
    table_rows = "".join(
        f'<tr data-lot="{row["lot_id"]}"><td>{row["line_id"]}</td><td>{row["lot_id"]}</td><td>{html.escape(row["manufacturer"])}</td><td>{html.escape(row["order_code"])}</td><td>{row["quantity"]}</td><td>{row["unit_price_usd"]}</td><td>${row["extended_known_usd"]}</td><td>{row["availability_state"]}</td><td>{row["authorization_state"]}</td></tr>'
        for row in lines
    )
    page = f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>HR-V0 Evaluation Batch A acquisition</title><style>:root{{--sky:#6bc9f2;--navy:#082b4c;--blue:#125a91;--gold:#f3b61f;--paper:#f7fbff;--hold:#fff3c4}}*{{box-sizing:border-box}}body{{margin:0;color:var(--navy);font:clamp(16px,1.2vw,19px)/1.5 Arial,sans-serif;background:#fff}}header{{padding:clamp(1.5rem,5vw,4.5rem);background:linear-gradient(135deg,var(--sky),#e9f8ff);border-bottom:7px solid var(--gold)}}h1{{font-size:clamp(2.1rem,5vw,4.7rem);line-height:1.04;margin:.3rem 0 1rem;max-width:18ch}}h2{{font-size:clamp(1.35rem,2vw,2rem);line-height:1.15}}main{{max-width:1450px;margin:auto;padding:2rem clamp(1rem,4vw,3.5rem)}}.warning{{padding:1rem;border:3px solid #c48b00;background:var(--hold);border-radius:.9rem;font-weight:700}}.summary{{font-size:clamp(1.15rem,2vw,1.6rem);max-width:58rem}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,280px),1fr));gap:1rem;margin:2rem 0}}.card{{padding:1.2rem;border:3px solid var(--blue);border-radius:1rem;background:var(--paper)}}.eyebrow,.badge{{font-size:14px;font-weight:700;letter-spacing:.04em}}.badge{{display:inline-block;background:var(--gold);padding:.35rem .6rem;border-radius:.4rem}}button{{font:inherit;font-weight:700;padding:.7rem 1rem;margin:.25rem;border:3px solid var(--blue);border-radius:.6rem;background:#fff;color:var(--navy)}}button[aria-pressed="true"]{{background:var(--gold)}}.table-wrap{{overflow:auto;border:2px solid #9bb8ca;border-radius:.7rem;margin-top:1rem}}table{{width:100%;border-collapse:collapse;min-width:1100px}}th,td{{padding:.8rem;text-align:left;vertical-align:top;border-bottom:1px solid #b8ccd8}}th{{position:sticky;top:0;background:var(--navy);color:#fff}}.boundary{{border-left:7px solid var(--gold);padding-left:1rem;margin:2rem 0}}[hidden]{{display:none!important}}</style></head><body><header><div class="eyebrow">{REVISION} / official records rechecked 2026-08-09</div><h1>Evaluation Batch A acquisition decision</h1><div class="warning">{WARNING}. No checkout, payment, order, shipment, fabrication, connection, motion, or energization is authorized.</div></header><main><p class="summary">All <strong>17 controlled evaluation lines</strong> are now grouped into four decision lots covering <strong>21 physical units</strong>. Current manufacturer pages expose a <strong>$1,864.73 known price floor</strong>; eight lines still require written pricing, and shipping, tax, fees, availability, and allocation remain outside that floor.</p><section class="grid">{lot_cards}</section><div class="boundary"><h2>What this packet can do</h2><p>It lets the program owner approve exact evaluation-only lines and a maximum spend after a current cart or quote is attached. Approval to buy is not approval to install, wire, connect, move, fabricate, or energize anything.</p></div><h2>Filter the controlled lines</h2><div><button data-filter="ALL" aria-pressed="true">All 17 lines</button><button data-filter="LOT-A">Lot A</button><button data-filter="LOT-B">Lot B</button><button data-filter="LOT-C">Lot C</button><button data-filter="LOT-D">Lot D</button></div><div class="table-wrap"><table><thead><tr><th>Line</th><th>Lot</th><th>Maker</th><th>Exact order code</th><th>Qty</th><th>Unit snapshot</th><th>Known extended</th><th>Availability</th><th>Authority</th></tr></thead><tbody>{table_rows}</tbody></table></div><div class="boundary"><h2>Release boundary</h2><p>Every line remains NOT AUTHORIZED, NOT ORDERED, and NOT RECEIVED. Quote-required does not mean unavailable, and a zero known extension does not mean zero cost. Current stock allocation and landed cost must be captured immediately before any separately signed purchase decision.</p></div></main><script>const buttons=[...document.querySelectorAll('button[data-filter]')],rows=[...document.querySelectorAll('tbody tr[data-lot]')];buttons.forEach(button=>button.addEventListener('click',()=>{{buttons.forEach(b=>b.setAttribute('aria-pressed','false'));button.setAttribute('aria-pressed','true');const f=button.dataset.filter;rows.forEach(row=>row.hidden=f!=='ALL'&&row.dataset.lot!==f)}}));</script></body></html>'''
    (OUT / "index.html").write_text(page, encoding="utf-8", newline="\n")
    print(f"{REVISION}: 17 lines / 21 units / 4 lots / $1,864.73 known floor / 8 quote-required")
    print(WARNING)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
