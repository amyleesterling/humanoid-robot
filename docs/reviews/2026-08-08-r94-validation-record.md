# R94 validation record — X430 arm P1.0 clearance candidate

> **PRELIMINARY — NOT APPROVED FOR QUOTATION, PROCUREMENT, FABRICATION, ASSEMBLY, MOTION, CONNECTION, OR ENERGIZATION.**

Date: 2026-08-08
Configuration: `HR-V0-ARM-ARCH-P1.0-X430-CLEARANCE-CANDIDATE`

## Generated evidence

- full-arm STEP and interactive GLB with separately named relieved striker;
- P10-C02 part STEP and review drawing;
- 413-row exact X430-clearance/stop-gap sweep at 0.25°;
- SHA-bound certificate supersession basis;
- complete 69-pair / 136-cell continuous certificate;
- six-row stop-sequencing tolerance budget;
- mass comparison, hold register and fail-closed package status.

## Controlled results

- 60 identical-solid P0.9 certificates retained;
- all nine changed-striker pair groups recomputed at a 3.000 mm requirement;
- changed-pair conservative minimum: 3.242248 mm;
- all-pair conservative minimum: 1.040321 mm;
- exact B-Rep distance calls: 94;
- nominal first stop contact: 117.999977°;
- exact X430 clearance: 3.942108 mm at 115° and 2.491516 mm at stop contact;
- physical residual requirement: 1.000 mm;
- maximum combined adverse variation: ≤1.491516 mm, unallocated and unproved;
- moving-striker CAD estimate: 51.184 g;
- incomplete subtotal/headroom: 576.040 g / 173.960 g;
- holds: 8 OPEN / 4 PARTIAL / 0 CLOSED;
- P0.7 remains controlled; P0.9/P1.0 are unselected; all ten release flags are false.

## Automated checks

`tools/check_hr_v0_x430_clearance_arm.py` passes. All 43 non-manifest `check_hr_v0_*.py` checkers pass using the controlled general, CadQuery or KiCad Python runtime as applicable. Traceability passes with 81 requirements, 40 risks, 109 procedures and 56 document references. The energization-gate schema passes with 30 unresolved gates: 22 PARTIAL and 8 OPEN; `--require-ready` returns exit 2 as required. Manifest and clean exact-commit results are bound to the immutable commit containing this record. None of these checks constitutes physical verification.

## Interactive-guide QA

- desktop 1280 x 720: 17 px body, 16 px tables, 13 px badges and no page overflow;
- mobile 390 x 844: 16 px body, 16 px tables, 13 px badges and no page overflow;
- the P1.0 GLB loaded and rendered visibly in the embedded model viewer;
- the stop slider updated to 118.5 degrees, placed the marker at 96.4286% and displayed the at-or-beyond-contact warning;
- browser console: zero errors or warnings.

## Release boundary

The ≤1.491516 mm limit has no accepted allocation. Material, machining, fasteners, received registration/runout, play, calibration, wear, temperature, deformation, bumper behavior and measurement uncertainty remain open. Cables, connectors, guards, gripper, complete mass/COM/inertia, actuator behavior, physical stops/stopping and qualified review are also open. No external work or energization is authorized.
