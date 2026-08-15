# R226 validation record

> **PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION**

Date: 2026-08-11  
Artifact: `HR-V0-K1K2-APP-P0.3`

## Source and configuration checks

- Current P1.15 and unaccepted P1.18 sheet-04 terminal/net schedules: 16/16 rows identical.
- Current P1.15 and unaccepted P1.18 sheet-05 terminal/net schedules: 16/16 rows identical.
- Both native sheet pairs retain the `LC1D25BD`, loaded-DC-interruption and critical-current warnings.
- Both KiCad netlists contain the exact six internal K1/K2 series-jumper nets and exact K1/K2 coil/EDM intermediate nets checked by the dedicated verifier.
- Thirteen source rows bind ten local repository inputs by SHA-256 and identify three current official Schneider records.
- Twelve application-evidence rows contain no `APPROVED`, `RELEASED`, `PASS`, or `CLOSED` state.
- Eleven holds remain `OPEN` and unaccepted.
- `EG-002`, `EG-004`, and `EG-013` remain partial.
- Every physical/work authority flag remains false.

## Repository and visual validation

- focused package checker: **PASS**;
- native KiCad/pcbnew checker sweep: **18 / 18 PASS**;
- pre-manifest standard repository checker sweep: **168 / 169 PASS**; every nonmanifest checker passed and the only failure was the expected untracked/stale-manifest gate;
- final staged standard repository checker sweep: **169 / 169 PASS**;
- supervisor firmware tests: **67 / 67 PASS**;
- watchdog firmware tests: **11 / 11 PASS**;
- desktop browser QA at 1280 x 720: **PASS**; no body overflow, 16 px body/functional text, 14 px code labels, 16 cards present, 32 parity rows shown, and both tables fit their 1,225 px wrappers;
- mobile browser QA at requested 390 x 844: **PASS**; 375 CSS-pixel document width, no body overflow, 16 px body/functional text, 14 px code labels, 339 px single-column cards, and both 920 px tables contained in 335 px horizontal-scroll regions;
- filter interaction: **PASS**; selecting `power_path` displayed exactly 16 rows and zero rows from the wrong domain;
- final deterministic release manifest: **PASS with 4,347 controlled package files**;
- independent electrical and functional-safety review: **OPEN**.

This record will be updated with exact final results before commit. Passing source/configuration checks will not prove DC making/breaking suitability, physical construction, stopping performance, achieved safety integrity, or permission to perform work.
