# R205 validation record

**PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION**

R205 issues `HR-V0-PI-OBS-INTEGRATION-P0.1` without changing P0.6, R161, R202 or R204 source. The R202 120 x 90 mm board is rotated into a 90 x 120 mm compute-column candidate at `(433.0, 300.0)`. Ten nominal planar screens show no encoded rectangle overlap, including 9.2 mm to WD2, 24.6 mm to GTM3, 55.2 mm to the protection reserve and 118.0 mm to the nearest R161 carrier.

Source-coordinate transformation places `JLOGIC1` at `(478.00, 306.00)` and `JFIELD1` at `(478.00, 414.00)`. The centred R204 reference transform places `JOBS1` at `(478.25, 119.25)` but is explicitly not a received transform. The two Manhattan route screens reproduce 335.4 mm and 276.0 mm. Every cut length remains `SELECTION REQUIRED`; all thirteen holds and sixteen acceptance rows remain open.

Passing repository checks prove deterministic source parity and arithmetic only. No physical article, Sol R12 finding, requirement, gate, qualified review, safety credit or work authority closes.

## Repository validation

- Ordinary fail-closed checker sweep: 146/146 passed.
- KiCad 10.0.5 `pcbnew` checker sweep: 15/15 passed, including the unchanged R202 and R204 native boards.
- Supervisor tests: 67/67 passed.
- Watchdog tests: 11/11 passed.
- Host-deployment tests: 16/16 passed while correctly reporting `ready: false` and `motion_authority: NONE`.
- Energization-gate audit through E6: 30 applicable, 0 closed, 23 partial, 7 open; `--require-ready` correctly exited 2.
- Desktop browser DOM and 1280 px visual inspection passed after correcting SVG label/route collisions and the clipped SVG warning. A 390 px rendered wrapper was not executed because the browser security policy rejected the local wrapper URL; responsive source checks still enforce 16 px body text, 14 px technical text, metric reflow and explicit horizontal scrolling for the full-size diagram/tables. No mobile rendered-pass claim is made.

The non-ready gate result is the required fail-closed outcome. These source and software checks do not substitute for received-article inspection, physical fit, harness measurement, termination qualification, electrical test, HIL, functional-safety validation or qualified review.
