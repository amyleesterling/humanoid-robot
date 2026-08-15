# R248 validation record

> **PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION**

R248 products: `HR-V0-MOVING-PROP-CLOSURE-P0.1` and `HR-V0-CONFIG-REC-P0.12`.

## Deterministic result

The dedicated checker proves exact coverage of all 17 current moving-mass ledger IDs, blank execution state, source/release parity, manifest integrity, package/configuration counts, warning propagation and open authorization boundaries. Synthetic tests independently exercise the two-support COM equation and the two-body calibrated-pendulum fit; an unexecuted record is rejected.

The physical templates retain zero results: 170 mass-repeat rows, 17 received-mass result rows, four assembly mass-closure rows, eight two-axis COM rows, four pendulum calibration rows, six inertia rows and seventeen uncertainty components are unexecuted. Twelve package holds and ten package acceptances remain open. Configuration P0.12 contains 32 current records, 50 open holds and 73 unexecuted acceptances.

## Executed results

- Python compile for generator, calculator and checker: **PASS**.
- Dedicated R248 checker: **PASS**.
- Blank-form calculator fail-closed check: **PASS**, exit code 78.
- Standard repository checker sweep: **191/191 PASS**.
- Native KiCad 10.0 checker sweep: **18/18 PASS**.
- Release-candidate manifest: **5,344 package files before adding this validation record; regenerated afterward**.
- Desktop browser QA at 1280 x 720:
  - moving-properties guide: exact warning visible, 16 px body text, 14 px minimum technical text, no page-level horizontal overflow, 14 tables, 14 download links and 285 body rows;
  - configuration P0.12 guide: exact warning visible, 16 px body text, 14 px minimum technical text, no page-level horizontal overflow, five tables, five download links and 185 body rows; and
  - both first-view screenshots were visually inspected; headings, warnings, status text and initial download controls were readable and nonoverlapping.
- Narrow/mobile browser execution: **NOT COMPLETED**. The pages use a 16 px body floor, 14 px table text and local table scrolling, but that static rule is not recorded as an executed mobile visual pass.

The first standard-suite attempt was unable to read the pre-existing CadQuery/OCP runtime in the Windows temporary directory under the restricted shell. The identical 191-check sweep passed when that runtime was made readable. This was an execution-environment access issue, not a repository failure.

## Boundary

These results establish source consistency, blank-template integrity, nominal formula implementation, configuration accounting and desktop legibility only. They do not establish instrument suitability, fixture accuracy, received mass, as-built COM, inertia, uncertainty, structural or torque sufficiency, stopping performance, functional safety, motion readiness or energization authority. Sol B-010 and R247-H11 remain open.
