# R182 validation record

> **PRELIMINARY - NOT APPROVED FOR PROCUREMENT, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION.**

Artifact: **HR-V0-E2-ACQ-COMPAT-P0.1**

Date: **2026-08-10**

## Package checks

- channel records: **8**;
- `TCP0030A` candidates: **4**;
- `TIVP02/TIVPMX10X` candidates: **4**;
- documented maximum population: **71.6 W** against **80.0 W** total;
- bank 1-4: **35.8 W** against **40.0 W**;
- bank 5-8: **35.8 W** against **40.0 W**;
- exact motion-witness candidate: **Banner Q4XFULAF110-Q8 / part 97540**;
- current primary source records: **6**;
- open closure holds: **15**;
- manufacturer inquiries sent: **0**;
- physical compatibility runs: **0**;
- released connections: **0**; and
- safety-function credit: **0**.

The package generator and package-specific checker pass.

## Repository regression

- ordinary non-`pcbnew` checks in the bundled Python runtime: **112/112 passed**;
- CadQuery checks in the controlled HR-V0 CAD runtime: **14/14 passed**;
- complete non-`pcbnew` count: **126/126 passed**;
- native KiCad `pcbnew` checks in KiCad 10.0.5 Python: **13/13 passed**;
- total domain checks: **139/139 passed**; and
- deterministic release manifest after synchronization: **3,095 files**.

The first general-runtime sweep reported fourteen failures solely because that interpreter does not contain CadQuery. All fourteen passed when rerun in the repository's controlled CAD environment; these are not design failures.

## Interactive-guide validation

Static package checks confirm 16 px body text, 14 px technical labels, responsive cards, explicit horizontal table scrolling, three power-budget cards, fifteen hold cards and the full preliminary warning. The in-app browser refused the local `file:` URL under its URL security policy. No alternate browser route was used, so desktop/mobile rendered visual inspection is recorded **NOT EXECUTED** for this round. This does not weaken any existing engineering hold or create work authority.

## Evidence boundary

This validation establishes arithmetic and file consistency only. It does not establish received identity, calibration, installed-probe compatibility, signal fidelity, noninterference, a Q4X mounting geometry, a no-motion threshold, a connection schedule, a physical run or qualified acceptance.
