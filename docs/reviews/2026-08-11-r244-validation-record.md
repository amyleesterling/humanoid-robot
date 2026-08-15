# R244 validation record

> **PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION**

Date: 2026-08-11

Configuration: `HR-V0-P121-DCR-DROP-P0.1` / `HR-V0-CONFIG-REC-P0.8`

Electrical candidate: P1.21 unaccepted; P1.15 remains current

## Source and calculation validation

- The current exact-product Alpha Wire 3057 page publishes nominal conductor DCR of 4.4 ohm/1000 ft at 20 C for engineering purposes. The current Belden consolidated record revision 0.120 dated 2026-06-30 separately confirms the held `3057 BL005` blue 100 ft variant and construction.
- The generator and independent checker reproduce `4.4 / 304.8 = 0.014435695538 ohm/m`.
- Seven route coefficients reproduce a 6.72325 m centerline sum and 0.097054790 ohm conditional nominal sum. Four path point estimates reproduce independently; C-05 remains uncalculated.
- Every numeric row is labeled one-way, centerline, 20 C and conductor-only. None is presented as an installed resistance bound or accepted circuit voltage drop.
- Current Pilz and Phoenix primary documents do not explicitly close exact driver-bit compatibility. Both bit selections remain open; Phoenix `1212568` is only the strongest held candidate for written confirmation and received fit/access evaluation.

## Machine validation

- R244 package checker: PASS; seven route coefficients, four numeric path screens, one uncalculated path, twelve open holds and both exact-bit selections open.
- Standard non-`pcbnew` repository checker sweep: **187/187 PASS**.
- Native KiCad/`pcbnew` checker sweep under KiCad 10.0.5: **18/18 PASS**; R244 does not modify native ECAD.
- Release manifest: regenerated against the synchronized staged tree and verified after staging; **5,102 package files** expected in the final R244 manifest including this record.
- These checks do not provide received-material, actual-cut, complete-circuit, protection, thermal, functional-safety or work-authorization evidence.

## Browser validation

- The local interactive guide was inspected at 1280 x 720 and 390 x 844.
- Both viewports had no page-level horizontal overflow: desktop body 1265/1265 px and mobile body 375/375 px client/scroll width.
- The smallest visible text was 14 CSS pixels, limited to short metadata/badge content; body and functional content remained at least 16 CSS pixels.
- At mobile width, both 1050 px tables remained inside their own 343 px horizontally scrollable containers with `overflow-x: auto`; the page itself did not widen.
- The warning remained visible at both widths. The mobile viewport screenshot showed readable reflow with no clipped card or warning text. Browser console inspection returned zero warnings or errors.

## Result boundary

R244 partially addresses but does not close `R242-H03` or the R243 exact-bit holds. Twelve R244 holds remain. P1.15 remains current; P1.21/R244 remain unaccepted. No procurement, fabrication, assembly, wiring, connection, powered testing, motion, functional-safety credit or energization is authorized.
