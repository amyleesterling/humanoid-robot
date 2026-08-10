# R93 validation record — X430 integrated arm P0.9

> **PRELIMINARY — NOT APPROVED FOR QUOTATION, PROCUREMENT, FABRICATION, ASSEMBLY, MOTION, CONNECTION, OR ENERGIZATION.**

Date: 2026-08-08
Configuration: `HR-V0-ARM-ARCH-P0.9-X430-INTEGRATED-CANDIDATE`

## Generated evidence

- full shoulder-column-to-H104 STEP and interactive GLB;
- separately identified P09-C01/P09-C02 STEP and review drawings;
- 9,464-pose full-arm collision sweep;
- 69-pair adaptive continuous-clearance summary and 130-cell certificate;
- 61-row hard-stop approach sweep;
- transform and interface schedules;
- four-row fastener-stack requirement register;
- five-row tolerance-control register;
- mass/load screen and twelve-hold disposition.

## Controlled results

- exact source geometry checks passed during generation;
- maximum sampled nonintentional intersection through J2 115°: 0 mm³;
- continuous domain: J1 −20°…70°, J2 15°…115°;
- required nominal continuous clearance: 0.750 mm;
- minimum guaranteed nominal clearance: 0.862928 mm;
- continuous pair/cell/exact-call counts: 69 / 130 / 85;
- nominal first metal stop contact: 117.999977°;
- incomplete mass/headroom: 577.091 g / 172.909 g;
- hold state: 8 OPEN / 4 PARTIAL / 0 CLOSED;
- P0.7 remains controlled; XM430 is not selected; all nine release flags are false.

## Automated checks

`tools/check_hr_v0_x430_integrated_arm.py` passes. All 42 non-manifest `check_hr_v0_*.py` checkers pass using the controlled general, CadQuery or KiCad Python runtime as applicable. Traceability passes with 81 requirements, 40 risks, 109 procedures and 56 document references. The energization-gate schema passes with 30 unresolved gates: 22 PARTIAL and 8 OPEN; `--require-ready` returns exit 2 as required. Manifest and clean exact-commit results are bound to the immutable commit containing this record. None of these checks constitutes physical verification.

## Interactive-guide QA

- desktop viewport: 17 px body, 16 px tables, 13 px badges, no page overflow;
- mobile 390 × 844: 16 px body, 16 px tables, 13 px badges, no page overflow;
- integrated 10.44 MB GLB loaded and rendered visibly;
- stop slider updated from 115.0° to 120.0°, placed the marker at 93.75%, and displayed the excluded-region warning;
- browser console: zero errors or warnings.

## Release boundary

The continuous certificate covers nominal rigid solids only through the software limit. It excludes tolerances, fastener projections, connectors, cables, strain relief, guards, deformation, compliance and stopping travel. No physical fit, stop, mass, COM, inertia, structural, actuator, electrical, firmware, safety or qualified-review evidence is closed. No quotation, purchase, fabrication, assembly, connection, motion or energization is authorized.
