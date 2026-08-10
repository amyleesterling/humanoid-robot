# R180 validation record

> **PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION.**

Artifact: **HR-V0-EVENT-OBS-CORR-P0.1**

Date: **2026-08-10**

## Package checks

The generator and checker produce and validate:

- four explicit supersession records, including R174 DTA-003 and the R175/R176/R177/R179 channel semantics;
- two eight-channel simultaneous run allocations;
- one common series-EDM current witness per STOP run;
- separate K1/K2 NO auxiliary diagnostic channels with zero safety credit;
- five instrument roles, including exact `MSO58B`, `TCP0030A` and `TIVP02/TIVPMX10X` evaluation candidates;
- eight diagnostic-load holds and twelve package closure holds;
- four unexecuted test cases and one blank evidence template; and
- zero diagnostic loads, connections, physical tests or safety-function credit.

The package checker passes.

## Source and configuration checks

- P1.15 confirms K1:21-22 and K2:21-22 form one series NC mirror-contact path between `ARM_AFTER_S2` and `SRA1_START_RETURN`.
- P1.15 confirms `EDM_K1_OUT` is only the intermediate node between those contacts.
- P1.15 confirms K1:13/K2:13 are fed from `SAFETY_24V`, while K1:14/K2:14 terminate at `XT1-05`/`XT1-06` without a defined load/return.
- Tektronix's current MSO58B record identifies eight analog/FlexChannel inputs, 6.25 GS/s maximum and configurable 350 MHz to 2 GHz bandwidth.
- Current Tektronix documents `51W-19042-12`, `51W-61655-7`, `071-3692-09` and the 5 Series B specification are recorded with dates/revisions in the source register.
- No bandwidth option, record-length option, order configuration, diagnostic load, motion sensor or physical connection was inferred.

## Interactive-guide validation

The guide was rendered headlessly with Microsoft Edge at 1280 x 720 and 390 x 844 viewports:

- desktop reported 1280 px viewport width and 1280 px document width;
- mobile reported 390 px viewport width and 390 px document width;
- both views contained all eight STOP-channel cards;
- body and functional text computed at 16 px;
- the smallest user-facing technical text computed at 14 px; and
- no page-level horizontal overflow was present.

The desktop and mobile captures were visually inspected. The warning, correction, series-chain diagram, cards, limitations, holds and footer are readable and unclipped. The temporary QA captures and script were removed after review and are not release artifacts.

## Repository validation

- non-`pcbnew` checker sweep: **124/124 passed**;
- KiCad 10.0.5 `pcbnew` checker sweep: **13/13 passed**;
- total domain checks: **137/137 passed**; and
- deterministic release manifest after R180 synchronization: **3,049 files**.

The first standard sweep failed only because the new R180 files were intentionally still untracked. After staging the controlled set and regenerating the manifest, all checks passed. The native PCB source was not changed; the thirteen `pcbnew` checks were nevertheless rerun individually under KiCad's bundled Python and passed.

## Engineering limitation

Repository checks establish internal synchronization, not physical correctness. No probe-power calculation, contact-load circuit, received-article inspection, calibration, physical noninterference trial, stopping test, reset-without-motion test or qualified functional-safety validation has executed.

No physical test was executed. No instrument was connected. No procurement, fabrication, connection, powered-test, motion, functional-safety or energization approval is created by repository validation.
