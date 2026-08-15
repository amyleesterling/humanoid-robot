# R227 validation record

> **PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION**

Date: 2026-08-11

Artifact: `HR-V0-E2-GND-BOUNDARY-P0.1`

## Source and configuration checks

- Current P1.15 and unaccepted P1.18 contain 26 identical terminal/net rows for `PSA1`, `PSU2`, `J24`, `PSU3`, `SP1` and `JFRAME1`.
- `ACT_0V_PE_BONDED`, `COMPUTE_0V`, `ROBOT_FRAME` and `CABLE_SHIELD_TERM` have identical connection membership.
- `SAFETY_0V` is not mislabeled as identical: P1.15 has 41 connections and P1.18 has 49 because P1.18 adds `XD0:LINE` plus `XD0:01..07`.
- Ten boundary items state what may be present, what must be absent/DNP and what remains unverified.
- Fifteen inspection/test rows remain `UNEXECUTED` with blank result/evidence fields.
- Twelve holds remain `OPEN` and unaccepted.
- Eighteen source rows include twelve SHA-256-bound repository sources and six current primary manufacturer records rechecked 2026-08-11.
- `EG-001`, `EG-004`, `EG-016` and `EG-022` remain partial.
- Every physical/work-authority flag remains false.

## Repository and visual validation

- focused package checker: **PASS**;
- native KiCad/pcbnew checker sweep: **18 / 18 PASS**;
- pre-manifest standard repository checker sweep: **169 / 170 PASS**; every nonmanifest checker passed and the only failure was the expected untracked/stale-manifest gate;
- supervisor firmware tests: **67 / 67 PASS**;
- watchdog firmware tests: **11 / 11 PASS**;
- desktop browser QA at 1280 x 720: **PASS**; no body overflow, 16 px body text, 14 px code text, ten boundary cards, five node rows, fifteen inspection rows and both tables fit their 1,229 px wrappers;
- mobile browser QA at requested 390 x 844: **PASS**; 375 CSS-pixel document width, no body overflow, 16 px body text, 14 px code text, 339 px single-column cards and both 920 px tables contained in 339 px horizontal-scroll regions;
- final staged deterministic release manifest: **PASS with 4,374 controlled package files**;
- independent electrical and functional-safety review: **OPEN**.

Passing source/configuration checks will not prove received condition, premises suitability, shock/fire protection, fault clearing, physical construction, functional safety or permission to perform work.
