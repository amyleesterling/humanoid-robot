# R137 independent conventional drawing review request

> **PRELIMINARY - NOT APPROVED FOR QUOTATION, FABRICATION, ASSEMBLY, MOTION, OR ENERGIZATION.**

Review `HR-V0-MECH-DWG-P0.1` and `HR-V0-ARM-ARCH-P0.8-DWG-CANDIDATE` against R134, R135, R136 and controlled P0.7. This is a drafting, metrology, DFM-readiness and configuration review—not supplier or fabrication authority.

## Reproduce

```powershell
& 'C:\Users\amyle\Documents\New project\.venvs\hr-v0-cad\Scripts\python.exe' tools/generate_hr_v0_manufacturing_drawings.py
& 'C:\Users\amyle\Documents\New project\.venvs\hr-v0-cad\Scripts\python.exe' tools/check_hr_v0_manufacturing_drawings.py
```

## Inspect

- `docs/hr-v0-manufacturing-drawing-p0.1.md`
- `cad/hr-v0/generated/mechanical-drawing-p0.1/drawings/`
- `cad/hr-v0/generated/mechanical-drawing-p0.1/dxf/`
- `release/hr-v0/mechanical-drawing-p0.1/source-binding.csv`
- `release/hr-v0/mechanical-drawing-p0.1/profile-entity-certificate.csv`
- `release/hr-v0/mechanical-drawing-p0.1/drawing-control-coverage.csv`
- `release/hr-v0/mechanical-drawing-p0.1/inspection-coordinate-register.csv`
- `release/hr-v0/mechanical-drawing-p0.1/first-article-drawing-map.csv`
- `release/hr-v0/mechanical-drawing-p0.1/finding-register.csv`
- `release/hr-v0/mechanical-drawing-p0.1/package-status.json`
- `release/hr-v0/mechanical-drawing-p0.1/index.html`

## Required questions

1. Re-import all five STEP/DXF pairs and independently compare finished-profile entity types, counts, bounds, hole centers/diameters and nominal countersink circles.
2. Confirm C06 and C07 each contain twelve exact LINE plus twelve exact ARC outer-profile entities derived from their bound STEP solid, including every R2 corner.
3. Confirm C01/C04/C06/C07 use the R136 nominal Ø11.30 x 2.90 mm / 90° countersink STEP candidates and C05 remains geometrically unchanged.
4. Inspect all five drawings for conventional completeness, dimension ambiguity, view/side selection, material/finish/tolerance conflicts, unreadable text, clipping and misleading authority.
5. Independently map all 26 R134 controls to the drawing graphics/notes/tables and identify any remaining schedule-only, inherited-only or contradictory instruction.
6. Review ICF-01 mathematically and metrologically: +Y broad-face constraint, rigid two-dimensional four-hole registration, no scaling, residual reporting and applicability to the asymmetric C04 pattern.
7. Decide whether ICF-01 is sufficient for candidate CMM/FAI work or must be replaced by a formal ASME Y14.5 datum reference frame before supplier inquiry.
8. Review C06 striker-top ±0.025 mm control and C07 1.000 ±0.05 mm twin face recess/coplanarity control against the exact STEP faces and intended stop load path.
9. Confirm every one of the 30 FAI rows points to the correct immutable drawing/DXF/STEP triplet and retains physical execution/acceptance holds.
10. State separately whether the package is ready for qualified mechanical review, provider DFM inquiry, quotation, fabrication, physical proof and energization.

Return `BLOCKER / MAJOR / MINOR` findings with exact part, drawing, entity, control ID or FAI row. Do not infer fabrication or energization authority from drawing completeness or checker success.
