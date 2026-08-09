# R157 validation record

> **PRELIMINARY - NOT APPROVED FOR SUPPLIER UPLOAD, QUOTATION, PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, MOTION, OR ENERGIZATION**

- Configuration: `HR-V0-BRANCH-FAULT-P0.1`
- Date: 2026-08-09
- Electrical source boundary: Electrical V3-P1.14

## Verified repository evidence

- The current V3 wire table was checked for `F0`, `F1`, `F2`, `F3`, `FSR1`, `FSR2`, `SD1`, `K1/K2`, `KP1/KP2`, `INJ1`, `U1`, `J1`, `J2`, `J3` and every named rail used by R157.
- The generated matrix contains exactly 24 cases, `BF-001` through `BF-024`, across four dependency stages.
- The synchronized execution form contains exactly 24 blank `NOT EXECUTED` records and no operator, authorization, result, raw-trace or reviewer claim.
- `EG-024` now has a concrete evidence location but deliberately remains `open`.
- The package explicitly prohibits a direct uncontrolled short across the robot source and robot-first fault testing.
- Recovery acceptance explicitly requires that clearing a fault, restoring a branch, releasing/resetting E-stop or rebooting ordinary control cannot itself command motion.

## Executed repository checks

- R157 package checker: PASS, 24/24 blank cases, four stages, EG-024 open and zero execution claims.
- Complete non-`pcbnew` repository sweep: 104/104 checkers passed using the controlled CAD environment.
- Native KiCad/PCB checker sweep: 8/8 passed under the KiCad 10.0 Python runtime.
- Staged release manifest: PASS for 2,305 package files after this record was added.
- `git diff --check`: PASS after generated trailing-whitespace correction.
- Desktop visual QA: PASS at the normal browser viewport; the warning, heading, summary and safe boundary are legible without zoom.
- Mobile visual QA: PASS at 390 x 844 px; text reflows without horizontal clipping and preserves the 16 px body / 14 px label floor.
- Interaction QA: PASS; the limited-energy filter displays exactly five cases.
- Tests executed on physical hardware: 0.
- Qualified approvals: 0.
- Work authorizations: 0.

Repository and UI checks establish only schema consistency, traceability and presentation. They do not establish protection coordination, fault energy, clearing performance, connector survival, source behavior, contactor DC application, grounding, stopping performance, functional safety or permission to perform physical work.
