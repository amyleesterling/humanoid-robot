# R195 validation record

> **PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION**

Artifact: `HR-V0-WD-P115-ID-P0.1`

Date: 2026-08-10

## Executed correction checks

- Native board title changed to `PCB-P1.0 / Electrical V3-P1.15`.
- P0.8/P1.0 structural digest equality passed with copper, placement and net-change flags false.
- P0.7/P1.0 assembly parity passed 46/46; 42 populated references, four NPTH features, 16 BOM lines and 294 exact hidden native fields remain controlled.
- Native KiCad watchdog PCB DRC remained zero with 201 segments, 56 vias, three zones and unchanged 16 Harwin test-point lands.
- CAM P0.2 regenerated from PCB-P1.0 with ten Gerber/job files, five drill/map/report files, exact 42-reference internal parity and all 18 holds open.
- BOM-048 and E2 P0.4 regenerated against the direct identity. All 12 E2 holds remain open and the actuator domain remains absent or unwired.
- `HR-V0-E2-P115-PARITY-P0.1` moved from the current electrical dependency list to controlled historical evidence.

Targeted checkers passed.

## Repository regression

- The first full sweep exposed genuine stale dependencies: the BOM closure, configuration reconciliation, build traveler, three downstream BOM-source hashes, three historical watchdog checkers and two native KiCad checkers. It also exposed the expected not-yet-regenerated release manifest. No failure was suppressed.
- After deterministic regeneration and checker correction, the complete standard-runtime sweep passed **139/139** under the CadQuery-capable project interpreter.
- All **13/13** native KiCad `pcbnew` checkers passed under KiCad 10.0.5.
- The final staged release manifest contains **3,358 package files** and passed its dedicated content/hash checker.
- `check_energization_gates.py --through E2 --require-ready` returned exit 2 as required: all **21/21** applicable gates remain partial and none are closed.

## Interactive-guide QA

The R195 guide was loaded from a local HTTP server in the in-app browser. At 1280 x 720, body and warning text were 16 px, metadata was 14 px, line height was 24.8 px and page-level horizontal overflow was zero. The `Current R195` control was exercised: pressed state transferred correctly, the historical panel hid and the direct-binding panel appeared. At 390 x 844, body and warning text remained 16 px, metadata 14 px, the heading 40 px, all four cards reflowed to one 335 px column and page-level horizontal overflow remained zero. A normal viewport screenshot confirmed the card/control/panel layout was readable. The browser console reported zero warnings or errors. The temporary viewport was reset and the preview server was stopped.

## Boundary

This correction proves encoded configuration consistency only. It does not prove manufacturability, physical correctness, electrical performance, continuous duty, stopping performance, functional safety or permission to procure, fabricate, assemble, connect, test, move or energize. EG-002 and EG-004 remain partial.
