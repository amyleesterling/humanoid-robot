# HR-V0 X430 fixture support route P0.1

> **PRELIMINARY — SUPPORT/RFI CANDIDATE ONLY — NOT APPROVED FOR QUOTATION, PROCUREMENT, MACHINING, FLOOR WORK, ASSEMBLY, POWERED TEST, MOTION, OR ENERGIZATION.**

Identifier: `HR-V0-X430-FIXTURE-SUP-P0.1`

Parent interfaces: `HR-V0-X430-FIXTURE-P0.1`; `HR-V0-X430-FIXTURE-IF-P0.2`

Date: 2026-08-08

## Decision

Use an 80/20 `40200-SP-K` static pedestal configured at the published 300 mm height with a centrally modified `40006-BP` blank mounting plate as the preferred **vertical-axis support inquiry candidate**. It is not selected hardware.

80/20 publishes a 3,207 N load capacity and 2,040 N·m maximum torque for the static pedestal **when mounted to the floor**. The project takes no capacity credit until the manufacturer identifies the exact configuration, load direction, duty, mounting plate, anchor reactions, excluded conditions and required installation. The 2,040/16.5 = 123.636 ratio is a catalog comparison, not a safety factor.

## Why vertical first

Rotating the P0.2 sensor/X430 interface so its joint axis is vertical produces a direct top-of-pedestal torque path and avoids transferring a manufacturer floor-mounted rating into an invented horizontal frame. It is suitable only as a proposed route for sensor-chain development, low-speed torque work and controlled-duty development after all holds close.

Gravity force is parallel to the vertical joint axis, so ideal gravity torque about that axis is zero. The vertical configuration therefore cannot replace a later horizontal configured-joint test that reproduces gravity, bearing loads, cables and the final FR12 assembly. `horizontal_test_still_required` is locked `true` in the package status.

Weighted/mobile support is rejected for use of the floor-mounted torque claim. Bench or woodworking clamps are prohibited as the primary support.

## Modified plate candidate

The exact `40006-BP` catalog envelope is 203.2 × 203.2 × 19.05 mm, 6061-T6. `FX101-C01` is a review-only central-machining candidate:

- Ø52.0 mm top pocket, 2.50 mm deep;
- retained Ø18.98 ±0.02 mm pilot;
- four Ø4.50 mm clearances on basic BCD31.75; and
- four underside Ø9.0 mm counterbores, 6.70 mm deep.

The manufacturer's existing mounting holes are not modeled because controlled CAD/drawing evidence has not been obtained. The part STEP must not be used for machining.

Accu `SSC-8-32-5/8-A2` and `HRDW-M4-A2` are dimensional candidates only. Using the nominal modified-plate stack gives 4.613–5.675 mm provisional engagement. Plate thickness tolerance, FUTEK acceptance, screw grade, washer, torque, locking, fatigue and proof remain open.

## Floor and anchor boundary

No Boston installation location has been selected or surveyed. The repository does not know whether the substrate is reinforced slab, post-tensioned slab, lightweight concrete, wood framing, a library workbench or another construction. It also does not know embedded services, edge distances, drilling permission, jurisdiction, permissible dust/noise, anchor installation qualifications or proof requirements.

`SUP-RFI-003` requests manufacturer anchor reactions/instructions. `SUP-RFI-007` requests an exact facilities survey. A qualified facilities/structural reviewer must select and accept the anchors for the actual site. No generic anchor order code is inferred.

## Evidence and holds

The package contains four topology dispositions, six BOM rows, four nonauthorizing screens, eight unsent RFI questions, four primary-source records and ten open holds. Exact pedestal body/base/anchor CAD is deliberately absent; the GLB uses only a 300 mm height datum and floor-interface extent marker.

The current primary records were accessed 2026-08-08: [80/20 40200-SP-K](https://8020.net/40200-sp-k.html), [80/20 40006-BP](https://8020.net/40006-bp.html), [Accu SSC-8-32-5/8-A2](https://www.accu.co.uk/imperial-cap-head-screws/29027-SSC-8-32-5-8-A2), and FUTEK FI1251-F/EM1040. Manufacturer statements are evidence inputs, not project approval.

Ten holds block every next physical action: controlled pedestal/plate CAD; rating acceptance; existing plate interface; DFM/FAI; fasteners; site survey; anchor design/proof; guard/catch/load device; vertical-to-horizontal evidence; and qualified powered-work authorization.

All quotation, procurement, machining, floor-work, assembly, powered-test, motion, energization, safety-credit and build-release flags remain false.
