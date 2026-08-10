# R123 independent review request

**Package:** `HR-V0-PANEL-RD-P0.1` / synchronized `HR-V0-CP-P0.6`

**Status:** **PRELIMINARY - NOT APPROVED FOR FABRICATION OR ENERGIZATION**

Please review R123 for engineering accuracy and completeness. Do not treat the package as shop authorization or energization approval.

## Questions

1. Verify the controlled Phoenix Contact facts for items `1207648`, `3240189` and `3022218` against current official records, including dimensions, material/construction, rail compatibility and published minimum rail-length rule. Identify unsupported inferences.
2. Reproduce the original defect: one 500 mm rail cannot cover 642.6 mm of planning segments, and 65/100 mm segments conflict with the greater-than-100-mm minimum stated for the former perforated candidate.
3. Recalculate every stock allocation and reserve before kerf. Confirm that all four `1207648` planning segments exceed its greater-than-20-mm unperforated minimum.
4. Review whether using unperforated rail creates any missing drilling, bonding, coating, corrosion, fastening, load or code inputs beyond the twelve explicit holds.
5. Verify that allocating six `3022218` brackets only to DR1/DR2/DR3 is supportable as a candidate and that DR4 remains unresolved. Challenge the 90.5 mm case / 100 mm rail / 19 mm two-bracket screen.
6. Check that application quantity is clearly separated from manufacturer pack/order quantity and that no order, distributor route or overbuy is implied.
7. Audit `BOM-059`, `BOM-083` through `BOM-085`, `PAN-006/008/009`, `BP-004/014/017/021`, `TS-007`, cut plan, holds, forms, gate evidence, metadata, checker and interactive guide for consistency.
8. Inspect desktop/mobile rendering for body overflow, technical-scroller containment, correct filter behavior and no text below 12 CSS px.

## Return format

- BLOCKER / MAJOR / MINOR with exact artifact and row/identifier.
- Corrected arithmetic or manufacturer fact with primary-source link.
- Missing maker-space, fabrication, fastening, bonding, mechanical-proof or qualification inputs.
- A clear statement whether this package is ready for qualified panel-layout/fabrication-process review. Do not mark it ready to purchase, cut, drill, assemble, connect or energize.

**PRELIMINARY - NOT APPROVED FOR FABRICATION OR ENERGIZATION**
