# R151 validation record - DXL-STAR-P0.1 manufacturing evidence

**PRELIMINARY - NOT APPROVED FOR SUPPLIER UPLOAD, QUOTATION, FABRICATION, ASSEMBLY, CONNECTION, MOTION, OR ENERGIZATION**

Date: 2026-08-09

Product: `HR-V0-DXL-STAR-MFG-P0.1`

## Configuration result

- Native DXL-STAR-P0.1 board/project, source BOM and connector schedule are SHA-256 bound without duplicating source files in the release package.
- KiCad 10.0.5 generated ten Gerber/job and five drill/map/report files, IPC-D-356, raw position, board statistics and native DRC records.
- Native DRC is zero within modeled scope.
- All seven populated connector centers/rotations reconcile exactly to native board data; maximum position and rotation error are zero.
- All eighteen connector-schedule terminals reconcile to native pads; JC1.2 is explicit `NO_NET_NO_COPPER`.
- Four NPTH mounting-hole records are present.
- `BOM-051` is an exact candidate hold tied to the package. System counts are 40 exact holds and 20 selection-required groups.
- Eighteen manufacturing/release holds and eleven manufacturing selections remain open.
- No upload archive exists. Supplier, quotation, fabrication, assembly, physical, connection, motion, energization and safety-credit authorizations remain false.
- `EG-003`, `EG-004` and `EG-015` remain partial; no gate closes.

## Visual QA and automated regression

- The interactive guide was served locally and inspected in the in-app browser at a 1280 × 720 viewport. The preliminary warning, 7/18/10/0 cards, board-encoding boundary, controlled-output table, all eighteen holds and three artifact links are present and legible. The page has no body-level horizontal overflow at the inspected width; the table is contained in an `overflow:auto` wrapper.
- Computed minimum functional text is 14 px, body text is at least 16 px, and responsive source uses `clamp()`, auto-fit cards and horizontal table containment. Narrow layout behavior was source-inspected; it is not claimed as a physical mobile-device test.
- Ninety-eight standard engineering checkers passed in the controlled CAD environment.
- Seven native KiCad checkers passed under KiCad 10.0.5 Python, including both DXL-star source and manufacturing-package checkers.
- The release manifest was regenerated over 2,132 package files and passed its dedicated checker in the working candidate. The clean committed-state manifest recheck also passed before push. Total regression is 106 engineering checkers: 98 standard, seven native KiCad and one release-manifest checker.

## Disposition

R151 closes only the absence of current DXL-star manufacturing-review outputs and exact BOM binding. It does not prove manufacturability, harness/current suitability, electrical performance, physical correctness, functional safety or readiness for fabrication or energization.
