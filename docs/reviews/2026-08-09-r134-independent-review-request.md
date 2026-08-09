# R134 independent mechanical DFM-data review request

> **PRELIMINARY - NOT APPROVED FOR QUOTATION, FABRICATION, ASSEMBLY, MOTION, OR ENERGIZATION.**

Review configuration `HR-V0-MECH-DFM-DATA-P0.1` against controlled `HR-V0-ARM-ARCH-P0.7`. This is an accuracy and completeness review, not permission to contact a provider, upload files, quote, machine, assemble, move or energize.

## Reproduce

```powershell
& 'C:\Users\amyle\Documents\New project\.venvs\hr-v0-cad\Scripts\python.exe' tools/generate_hr_v0_mechanical_dfm_data.py
& 'C:\Users\amyle\Documents\New project\.venvs\hr-v0-cad\Scripts\python.exe' tools/check_hr_v0_mechanical_dfm_data.py
```

## Inspect every controlled artifact

- `docs/hr-v0-mechanical-dfm-data-p0.1.md`
- `docs/hr-v0-boston-fabrication-decision-p0.2.md`
- `release/hr-v0/mechanical-dfm-data-p0.1/part-register.csv`
- `release/hr-v0/mechanical-dfm-data-p0.1/geometry-file-register.csv`
- `release/hr-v0/mechanical-dfm-data-p0.1/inspection-control-register.csv`
- `release/hr-v0/mechanical-dfm-data-p0.1/first-article-plan.csv`
- `release/hr-v0/mechanical-dfm-data-p0.1/dfm-question-register.csv`
- `release/hr-v0/mechanical-dfm-data-p0.1/hold-register.csv`
- `release/hr-v0/mechanical-dfm-data-p0.1/package-status.json`
- `release/hr-v0/mechanical-dfm-data-p0.1/index.html`
- all fifteen referenced P0.7 STEP/DXF/SVG files

## Required review questions

1. Confirm that all fifteen file hashes, sizes, units, revisions and part associations match the repository source.
2. Challenge whether the drawings plus twenty-six source controls completely define material, datums, profiles, holes, countersinks, flatness, parallelism, edge treatment and inspection.
3. Review C01/C04/C05 joint load paths, fastener access/engagement, T-slot behavior and the required received dry fits.
4. Review C06/C07 stop geometry, single-rail contact, tolerance stack, bumper inputs, local stress, deformation, rebound, fatigue, impact and proof evidence.
5. Determine whether the thirty first-article operations are sufficient, sequenced correctly and objectively accept/reject every critical feature without permitting further work automatically.
6. Challenge the 6061-T651, 9.525 mm nominal / 9.00..10.00 mm finished candidate definition and required MTR/heat-lot evidence.
7. Verify that the R91 route statement is correctly reconciled: X430 comparison evidence exists through P1.1 but remains nonselected and incomplete; P0.7 stays controlled.
8. Confirm that the dataset cannot be mistaken for a supplier payload or fabrication release.
9. Identify every missing input needed for a qualified mechanical release, including complete mass/COM/inertia, continuous duty, received interfaces, cables/guard, stopping and physical proof.
10. Inspect the web guide at mobile and desktop widths for legibility, broken links, ambiguity or misleading authority cues.

## Deliver

Return prioritized `BLOCKER / MAJOR / MINOR` findings with exact file, part, control, FAI row or hold references; proposed corrections; primary-source evidence where applicable; and separate verdicts for design completeness, provider-inquiry readiness, fabrication readiness, physical-test readiness and energization readiness.

Do not infer strength, fit, manufacturability, safety or release from checker success.
