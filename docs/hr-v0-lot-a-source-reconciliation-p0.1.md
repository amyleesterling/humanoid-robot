# HR-V0 Lot A source reconciliation P0.1

> **PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION**

Identifier: `HR-V0-LOT-A-SRC-P0.1`

Round: R237

Date: 2026-08-11

## Result

Lot A is the shortest current route to physical mechanical evidence: two `XM540-W270-T` actuators, two `FR13-H101K` hinge/idler kits and two `FR13-S102K` side-frame kits. Those six articles support the existing receipt, quarantine, loose-part metrology and later qualified joint-stack work needed to close `HSI-001..020` and design the missing J1/J2 hard stops.

The current official-page visible subtotal remains **$1,182.22**. That is not landed cost or a spending authorization. Shipping, Massachusetts tax or exemption, fees, allocation, price validity, ship-to, receiving owner and maximum spend remain open.

## Purchase blocker found

The current official ROBOTIS US page is internally inconsistent:

- the product title is `DYNAMIXEL XM540-W270-T`;
- SKU is `902-0137-000`;
- the page states `TTL`; but
- its package-content table names `XM540-W270-R`.

The project requires `-T` for the current TTL architecture. No title, SKU, image or package table is allowed to silently override the contradiction. Lot A is therefore purchase-blocked until ROBOTIS US provides written SKU-to-shipped-model-to-communication binding. Any received `-R` article must be quarantined rather than substituted.

The same pages expose no numeric stock value for the XM540 or H101. Blank is neither in-stock nor zero-stock evidence. The S102 page displayed stock 94 at access time, but that does not reserve two units.

## Controlled decision route

The package supplies:

- three unique item groups / six physical articles;
- thirteen exact source facts;
- four open anomalies, including one blocker;
- eight unsent supplier questions;
- ten open acquisition decision gates;
- twelve blank receiving/acceptance records; and
- a responsive interactive guide.

If a later human authorization closes every gate, its scope is limited to purchase, receipt, quarantine, inventory, photography and separately accepted unpowered loose-part metrology. It does not authorize thread engagement, temporary assembly, cable connection, power, encoder access, motion, fabrication or energization.

## Primary sources

- [ROBOTIS US XM540-W270-T product page](https://www.robotis.us/dynamixel-xm540-w270-t/), no revision shown, accessed 2026-08-11.
- [ROBOTIS US FR13-H101K product page](https://robotis.us/fr13-h101k-set/), no revision shown, accessed 2026-08-11.
- [ROBOTIS US FR13-S102K product page](https://www.robotis.us/fr13-s102k-set/), no revision shown, accessed 2026-08-11.
- [ROBOTIS XH540-W270 e-Manual](https://emanual.robotis.com/docs/en/dxl/x/xh540-w270/), live e-Manual, accessed 2026-08-11.

## Controlled artifacts

- `procurement/hr-v0/lot-a-source-reconciliation-p0.1/`
- `release/hr-v0/lot-a-source-reconciliation-p0.1/`
- `tools/generate_hr_v0_lot_a_source_reconciliation_p01.py`
- `tools/check_hr_v0_lot_a_source_reconciliation_p01.py`
- `requirements/hr-v0-gate-evidence-supplement-r237.csv`

This is purchasing evidence control, not permission to buy or use an article.
