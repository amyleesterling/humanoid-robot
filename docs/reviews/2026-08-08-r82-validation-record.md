# R82 validation record — compute-heartbeat and watchdog-debug reconciliation

> **PRELIMINARY—NOT APPROVED FOR FABRICATION OR ENERGIZATION.**

Date: 2026-08-08

Round: R82

Independent baseline being dispositioned: Sol R12; not counted again

## Controlled correction

- Electrical V3-P1.12 removes the unselected installed `JDBG1` block and its three `TBD-*` terminals.
- PI1 now models USB-C VBUS/return, physical header pin 6 compute return, BCM GPIO17 at physical header pin 11, and the USB-to-U2D2 boundary.
- PCB debug access remains only TP15 `WD_SWDIO`, TP16 `WD_SWCLK` and TP2 `SAFETY_0V`, each exact Harwin `S1751-46R`.
- `HR-V0-COMPUTE-IF-P0.1` records nine pin rows, ten explicit holds, six primary-source rows, a fail-closed firmware binding and a readable interactive HTML guide.

## Reproduced checks

- KiCad version: 10.0.5.
- Native pages: 13 total, one root plus twelve child sheets.
- Electrical model: 76 components, 296 terminals, 103 nets (64 named connected plus 39 deliberate unconnected), 257 unique wire labels, 74 nonzero-quantity BOM rows, 64 unresolved component/interface rows and 10 deliberate `TBD-*` terminals.
- ERC: 0 errors / 0 warnings.
- Native netlist and thirteen-page PDF/SVG exports generated successfully.
- `tools/check_hr_v0_compute_debug_interface.py`: PASS.
- `tools/check_hr_v0_electrical_v3.py`: PASS.

## Repository and remote reproduction

- Local repository-wide sweep: 31/31 `check_hr_v0_*.py` checkers passed.
- Release manifest: 908 package files; staged-manifest check passed.
- Pushed source state: `0dd207584d57475d042abf187324cf256d5f9edb` on `codex/review-ledger-handoff`.
- Remote clean clone at that exact commit passed `check_hr_v0_release_manifest.py --require-clean` and all 31 repository checkers.
- The first clean-clone attempt at `7b7df98...` exposed a CRLF checkout hash mismatch for the generated gripper HTML. R82 added `cad/hr-v0/**/*.html text eol=lf`; the subsequent clean clone at `0dd2075...` passed. No CAD geometry changed.

## Evidence limits

Current Raspberry Pi documentation supports Pi 5's standard 40-pin header, 3.3 V GPIO output semantics and GPIO17 at physical pin 11. Manufacturer documentation also identifies physical pin 6 as ground. Harwin's current product page and issue-10 drawing support the exact installed test-point identity and standard probe/clip/hook compatibility. None selects the project cable, contacts, housing, runtime, programmer or fixture.

No local interactive-browser rendering result is claimed. The generated guide has explicit 16 px body and 14 px secondary text floors and responsive/scrolling layouts; static checker evidence is not a substitute for browser visual QA.

## Open authorization state

Harness, runtime/backend, startup and shutdown behavior, waveform/timing, HIL, programmer, unpowered fixture, no-back-power proof, EMC/retention, receiving, installed access and qualified review remain open. The heartbeat/debug path has no safety credit. No cable, fixture, programming connection, powered debug, fabrication, motion or energization is authorized.
