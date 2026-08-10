# R187 independent review request — Q4X unpowered acquisition

> **PRELIMINARY - UNPOWERED ACQUISITION DECISION ONLY - NOT APPROVED FOR PROCUREMENT, FABRICATION, DRILLING, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION**

Review the exact commit containing artifact `HR-V0-Q4X-UNPOWERED-ACQ-P0.1`.

## Reproduce

```text
python tools/generate_hr_v0_q4x_unpowered_acquisition_p01.py
python tools/check_hr_v0_q4x_unpowered_acquisition_p01.py
```

## Required challenge

1. Reconcile all ten `QRL-*` rows to the frozen R186 receiving lot. Confirm no manufacturer part number or needed evidence quantity changed.
2. Reopen every direct seller record. Confirm seller identity, exact MPN, order code, purchase quantity, price break, stock/lead-time state and seller multiplicity in a same-session cart or written quote. Do not use the dated snapshots as checkout authority.
3. Independently recalculate the $211.30 fit-lot, $22.83 PTCB-lot and $234.13 combined subtotals. Confirm shipping, sales tax, fees, tariff changes and price movement are excluded.
4. Confirm LAPP manufacturer bag size 100 is not misrepresented as the TME seller minimum. Challenge the five-locknut purchase quantity and three-spare quarantine rule.
5. Confirm `QRL-002` remains held for a direct line/cart check and `QRL-006` remains held for current direct availability because live browser access was denied.
6. Audit the signed-decision template for exact lot/line scope, maximum spend, seller/stock verification, Boston ship-to, receiving ownership and a permitted-action boundary limited to quarantine and unpowered metrology.
7. Confirm the HTML, CSVs, JSON, Markdown and R186 metrology package agree. State separately whether each lot is ready for a human acquisition decision, checkout, received-part metrology, drilling, fabrication, connection and energization.

Report BLOCKER / MAJOR / MINOR findings with exact file, row, source and correction. This review provides no purchase, work or functional-safety authority.
