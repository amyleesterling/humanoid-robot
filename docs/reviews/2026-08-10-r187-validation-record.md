# R187 validation record

> **PRELIMINARY - UNPOWERED ACQUISITION DECISION ONLY - NOT APPROVED FOR PROCUREMENT, FABRICATION, DRILLING, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION**

Artifact: `HR-V0-Q4X-UNPOWERED-ACQ-P0.1`

Date: 2026-08-10

## Commercial-source verification

- Direct DigiKey pages were rechecked for exact `PJ1084T`, `1207650`, `3209578`, `3209510`, `3030417` and `3022218` commercial records. The exact `14F0907` price is an associated-product snapshot, so a direct line/cart check remains mandatory.
- Live TME US pages were inspected in-browser. Exact LAPP `53111000` showed 6,709 in TME stock, multiplicity 1 and a 1+ net price of $1.070. Exact `53119000` showed 4,552 in TME stock, multiplicity 1 and its first displayed price break at five units for $0.176 each. Both pages state manufacturer bag size 100 and that net prices exclude sales tax and shipping.
- The direct Mouser record supports exact `1464484` and a one-unit $22.83 snapshot, but live browser access was denied. Current availability remains unverified and held for a same-session direct cart or written quote.
- Commercial records have zero technical authority. R184-R186 manufacturer records remain authoritative for part identity, geometry, ratings and installation evidence.

## Package validation

- Generator completed.
- Dedicated fail-closed package checker passed.
- Ten R186 receiving-line identities and exact MPNs reconcile; eighteen needed evidence articles map to 21 seller units because three extra locknuts remain quarantined spares.
- Independent decimal arithmetic reproduced $211.30 for `LOT-Q4X-FIT`, $22.83 for `LOT-Q4X-PTCB` and $234.13 combined before shipping, sales tax, fees and price movement.
- Every cart, authorization, order, receiving and physical-work field remains negative or unexecuted.

## Web QA

- Desktop viewport: 1280 px inner width, 1265 px document/client width and no page overflow. Body and controls are 16 px, technical tags are 14 px, and the warning is 17.92 px.
- All four tabs activated the matching overview, exact-lines, seller-evidence and human-decision panels.
- True mobile viewport: 390 x 844 px, 390 px document/client width and no page overflow. Body and controls are 16 px, technical tags are 14 px, and the warning is 16 px.
- Desktop and mobile renders were visually inspected; the complete preliminary warning remains prominent and the table is contained in its own horizontal scroller.

## Repository regression

- Complete non-`pcbnew` sweep under the controlled CadQuery runtime: 131/131 passed.
- Native KiCad 10.0 `pcbnew` checker sweep: 13/13 passed.
- Combined controlled checker count: 144/144 passed.
- Release manifest: 3,194 package files; checker passed before final commit. The configuration gate remains partial until merge and formal acceptance.

## Authority boundary

This record proves internal consistency and a dated commercial snapshot only. It provides zero cart, procurement, drilling, fabrication, connection, powered-test, motion, energization, safety or qualified-review authority. It closes zero Sol R12 blockers.
