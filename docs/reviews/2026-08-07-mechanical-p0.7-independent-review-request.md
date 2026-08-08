# Independent review request — HR-V0 mechanical P0.7/P0.6 positive-stop candidate

> **PRELIMINARY—NOT APPROVED FOR QUOTATION, FABRICATION, ASSEMBLY, MOTION, OR ENERGIZATION.**

Review `HR-V0-ARM-ARCH-P0.7`, `HR-V0-MECH-P0.6`, `HR-V0-HS-P0.3`, `HR-V0-J2-STOP-P0.1`, and the synchronized P0.4/P0.3 firmware binding for accuracy and completeness.

Please independently check:

1. C06/C07 manufacturability, datum scheme, face step, profile fillets, tool access, stress raisers, contact location and load path.
2. Whether two-rail sharing is credible and what prying, local contact, impact, fatigue, unequal sharing and parent-joint analyses are required.
3. The 117.999985° contact calculation, 115° gaps, 121.643289° body-contact result, and the complete tolerance/uncertainty budget.
4. Whether the maximum bumper envelope is an adequate space reservation without implying a component selection; specify evidence needed to select a bumper.
5. The intentional-pair exclusion and all 69 non-intentional pair certificates; confirm no unrelated collision was masked.
6. Cable/guard/fastener/service envelopes and all missing physical inputs.
7. Exact consistency among STEP, GLB, DXF, SVG, CSV, JSON, mechanical release, firmware binding, tests and release metadata.
8. Whether the package remains fail closed and clearly avoids fabrication, motion, energization or functional-safety approval claims.

Run:

```powershell
& 'C:\Users\amyle\Documents\New project\.venvs\hr-v0-cad\Scripts\python.exe' tools/check_hr_v0_arm_architecture.py
& 'C:\Users\amyle\Documents\New project\.venvs\hr-v0-cad\Scripts\python.exe' tools/check_hr_v0_mechanical_release.py
& 'C:\Users\amyle\Documents\New project\.venvs\hr-v0-cad\Scripts\python.exe' tools/check_hr_v0_firmware.py
```

Report BLOCKER / MAJOR / MINOR findings with exact file, part/control ID, input assumptions, calculation units, proposed correction and evidence required to close. Do not treat clean source checks as physical verification.
