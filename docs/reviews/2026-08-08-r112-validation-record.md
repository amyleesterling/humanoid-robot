# R112 validation record - direct gripper adapter and ordinary-control interface

Status: **PRELIMINARY - NOT RELEASED FOR PROCUREMENT, FABRICATION, CONNECTION, MOTION, OR ENERGIZATION**

R112 issues `HR-V0-GRIP-ADAPT-P0.1` and `HR-V0-GRIP-ELEC-P0.1`. Pololu item 3551, item 1350 and item 2859 remain preferred evaluation candidates only.

## Mechanical validation

- Generated adapter STEP/STL and four-solid adapter-plus-gripper STEP/GLB parse under the controlled CadQuery runtime.
- Adapter bounding box: `40.0 x 28.5 x 40.0 mm`; volume `9,366.558784 mm3`; calculated mass `25.289709 g`.
- The nominal assembly contains no adapter/manufacturer-solid intersection. Recorded minimum separations are `0.300`, `8.122` and `11.161 mm`.
- Twelve `PAH-*` holds remain open; all procurement/fabrication/assembly/motion/energization flags remain false.

## Electrical validation

- Five new Pololu manufacturer payloads were checked by byte count and SHA-256.
- KiCad 10.0.5 parsed the root and child schematic, exported a netlist/PDF/SVG and returned ERC `0 errors / 0 warnings`.
- The connected PG candidate was specifically rechecked: D24V22F6 PG, the 10 kOhm pull-up and Maestro CH2 share `GRIP_PG_SENSE`; EN remains an isolated no-connect.
- Visual PDF QA forced the child sheet from A3 to A4 and reduced the note block after the initial export showed clipping. The KiCad export remains a diagnostic engineering artifact; the web guide is the human-facing presentation.

## Web-guide QA

The electrical guide rendered in installed Google Chrome at `1440 x 1100` and `390 x 844`. Both viewports had zero page-width overflow. Computed body, secondary and badge text were `16 px`, `14 px` and `14 px`. All four native buttons worked and the reset view changed the diagram state. Desktop and mobile screenshots were visually inspected; the mobile layout reflowed to one column and the warning remained visible.

The adapter guide rendered at the same two viewports through a local HTTP origin. The GLB reported visible at both sizes, body text computed to `16 px`, page-width overflow was zero, and desktop/mobile screenshots were visually inspected. The mobile metrics reflowed to one column and the detailed table retained local horizontal scrolling rather than shrinking its text.

## Release boundary

These packages close zero requirements and zero energization gates. They add source-controlled evidence and expose the exact remaining work. The adapter, gripper, controller and regulator are not selected; no physical connector pin order, fuse, wire, carrier, setting, HIL result or proof test is released. Qualified mechanical, electrical and functional-safety review remains required.

## Repository validation

All 65 unique checker programs passed:

- 55 workspace-Python checks;
- seven controlled CadQuery checks;
- three KiCad 10.0.5 `pcbnew` checks; and
- 47 compiled firmware unit tests inside the firmware checker, with no target flash or HIL.

The deterministic staged release manifest contains 1,527 package files. It identifies a reviewable configuration only; `EG-002` remains partial pending immutable acceptance.

The intentional command `python tools/check_energization_gates.py --through-stage E2 --require-ready` returned exit code 2. All 21 gates applicable through E2 remain partial and none is closed; all 30 total gates remain unresolved. The package correctly refuses a readiness claim.
