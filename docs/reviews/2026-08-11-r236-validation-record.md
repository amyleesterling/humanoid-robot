# R236 validation record

> **PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION**

Configuration: `HR-V0-EVID-LOG-P0.1`

Validation date: 2026-08-11

R236 validation is source/repository validation only. The focused checker validates fourteen event classes, ten clock-budget rows, twelve blank calibration records, fifteen unexecuted tests, fifteen open holds, strict package manifests and the committed 49-hold host preflight. Supervisor/logging unit tests cover exclusive creation, context validation, canonical finite JSON, monotonic regression, tamper detection, chain verification, clean/truncated close and runtime logging failure during active motion.

## Executed repository validation

- Standard repository checker sweep: **179/179 PASS** using the controlled Python/CadQuery validation environment.
- Native `pcbnew` checker sweep under KiCad 10.0.5 Python: **18/18 PASS**.
- Firmware source validation: **86/86 PASS**, comprising 75 supervisor/runtime/logging tests and 11 watchdog tests.
- Host source validation: **16/16 PASS**; the disabled overlay contains 22 controlled files and the current preflight exits fail-closed with 49 holds.
- R236 focused package check: **PASS** with fourteen event classes, ten open clock-budget records, twelve blank calibration records, fifteen unexecuted tests and fifteen open holds.
- Release manifest generation: **4,774 package files**; final manifest and clean-tree verification are performed after this record is staged in the release commit.
- Interactive guide QA: desktop rendering at 1280 x 720, section navigation, `#holds` deep link, fourteen event cards, fifteen test rows and two horizontally scrollable tables were inspected. The minimum visible text measured 16 CSS px. Responsive media rules and table overflow were checked statically; an actual narrow-browser viewport was not executed.

No target clock, calibrated instrument, installed image, physical interface, hardware-in-the-loop run, powered test or safety validation was executed. The software evidence is not proof of stopping performance, functional-safety integrity, electrical suitability or physical readiness.

Sol M-022 remains `PARTIALLY_ADDRESSED_OPEN`; all affected gates remain unresolved.
