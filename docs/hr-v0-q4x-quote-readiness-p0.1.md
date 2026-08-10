# HR-V0 Q4X quote-readiness amendment P0.1

> **PRELIMINARY - COMMERCIAL EVIDENCE AMENDMENT ONLY - NOT APPROVED FOR PROCUREMENT, FABRICATION, DRILLING, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION**

Identifier: `HR-V0-Q4X-QUOTE-READINESS-P0.1`

Round: **R188**

Date: **2026-08-10**

## Result

R188 replaces two ambiguous R187 commercial observations with direct DigiKey product-line evidence:

- `QRL-002` / Hammond `14F0907`: exact DigiKey order code `14F0907-ND`, one-unit snapshot **$29.80**, available to order, factory stock 60, and a four-week manufacturer standard lead time.
- `QRL-006` / Phoenix Contact `1464484`: exact DigiKey order code `277-1464484-ND`, one-unit snapshot **$22.83**, **zero stock**, an eight-week manufacturer standard lead time, and a tariff-may-apply notice.

Factory stock is not represented as DigiKey shelf stock. Manufacturer standard lead time is not represented as a promised delivery date. Commercial pages have zero engineering or safety authority.

## Corrected arithmetic

The direct `14F0907` price is $0.33 higher than the R187 associated-product snapshot. The corrected dated totals are:

| Lot | R187 | R188 delta | R188 snapshot |
|---|---:|---:|---:|
| `LOT-Q4X-FIT` | $211.30 | +$0.33 | **$211.63** |
| `LOT-Q4X-PTCB` | $22.83 | $0.00 | **$22.83** |
| Combined | $234.13 | +$0.33 | **$234.46** |

These figures exclude shipping, sales tax, tariff, fees and price movement.

## Decision boundary

The fit lot is ready only for creation of a same-session cart or written quote. It is not checkout-ready. The PTCB lot is not ready for immediate checkout because the observed direct listing has zero stock. Back-order acceptance, delivery timing, or an exact alternate seller route requires a human supply decision. No substitution is authorized.

No cart was created, no quote was requested or received, no purchase was authorized, and no order was placed. No physical evidence exists. Any later signed purchase may authorize only receipt, quarantine, identity inspection and separately authorized unpowered metrology. It cannot authorize drilling, cutting, wiring, connection, powered testing, motion, child access or energization.

R188 closes zero Sol R12 blockers. It closes one commercial direct-line ambiguity and converts one unknown-availability ambiguity into an explicit zero-stock supply hold.

## Controlled outputs

- `procurement/hr-v0/q4x-quote-readiness-p0.1/source-delta.csv`
- `procurement/hr-v0/q4x-quote-readiness-p0.1/line-disposition.csv`
- `procurement/hr-v0/q4x-quote-readiness-p0.1/cost-reconciliation.csv`
- `procurement/hr-v0/q4x-quote-readiness-p0.1/package-status.json`
- `procurement/hr-v0/q4x-quote-readiness-p0.1/index.html`
- `tools/generate_hr_v0_q4x_quote_readiness_p01.py`
- `tools/check_hr_v0_q4x_quote_readiness_p01.py`

This amendment provides no procurement, fabrication, connection, powered-test, motion, safety, or energization authority.
