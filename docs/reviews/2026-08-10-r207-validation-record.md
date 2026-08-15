# R207 validation record

**PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION**

R207 issues `HR-V0-OBSERVATION-COMPUTE-HARNESS-P0.1` without superseding R202, R204, R205 or Electrical P1.16.

The dedicated checker proves exact six-row parity to R204 and P1.16, both-end Phoenix process parity, deterministic engineering/web mirrors, controlled source hashes and false-authority flags. The 322.5 mm rounded route and 12.06 mm2 bare-area values are analytical screens only. Every cut length, duct-fill result, Pi external-load/back-power result, physical test and acceptance row remains open.

## Repository validation

- R207 dedicated checker: PASS. It verifies exact six-row R202/R204/P1.16 parity, W14001-W14006 color/order-code candidates, both-end Phoenix 1751280 process envelopes, route and area arithmetic, deterministic engineering/web mirrors, source hashes, thirteen open holds, thirteen unexecuted acceptance rows and all false-authority flags.
- Standard fail-closed checker sweep: 149/149 PASS.
- Native KiCad/pcbnew checker sweep: 15/15 PASS.
- Supervisor software: 67/67 unit tests PASS.
- Independent watchdog firmware model and compiled differential tests: 11/11 PASS.
- Host deployment/backend software: 16/16 unit tests PASS. The committed package correctly remains `ready: false` with `motion_authority: NONE` and unresolved deployment, hardware-observation and evidence holds.
- Energization-gate audit: schema PASS; 30 gates apply through E6; 0 closed, 23 partial and 7 open. `--require-ready` correctly returned exit code 2.
- Browser QA: PASS at 1280 px desktop and 390 x 844 px mobile. Minimum observed functional text was 14 px, the full warning remained visible, the page had no body-level horizontal overflow, tables retained their deliberate local scrolling and the wiring view rendered at both sizes.

The first browser render exposed invalid XML in the generated white-conductor outline: one SVG path carried two `stroke` attributes, so the browser displayed only fallback text. The generator was corrected to emit a separate outline path, both mirrors were regenerated, and the dedicated checker now parses the SVG as XML so the same defect fails closed. Desktop and mobile were rechecked after correction.

These results validate repository consistency and fail-closed source behavior only. They do not establish a cut length, installed route, duct fill, cable voltage drop, Raspberry Pi external-load/back-power acceptance, termination qualification, physical harness result, functional-safety credit, qualified approval or work authorization.
