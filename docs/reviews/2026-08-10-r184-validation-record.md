# R184 validation record

> **PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION.**

Artifact: **HR-V0-Q4X-BOX-P0.1**

Date: **2026-08-10**

## Package checks

- candidate-BOM rows: **19**;
- current primary manufacturer source records: **14**;
- connection/termination rows: **11**, all unreleased or intentionally unwired;
- enclosure-layout rows: **7**;
- controlled calculation rows: **6**;
- closure holds: **14**;
- native KiCad sheets including root: **3**;
- KiCad 10.0.5 ERC: **0 errors / 0 warnings**;
- stable KiCad SVG exports: **3**;
- package-specific checker: **35/35 passed**;
- released connections: **0**;
- authorized procurement/fabrication/powered runs: **0 / 0 / 0**;
- physical runs: **0**;
- robot-baseline changes: **0**; and
- safety-function credit: **0**.

## Repository regression

- ordinary non-`pcbnew` checks in the bundled Python runtime: **114/114 passed**;
- CadQuery checks in the controlled HR-V0 CAD runtime: **14/14 passed**;
- complete non-`pcbnew` count: **128/128 passed**;
- native KiCad `pcbnew` checks in KiCad 10.0.5 Python: **13/13 passed**;
- total domain checks: **141/141 passed**; and
- deterministic release manifest after synchronization: **3,146 package files**.

The first general-runtime sweep reported only the fourteen expected missing-`cadquery` routes plus the not-yet-synchronized manifest. All fourteen CAD checks were routed to the controlled CadQuery environment and passed. These are runtime-routing observations, not design failures.

## Interactive-guide validation

Rendered desktop and 390 x 844 mobile checks were executed against the local guide through the in-app browser. The three schematic tabs changed the active native SVG correctly; all three SVGs loaded; no broken images were found; body, lead and table text computed to 16 px, 18 px and 14 px respectively at mobile width; the flow reflowed to one column; and the page had no document-level horizontal overflow. The wide native schematic itself remains intentionally scrollable inside its bounded viewer.

## Evidence boundary

This validation establishes source/register/file consistency and browser rendering only. It does not establish received identity, exact source-cable procurement form or length, current-limit setting, inrush, trip or short behavior, no-backfeed, drill coordinates, gland torque, crimp quality, conductor retention, isolation/grounding acceptance, environmental rating, closed-box temperature, physical analog fixture, Q4X calibration, no-motion threshold, physical connection, E2 execution, powered stopping or qualified acceptance.
