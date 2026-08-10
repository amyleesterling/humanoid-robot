# R120 validation record

> **PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TEST, MOTION, OR ENERGIZATION.**

Date: 2026-08-08

Package: `HR-V0-COMPUTE-SUBASM-P0.1`

## Controlled results

- `tools/check_hr_v0_compute_subassembly_p01.py`: PASS.
- System BOM closure regeneration: 79 groups; 17 evaluation candidates; 28 exact-candidate holds; three grouped-component holds; 26 selection-required groups; four exclusions; one integrated item.
- Repository checker inventory: 73 checkers. All 72 non-manifest checkers passed in bounded batches using the controlled CadQuery or KiCad interpreter; the manifest checker then passed after final regeneration.
- Traceability: 81 requirements, 40 risks, 110 procedure records and 57 release/walking-document procedure references resolve.
- Electrical V3 consistency: PASS at retained `V3-P1.14`; 13 native pages, 76 component blocks, 296 modeled terminals, 64 named connected nets, 39 deliberate unconnected nets, 257 wire labels and 63 unresolved rows.
- E0-E2 readiness check: expected fail-closed exit 2; 21 of 21 applicable gates remain partial and zero are closed.
- Responsive guide QA: desktop 1440 x 1100 and mobile 390 x 844; no body horizontal overflow; smallest user-facing text 12 CSS px; body and functional text 16 CSS px; desktop and mobile screenshots visually inspected with no clipping or illegible functional text.
- Final release-manifest generation/check: PASS; 1,605 package files. `EG-002` remains partial pending merge and formal acceptance.

## Evidence boundary

These checks prove repository consistency only. No Raspberry Pi, supply, cooler or card has been purchased or received. The image has not been downloaded, hashed locally, written, booted, configured, hardened or tested. No mounting tray, enclosure, cable, retention, electrical-load, thermal, power-loss, EMC/HIL or qualified-review evidence has been executed.

R120 closes no energization gate and does not change Sol R12's buildability or energization verdict.
