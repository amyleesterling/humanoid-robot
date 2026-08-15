# R204 validation record

**PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION**

R204 issues `HR-V0-PI-OBS-CARRIER-P0.1` with a native root and child schematic, native two-layer PCB, exact connector schedule, exact-color wire-stock candidates, source register, ten open holds and an interactive web guide.

- KiCad ERC: 0 errors / 0 warnings.
- KiCad DRC: 0 violations.
- Board: 65.0 x 56.5 mm reference candidate; two layers; two mounted connector footprints; four board-only 2.7 mm reference holes.
- Copper: six named nets, 28 track segments and 12 vias. Thirty-four JPI1 positions are no-net/no-copper.
- Explicit absences: no 5 V copper, no ID-pin copper, no EEPROM, no duplicate output pulldowns and no CAM/Gerber/drill/supplier archive.
- Harness: six exact Belden 3051 color/order-code stock candidates; every cut length remains `SELECTION REQUIRED`.

Repository-wide validation at the staged R204 candidate:

- Ordinary source checker sweep: 145/145 passed.
- Native `pcbnew` checker sweep: 15/15 passed, including the new R204 footprint/net/no-copper parity check.
- Supervisor source tests: 67/67 passed.
- Watchdog source tests: 11/11 passed; combined firmware result 78/78.
- Host source tests: 16/16 passed. The source preflight remains deliberately fail-closed with 36 explicit holds and no motion authority.
- Energization-gate readiness check with `--require-ready`: documented non-ready exit 2; 0/30 gates closed, 23 partial and 7 open through E6.
- Browser visual QA: default desktop and 390 x 844 px mobile views were inspected. The warning, metrics, board view and scrollable tables remained legible; CSS contains no user-facing text below 12 px. Browser QA is presentation evidence only.

All ten R204 holds remain open. Native zero-violation results prove only encoded source connectivity and annotation. No physical article, connection, powered test, Sol R12 blocker, requirement, release gate, safety credit or work authority closes.
