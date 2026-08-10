# R121 validation record

> **PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TEST, OR ENERGIZATION.**

Date: 2026-08-08

Configuration: `HR-V0-CP-P0.6` / `HR-V0-COMPUTE-INSTALL-P0.1` / Electrical `V3-P1.14`

## Automated validation

- R121 compute-installation checker: pass; 26 bounded planning envelopes, 33 panel-BOM rows, 15 thermal/space screens, 16 fail-closed holds and 20 unexecuted/not-authorized receiving rows.
- System BOM closure regeneration: 82 groups; 17 evaluation candidates; 32 exact-candidate holds; three grouped-component holds; 25 selection-required groups; four exclusions; one integrated item.
- Repository checker inventory: 74 checkers. All 73 non-manifest checkers passed in one controlled full pass using the CadQuery or KiCad interpreter assigned by checker class. The manifest checker is executed separately after final staging and manifest regeneration.
- Readiness command: `tools/check_energization_gates.py --through-stage E2 --require-ready` exited `2` as required; all 21 applicable E0-E2 gates remain `partial`, zero are closed.
- SVG parse/boundary checks: pass; all 26 rectangles lie inside the nominal 533.4 x 685.8 mm panel boundary.
- Responsive guide QA: desktop 1440 x 1100 and mobile 390 x 844 rendered with no body overflow; minimum computed text size 12 CSS px. The technical diagram uses an internal horizontal scroll region on narrow screens so annotation text is not shrunk to fit. The standalone SVG rendered at 1600 x 1100 with a 14 px minimum text size.

## Configuration result

P0.5 is superseded as the current physical-layout candidate because it had no honest simultaneous compute allocation and preserved reserve. P0.6 changes the enclosure/backplate and physical planning evidence only. It does not change KiCad topology, firmware, safety allocation or any authorized state.

`BOM-070` remains `SELECTION REQUIRED`. No received measurements, holes, cut lengths, fasteners, cable entries, USB cable, pull/vibration result, depth/closed-cover result, duct-fill result, grounding/EMC result or powered thermal result exists.

R121 closes no energization gate and does not change Sol R12's overall buildability or energization verdict.
