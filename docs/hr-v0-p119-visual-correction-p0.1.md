# HR-V0 P1.19 visual-correction dossier P0.1

> **PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION**

Identifier: `HR-V0-P119-VISUAL-CORRECTION-P0.1`
Round: R230
Date: 2026-08-11

## Outcome

The native P1.18 electrical package was not visually reviewable as released: all title blocks overflowed; sheets 01-03 clipped or collided labels; sheet 07 overlapped controller/driver content; sheet 09 allowed notes and the XT1 caption to exceed their intended regions; and sheet 10 overlapped the DXL-star and actuator-port label fields.

P1.19 is a new unaccepted layout-only candidate. P1.18 remains immutable. Five dense pages (01, 02, 03, 07 and 10) use A2; the other child pages remain A3. Title-block fields are bounded, the full preliminary warning remains a prominent native text item on every page, and exact values remain in the hidden KiCad `Value` fields/BOM where selected visible captions were shortened.

## Machine parity

- 84 component blocks unchanged.
- 106 native nets unchanged.
- 82 BOM rows, 340 connector/terminal rows, 106 net-schedule rows, 301 wire-table rows and 63 unresolved-selection rows are exactly equal between P1.18 and P1.19.
- Native KiCad netlist component/value/footprint and net-node membership are equal.
- KiCad 10.0.5 ERC: 0 errors / 0 warnings.

## Visual review

All thirteen native SVG exports were inspected at a 1680 x 1188 review viewport. The final P1.19 exports received thirteen project-owned visual passes. The browser surface supports sheet selection, side-by-side P1.18/P1.19 comparison, direct native SVG rendering and mobile reflow. This is not independent or qualified review.

## Configuration boundary

P1.15 remains the current electrical configuration. P1.18 and P1.19 are unaccepted supporting candidates. P1.19 cannot supersede P1.15 without independent and qualified electrical disposition plus formal configuration authority.

## Open holds

Seven holds remain in `release/hr-v0/p119-visual-correction-p0.1/open-holds.csv`: independent native-sheet review, qualified electrical review, functional-safety allocation/validation, physical panel/harness definition, unresolved selections, executed pre-power evidence and configuration promotion.

No procurement, fabrication, assembly, connection, powered test, motion or energization authority is created.
