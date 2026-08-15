# R196 validation record

> **PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION**

Artifact: `HR-V0-STALE-AUTH-P0.1`

Date: 2026-08-10

## Executed source checks

- Bound all 20 current E2 safety-logic case IDs to explicit supervisor-state, active-target, torque-request and stale-replay expectations.
- Corrected the ambiguity in `E2-SL-019`: K1/K2 power-path restoration after valid RESET and distinct ARM does not mean motion authority. Expected software state is `ARMED`, active trajectory `NONE`, torque-enable request `FALSE`, old sequence `REJECTED`.
- Added and passed a supervisor regression that accepts a command, induces dropout, clears the target, completes fault acknowledgement and re-arm, rejects replay of the old sequence, and accepts only a later sequence.

## Repository regression

- Supervisor suite: 38/38 tests passed, including the new dropout/re-arm replay case.
- Firmware validation: 49 executable unit tests passed; target flash, received-hardware execution and HIL remain not performed.
- Complete standard-runtime sweep: 140/140 checkers passed.
- Native KiCad `pcbnew` sweep: 13/13 checkers passed.
- Deterministic release manifest: 3,365 package files; dedicated checker passed.
- `check_energization_gates.py --through E2 --require-ready` returned exit 2 as required: 0/21 gates closed and all 21 remain partial.

## Web-guide inspection boundary

The fail-closed guide checker passed the 16 px body, 14 px metadata, responsive single-column breakpoint and undersized-declaration rules. The in-app preview remained attached to an older cached local page, so no R196 browser screenshot or visual-layout claim is made in this record. Independent desktop/mobile visual inspection remains requested.

## Boundary

This is source/model evidence only. The form remains entirely `NOT EXECUTED`. No target image, HIL, physical input, contactor, actuator, stopping, guard or functional-safety behavior is proved. The supervisor and ordinary heartbeat diagnostic retain zero safety credit. No requirement, Sol R12 finding or energization gate closes.
