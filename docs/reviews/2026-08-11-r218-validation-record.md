# R218 validation record

> **PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION.**

Identifier: `HR-V0-SRS-P0.2`

## Controlled checks

- Seven current configuration inputs are SHA-256 bound, including the controlled Pilz `21396-EN-23` PDF.
- Fifteen candidate requirements define scope, stop, restart, diagnostic, guard, qualified-allocation and authority boundaries.
- Seven timing records reproduce the 200.000 ms setup, 66.667 ms automatic, 44.000 ms component-screen and residual-allocation arithmetic.
- Sixteen validation scenarios remain `NOT EXECUTED`.
- Twelve common-cause records remain open with no accepted fault exclusion or safety credit.
- Both qualified-allocation rows retain PLr/SIL, architecture, reliability, DC, CCF, reviewer and signature fields as unresolved.
- All procurement, fabrication, assembly, connection, powered-test, motion and energization authority flags remain false.

## Validation state

- Dedicated package checker: PASS (15 requirements, seven timing rows, sixteen unexecuted scenarios, twelve open common-cause rows, two unresolved qualified-allocation rows and no authority).
- The first pre-stage sweep exposed three stale downstream checker expectations for the former functional-safety release-state string/list. Those checkers were updated to require `HR-V0-SRS-P0.2` and the new, still fail-closed state.
- Corrected pre-stage standard repository sweep: 159/160 PASS. The sole expected failure was the release-manifest checker rejecting the seventeen new, still-untracked R218 files before staging.
- Native KiCad checker sweep under KiCad 10 Python: 18/18 PASS.
- Firmware source validation: 78 executable unit tests PASS. Target flash, received-hardware execution and HIL were not performed.
- Interactive desktop QA at 1280 x 900: body/control text 16 px minimum, secondary text 14 px minimum, fifteen requirement cards, no horizontal overflow and the preliminary warning present.
- Interactive filters returned seven `SF-01`, five `SF-03`, one `DF-01`, one `PG-01`, thirteen open/selection and fifteen all-requirement cards. The combined `SF-01/SF-03` allocation row intentionally appears in both credited-function filters.
- Interactive mobile QA at 390 x 844: body/control text 16 px minimum, secondary text 14 px minimum, 335 px single-column controls/cards, no horizontal overflow and the preliminary warning present.
- Final synchronized standard sweep, release-manifest count and clean-commit verification are recorded below after staging.

## Final synchronized state

- Final standard repository sweep: 160/160 PASS.
- Release manifest regenerated with 4,095 package files.
- Dedicated package checker, native KiCad sweep, firmware validation and `git diff --check`: PASS.
- Clean-commit and remote-identity verification are recorded in the commit/PR handoff after publication.

Passing source checks establish identity, arithmetic, provenance, fail-closed state and presentation consistency only. They do not establish risk reduction, achieved stopping performance, contactor suitability, guard adequacy, PLr/SIL, functional-safety validation or permission to energize.
