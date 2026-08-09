# R158 validation record

> **PRELIMINARY - NOT APPROVED FOR SUPPLIER UPLOAD, QUOTATION, PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, MOTION, OR ENERGIZATION**

- Configuration: `HR-V0-DXL-PROT-CARRIER-P0.2`
- Date: 2026-08-09
- Primary basis: TI TPS25946 datasheet `SLVSGA8B`, revision B, April 2022; package drawing `4225183/A`, 08/2019

## Defect found and disposition

The R156 P0.1 custom RPW footprint was not drawing-faithful. It encoded 0.475 mm side spacing instead of 0.45 mm pitch, 1.80 mm rather than 2.40 mm central copper, undersized/misplaced corner L geometry and full-copper paste instead of TI's reduced stencil example. P0.1 is preserved as historical evidence and explicitly prohibited for supplier use.

P0.2 is a separate review candidate. It does not silently rewrite the R156 release package or change the robot baseline.

## Executed repository checks

- Official source hash recorded: `AC74BA4AE2470ECD4E8657B2E964DEC5CE0643A8D4466476BA3486E980CED490`.
- KiCad 10.0.5: five native sheets parsed; ERC 0 errors / 0 warnings.
- KiCad 10.0.5: DRC 0 violations / 0 unconnected pads / 0 footprint errors within modeled rules.
- Native geometry checker: exact 14 copper/mask plus 16 paste-only primitives passed.
- Comparison register: 10 checks, eight explicit P0.1 failures corrected in P0.2.
- Complete non-`pcbnew` repository sweep: 104/104 checkers passed.
- Native KiCad/PCB checker sweep: 9/9 passed under the KiCad 10.0 Python runtime.
- Staged release manifest: 2,381 controlled package files passed before commit.
- Interactive guide: desktop DOM/visual QA passed; warning, headings, source links, board renders and the corrected schematic asset resolve. Body text is 18 px, metadata 14 px, the mobile rule preserves a 16 px body floor, and no image asset is broken.
- Release flags: fabrication, assembly, connection, energization and functional-safety credit all false.
- Physical tests: 0. Qualified approvals: 0. Work authorizations: 0.

## What remains unverified

Independent land-pattern parity, fabricator/assembler/stencil DFM, solder-mask and paste tolerances, first-article AOI/X-ray, electrical/thermal performance and every physical system hold remain unexecuted. A clean ERC/DRC is not a release decision.
