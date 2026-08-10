# R150 validation record - current PCB-P0.9 CAM review package

**PRELIMINARY - NOT APPROVED FOR SUPPLIER UPLOAD, QUOTATION, FABRICATION, ASSEMBLY, CONNECTION, MOTION, OR ENERGIZATION**

Date: 2026-08-09

Product: `HR-V0-WD-CAM-P0.1`

## Configuration result

- Current PCB-P0.9 and Electrical V3-P1.14 authoritative sources are hash-bound without duplicating them inside the CAM package.
- KiCad 10.0.5 generated ten Gerber/job and five drill/map/report files, IPC-D-356, raw position, board statistics and native DRC records.
- Native DRC is zero within modeled scope.
- All 42 populated references reconcile exactly between raw KiCad positions and P0.2 internal assembly placement; maximum position and rotation error are zero.
- The raw position file remains internal and is not machine-ready supplier XYRS.
- Eighteen manufacturing/release holds remain open; eleven manufacturing inputs remain `SELECTION REQUIRED`.
- No upload archive exists. All supplier, quotation, fabrication, assembly, physical, connection, motion, energization and safety-credit authorizations remain false.
- `EG-004` remains partial.

## Visual QA and automated regression

- The interactive guide was served locally and inspected in the in-app browser at the available desktop viewport. The preliminary warning, 42/10/5/0 cards, internal-parity boundary, controlled-package table, all eighteen holds and three artifact links are present and legible. The table is contained in a horizontal-scroll wrapper. Source inspection confirms 16-pixel-or-larger body text, 14-pixel code/helper text, responsive `clamp()` sizing and an auto-fit card grid; narrow behavior was source-inspected but is not claimed as a separate physical mobile-device test.
- Ninety-eight standard engineering checkers passed in the controlled project environment.
- Six native KiCad checkers passed under KiCad 10.0.5 Python, including the new current-CAM checker and native board DRC at zero within modeled scope.
- The release manifest was regenerated over 2,094 package files and passed its dedicated checker. Total regression: 105 engineering checkers passed (98 standard, six native KiCad and one release-manifest checker).

## Disposition

R150 closes only the absence of current-board CAM review outputs. It does not produce an accepted supplier packet or prove manufacturability, physical correctness, electrical performance, functional safety or readiness for fabrication or energization.
