# R198 validation record

> **PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION**

Artifact: `HR-V0-RUNTIME-P0.1`

Date: 2026-08-10

## Source correction

- Added the runtime executive and exact target entrypoint.
- Expanded the proposed disabled overlay from six to nineteen repository sources.
- Bound the entrypoint target and source hash while retaining 24 explicit preflight holds.
- Added inverse received-position conversion and corrected the torque-off goal-current invariant.
- Added source tests for RESET/ARM without torque, fresh trajectory sequencing, dropout, sample lateness and shutdown.

## Executed checks

- Firmware checker: 72 executable unit tests passed; target flash, received-hardware execution and HIL remain not performed.
- Host package: 8/8 tests passed; committed configuration returned exit 78 with 24 holds before child process or backend import.
- Complete standard-runtime coverage: 142/142 checkers passed, comprising 141 non-release checkers plus the staged release-manifest checker.
- Native KiCad `pcbnew` sweep: 13/13 checkers passed.
- Deterministic release manifest: 3,383 package files; dedicated checker passed against the staged candidate.
- `check_energization_gates.py --through E2 --require-ready` returned exit 2 as required: 0/21 gates closed and all 21 remain partial.

## Web-guide inspection boundary

The dedicated check enforces 16 px body/functional text, 14 px metadata and technical annotations, four filter controls, responsive reflow and the exact fail-closed counts. No browser screenshot or manual visual-layout claim is made; independent desktop/mobile inspection remains requested.

## Boundary

This is source/model evidence only. No target backend, installed image, GPIO waveform, serial packet, HIL, physical motion, stopping or qualified-review evidence exists. No Sol finding, requirement, gate or work authority closes.
