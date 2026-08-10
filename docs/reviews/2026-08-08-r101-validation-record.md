# R101 validation record — X430 fixture support route P0.1

> **PRELIMINARY — NOT APPROVED FOR QUOTATION, PROCUREMENT, MACHINING, FLOOR WORK, ASSEMBLY, POWERED TEST, MOTION, OR ENERGIZATION.**

R101 replaces R99's generic base/upright envelope with a sourced support inquiry path without inventing pedestal or anchor geometry. It identifies `40200-SP-K` at the published 300 mm height and `40006-BP` as nonselected evaluation candidates, rotates the controlled P0.2 sensor/X430 stack to a vertical axis, and defines `FX101-C01` central machining only as review geometry.

The package records four topology dispositions, six candidate/selection-required BOM rows, four arithmetic screens, eight unsent RFIs, four current primary-source records, ten open holds and ten false release flags. Weighted/mobile rating transfer is rejected and clamp-only support is prohibited.

`tools/check_hr_v0_x430_fixture_support.py` passes. It verifies the topology dispositions, catalog ratio, vertical-gravity boundary, provisional engagement arithmetic, absent pedestal CAD, mandatory horizontal test, unsent RFIs, open holds and false flags.

Repository-wide validation after regeneration:

- 50 non-manifest `check_hr_v0*.py` checkers executed with their controlled Python/KiCad/CadQuery runtimes: 50 passed, 0 failed;
- traceability: 81 requirements, 40 risks, 109 verification procedures and 56 release/walking-document procedure references resolve;
- energization gates through E2: 21 applicable, 0 closed and 21 partial — `NOT READY`;
- source diff whitespace check: passed; and
- the release manifest is regenerated at 1,282 package files; clean-clone identity is checked after the R101 commit.

The GLB/STEP contain a 300 mm height datum rather than invented pedestal body geometry. No supplier contact, quote, order, floor survey, drilling, anchor, controlled pedestal CAD, modified-plate DFM, physical result, guard/catch/load device or work authorization exists.

All release flags remain false.
