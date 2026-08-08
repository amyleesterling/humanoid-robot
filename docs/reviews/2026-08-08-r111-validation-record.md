# R111 validation record - source-controlled alternate-gripper trade study

Status: **PRELIMINARY - NOT SELECTED - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, MOTION, OR ENERGIZATION**

R111 issues `HR-V0-GRIP-ALT-P0.1`. It controls seven current manufacturer payloads for two complete catalog grippers and identifies Pololu item 3551 as the preferred evaluation candidate, not a selected part. The current mechanical and electrical candidates are unchanged.

## Source and geometry evidence

- Seven files were checked against recorded byte counts, SHA-256 hashes and PDF/ZIP/STEP signatures.
- The Pololu assembled STEP parsed as three solids with a `48.3233046 x 62.3000002 x 36.6002866 mm` native-coordinate bounding box.
- The ServoCity assembled STEP parsed as 43 solids with a `60.9235229 x 132.0163877 x 54.2000002 mm` native-coordinate bounding box.
- Both manufacturer PDF sets were visually inspected. No native coordinate was accepted as a Project Button assembly transform.
- Twelve `GAH-*` selection holds remain `OPEN`; all six `GSI-*` interface rows are `SELECTION REQUIRED` or unverified.

## Repository validation

All 63 unique checker programs passed:

- 55 workspace-Python checks;
- five controlled CadQuery checks;
- three KiCad 10.0.5 `pcbnew` runtime checks; and
- 47 executable firmware unit tests inside the firmware checker, with no target flash or HIL.

The deterministic staged release manifest contains 1,482 package files after this record is included. It identifies a reviewable configuration only; `EG-002` remains partial pending immutable acceptance.

The intentional command `python tools/check_energization_gates.py --through-stage E2 --require-ready` returned exit code 2. All 21 gates applicable through E2 are partial, none is closed, and the package correctly refuses a readiness claim. Across the complete register, all 30 energization gates remain unresolved.

## Web-guide QA

The interactive guide was rendered in installed Google Chrome at 1,440 x 1,100 and 390 x 844 viewports. The desktop viewport had no page-width overflow; the mobile layout reflowed to one card column and retained table-local horizontal scrolling. Computed body, secondary and badge text sizes were 16 px, 14 px and 12 px. All three candidates rendered, the filter controls are keyboard-native buttons, and the warning remained visible. The guide passed source-level interaction checks and rendered visual inspection for clipping, contrast and legibility.

No gripper was selected or purchased. No adapter, wire, circuit, firmware command, guard or physical result was released. No requirement, risk, fabrication gate, motion gate or energization gate closed.
