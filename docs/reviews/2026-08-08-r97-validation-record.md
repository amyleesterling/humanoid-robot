# R97 validation record — FR12 moving-mass metrology P0.1

> **PRELIMINARY — NOT APPROVED FOR PURCHASE, ASSEMBLY, FABRICATION, MOTION, CONNECTION, OR ENERGIZATION.**

Date: 2026-08-08

Configuration: `HR-V0-FR12-MASS-MET-P0.1`

## Controlled results

- exact manufacturer STEP: one solid, 2,854.117032 mm³ frame-only volume;
- uniform-geometry centroid: X=0.000000, Y=20.046637, Z=0.000000 mm;
- conservative frame-only bounding radius about J2 X: 30.463092 mm;
- official `0.10 lb` FR12 kit and `0.20 lb` included idler-set commerce fields: rejected for mass credit;
- twelve-operation unpowered measurement route with two open hard holds;
- three blank result rows and thirty blank raw repeat rows, all `NOT EXECUTED`;
- twenty-five mass/radius bound sensitivities, none promoted as a measured value or acceptance limit;
- `LOAD-OPEN-01`, mass, COM, inertia, selection and every authorization flag remain false/open.

## Automated and interactive status

`tools/check_hr_v0_fr12_mass_metrology.py` passes. All 46 non-manifest `check_hr_v0_*.py` checkers pass using the controlled general, CadQuery or KiCad Python runtime as applicable. Traceability passes with 81 requirements, 40 risks, 109 procedures and 56 document references. The energization-gate schema passes with 30 unresolved gates: 22 PARTIAL and 8 OPEN; `--require-ready` returns exit 2 as required. The CAD source manifest contains 314 hashed generated artifacts. Release-manifest and clean exact-commit results are bound to the immutable commit containing this record. None of these checks constitutes physical verification.

## Interactive-guide QA

- desktop direct page: 16 px body/table text, 13 px minimum annotation text and no horizontal overflow;
- 390 px mobile frame: 16 px body/table text, 13 px minimum annotation text and no horizontal overflow;
- the mass/radius calculator updated to 0.000101250000 kg·m² and 0.022065 N·m for the entered 50 g / 45 mm exploratory values;
- the reaction calculator updated to 50.000 mm for the entered 10 g / 30 g reactions, 120 mm span and −40 mm support-A datum;
- desktop and mobile browser diagnostics: zero errors or warnings.

## Release boundary

No article exists and no purchase/work authorization exists. The package defines a physical evidence route; it does not execute it. It does not include reflected drive inertia, complete moving hardware/harness, gripper distribution, bumper behavior, continuous torque or physical stop evidence.
