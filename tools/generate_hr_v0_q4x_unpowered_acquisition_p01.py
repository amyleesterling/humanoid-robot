#!/usr/bin/env python3
"""Generate the R187 fail-closed Q4X unpowered acquisition packet."""

from __future__ import annotations

import csv
import html
import json
from decimal import Decimal
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "procurement/hr-v0/q4x-unpowered-acquisition-p0.1"
FORM = ROOT / "tests/forms/hr-v0-q4x-unpowered-acquisition-authorization-template-p0.1.csv"
DOC = ROOT / "docs/hr-v0-q4x-unpowered-acquisition-p0.1.md"
REVISION = "HR-V0-Q4X-UNPOWERED-ACQ-P0.1"
DATE = "2026-08-10"
WARNING = (
    "PRELIMINARY - UNPOWERED ACQUISITION DECISION ONLY - NOT APPROVED FOR "
    "PROCUREMENT, FABRICATION, DRILLING, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION"
)


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    if not rows:
        raise ValueError(f"refusing to write empty CSV: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


sources = [
    {
        "source_id": "QAS-001",
        "seller": "DigiKey",
        "line_ids": "QRL-001;QRL-002",
        "url": "https://www.digikey.com/en/products/detail/hammond-manufacturing/PJ1084T/2569670",
        "access_record": "direct seller page rechecked 2026-08-10",
        "controlled_commercial_fact": "PJ1084T exact MPN, one-unit USD price and stock snapshot; exact 14F0907 associated-product USD price",
        "boundary": "14F0907 needs direct line/cart confirmation; seller copy does not control engineering geometry or rating",
    },
    {
        "source_id": "QAS-002",
        "seller": "DigiKey",
        "line_ids": "QRL-003",
        "url": "https://www.digikey.com/en/products/detail/phoenix-contact/1207650/7557943",
        "access_record": "direct seller page rechecked 2026-08-10",
        "controlled_commercial_fact": "1207650 exact MPN, one-unit USD price and stock snapshot",
        "boundary": "cart allocation, tariff, shipping and received identity remain unverified",
    },
    {
        "source_id": "QAS-003",
        "seller": "TME US",
        "line_ids": "QRL-004",
        "url": "https://www.tme.com/us/en-us/details/skintop-12x1.5g/glands/lapp/53111000/",
        "access_record": "live browser inspection 2026-08-10",
        "controlled_commercial_fact": "53111000 exact MPN; 6,709 shown in TME stock; one-piece multiplicity; 1+ net price USD 1.070; manufacturer bag 100",
        "boundary": "net price excludes sales tax and shipping; stock and price require cart recheck",
    },
    {
        "source_id": "QAS-004",
        "seller": "TME US",
        "line_ids": "QRL-005",
        "url": "https://www.tme.com/us/en-us/details/skintop-n12g/nuts-for-glands/lapp/53119000/",
        "access_record": "live browser inspection 2026-08-10",
        "controlled_commercial_fact": "53119000 exact MPN; 4,552 shown in TME stock; one-piece multiplicity; 5+ net price USD 0.176; manufacturer bag 100",
        "boundary": "five-piece priced purchase is proposed for two needed articles; net price excludes sales tax and shipping",
    },
    {
        "source_id": "QAS-005",
        "seller": "Mouser USA",
        "line_ids": "QRL-006",
        "url": "https://www.mouser.com/ProductDetail/Phoenix-Contact/1464484?qs=17ckDYBRdek8QCsQHZRXgA%3D%3D",
        "access_record": "cached direct seller record reviewed 2026-08-10; live browser access denied",
        "controlled_commercial_fact": "1464484 exact MPN and one-unit USD 22.83 snapshot",
        "boundary": "availability is UNVERIFIED and a current direct cart check is mandatory; engineering identity remains Phoenix-controlled",
    },
    {
        "source_id": "QAS-006",
        "seller": "DigiKey",
        "line_ids": "QRL-007",
        "url": "https://www.digikey.com/en/products/detail/phoenix-contact/3209578/2263912",
        "access_record": "direct seller page rechecked 2026-08-10",
        "controlled_commercial_fact": "3209578 exact MPN, one-unit USD price and stock snapshot",
        "boundary": "cart allocation, tariff, shipping and received identity remain unverified",
    },
    {
        "source_id": "QAS-007",
        "seller": "DigiKey",
        "line_ids": "QRL-008",
        "url": "https://www.digikey.com/en/products/detail/phoenix-contact/3209510/2263910",
        "access_record": "direct seller page rechecked 2026-08-10",
        "controlled_commercial_fact": "3209510 exact MPN, one-unit USD price and stock snapshot",
        "boundary": "cart allocation, tariff, shipping and received identity remain unverified",
    },
    {
        "source_id": "QAS-008",
        "seller": "DigiKey",
        "line_ids": "QRL-009",
        "url": "https://www.digikey.com/en/products/detail/phoenix-contact/3030417/2263929",
        "access_record": "direct seller page rechecked 2026-08-10",
        "controlled_commercial_fact": "3030417 exact MPN, one-unit USD price and stock snapshot",
        "boundary": "cart allocation, tariff, shipping and received identity remain unverified",
    },
    {
        "source_id": "QAS-009",
        "seller": "DigiKey",
        "line_ids": "QRL-010",
        "url": "https://www.digikey.com/en/products/detail/phoenix-contact/3022218/349871",
        "access_record": "direct seller page rechecked 2026-08-10",
        "controlled_commercial_fact": "3022218 exact MPN, one-unit USD price and stock snapshot",
        "boundary": "cart allocation, tariff, shipping and received identity remain unverified",
    },
    {
        "source_id": "QAS-010",
        "seller": "LAPP Tannehill",
        "line_ids": "QRL-004;QRL-005",
        "url": "https://www.lapptannehill.com/media/wysiwyg/pdf/catalogs/LAPP/SKINTOP-catalog.pdf",
        "access_record": "catalog record rechecked 2026-08-10",
        "controlled_commercial_fact": "manufacturer pack size 100 for exact 53111000 and 53119000",
        "boundary": "TME seller multiplicity is distinct from the manufacturer package; no substitution is authorized",
    },
]
for source in sources:
    source["warning"] = WARNING


raw_lines = [
    ("QRL-001", "LOT-Q4X-FIT", "Hammond Manufacturing", "PJ1084T", 1, 1, "DigiKey", "PJ1084T-ND", "158.47", "DIRECT PAGE; 2 SHOWN IN STOCK / FACTORY 36", "QAS-001", "enclosure survey article"),
    ("QRL-002", "LOT-Q4X-FIT", "Hammond Manufacturing", "14F0907", 1, 1, "DigiKey", "DIRECT SELLER ORDER CODE SELECTION REQUIRED", "29.47", "ASSOCIATED-PRODUCT SNAPSHOT; DIRECT LINE/CART CHECK REQUIRED", "QAS-001", "panel survey article"),
    ("QRL-003", "LOT-Q4X-FIT", "Phoenix Contact", "1207650", 1, 1, "DigiKey", "277-16990-ND", "7.21", "DIRECT PAGE; 530 SHOWN IN STOCK", "QAS-002", "one usable 500 mm rail survey/cut-planning article"),
    ("QRL-004", "LOT-Q4X-FIT", "LAPP", "53111000", 2, 2, "TME US", "SKINTOP-12X1.5G", "1.070", "LIVE PAGE; 6,709 SHOWN IN STOCK; MULTIPLICITY 1", "QAS-003;QAS-010", "two G1/G2 gland fit articles"),
    ("QRL-005", "LOT-Q4X-FIT", "LAPP", "53119000", 2, 5, "TME US", "SKINTOP-N12G", "0.176", "LIVE PAGE; 4,552 SHOWN IN STOCK; 5+ PRICE BREAK", "QAS-004;QAS-010", "two G1/G2 locknut fit articles plus three quarantined spares"),
    ("QRL-006", "LOT-Q4X-PTCB", "Phoenix Contact", "1464484", 1, 1, "Mouser USA", "651-1464484", "22.83", "CACHED SELLER SNAPSHOT; LIVE AVAILABILITY UNVERIFIED", "QAS-005", "catalog-envelope/device-retention article"),
    ("QRL-007", "LOT-Q4X-FIT", "Phoenix Contact", "3209578", 1, 1, "DigiKey", "277-2096-ND", "1.77", "DIRECT PAGE; STOCK SNAPSHOT SHOWN", "QAS-006", "PT 2.5-QUATTRO catalog-envelope article"),
    ("QRL-008", "LOT-Q4X-FIT", "Phoenix Contact", "3209510", 5, 5, "DigiKey", "277-2094-ND", "1.46", "DIRECT PAGE; 34,867 SHOWN IN STOCK", "QAS-007", "five PT 2.5 catalog-envelope articles"),
    ("QRL-009", "LOT-Q4X-FIT", "Phoenix Contact", "3030417", 2, 2, "DigiKey", "277-2113-ND", "0.86", "DIRECT PAGE; 19,066 SHOWN IN STOCK", "QAS-008", "two D-ST 2.5 end-cover articles"),
    ("QRL-010", "LOT-Q4X-FIT", "Phoenix Contact", "3022218", 2, 2, "DigiKey", "277-2292-ND", "1.17", "DIRECT PAGE; 43,762 SHOWN IN STOCK", "QAS-009", "two CLIPFIX 35 end-bracket articles"),
]

lines: list[dict[str, str]] = []
for item in raw_lines:
    price = Decimal(item[8])
    purchase_quantity = item[5]
    lines.append(
        {
            "line_id": item[0],
            "lot_id": item[1],
            "manufacturer": item[2],
            "manufacturer_part_number": item[3],
            "evaluation_quantity": str(item[4]),
            "seller_purchase_quantity": str(purchase_quantity),
            "seller": item[6],
            "seller_order_code": item[7],
            "unit_price_snapshot_usd": item[8],
            "extended_snapshot_usd": f"{price * purchase_quantity:.2f}",
            "availability_snapshot": item[9],
            "source_ids": item[10],
            "purpose": item[11],
            "cart_state": "NOT EXECUTED",
            "authorization_state": "NOT AUTHORIZED",
            "order_state": "NOT ORDERED",
            "receiving_state": "NOT RECEIVED",
            "permitted_use_if_later_authorized": "receipt, quarantine, identity inspection and separately authorized unpowered metrology only",
            "prohibited_use": "substitution; drilling; cutting; wiring; connection; powered test; motion; child access; energization",
            "warning": WARNING,
        }
    )


lot_definitions = [
    ("LOT-Q4X-FIT", "Unpowered enclosure, panel, rail, gland and terminal fit", "Nine exact lines; leaves the PTCB physical-fit row open"),
    ("LOT-Q4X-PTCB", "Unpowered exact PTCB identity and fit", "One exact line; current direct availability must be reconfirmed"),
]
lots: list[dict[str, str]] = []
decisions: list[dict[str, str]] = []
for lot_id, purpose, boundary in lot_definitions:
    members = [row for row in lines if row["lot_id"] == lot_id]
    subtotal = sum(Decimal(row["extended_snapshot_usd"]) for row in members)
    line_ids = ";".join(row["line_id"] for row in members)
    lots.append(
        {
            "lot_id": lot_id,
            "purpose": purpose,
            "line_ids": line_ids,
            "line_count": str(len(members)),
            "purchase_unit_count": str(sum(int(row["seller_purchase_quantity"]) for row in members)),
            "snapshot_subtotal_usd": f"{subtotal:.2f}",
            "cost_boundary": "INCOMPLETE - SHIPPING, SALES TAX, TARIFF CHANGES, FEES AND PRICE MOVEMENT EXCLUDED",
            "evidence_boundary": boundary,
            "decision_state": "NOT AUTHORIZED",
            "warning": WARNING,
        }
    )
    decisions.append(
        {
            "decision_id": f"Q4X-ACQ-{len(decisions) + 1:02d}",
            "lot_id": lot_id,
            "line_ids": line_ids,
            "program_owner_decision": "NOT AUTHORIZED",
            "maximum_authorized_usd": "NOT AUTHORIZED",
            "dated_cart_or_quote_uri": "NOT EXECUTED",
            "seller_and_stock_verified_by": "SELECTION REQUIRED",
            "ship_to": "SELECTION REQUIRED",
            "receiving_owner": "SELECTION REQUIRED",
            "approver_name": "SELECTION REQUIRED",
            "approver_signature_date": "NOT EXECUTED",
            "purchase_order_or_receipt": "NOT EXECUTED",
            "permitted_action": "NOT AUTHORIZED",
            "warning": WARNING,
        }
    )


write_csv(OUT / "line-register.csv", lines)
write_csv(OUT / "lot-register.csv", lots)
write_csv(OUT / "source-register.csv", sources)
write_csv(OUT / "purchase-decision-register.csv", decisions)
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
            "dated_cart_or_quote_uri": "NOT EXECUTED",
            "seller_stock_and_exact_mpn_check": "NOT EXECUTED",
            "ship_to": "SELECTION REQUIRED",
            "receiving_owner": "SELECTION REQUIRED",
            "program_owner_name": "SELECTION REQUIRED",
            "program_owner_signature": "NOT EXECUTED",
            "approval_date": "NOT EXECUTED",
            "permitted_action": "NOT AUTHORIZED",
            "purchase_order_or_receipt": "NOT EXECUTED",
            "decision": "NOT AUTHORIZED",
            "warning": WARNING,
        }
    ],
)

fit_subtotal = Decimal(lots[0]["snapshot_subtotal_usd"])
ptcb_subtotal = Decimal(lots[1]["snapshot_subtotal_usd"])
total = fit_subtotal + ptcb_subtotal
if fit_subtotal != Decimal("211.30") or ptcb_subtotal != Decimal("22.83") or total != Decimal("234.13"):
    raise AssertionError("R187 snapshot arithmetic changed")

status = {
    "revision": REVISION,
    "round": "R187",
    "date": DATE,
    "source_receiving_package": "HR-V0-Q4X-INSTALL-EVIDENCE-P0.1",
    "line_count": len(lines),
    "lot_count": len(lots),
    "evaluation_unit_count": sum(int(row["evaluation_quantity"]) for row in lines),
    "purchase_unit_count": sum(int(row["seller_purchase_quantity"]) for row in lines),
    "excess_quarantined_spare_count": 3,
    "fit_lot_snapshot_subtotal_usd": "211.30",
    "ptcb_lot_snapshot_subtotal_usd": "22.83",
    "combined_snapshot_subtotal_usd": "234.13",
    "shipping_sales_tax_fees_included": False,
    "current_cart_executed": False,
    "purchase_authorized": False,
    "order_placed": False,
    "physical_evidence_received": False,
    "fabrication_authorized": False,
    "drilling_authorized": False,
    "connection_authorized": False,
    "powered_test_authorized": False,
    "motion_authorized": False,
    "energization_authorized": False,
    "sol_r12_blockers_closed": 0,
    "warning": WARNING,
}
OUT.mkdir(parents=True, exist_ok=True)
(OUT / "package-status.json").write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8", newline="\n")

source_rows = "".join(
    f"<tr><td>{row['source_id']}</td><td>{html.escape(row['seller'])}</td><td>{html.escape(row['line_ids'])}</td><td><a href='{html.escape(row['url'])}' rel='noreferrer'>Open seller record</a></td><td>{html.escape(row['access_record'])}</td><td>{html.escape(row['boundary'])}</td></tr>"
    for row in sources
)
line_rows = "".join(
    f"<tr data-lot='{row['lot_id']}'><td>{row['line_id']}</td><td>{row['lot_id']}</td><td>{html.escape(row['manufacturer_part_number'])}</td><td>{row['evaluation_quantity']}</td><td>{row['seller_purchase_quantity']}</td><td>{html.escape(row['seller'])}</td><td>${row['unit_price_snapshot_usd']}</td><td>${row['extended_snapshot_usd']}</td><td>{html.escape(row['availability_snapshot'])}</td><td>{row['authorization_state']}</td></tr>"
    for row in lines
)
lot_cards = "".join(
    f"<article class='card'><p class='tag'>{row['lot_id']}</p><h3>{html.escape(row['purpose'])}</h3><p><strong>{row['line_count']}</strong> lines / <strong>{row['purchase_unit_count']}</strong> seller units</p><p class='price'>${row['snapshot_subtotal_usd']}</p><p>{html.escape(row['evidence_boundary'])}</p><span class='hold'>{row['decision_state']}</span></article>"
    for row in lots
)

page = f"""<!doctype html><html lang='en'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'><title>HR-V0 Q4X unpowered acquisition</title><style>:root{{--sky:#74c9f4;--navy:#072b50;--blue:#145f99;--gold:#f4b928;--paper:#f7fbff;--hold:#fff1b8}}*{{box-sizing:border-box}}body{{margin:0;color:var(--navy);font:16px/1.55 Arial,sans-serif;background:white}}header{{padding:clamp(1.5rem,5vw,4rem);background:linear-gradient(135deg,var(--sky),#eaf8ff);border-bottom:8px solid var(--gold)}}h1{{font-size:clamp(2.2rem,6vw,5rem);line-height:1.02;margin:.25rem 0 1rem;max-width:16ch}}h2{{font-size:clamp(1.65rem,3vw,2.6rem);line-height:1.15}}h3{{font-size:clamp(1.25rem,2vw,1.6rem);line-height:1.2}}main{{max-width:1480px;margin:auto;padding:2rem clamp(1rem,4vw,3.5rem)}}.warning{{padding:1rem;border:3px solid #a76e00;background:var(--hold);border-radius:.8rem;font-weight:700;font-size:clamp(16px,1.4vw,20px)}}.summary{{font-size:clamp(18px,2vw,26px);max-width:70ch}}.metrics,.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,250px),1fr));gap:1rem;margin:1.5rem 0}}.metric,.card{{border:3px solid var(--blue);border-radius:1rem;padding:1.15rem;background:var(--paper)}}.metric strong,.price{{display:block;font-size:clamp(1.8rem,4vw,3rem);font-weight:800}}.tag,.hold{{font-size:14px;font-weight:800;letter-spacing:.04em}}.hold{{display:inline-block;background:var(--gold);padding:.35rem .6rem;border-radius:.35rem}}nav{{display:flex;gap:.5rem;flex-wrap:wrap;margin:2rem 0}}button{{font:700 16px/1.2 Arial,sans-serif;border:3px solid var(--blue);border-radius:.55rem;background:white;color:var(--navy);padding:.75rem 1rem}}button[aria-selected='true']{{background:var(--gold)}}section[hidden]{{display:none}}.table-wrap{{overflow:auto;border:2px solid #9cb9cc;border-radius:.7rem}}table{{border-collapse:collapse;width:100%;min-width:1150px}}th,td{{padding:.8rem;text-align:left;vertical-align:top;border-bottom:1px solid #b7cbd8}}th{{background:var(--navy);color:white;position:sticky;top:0}}a{{color:#074f8c;font-weight:700}}.boundary{{border-left:8px solid var(--gold);padding-left:1rem;margin:2rem 0}}.steps li{{margin:.75rem 0}}@media(max-width:600px){{main{{padding:1rem}}header{{padding:1.25rem}}table{{min-width:1000px}}}}</style></head><body><header><p class='tag'>{REVISION} / R187 / {DATE}</p><h1>Buy evidence, not a robot</h1><div class='warning'>{WARNING}. Every line is still NOT AUTHORIZED, NOT ORDERED and NOT RECEIVED.</div></header><main><p class='summary'>This packet turns the R186 ten-line receiving list into two small human decisions. The known seller-page subtotal is <strong>$234.13</strong> before shipping, sales tax, fees and price movement. It buys only articles for quarantine, identity checks and unpowered fit/metrology.</p><div class='metrics'><div class='metric'><strong>10</strong>exact lines</div><div class='metric'><strong>2</strong>decision lots</div><div class='metric'><strong>18</strong>needed evidence articles</div><div class='metric'><strong>0</strong>work authorizations</div></div><nav role='tablist' aria-label='Acquisition views'><button role='tab' aria-selected='true' data-tab='overview'>Overview</button><button role='tab' aria-selected='false' data-tab='lines'>Exact lines</button><button role='tab' aria-selected='false' data-tab='sources'>Seller evidence</button><button role='tab' aria-selected='false' data-tab='decision'>Human decision</button></nav><section data-panel='overview'>{lot_cards}<div class='boundary'><h2>Why two lots?</h2><p><strong>LOT-Q4X-FIT</strong> can collect the enclosure, panel, rail, gland, locknut and terminal geometry for $211.30 in page-price snapshots. <strong>LOT-Q4X-PTCB</strong> isolates the exact protection-device article because its current direct availability still needs a live cart check. Deferring it leaves the PTCB physical-fit evidence open.</p></div></section><section data-panel='lines' hidden><h2>Exact controlled lines</h2><div class='table-wrap'><table><thead><tr><th>Line</th><th>Lot</th><th>Exact MPN</th><th>Needed</th><th>Buy qty</th><th>Seller</th><th>Unit snapshot</th><th>Extended</th><th>Availability snapshot</th><th>Authority</th></tr></thead><tbody>{line_rows}</tbody></table></div><p>Five exact 53119000 locknuts are priced because the seller page exposes its first price break at five; only two are evidence articles and three remain quarantined spares. Manufacturer bag size 100 is not treated as the seller minimum.</p></section><section data-panel='sources' hidden><h2>Commercial evidence only</h2><p>These direct seller records control only the dated commercial snapshot. Manufacturer records in R184-R186 remain authoritative for technical identity, dimensions, ratings and installation evidence.</p><div class='table-wrap'><table><thead><tr><th>Source</th><th>Seller</th><th>Lines</th><th>Record</th><th>Access</th><th>Boundary</th></tr></thead><tbody>{source_rows}</tbody></table></div></section><section data-panel='decision' hidden><h2>Required human decision</h2><ol class='steps'><li>Choose exact lot and line IDs.</li><li>Attach a same-session cart or written quote that confirms exact MPNs, seller identities, quantities, current stock/lead time, shipping and tax.</li><li>Set a maximum total spend, Boston ship-to address and receiving owner.</li><li>Sign the authorization template. Until then, purchase authority remains zero.</li><li>If authorized, receive into quarantine and execute only the separately signed R186 unpowered metrology scope.</li></ol><div class='boundary'><h2>What approval still would not mean</h2><p>Buying these articles would not authorize substitution, drilling, cutting, wiring, installation, connection, powered testing, motion, child access or energization. It would close no Sol R12 blocker by itself.</p></div></section></main><script>const tabs=[...document.querySelectorAll('[data-tab]')],panels=[...document.querySelectorAll('[data-panel]')];tabs.forEach(t=>t.addEventListener('click',()=>{{tabs.forEach(x=>x.setAttribute('aria-selected',String(x===t)));panels.forEach(p=>p.hidden=p.dataset.panel!==t.dataset.tab)}}));</script></body></html>"""
(OUT / "index.html").write_text(page, encoding="utf-8", newline="\n")

doc = f"""# HR-V0 Q4X unpowered acquisition decision P0.1

**{WARNING}**

Identifier: `{REVISION}`

Round: **R187**

Date: **{DATE}**

## Result

R187 converts the R186 ten-line receiving lot into two separately decidable, fail-closed acquisition lots. The dated seller-page snapshot totals are:

| Lot | Scope | Lines | Seller units | Snapshot subtotal |
|---|---|---:|---:|---:|
| `LOT-Q4X-FIT` | enclosure, panel, rail, glands, locknuts and terminal fit | 9 | 20 | $211.30 |
| `LOT-Q4X-PTCB` | exact `1464484` identity and physical fit | 1 | 1 | $22.83 |
| **Combined** |  | **10** | **21** | **$234.13** |

The total is not a budget or landed-cost claim. It excludes shipping, sales tax, tariff changes, fees and price movement. No cart was created. `QRL-002` is supported by an exact associated-product price but still needs a direct line/cart check. `QRL-006` is supported by a cached direct Mouser record; live browser access was denied, so availability is explicitly unverified.

## Pack-size correction

LAPP's manufacturer catalog lists bags of 100 for `53111000` and `53119000`, but that does not prove a seller minimum. Live TME US pages on {DATE} showed multiplicity 1 for both exact MPNs. The gland page showed a 1+ net price of $1.070 and 6,709 in stock; the locknut page showed its first price break at five units for $0.176 each and 4,552 in stock. R187 therefore proposes two glands and five locknuts, leaving three locknuts as quarantined spares. The pages state that net prices exclude sales tax and shipping.

## Decision boundary

Every line remains `NOT AUTHORIZED`, `NOT ORDERED` and `NOT RECEIVED`. A program owner may later sign exact lot/line IDs and a maximum spend only after a same-session cart or written quote confirms exact MPNs, seller identity, quantity, availability/lead time, shipping and tax. The signed decision must also name the Boston ship-to address and receiving owner.

If later authorized, the only permitted action is receipt, quarantine, identity inspection and the separately authorized R186 unpowered metrology procedure. Purchase approval would not authorize substitution, drilling, cutting, wiring, installation, connection, powered testing, motion, child access or energization.

## Sol R12 disposition

The supplied Sol analysis remains the existing R12 independent review: 18 BLOCKER, 30 MAJOR and 8 MINOR findings against the earlier baseline. It is not a new review round. R187 closes zero Sol blockers because no part has been received and no physical measurement has been executed. It creates a bounded route to begin obtaining physical evidence without buying the complete robot.

## Controlled outputs

- `procurement/hr-v0/q4x-unpowered-acquisition-p0.1/line-register.csv`
- `procurement/hr-v0/q4x-unpowered-acquisition-p0.1/lot-register.csv`
- `procurement/hr-v0/q4x-unpowered-acquisition-p0.1/source-register.csv`
- `procurement/hr-v0/q4x-unpowered-acquisition-p0.1/purchase-decision-register.csv`
- `procurement/hr-v0/q4x-unpowered-acquisition-p0.1/package-status.json`
- `procurement/hr-v0/q4x-unpowered-acquisition-p0.1/index.html`
- `tests/forms/hr-v0-q4x-unpowered-acquisition-authorization-template-p0.1.csv`
- `tools/generate_hr_v0_q4x_unpowered_acquisition_p01.py`
- `tools/check_hr_v0_q4x_unpowered_acquisition_p01.py`

This package closes no engineering release, fabrication or energization gate.
"""
DOC.write_text(doc, encoding="utf-8", newline="\n")

print(f"{REVISION}: 10 lines / 2 lots / $234.13 snapshot subtotal / 0 authorized")
print(WARNING)
