# R135 independent mechanical parity review request

> **PRELIMINARY - NOT APPROVED FOR QUOTATION, FABRICATION, ASSEMBLY, MOTION, OR ENERGIZATION.**

Review `HR-V0-MECH-PARITY-P0.1` against `HR-V0-ARM-ARCH-P0.7` and parent `HR-V0-MECH-DFM-DATA-P0.1`. This is an accuracy and completeness review, not supplier or fabrication authority.

## Reproduce

```powershell
& 'C:\Users\amyle\Documents\New project\.venvs\hr-v0-cad\Scripts\python.exe' tools/generate_hr_v0_mechanical_parity.py
& 'C:\Users\amyle\Documents\New project\.venvs\hr-v0-cad\Scripts\python.exe' tools/check_hr_v0_mechanical_parity.py
```

## Inspect

- `docs/hr-v0-mechanical-parity-p0.1.md`
- `release/hr-v0/mechanical-parity-p0.1/profile-parity.csv`
- `release/hr-v0/mechanical-parity-p0.1/feature-parity.csv`
- `release/hr-v0/mechanical-parity-p0.1/drawing-control-coverage.csv`
- `release/hr-v0/mechanical-parity-p0.1/finding-register.csv`
- `release/hr-v0/mechanical-parity-p0.1/package-status.json`
- `release/hr-v0/mechanical-parity-p0.1/index.html`
- all five referenced STEP/DXF/drawing triplets

## Required questions

1. Independently reproduce all STEP bounding extents, solid counts, thicknesses, cylinder/cone-edge positions and C07 face-recess depth.
2. Reparse every DXF entity and confirm all thirty exact holes and eight controlled-upper-limit countersink matches.
3. Determine whether modeling the Ø11.30 +0.10/-0.00 countersink at Ø11.40 in STEP is acceptable model-based-definition practice here or must be corrected to nominal.
4. Determine whether C06/C07 pre-fillet DXFs plus finished STEP are unambiguous enough for DFM, or whether finished-profile DXFs and conventional drawings are required.
5. Review all twenty-six drawing-control bindings and identify any feature, datum, tolerance, material, process, inspection or acceptance control still missing or ambiguous.
6. Challenge the classification of six controls as schedule-bound and decide whether released supplier drawings must display them graphically.
7. Confirm that the interactive feature maps accurately render the DXF entities without implying finished C06/C07 fillet geometry.
8. Verify that no artifact can reasonably be mistaken for a machining or fabrication release.

Return `BLOCKER / MAJOR / MINOR` findings with exact part, path, feature/control ID and evidence. Separately state readiness for qualified mechanical review, provider DFM inquiry, fabrication, physical proof and energization. Do not infer approval from checker success.
