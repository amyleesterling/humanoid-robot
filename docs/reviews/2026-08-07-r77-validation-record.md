# R77 validation record - guard impact-energy allocation input

**PRELIMINARY - NOT APPROVED FOR PANEL SELECTION, PROCUREMENT, FABRICATION, ASSEMBLY, MOTION, CONNECTION, OR ENERGIZATION.**

Date: 2026-08-07

Round: R77

Candidate: `HR-V0-GUARD-IMPACT-P0.1`

## Scope and correction

R77 supplies the missing impact-energy allocation input identified by R76 without pretending that one calculated number can rate the complete guard. It creates fifteen inputs, eleven energy cases, six direction rows, twelve fail-closed test controls, six dated sources and a responsive interactive guide.

Eight arithmetic/sensitivity results are deterministic. Three blocking energy classes remain `SELECTION REQUIRED`: detached hardware/tool impact, powered link bearing on a panel, and static access/push-out. The no-load endpoint screens remain incomplete and stall/no-load endpoints are never combined.

## Validation boundary

The calculated payload-only combined screen is 0.932757 J. The single-axis and deliberately conservative combined-axis mass-ceiling catalog-endpoint screens are 0.479663 J and 0.990987 J. The RAW 800 torque-line sensitivity is 0.090408 J per degree per XM540. None is an impact rating or proof-test release.

Repository, visual, manifest and clean-clone results are recorded against the final R77 commit. No physical or authorization gate is closed.

## Validation results

- The R77 generator/checker passed with fifteen inputs, eleven energy cases, six open direction rows, twelve non-closed controls and six dated sources.
- All 29 repository `tools/check_*.py` validators passed. The DXL-star and watchdog-PCB checks used KiCad 10.0 Python; the other engineering checks used the controlled CAD Python environment. The manifest checker was rerun after final staging.
- Traceability remained at 81 requirements, 40 risks and 104 procedures. The gate checker remained fail-closed at 0 closed, 22 partial and 8 open.
- The release manifest contains 838 package files, passed exact membership/hash validation and was reproduced from a clean clone after the final commit.

## Interactive-guide QA

The generated guide uses a 16 px body font and larger headings, warnings and numerical values. At the available 1280 x 720 desktop viewport, the document width was 1265 px, the eleven cases rendered in four 271 px columns, and the title/warning were readable without horizontal overflow. At an exact 390 x 844 mobile viewport, `innerWidth` was 390 px, document `scrollWidth` was 375 px, body text was 16 px, and both the case cards and five hazard-class controls reflowed to one 339 px column. The viewport was reset and the QA tabs/server were closed.

Passing these checks establishes arithmetic, source-trace and package consistency only. It does not establish containment, structural strength, functional safety, fabrication readiness or permission to energize.
