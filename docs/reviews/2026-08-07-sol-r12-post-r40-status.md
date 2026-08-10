# Sol R12 Findings Rechecked against R40

> **PRELIMINARY—NOT APPROVED FOR FABRICATION OR ENERGIZATION**

Date: 2026-08-07

System baseline: `HR-30-SYS-R0.2`

Correction baseline: `HR-V0-WD-BUILD-P0.2`

This is a project-owned status reconciliation, not a new independent review. The newly supplied Sol analysis is the same R12 assessment of the pre-correction `ee276af...` baseline: 18 BLOCKER, 30 MAJOR and 8 MINOR findings; 62 of 62 requirements draft; 106 unresolved electrical selections; and no executed, approved verification evidence. It is not double-counted.

## R40 correction

R40 closes a narrower implementation-evidence defect inside `EG-017`:

- found and corrected inconsistent 32-bit clock behavior between the portable C logic and Python reference model;
- added a distinct latched clock-regression fault while accepting legitimate `uint32_t` wrap;
- defined the exact half-range fail-closed assumption;
- added a deterministic compiled-C vector runner and nine-scenario / 44-step differential oracle;
- pinned LLVM-MinGW 20260616 / LLVM 22.1.8 to the publisher's exact 187,504,083-byte archive and SHA-256;
- reproduced the host executable across two clean strict builds; and
- issued reproducible Pico target P0.2 artifacts without overwriting historical P0.1 evidence.

## What this narrows

Portable watchdog logic is no longer supported only by a Python model and target compilation. The actual C state logic has now executed on a host and matched the reference model at the controlled startup, timeout, feedback, recovery, wrap and regression boundaries. The target artifact contains the corrected code.

## What remains open

- The P0.2 UF2 has not been flashed or executed on a received Pico.
- Host execution does not prove RP2040 timing, GPIO, electrical default-off behavior, brownout/reset/debug-halt response or clock-fault behavior.
- No disconnected-load HIL, relay timing, welded-contact injection, total stopping-time or common-cause evidence exists.
- The watchdog remains a shared-MCU ordinary diagnostic function with no PL/SIL credit.
- Sol's mechanical, power-loss, continuous-torque, protection, grounding, bus, battery, restraint, real-time, functional-safety, fabrication and walking blockers remain open.
- Through E2 the gate result remains 0 closed, 15 partial and 6 open. `EG-017` remains partial.

## Disposition

Sol's central verdict is unchanged: HR-V0 is not ready for fabrication or energization, and HR-30W walking is not demonstrated. R40 improves reviewability and catches one software-model defect; it is not target or safety validation and grants no permission to flash, fabricate or energize.
