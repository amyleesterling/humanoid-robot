# R86 validation record - watchdog dependent-failure package

Date: 2026-08-08

Product: `HR-V0-WD-CCF-P0.1`

Configuration: `Electrical V3-P1.12 / PCB-P0.5 / HR-V0-CP-P0.4`

Status: **PRELIMINARY - ANALYSIS AND UNEXECUTED TEST CONTROL ONLY - NOT APPROVED FOR FABRICATION OR ENERGIZATION**

## Correction

R86 binds `ANALYSIS-SAFE-002` to the exact V3 terminals and exposes a previously unrecorded negative-contribution blocker: KWD A1/21 carries `SAFETY_24V` while KWD terminal 14 returns to SR1 downstream of an E-stop NC contact. No internal fault exclusion is accepted and topology non-interference is explicitly `NOT PROVED`.

## Executed source validation

- the package generator completed successfully;
- the package checker passed;
- 18 exact paths, 32 failure modes, 12 common-cause groups, 28 unexecuted cases, 16 separation controls and eight open decisions are machine controlled;
- the V3 source contains every required KWD/SR1/feedback net and terminal;
- the interactive HTML uses a 16 px body minimum and the SVG uses 18 px body text;
- all physical cases remain `NOT EXECUTED` and `NOT AUTHORIZED`;
- DF-01 safety credit remains zero;
- `SF-01`/`SF-03` PLr, category and achieved performance remain `SELECTION REQUIRED`; and
- no fabrication, wiring, connection, physical test, motion or energization authorization exists.

The complete repository sweep passed all `36` non-manifest checkers. Traceability reports `81` requirements, `40` risks and `106` controlled procedures. The energization register remains `30` applicable gates: `0` closed, `22` partial and `8` open.

The staged release manifest contains `974` package files and passed its content/hash checker before commit. Remote clean-clone results are recorded after push.

## Boundary

This is a source and analysis-control validation. It is not the signed `ANALYSIS-SAFE-002` result, a fault-exclusion justification, a physical test, a PL calculation, a qualified review or an energization release. `EG-012` remains partial.
