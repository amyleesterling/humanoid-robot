# R146 validation record - Evaluation Batch A receiving campaign

**PRELIMINARY - NOT APPROVED FOR FABRICATION, CONNECTION, MOTION, OR ENERGIZATION**

Date: 2026-08-09

Product: `HR-V0-EVAL-BATCH-A-RCV-P0.1`

## Data validation

- Exact source/acquisition parity passed for all 17 lines.
- Quantity expansion produced 21 deterministic unit IDs without omission or duplication.
- The traveler contains exactly twelve records per unit: 252 unique records total.
- The evidence manifest contains exactly seven placeholders per unit: 147 unique records total.
- All 21 unit rows, 252 traveler rows, 147 evidence rows and 21 labels remain fail-closed and unexecuted.
- The generated execution form is an exact copy of the controlled traveler.
- Regression exposed an inherited historical-snapshot defect: the P0.1/P0.2 governance checkers compared their recorded source hashes to later live source files. R146 pins those historical checkers to their recorded path/hash identities; current P0.3 continues to validate the live gate source.

## Visual and interaction QA

The interactive guide was inspected in the in-app browser at a 1265-pixel content width. Body and warning text render at 16 CSS pixels; label helper text renders at 14 pixels. The page has no horizontal overflow, both wide tables use their own controlled scroll containers, and all 21 labels render. The LOT-C filter displayed exactly ten physical units and the `Pilz` search reduced the result to `EVA-005-U01` and `EVA-005-U02`. Source inspection confirmed responsive grids, wrapping, relative spacing and internal table scrolling without any user-facing text below 14 pixels.

## Disposition

All 95 standard Python engineering checkers passed, including the corrected historical P0.1/P0.2 and current P0.3 governance checks. All five native KiCad/Python checkers passed. After staging, the release manifest was regenerated and its separate checker passed over 2,028 controlled package files. In total, 101 engineering checkers passed.

The generated campaign is internally consistent as an unpowered receiving/evidence scaffold. It does not establish purchase authority, shipment, receipt, identity, condition, calibration, measurement, application suitability, qualified disposition, machine acceptance or any release-gate closure.
