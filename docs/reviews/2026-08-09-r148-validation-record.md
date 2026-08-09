# R148 validation record - mechanical BOM binding

**PRELIMINARY - NOT APPROVED FOR QUOTATION, FABRICATION, ASSEMBLY, MOTION, OR ENERGIZATION**

Date: 2026-08-09

Product: `HR-V0-MECH-BOM-BIND-P0.1`

## Configuration result

- `BOM-027` binds one each `MV0-C01/C04/C05/C06/C07`, total candidate quantity five.
- The binding points to fifteen existing SHA-256-controlled STEP/DXF/SVG identities from `HR-V0-MECH-DFM-DATA-P0.1`.
- The stale current P0.5 three-C01 description is removed from the live BOM and current BOM closure guidance.
- Closure state advances to `exact_candidate_hold`; supplier/process/application state remains held.
- All fifteen inherited DFM holds remain open and every external-action authorization remains false.

## Visual QA and automated regression

- The interactive guide was served locally and inspected in the in-app browser at the available desktop viewport.
- The preliminary warning is fully visible without clipping; all five part cards are legible; the five-row STEP table is isolated in a horizontal-scroll container; and the DOM snapshot contains the complete binding, all `FALSE` upload states and both artifact links.
- The stylesheet uses 16-pixel-or-larger body text, 14-pixel code text, `clamp()` heading/body sizing, an auto-fit card grid and a contained table. Narrow-screen behavior was source-inspected but is not claimed as a separate physical mobile-device test.
- Ninety-seven standard engineering checkers passed in the controlled CadQuery environment.
- Five native KiCad checkers passed under KiCad 10.0.5 Python.
- The release manifest was regenerated over 2,050 package files and passed its dedicated checker. Total regression: 103 engineering checkers passed (97 standard, five native KiCad and one release-manifest checker).

## Disposition

The correction closes a configuration-identity mismatch only. It does not demonstrate strength, machinability, tolerance capability, fit, stopping behavior, physical acceptance, or safety. No provider contact, upload, quotation, purchase, first article, fabrication, assembly, motion, or energization is authorized.
