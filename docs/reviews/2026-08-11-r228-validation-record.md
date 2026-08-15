# R228 validation record

> **PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION**

Date: 2026-08-11

Artifact: `HR-V0-E2-PREPOWER-P0.1`

## Source and configuration checks

- All 55 unaccepted P1.18 point-to-point conductor candidates have exact continuity rows.
- Forty-five rows are fixed-internal method candidates; ten moving-door rows remain blocked.
- Sixteen isolation pairs, eight no-backfeed cases and twelve absence-of-voltage points are recorded.
- Five instrument rows include a nonaccepted Keysight U1282A candidate; all exact options, calibration, leads, proving references, uncertainty and received evidence remain open.
- Six prohibited activities prevent high-voltage testing across connected electronics, unqualified stimulus injection and false absence-of-voltage claims.
- Ten holds remain open.
- All numeric limits are unreleased, all physical result fields are blank/not executed and all work-authority fields remain false.
- P1.15 remains current; P1.18 remains unaccepted.
- `EG-004`, `EG-019`, `EG-020` and `EG-022` remain partial.

## Repository and visual validation

- focused package checker: **PASS**;
- native KiCad/pcbnew checker sweep: **18 / 18 PASS**;
- pre-manifest standard repository checker sweep: **170 / 171 PASS**; every nonmanifest checker passed and the only failure was the expected untracked/stale-manifest gate;
- final staged standard repository checker sweep: **171 / 171 PASS**;
- supervisor firmware tests: **67 / 67 PASS**;
- watchdog firmware tests: **11 / 11 PASS**;
- desktop browser QA at 1280 x 720: **PASS**; 55 initial rows, 45 fixed-only rows and ten blocked-door rows filter correctly; no body overflow; 16 px body and 14 px code text; both tables fit their 1,225 px containers;
- mobile browser QA at requested 390 x 844: **PASS**; 375 CSS-pixel document width, no body overflow, 16 px body and 14 px code text, 339 px cards and both 920 px tables contained in 335 px horizontal-scroll regions;
- staged deterministic release manifest: **PASS with 4,405 controlled package files**;
- independent electrical and functional-safety review: **OPEN**.

Passing source/configuration checks will not prove premises suitability, shock/fire protection, fault clearing, received condition, physical construction, functional safety or permission to perform work.
