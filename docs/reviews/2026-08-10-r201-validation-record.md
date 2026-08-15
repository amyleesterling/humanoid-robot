# R201 validation record

**PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION**

## Native electrical source

- KiCad: 10.0.5.
- Project: `electrical/kicad/hr-v0-runtime-observation-interface-p0.1/hr-v0-runtime-observation-interface-p0.1.kicad_pro`.
- Parse/export: root plus four child sheets succeeded.
- Native netlist: 33 component blocks and 33 nets.
- ERC: 0 errors / 0 warnings. The report records ignored checks for single-use global labels, four-way joins, SPICE models and footprint filters; ERC establishes encoded connectivity/annotation only.
- Browser-readable exports: root plus four child SVGs generated. The guide uses 16 px body/functional text, 14 px secondary text, responsive tables and horizontal reflow. Local in-app-browser navigation to the unpublished file tree was blocked by browser security policy, so post-deployment visual inspection remains open; source paths, file presence and encoded legibility minima were checked.

## Calculation screens reproduced

- TI ISO1212 input: 2.05 to 2.75 mA with 562 ohm RSENSE over the applicable less-than-30 V sense range.
- SRA1/K1/K2 total channel load: 10.41 to 12.18 mA using 22.8/25.2 V rail limits and 2.70 kohm +/-1% shunts.
- K1/K2 at Schneider's 17 V signalling minimum: 8.28 mA minimum screen, above 5 mA.
- Shunt power: 0.238 W maximum, 47.6% of the 0.5 W 70 C rating before installed derating.
- Pilz residual-voltage screen across nominal 2.70 kohm: 0.27 V maximum.
- SR1 catalog-only aggregate: 7 mA IDEC family value plus 2.75 mA receiver = 9.75 mA, leaving 10.25 mA to Pilz's 20 mA limit. Received H1 current and 17.8 V brightness remain open.
- Proposed 3.3 V logic load: no more than 5.0 mA calculation screen; Raspberry Pi source/application acceptance remains open.

## Package checker

`tools/check_hr_v0_runtime_observation_interface_p01.py` passes and confirms five native sheets, 33 components, 33 nets, ERC 0/0, four diagnostic channels, exactly three shunts, separate field/compute returns, floating SUB nets, seven current primary-source records including both Phoenix terminal candidates, four SVGs, ten open holds, legibility minima and no inferred Pi pins.

## Repository regression

- The first complete standard-runtime sweep passed 141/144 checkers and exposed exactly three controlled stale dependencies: the release-candidate hash in configuration reconciliation, the release-candidate hash in the build traveler, and the not-yet-staged deterministic release manifest. Both hash-bound packages were regenerated; no failure was suppressed.
- Supervisor tests: 67/67 passed. Watchdog tests: 11/11 passed. Total firmware source tests: 78/78. No target flash or physical execution occurred.
- Host tests: 16/16 passed. The committed preflight remains fail-closed with 45 explicit holds and no motion authority.
- Native KiCad `pcbnew` checker sweep under KiCad 10.0.5 Python: 13/13 passed.
- `check_energization_gates.py --through E2 --require-ready` returned its documented non-ready exit 2: 0/21 gates closed and all 21 partial.
- After deliberate staging, deterministic manifest regeneration and the final sweep, all 144/144 standard-runtime checkers passed. These are source/configuration checks only.
- The deterministic release manifest contains 3,431 staged package files and passes its dedicated checker; it does not imply release acceptance.

## Release boundary

No PCB, footprint/placement/layout release, harness, exact Pi GPIO/header pin, accepted insulation/grounding/EMC/thermal/fault evidence, physical article or qualified review exists. All ten interface holds and all pre-existing system gates remain open. No result in this record authorizes procurement, fabrication, assembly, connection, powered testing, motion or energization.
