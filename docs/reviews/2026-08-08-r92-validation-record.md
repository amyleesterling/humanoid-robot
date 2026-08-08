# R92 validation record — exact-coordinate X430 elbow P0.8

> **PRELIMINARY — NOT APPROVED FOR QUOTATION, PROCUREMENT, FABRICATION, ASSEMBLY, MOTION, CONNECTION, OR ENERGIZATION.**

Date: 2026-08-08

Configuration: `HR-V0-ARM-ARCH-P0.8-X430-CANDIDATE`

Disposition: comparison candidate only; P0.7 remains controlled and XM430 is not selected.

## Trigger and correction

R91 required an exact-coordinate X430/FR12 comparison before the held P0.7 metal route could be dispositioned. R92 creates that native comparison and corrects a datum error found during development: the FR12-S102 bounding box does not directly express its assembled distance from J2.

The controlled generator verifies the X430 rear case axes, S102 side axes and H101 link axes. Registering the S102 side axes to the X430 rear case requires a `+21 mm` local-Z frame shift and produces a 40.5 mm fixed-face offset. The rejected bounding-box-only reading would have used 19.5 mm.

## Manufacturer-document inspection

The official one-page FR12-H101K and FR12-S102K reference drawings were rendered at full resolution and visually inspected. Both drawings are dated 2026-01-07, use millimetres and are marked as reference drawings. The selected STEP axes were checked against the dimensioned patterns rather than taken from the raster alone.

The official twelve-page OpenMANIPULATOR-X Assembly Manual was inspected at pages 8–13. The manual PDF reports creation/modification 2019-03-25, Adobe PDF Library 10.0.1, A4 pages, no encryption, form or JavaScript. The assembly sequence confirms the X430/FR12 relationship used to challenge the first local-origin interpretation. This precedent does not approve the Project Button topology.

## Generated evidence

- integrated native STEP and GLB elbow comparison;
- two separately identified P08-C01/P08-C02 part STEP files and review-only SVG drawings;
- three exact feature records, three transform records and three interface records;
- 221 nominal rigid-body samples from J2 15° through 125° at 0.5° increments;
- 61 stop-approach samples from 115° through 118° at 0.05° increments;
- nominal first metal contact at 117.999991°;
- zero nonintentional positive-volume intersection in the sampled model through the 115° soft limit and 118° stop target;
- first sampled nonintentional positive-volume intersection at 120°;
- X430/S102 and X430/H101 candidate assembly-model overlaps separately exposed for independent audit rather than hidden;
- 577.091 g incomplete known/CAD-estimated subtotal and 172.909 g provisional headroom;
- 0.491 N m incomplete elbow gravity result, 1.104 N m 2.25 screen and 3.713 catalog stall-endpoint ratio only; and
- nine OPEN and three PARTIAL architecture holds, with zero closed.

The 2° nominal interval from modeled stop contact to the next sampled collision is not accepted as a tolerance, stopping or uncertainty budget. No continuous collision certificate exists for P0.8, and no cable, connector, strain relief, bumper or guard geometry is included.

## Interactive-guide QA

The generated GLB loaded in the in-app browser and the user could orbit and zoom it. The default desktop view showed 17 px body text, 16 px table text and 13 px badges with no horizontal page overflow. The model framing was adjusted to show the complete elbow/link candidate at a useful scale.

At a 390 × 844 viewport, computed body/table/badge sizes were 16/16/13 px, the page client and scroll widths were both 375 px, and the model viewer reflowed to 341 px without page overflow. The angle control resolved uniquely; changing it from 115° to 120° updated the output to `120.0°`, placed the marker at 93.75%, and displayed the excluded-collision-region message. The console reported zero warnings or errors.

## Executed validation

- `tools/generate_hr_v0_x430_elbow_architecture.py`: PASS with CadQuery 2.8.0;
- `tools/check_hr_v0_x430_elbow_architecture.py`: PASS;
- interactive inline JavaScript syntax: PASS;
- 41 non-manifest `check_hr_v0_*.py` checks: PASS after using KiCad 10.0.5 bundled Python for the three `pcbnew` checks and the controlled CadQuery interpreter for the three generator-importing checks;
- `tools/check_hr_v0_cad.py`: PASS after refreshing the generated source manifest to include all fifteen P0.8 package files;
- `tools/check_traceability.py`: PASS — 81 requirements, 40 risks, 109 procedures and 56 release/walking-document procedure references resolve;
- `tools/check_energization_gates.py`: deliberately NOT READY — all 30 gates unresolved, with 22 partial and 8 open;
- through E2: all 21 applicable gates remain partial; `--require-ready` returns 2 as required; and
- `git diff --check`: PASS.

The first broad checker pass correctly failed P0.8 source-manifest parity and three interpreter selections. Those were tooling/configuration failures, not suppressed results: the generated source manifest was refreshed, the three CadQuery-dependent checkers were rerun with the controlled CAD interpreter, and all four checks then passed.

## Remaining evidence

Independent transform and assembly-overlap audit; received X430/FR12/H104 identity and fit; exact fastener selection and access; complete calibrated mass/COM/inertia; continuous/cyclic torque and thermal data; installed branch-current, connector, conductor and protection evidence; continuous collision proof including cables/connectors/strain relief/guard/tolerances/deformation; bumper selection and retention; physical stopping/overtravel/rebound; structural calculations and proof; firmware/calibration and electrical-source synchronization; physical build; fault injection; and qualified mechanical/electrical/controls/functional-safety disposition all remain open.

R92 closes zero energization gates and provides no quotation, procurement, fabrication, assembly, motion, connection or energization authority.
