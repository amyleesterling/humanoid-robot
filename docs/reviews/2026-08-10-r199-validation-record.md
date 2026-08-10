# R199 validation record

> **PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION**

Artifacts: `HR-V0-RUNTIME-P0.1` / `HR-V0-RUNTIME-BACKENDS-P0.1` / `HR-V0-HOST-DEPLOY-P0.1`

Date: 2026-08-10

## Correction

- Replaced the static heartbeat-permission interface with a monotonic edge scheduler that forces its output inactive on disable, lateness, time reversal, startup failure and shutdown.
- Added a hash-bound libgpiod 2.x GPIO source candidate and exact nine-input observation schema.
- Added a hash-bound local AF_UNIX datagram command source with kernel UID/GID credentials, exact schema, bounded datagrams and finite-number rejection.
- Added mandatory sample-count, trajectory-duration and execution-slack selections; all remain unreleased.
- Expanded the proposed overlay from 19 to 21 sources and the pure-file preflight from 24 to 50 explicit holds.
- Exposed the critical physical-interface gap: no qualified circuit or Pi allocation exists for the nine observations.

## Executed source checks

- Firmware: 75/75 tests passed: 64 supervisor/runtime tests plus 11 watchdog tests.
- Host: 16/16 tests passed, including eight backend tests.
- Committed preflight: exit 78 with 50 holds before backend import.
- Complete standard-runtime sweep: 142/142 checkers passed, including the staged release-manifest checker.
- Native KiCad `pcbnew` sweep: 13/13 checkers passed.
- Deterministic release manifest: 3,392 package files before this final validation-record refresh; regenerated after the refresh.
- R200 correction: `check_energization_gates.py --through E2 --require-ready` returns exit 2 for a valid but unresolved register. R199 incorrectly recorded exit 1. The substantive result was and remains 0/21 gates closed with all 21 partial.

## Web-guide inspection boundary

The dedicated checks enforce 16 px body/functional text, 14 px metadata and technical annotations, four filter controls and responsive reflow. No manual browser-layout or accessibility approval is claimed; independent desktop/mobile inspection remains requested.

## Boundary

No target image was installed. No GPIO line, observation circuit, serial device, UID/GID, timing limit or trajectory resource limit was released. No waveform, packet trace, HIL, physical fault injection, powered test or motion occurred. No functional-safety credit, Sol finding, requirement, gate or work authority closes.
