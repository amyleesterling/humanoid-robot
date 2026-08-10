# HR-V0 Q4X unpowered acquisition decision P0.1

**PRELIMINARY - UNPOWERED ACQUISITION DECISION ONLY - NOT APPROVED FOR PROCUREMENT, FABRICATION, DRILLING, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION**

Identifier: `HR-V0-Q4X-UNPOWERED-ACQ-P0.1`

Round: **R187**

Date: **2026-08-10**

## Result

R187 converts the R186 ten-line receiving lot into two separately decidable, fail-closed acquisition lots. The dated seller-page snapshot totals are:

| Lot | Scope | Lines | Seller units | Snapshot subtotal |
|---|---|---:|---:|---:|
| `LOT-Q4X-FIT` | enclosure, panel, rail, glands, locknuts and terminal fit | 9 | 20 | $211.30 |
| `LOT-Q4X-PTCB` | exact `1464484` identity and physical fit | 1 | 1 | $22.83 |
| **Combined** |  | **10** | **21** | **$234.13** |

The total is not a budget or landed-cost claim. It excludes shipping, sales tax, tariff changes, fees and price movement. No cart was created. `QRL-002` is supported by an exact associated-product price but still needs a direct line/cart check. `QRL-006` is supported by a cached direct Mouser record; live browser access was denied, so availability is explicitly unverified.

## Pack-size correction

LAPP's manufacturer catalog lists bags of 100 for `53111000` and `53119000`, but that does not prove a seller minimum. Live TME US pages on 2026-08-10 showed multiplicity 1 for both exact MPNs. The gland page showed a 1+ net price of $1.070 and 6,709 in stock; the locknut page showed its first price break at five units for $0.176 each and 4,552 in stock. R187 therefore proposes two glands and five locknuts, leaving three locknuts as quarantined spares. The pages state that net prices exclude sales tax and shipping.

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
