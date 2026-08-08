# R96 validation record — P1.1 X430 load basis

> **PRELIMINARY — NOT APPROVED FOR QUOTATION, PROCUREMENT, FABRICATION, ASSEMBLY, MOTION, CONNECTION, OR ENERGIZATION.**

Date: 2026-08-08
Configuration: `HR-V0-ARM-LOAD-P1.1-X430-CANDIDATE`

## Generated evidence

- seven-row component evidence ledger;
- 401-row 0.25° gravity envelope;
- twenty inertia/energy sensitivity rows;
- sixteen stop moment/energy sensitivity rows;
- four SHA-bound source records;
- ten-row open-input register;
- fail-closed package status with twelve false release flags.

## Controlled analytical results

- known exact/catalog-estimated subset: 143.485169 g;
- incomplete reference allocation: 453.485169 g;
- known nominal / geometry-support inertia: 0.000650235102 / 0.000921987948 kg·m²;
- incomplete point / support-plus-point reference inertia: 0.006303990877 / 0.006575743723 kg·m²;
- maximum incomplete-reference gravity: 0.483257699 N·m at J2=15°;
- 2.25× / three-times-proof screen inputs: 1.087329823 / 3.261989468 N·m;
- four nominal stop contacts at 45.604835001 mm radius;
- one-rail static equivalent of the incomplete proof screen: 71.527272672 N;
- open inputs: 10;
- mass, COM, inertia, continuous torque, stop load, structure and every authorization flag: false.

## Automated and interactive status

`tools/check_hr_v0_x430_load_basis.py` passes. All 45 non-manifest `check_hr_v0_*.py` checkers pass using the controlled general, CadQuery or KiCad Python runtime as applicable. Traceability passes with 81 requirements, 40 risks, 109 procedures and 56 document references. The energization-gate schema passes with 30 unresolved gates: 22 PARTIAL and 8 OPEN; `--require-ready` returns exit 2 as required. The CAD source manifest contains 307 hashed generated artifacts. Release-manifest and clean exact-commit results are bound to the immutable commit containing this record. None of these checks constitutes physical verification.

## Interactive-guide QA

- desktop direct page: 17 px body and table text, 13 px minimum functional text, and no horizontal overflow;
- 390 px mobile iframe: 16 px body and table text, 13 px minimum functional text, and no horizontal overflow;
- J2 angle, speed, stroke and applied-moment sliders updated the gravity, energy and one-rail static-equivalent outputs;
- direct guide diagnostics: zero errors or warnings;
- the mobile iframe rendered and measured correctly, but the browser QA host emitted one iframe-only `MutationObserver.observe` instrumentation error. No corresponding guide script error was observed. This harness diagnostic is disclosed and is not treated as a clean mobile-console result.

## Release boundary

No numeric total includes FR12-H101/idler, moving hardware/harness or complete gripper distribution. No reference inertia is a complete upper bound. No energy/stroke force is a peak. Speed, drive inertia, bumper/contact dynamics, material allowables, proof acceptance and measurement uncertainty remain open. No external work or energization is authorized.
