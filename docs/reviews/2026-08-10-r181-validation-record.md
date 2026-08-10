# R181 validation record

> **PRELIMINARY - NOT APPROVED FOR CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION.**

Artifact: **HR-V0-DYN-TRACE-P0.2**

Date: **2026-08-10**

## Package and algorithm checks

- generator and package-specific checker: **PASS**;
- physical run types: **2** (`STOP`, `RESET_ARM`);
- simultaneous physical channels per run: **8**;
- acceptance rules: **9**;
- synthetic fixtures: **6**;
- expected results: **2 computed PASS/HOLD and 4 FAIL/REJECT**;
- physical templates: both reject unresolved numeric configuration; and
- executed physical runs, released thresholds and safety-function credit: **0**.

The nominal E2 STOP fixture reports synthetic K1/K2 coil drops at 5/6 ms, K1/K2 auxiliary openings at 10/11 ms and common-EDM closure at 12 ms, while the 24 V control source remains valid and angle change remains zero. The nominal RESET/ARM fixture computes a 0.070 s reset-to-ARM interval with zero angle change. These are synthetic code-path values only and make no powered-motion stopping claim.

## Interactive-guide validation

The guide was rendered headlessly with Microsoft Edge at 1280 x 720 and 390 x 844 viewports:

- desktop document width: 1280 px for a 1280 px viewport;
- mobile document width: 390 px for a 390 px viewport;
- both views contained two run cards and nine rule cards;
- body text computed at 16 px and the smallest user-facing technical text at 14 px; and
- no page-level horizontal overflow remained.

The first mobile render exposed a 532 px min-content overflow caused by a slash-delimited rule label. The responsive grid was corrected with zero-minimum tracks and wrap-safe cards; the label was rewritten in ordinary prose. Desktop and mobile captures were visually inspected and the temporary QA files were removed.

## Repository validation

- non-`pcbnew` checker sweep: **125/125 passed**;
- KiCad 10.0.5 `pcbnew` checker sweep: **13/13 passed**;
- total domain checks: **138/138 passed**; and
- deterministic release manifest after R181 synchronization: **3,080 files**.

The first standard sweep failed only because the new R181 files were intentionally untracked; the other 124 checkers passed. After staging and manifest synchronization, all 125 non-`pcbnew` checks passed. The native PCB source was unchanged, but all thirteen `pcbnew` checks were rerun under KiCad's bundled Python and passed.

No physical trace was acquired. No instrument was connected. Repository validation cannot authorize procurement, connection, powered testing, motion, functional safety or energization.
