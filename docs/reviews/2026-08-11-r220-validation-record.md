# R220 validation record

> **PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION.**

Identifier: `HR-V0-CP-CONFIG-P0.1`

## Controlled checks

- Eight current configuration inputs are SHA-256 bound.
- Five identity records distinguish inherited P0.6 geometry, current P1.15 core, current PCB-P1.0, current DXL-STAR-P0.2 and supporting-only P1.17.
- All 66 current P1.15 panel endpoints exactly match the inherited P0.6 schedule across wire, sheet, reference, terminal, pin name and net.
- The current schedule retains `SELECTION REQUIRED` for conductor, gauge, color, length and both terminations on all 66 records.
- The current 34-row panel BOM replaces only the two stale board identities and releases no physical item.
- The current 26-row layout replaces only the two stale board mounting-basis labels and releases no hole or fit.
- Both board envelopes retain `NOT EXECUTED` received fit and `FALSE` mounting-hole release.
- Twelve installation holds remain open; all supplier, procurement, fabrication, assembly, connection, powered-test, motion and energization flags remain false.

## Validation state

- Dedicated package checker: PASS.
- Correct-runtime pre-stage standard repository sweep: 161/162 PASS. The sole expected failure was the release-manifest checker rejecting the seventeen new, still-untracked R220 files before staging.
- Native KiCad checker sweep: 18/18 PASS; no ECAD source changed in R220.
- Firmware source validation: supervisor 67/67 and watchdog 11/11, total 78/78 PASS; no firmware source changed in R220.
- Interactive desktop QA at 1280 x 720: 16 px body text, 14 px metadata, five identity cards, 66/66 metric, warning present and no horizontal overflow.
- Visual inspection confirmed readable sky-blue/dark-blue/gold presentation and explicit physical-evidence boundary.

## Final synchronized state

- Final standard repository sweep: 162/162 PASS.
- Native KiCad 18/18 and firmware 78/78 checks: PASS.
- Release manifest regenerated with 4,132 package files; `git diff --check`: PASS.

Passing parity proves current source identity and encoded endpoint equality only. It does not establish supplier release, received fit, a production hole schedule, conductor/protection selection, physical installation, electrical acceptance, functional-safety approval or permission for powered work.
