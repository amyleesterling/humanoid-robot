# R136 independent countersink model-definition review request

> **PRELIMINARY - NOT APPROVED FOR QUOTATION, FABRICATION, ASSEMBLY, MOTION, OR ENERGIZATION.**

Review `HR-V0-CSK-MBD-P0.1` and the nonselected `HR-V0-ARM-ARCH-P0.8-CSK-MBD-CANDIDATE` against controlled `HR-V0-ARM-ARCH-P0.7`, R134 and R135. This is an accuracy and completeness review, not supplier or fabrication authority.

## Reproduce

```powershell
& 'C:\Users\amyle\Documents\New project\.venvs\hr-v0-cad\Scripts\python.exe' tools/generate_hr_v0_countersink_mbd.py
& 'C:\Users\amyle\Documents\New project\.venvs\hr-v0-cad\Scripts\python.exe' tools/check_hr_v0_countersink_mbd.py
```

## Inspect

- `docs/hr-v0-countersink-mbd-p0.1.md`
- `release/hr-v0/countersink-mbd-p0.1/part-comparison.csv`
- `release/hr-v0/countersink-mbd-p0.1/feature-certificate.csv`
- `release/hr-v0/countersink-mbd-p0.1/decision-register.csv`
- `release/hr-v0/countersink-mbd-p0.1/finding-register.csv`
- `release/hr-v0/countersink-mbd-p0.1/package-status.json`
- `release/hr-v0/countersink-mbd-p0.1/index.html`
- all four candidate STEP files under `cad/hr-v0/generated/countersink-mbd-p0.1/`

## Required questions

1. Independently derive the included angle represented by P0.7's Ø11.40 mm major diameter, Ø5.50 mm minor diameter and 3.10 mm axial depth.
2. Independently prove that Ø11.30 mm, Ø5.50 mm and 2.90 mm axial depth define a 90° included cone.
3. Re-import all four candidate STEP files and verify one-solid topology, two Ø11.30 mm cone openings at X=0/Z=±10 mm and unchanged external bounding envelopes.
4. Decide whether a controlled STEP should represent nominal geometry while tolerance lives in drawing/MBD controls, or whether another explicit convention is required.
5. Decide whether Ø11.40 maximum diameter and 3.10 mm maximum depth are valid as independent conservative screens; do not interpret them as a single exact 90° manufactured cone.
6. Review the selected M5 candidate, permitted countersink range, head-seat contact, flushness, residual material and functional gauge plan.
7. Identify every downstream CAD, mass, collision, drawing, DFM, manifest and release hash that must be regenerated if P0.8 is selected.
8. Verify that no artifact can reasonably be mistaken for supplier, quotation, fabrication, assembly, motion or energization authority.

Return `BLOCKER / MAJOR / MINOR` findings with exact part, file and feature. State separately whether P0.8 may be selected into configuration control and what physical evidence remains mandatory.
