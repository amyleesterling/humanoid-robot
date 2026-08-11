# R213 validation record

**PRELIMINARY - NOT APPROVED FOR PROCUREMENT, QUOTATION, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION**

R213 issues `HR-V0-MECH-BOM-BIND-P0.2` and makes `HR-V0-ARM-ARCH-P0.8-DWG-CANDIDATE` the current held BOM-027 custom-part manufacturing identity for qualified review.

Repository checks prove five one-each custom parts, fifteen exact STEP/DXF/drawing identities, 26 drawing-explicit controls, 30 blank FAI operations, zero external bounding-box delta from P0.7 and twelve open holds. Four STEP solids encode nominal 11.30 mm x 2.90 mm, 90 degree countersinks; C05 is unchanged. P0.7 remains only the system placement/collision basis.

Completed checks against the synchronized staged package on 2026-08-10:

- P0.2 generator and dedicated checker: PASS;
- historical P0.1 checker under explicit P0.2 supersession handling: PASS;
- five parts, quantity five, fifteen source identities, 26 drawing controls, 30 blank FAI operations and twelve open holds: exact;
- P0.8-to-P0.7 external bounding-box delta: 0.0 mm for all five parts;
- standard non-`pcbnew` checker sweep: 153/153 PASS;
- native KiCad/`pcbnew` checker sweep under KiCad 10.0.5 Python: 18/18 PASS;
- supervisor tests: 67/67 PASS;
- watchdog reference-model and compiled-C differential tests: 11/11 PASS;
- fail-closed host-deployment tests: 16/16 PASS with `ready:false` and `motion_authority:NONE`;
- full energization-gate audit: 0 closed, 23 partial and 7 open; `--require-ready` returned the expected exit 2;
- E2 boundary audit: 0 closed and 21 partial; `--require-ready` returned the expected exit 2;
- desktop guide check at 1280 x 720: warning visible, five cards, five controlled links, 14 CSS px minimum functional text and no horizontal overflow;
- mobile guide check at 390 x 844: warning visible, five reflowed cards, 14 CSS px minimum functional text and no horizontal overflow; and
- synchronized release-manifest checker: PASS after the complete R213 package was staged.

None of these results is physical evidence. Independent/qualified drawing review, provider DFM, material/MTR, received fit, FAI, stop/structural proof, mass properties, configuration acceptance and all separate work authorizations remain open. All 30 full-program energization gates remain unresolved.
