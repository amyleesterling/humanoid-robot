# R173 validation record

R173 issues `HR-V0-FAB-INPUT-P0.1` as a requirements-to-fabrication reconciliation, not a fabrication or motion release.

- Ten fabrication-input rows retain stable `FAB-IN-001` through `FAB-IN-010` identities.
- One payload input is reconciled to the controlled draft requirement; two duty/motion inputs remain partial; six engineering inputs remain open or selection-required; work authorization remains denied.
- Five energy and kinematic calculations reproduce from stated formulas and units.
- The 30 deg/s shoulder-only full-reach screen produces 0.1884955592 m/s and therefore cannot substitute for the 0.15 m/s TCP limit.
- `EG-006` and `EG-007` remain partial.

## Browser validation

The interactive guide was inspected at 1280 x 720 and 390 x 844. The first pass exposed an invalid font shorthand that rendered buttons at 13.3333 px; R173 corrected it before acceptance.

- body and button text after correction: 16 px;
- technical text: 14 px;
- no horizontal overflow;
- filter results: Everything 4, Controlled inputs 2, Open engineering 2;
- no console warnings or errors; and
- the header, warning, summary cards and controls reflow without clipping.

## Repository validation

- General repository checks: **102/102 passed**.
- Native KiCad-dependent checks under KiCad 10.0: **13/13 passed**.
- CadQuery geometry checks: **14/14 passed**.
- Pre-manifest total: **129/129 passed**.
- The staged release-manifest check brings the controlled total to **130 checks**.

These checks prove requirement trace, arithmetic, parser compatibility, digital invariants and reference-model behavior only. They do not provide accepted acceleration, jerk, duty, restraint, safety factors, complete load cases, provider acceptance, physical evidence or qualified mechanical approval. No quotation, fabrication, motion or energization authority exists.
