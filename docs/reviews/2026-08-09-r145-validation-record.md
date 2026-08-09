# R145 validation record - complete Evaluation Batch A acquisition P0.1

**PRELIMINARY - NOT APPROVED FOR FABRICATION, CONNECTION, MOTION, OR ENERGIZATION**

Date: 2026-08-09

Product: `HR-V0-EVAL-BATCH-A-ACQ-P0.1`

## Data validation

- Exact parity passed for all 17 source evaluation lines, including parent item, manufacturer, order code, quantity, official source and receiving route.
- The four lots cover exactly 17 lines and 21 physical units without duplication or omission.
- Current official manufacturer-page snapshots produce a $1,864.73 known-price floor.
- Eight lines remain `QUOTE REQUIRED`; shipping, tax, fees and allocation remain excluded.
- Fifteen unique official product records are controlled with a 2026-08-09 access record.
- All 17 lines, four lots and the authorization template remain fail-closed: zero authorized, zero ordered and zero received.

## Visual and interaction QA

The generated web guide was inspected at the normal 1265-pixel desktop viewport and at 390 x 844 mobile. Body text is 16 CSS pixels, labels/badges are 14 pixels, the warning is visible, desktop has no page-level horizontal overflow, mobile copy wraps without clipping, and the wide line table scrolls only inside its controlled container.

## Repository regression

- All 94 standard Python engineering checkers passed after regenerating the build traveler's controlled source hash for the updated release-candidate record.
- All five native KiCad/Python checkers passed using the installed KiCad 10.0.5 runtime.
- The release manifest was regenerated and its separate checker passed over 2,015 controlled package files. Together, 100 engineering checkers passed: 94 standard Python checks, five native KiCad/Python checks and the release-manifest check.
- Regression exposed an inherited R144 hash cycle: the build-traveler source register hashed the release manifest while the manifest hashed that source register. R145 retains the manifest as a controlled traveler input but replaces that impossible inner hash with the exact machine-checked `SELF-REFERENTIAL-MANIFEST-HASH-OMITTED` marker. Manifest integrity remains independently enforced by the release-manifest checker.
- No checker result closes a physical release gate or supplies missing received, measured, inspected or qualified-review evidence.

## Disposition

The packet is internally consistent as a purchase-decision candidate. It does not establish total landed cost, allocated stock, seller/ship-to/payment authority, application selection, received identity or physical evidence. No release gate closes.
