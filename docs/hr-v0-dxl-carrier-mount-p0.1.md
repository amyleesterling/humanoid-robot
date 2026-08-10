# HR-V0 DXL carrier mounting interface P0.1

> **PRELIMINARY - NOT APPROVED FOR SUPPLIER UPLOAD, QUOTATION, PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, MOTION, OR ENERGIZATION**

Identifier: `HR-V0-DXL-CARRIER-MOUNT-IF-P0.1`

Round: R162

Date: 2026-08-09

## Result

R162 adds an exact but unreleased mounting-stack candidate for the three P0.3 current-limiter carriers:

- twelve Essentra `TNM3-6.5-10-1` M3 female/female insulating standoffs, nominally 10 mm long, 6.5 mm diameter and 6 mm internal thread depth;
- twelve PCB-side and twelve panel-side Essentra `0120070000VR` nylon M3 x 0.5 x 6 mm pan-head screws, with 5.9 mm nominal head diameter and 1.8 mm nominal head height; and
- twelve backplate hole centers whose diameters, tolerances, deburr, coating and drilling authority remain `SELECTION REQUIRED`.

The native carrier source records a 1.6 mm candidate PCB thickness, 100 x 60 mm outline and four 3.2 mm NPTH mounting datums. The Hammond 18P2721 drawing records a 533.4 x 685.8 mm panel, 2.54 mm nominal panel thickness and 19.05 mm formed flange. With those nominal values, the board-side screw engagement is 4.4 mm, the panel-side engagement is 3.46 mm and both retain positive nominal bottom-out reserve inside a 6 mm thread depth. These are arithmetic screens, not tolerance, torque or load proofs.

## Placement correction

The R161 LIM1 placement was flush with the left edge of the P0.6 BP-026 reserve. R162 supersedes those no-drill placement coordinates for physical-fit evaluation and re-centers the two-row layout:

| Carrier | Lower-left x | Lower-left y |
|---|---:|---:|
| LIM1 | 64.0 mm | 539.6 mm |
| LIM2 | 174.0 mm | 539.6 mm |
| LIM3 | 64.0 mm | 609.6 mm |

The new analytical margins are 10 mm at the left, 10 mm between adjacent board envelopes, 6.2 mm at the top and bottom, and 103.8 mm to the right of LIM2. Connector housings, conductor bends, strain relief, service tools, components and cover depth are not contained by the bare-board rectangles. The six R161 route lower-bound screens are therefore stale and must be recomputed after received-part fit; no cut length was released by R161 or R162.

## No-drill closure route

The package includes ten blank metrology rows requiring received panel/enclosure, board, standoff and screw identification and measurement; a center-only overlay fit using nonconductive envelopes; exact connector/wire sweeps; empty-enclosure closure; and a discrepancy reconciliation. It explicitly prohibits a center punch, drill, adhesive, wiring and power during that screen.

Fourteen selections and twelve acceptance rows remain open. These include hole process, positional tolerance, torque, locking/reuse, pull/shear/creep/vibration loads, nylon fire/temperature suitability, populated-board height, connector/contact/conductor geometry, cover/rear clearance, touch/contamination control, route recomputation and qualified review.

## Primary-source record

- Hammond 18P2721 product page: <https://www.hammfg.com/part/18P2721>, live page accessed 2026-08-09.
- Hammond 18P2721 drawing: <https://www.hammfg.com/files/parts/pdf/18P2721.pdf>, drawing dated 2020-02-07.
- Essentra `TNM3-6.5-10-1`: <https://www.essentracomponents.com/en-us/p/pcb-standoffs-round-metric-threaded-insulator-nylon-brass/tnm3-6-5-10-1>, no revision printed; accessed 2026-08-09.
- Essentra `0120070000VR`: <https://www.essentracomponents.com/en-gb/p/machine-screws-pan/0120070000vr>, no revision printed; accessed 2026-08-09.
- JST VH series `eVH`: <https://www.jst-mfg.com/product/pdf/eng/eVH.pdf>, no revision/date printed in the controlled record; accessed 2026-08-09.

[Interactive mounting and metrology guide](../release/hr-v0/dxl-carrier-mount-p0.1/index.html)

No part has been ordered or received. No panel or board has been marked, drilled, assembled, connected or energized. No qualified reviewer has accepted the stack or enclosure application.
