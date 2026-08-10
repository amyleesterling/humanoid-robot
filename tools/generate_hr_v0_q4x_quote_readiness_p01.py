#!/usr/bin/env python3
"""Generate the R188 source-bound Q4X quote-readiness amendment."""

from __future__ import annotations

import csv
import html
import json
from decimal import Decimal
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "procurement/hr-v0/q4x-unpowered-acquisition-p0.1"
OUT = ROOT / "procurement/hr-v0/q4x-quote-readiness-p0.1"
REVISION = "HR-V0-Q4X-QUOTE-READINESS-P0.1"
WARNING = (
    "PRELIMINARY - COMMERCIAL EVIDENCE AMENDMENT ONLY - NOT APPROVED FOR "
    "PROCUREMENT, FABRICATION, DRILLING, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION"
)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


base_lines = read_csv(BASE / "line-register.csv")
base_by_id = {row["line_id"]: row for row in base_lines}

source_delta = [
    {
        "source_id": "QRD-001",
        "line_id": "QRL-002",
        "seller": "DigiKey",
        "url": "https://www.digikey.com/en/products/detail/hammond-manufacturing/14F0907/2357844",
        "access_date": "2026-08-10",
        "exact_manufacturer_part_number": "14F0907",
        "seller_order_code": "14F0907-ND",
        "unit_price_snapshot_usd": "29.80",
        "availability_snapshot": "AVAILABLE TO ORDER; FACTORY STOCK 60; MANUFACTURER STANDARD LEAD TIME 4 WEEKS",
        "boundary": "Factory stock is not DigiKey shelf stock; price, allocation, shipping, tax and delivery require a same-session cart or written quote",
        "warning": WARNING,
    },
    {
        "source_id": "QRD-002",
        "line_id": "QRL-006",
        "seller": "DigiKey",
        "url": "https://www.digikey.com/en/products/detail/phoenix-contact/1464484/22032786",
        "access_date": "2026-08-10",
        "exact_manufacturer_part_number": "1464484",
        "seller_order_code": "277-1464484-ND",
        "unit_price_snapshot_usd": "22.83",
        "availability_snapshot": "IN-STOCK 0; MANUFACTURER STANDARD LEAD TIME 8 WEEKS; TARIFF MAY APPLY",
        "boundary": "No immediate-stock claim; back-order acceptance, allocation, tariff, shipping, tax and delivery require a same-session cart or written quote",
        "warning": WARNING,
    },
]

line_disposition = [
    {
        "line_id": "QRL-002",
        "base_exact_mpn": base_by_id["QRL-002"]["manufacturer_part_number"],
        "base_gap": "DIRECT SELLER ORDER CODE SELECTION REQUIRED; ASSOCIATED-PRODUCT SNAPSHOT ONLY",
        "r188_result": "DIRECT PRODUCT LINE VERIFIED",
        "exact_seller_order_code": "14F0907-ND",
        "current_commercial_state": "AVAILABLE TO ORDER; FACTORY STOCK 60; 4-WEEK MANUFACTURER STANDARD LEAD TIME",
        "decision_effect": "Former direct-line ambiguity closed; same-session cart or quote still mandatory",
        "checkout_state": "NOT READY - NO CART OR QUOTE",
        "warning": WARNING,
    },
    {
        "line_id": "QRL-006",
        "base_exact_mpn": base_by_id["QRL-006"]["manufacturer_part_number"],
        "base_gap": "LIVE AVAILABILITY UNVERIFIED",
        "r188_result": "DIRECT PRODUCT LINE VERIFIED; ZERO IMMEDIATE STOCK OBSERVED",
        "exact_seller_order_code": "277-1464484-ND",
        "current_commercial_state": "IN-STOCK 0; 8-WEEK MANUFACTURER STANDARD LEAD TIME; TARIFF MAY APPLY",
        "decision_effect": "Unknown availability replaced by explicit zero-stock/back-order hold; no substitution authorized",
        "checkout_state": "NOT READY - SUPPLY/DELIVERY DECISION REQUIRED",
        "warning": WARNING,
    },
]

fit_base = Decimal("211.30")
panel_old = Decimal("29.47")
panel_new = Decimal("29.80")
ptcb = Decimal("22.83")
fit_new = fit_base - panel_old + panel_new
combined = fit_new + ptcb

cost_rows = [
    {
        "lot_id": "LOT-Q4X-FIT",
        "r187_snapshot_subtotal_usd": "211.30",
        "r188_delta_usd": f"{panel_new - panel_old:.2f}",
        "r188_snapshot_subtotal_usd": f"{fit_new:.2f}",
        "quote_readiness": "READY FOR SAME-SESSION CART OR WRITTEN QUOTE ASSEMBLY; NOT CHECKOUT",
        "blocking_condition": "No cart/quote, shipping, tax, delivery allocation, Boston ship-to or authorization",
        "warning": WARNING,
    },
    {
        "lot_id": "LOT-Q4X-PTCB",
        "r187_snapshot_subtotal_usd": "22.83",
        "r188_delta_usd": "0.00",
        "r188_snapshot_subtotal_usd": f"{ptcb:.2f}",
        "quote_readiness": "NOT READY FOR IMMEDIATE CHECKOUT",
        "blocking_condition": "DigiKey in-stock 0; supply/delivery route and same-session cart/quote required",
        "warning": WARNING,
    },
    {
        "lot_id": "COMBINED",
        "r187_snapshot_subtotal_usd": "234.13",
        "r188_delta_usd": f"{panel_new - panel_old:.2f}",
        "r188_snapshot_subtotal_usd": f"{combined:.2f}",
        "quote_readiness": "NOT READY FOR CHECKOUT",
        "blocking_condition": "PTCB zero stock plus all landed-cost and authorization fields remain open",
        "warning": WARNING,
    },
]

status = {
    "revision": REVISION,
    "date": "2026-08-10",
    "supersedes_commercial_snapshot": "HR-V0-Q4X-UNPOWERED-ACQ-P0.1",
    "source_delta_count": 2,
    "direct_line_ambiguities_closed": 1,
    "explicit_zero_stock_holds": 1,
    "fit_lot_snapshot_subtotal_usd": f"{fit_new:.2f}",
    "ptcb_lot_snapshot_subtotal_usd": f"{ptcb:.2f}",
    "combined_snapshot_subtotal_usd": f"{combined:.2f}",
    "cart_executed": False,
    "quote_received": False,
    "purchase_authorized": False,
    "order_placed": False,
    "physical_evidence_received": False,
    "fabrication_authorized": False,
    "connection_authorized": False,
    "energization_authorized": False,
    "sol_r12_blockers_closed": 0,
    "warning": WARNING,
}

write_csv(OUT / "source-delta.csv", source_delta)
write_csv(OUT / "line-disposition.csv", line_disposition)
write_csv(OUT / "cost-reconciliation.csv", cost_rows)
OUT.mkdir(parents=True, exist_ok=True)
(OUT / "package-status.json").write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8")


def table(rows: list[dict[str, str]], columns: list[str]) -> str:
    labels = {name: name.replace("_", " ").title() for name in columns}
    head = "".join(f"<th>{html.escape(labels[name])}</th>" for name in columns)
    body = "".join(
        "<tr>" + "".join(f"<td>{html.escape(row[name])}</td>" for name in columns) + "</tr>"
        for row in rows
    )
    return f"<div class='scroll'><table><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></div>"


page = f"""<!doctype html>
<html lang='en'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'>
<title>R188 Q4X quote readiness</title>
<style>
:root{{--sky:#dff4ff;--blue:#082f62;--gold:#f4bd32;--ink:#10243e;--paper:#f8fbff;--line:#9ec9e8}}
*{{box-sizing:border-box}} body{{margin:0;background:var(--paper);color:var(--ink);font:16px/1.55 system-ui,sans-serif}}
header{{background:linear-gradient(135deg,var(--sky),#fff);border-bottom:5px solid var(--gold);padding:clamp(24px,5vw,64px)}}
main{{max-width:1180px;margin:auto;padding:24px}} h1{{color:var(--blue);font-size:clamp(2rem,6vw,4.5rem);line-height:1.02;margin:.25rem 0 1rem}}
.warning{{background:var(--blue);color:#fff;border-left:10px solid var(--gold);padding:18px;font-size:clamp(16px,2vw,20px);font-weight:800}}
.metrics{{display:grid;grid-template-columns:repeat(auto-fit,minmax(210px,1fr));gap:16px;margin:24px 0}} .card{{background:#fff;border:2px solid var(--line);border-radius:16px;padding:18px}}
.card strong{{display:block;color:var(--blue);font-size:clamp(1.6rem,4vw,2.4rem)}} nav{{display:flex;gap:10px;flex-wrap:wrap;margin:24px 0}}
button{{font:700 16px/1.2 system-ui;padding:12px 16px;border:2px solid var(--blue);border-radius:999px;background:#fff;color:var(--blue);cursor:pointer}}
button[aria-selected='true']{{background:var(--blue);color:#fff}} section[hidden]{{display:none}} section{{background:#fff;border:2px solid var(--line);border-radius:16px;padding:20px;margin-bottom:24px}}
.scroll{{overflow:auto}} table{{border-collapse:collapse;min-width:850px;width:100%}} th,td{{border:1px solid #b8cfe3;padding:12px;text-align:left;vertical-align:top;font-size:14px}} th{{background:var(--sky);color:var(--blue)}}
.hold{{color:#7a3700;font-weight:800}} code{{font-size:14px}} @media(max-width:520px){{main{{padding:14px}} header{{padding:22px 14px}} section{{padding:14px}}}}
</style></head><body>
<header><div class='warning'>{html.escape(WARNING)}</div><p>Project Button · R188 · {REVISION}</p><h1>Quote readiness, without checkout.</h1><p>Two previously ambiguous commercial lines now have direct seller evidence. One becomes quote-ready; the other becomes an explicit zero-stock hold.</p></header>
<main><div class='metrics'>
<div class='card'><span>Corrected fit-lot snapshot</span><strong>${fit_new:.2f}</strong></div>
<div class='card'><span>PTCB snapshot</span><strong>${ptcb:.2f}</strong><span class='hold'>0 in stock</span></div>
<div class='card'><span>Combined snapshot</span><strong>${combined:.2f}</strong></div>
<div class='card'><span>Authority created</span><strong>0</strong><span>No cart, quote, order or work authority</span></div>
</div>
<nav aria-label='Guide sections'><button data-tab='result' aria-selected='true'>Result</button><button data-tab='lines' aria-selected='false'>Line evidence</button><button data-tab='cost' aria-selected='false'>Cost reconciliation</button></nav>
<section data-panel='result'><h2>Decision result</h2><p><code>QRL-002</code> now has direct DigiKey identity, order code and availability evidence. <code>QRL-006</code> now has direct DigiKey evidence showing zero stock and an eight-week manufacturer lead time.</p><p class='hold'>Neither lot is approved for checkout. The PTCB lot needs a supply/delivery decision; substitution is prohibited.</p><p>The $234.46 figure excludes shipping, tax, tariffs, fees and price movement. A same-session cart or written quote plus explicit human authorization remains mandatory.</p></section>
<section data-panel='lines' hidden><h2>Exact line evidence</h2>{table(line_disposition, ['line_id','base_exact_mpn','exact_seller_order_code','current_commercial_state','decision_effect','checkout_state'])}</section>
<section data-panel='cost' hidden><h2>Cost reconciliation</h2>{table(cost_rows, ['lot_id','r187_snapshot_subtotal_usd','r188_delta_usd','r188_snapshot_subtotal_usd','quote_readiness','blocking_condition'])}</section>
</main><script>document.querySelectorAll('button[data-tab]').forEach(b=>b.addEventListener('click',()=>{{document.querySelectorAll('button[data-tab]').forEach(x=>x.setAttribute('aria-selected',String(x===b)));document.querySelectorAll('section[data-panel]').forEach(s=>s.hidden=s.dataset.panel!==b.dataset.tab)}}));</script>
</body></html>"""
(OUT / "index.html").write_text(page, encoding="utf-8")
print(f"{REVISION}: generated ${combined:.2f} corrected snapshot; zero purchase or work authority")
