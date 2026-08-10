# R95 validation record — X430 lowered-forearm P1.1

> **PRELIMINARY — NOT APPROVED FOR QUOTATION, PROCUREMENT, FABRICATION, ASSEMBLY, MOTION, CONNECTION, OR ENERGIZATION.**

Date: 2026-08-08
Configuration: `HR-V0-ARM-ARCH-P1.1-X430-LOWERED-FOREARM-CANDIDATE`

## Generated evidence

- full-arm STEP and interactive GLB;
- separately controlled P11-C02 STEP and review drawing;
- 30-pair SHA-bound certificate retention plus 39 changed-solid recomputations;
- complete 69-pair / 140-cell continuous certificate;
- 413-row exact 0.25° stop sweep;
- transform register, feature screen, tolerance allocation, mass comparison and hold register.

## Controlled nominal results

- J2 axis / moving face: Y=191.550 / 219.550 mm;
- forearm-member, distal adapter and H104 offset: Z=−7.000 mm;
- member axes: Z=+3 / −17 mm;
- M5 countersink edge land: 4.300 mm nominal;
- critical X430/striker guaranteed commanded-domain clearance: 4.798163 mm against 4.750 mm;
- all-pair conservative minimum: 1.313579 mm against 0.750 mm;
- nominal first contact: 117.999977°;
- exact X430 clearance: 4.875499 mm at 115° and 4.369402 mm at contact;
- physical residual requirement / proposed adverse allocation / nominal remainder: 1.500 / 2.500 / 0.369402 mm;
- incomplete subtotal/headroom: 583.138 / 166.862 g;
- holds: 8 OPEN / 4 PARTIAL / 0 CLOSED;
- P0.7 remains controlled; P1.1/X430 are unselected; all ten release flags are false.

## Automated checks

`tools/check_hr_v0_x430_lowered_forearm.py` passes. All 44 non-manifest `check_hr_v0_*.py` checkers pass using the controlled general, CadQuery or KiCad Python runtime as applicable. Traceability passes with 81 requirements, 40 risks, 109 procedures and 56 document references. The energization-gate schema passes with 30 unresolved gates: 22 PARTIAL and 8 OPEN; `--require-ready` returns exit 2 as required. The CAD source manifest contains 299 hashed generated artifacts. Release-manifest and clean exact-commit results are bound to the immutable commit containing this record. None of these checks constitutes physical verification.

## Interactive-guide QA

- desktop 1280 × 720: 17 px body, 16 px tables, 13 px badges, 504 px model viewer and no page overflow;
- mobile 390 × 844 frame: 16 px body, 16 px tables, 13 px badges, 470 px model viewer and no page overflow;
- the 10.44 MB P1.1 GLB loaded and rendered visibly;
- the stop slider updated to 118.5°, placed the marker at 96.4286% and displayed the at-or-beyond-contact warning;
- desktop and mobile browser diagnostics: zero errors or warnings.

## Release boundary

The 2.500 mm allocation is a set of unverified rejection limits, not achieved tolerance evidence. Material, DFM, FAI, received registration/runout, play, calibration, fasteners, deformation, bumper, stopping, cables, connectors, guards, gripper, complete mass/COM/inertia, actuator behavior and qualified review remain open. No external work or energization is authorized.
