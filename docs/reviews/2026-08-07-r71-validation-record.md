# R71 validation record - HR-V0 gripper integration inputs

Date: 2026-08-07

Configuration: `HR-V0-GRIP-P0.2` against `HR-V0-MECH-P0.6` / `HR-V0-ARM-ARCH-P0.7`

Status: **PRELIMINARY - NOT APPROVED FOR FABRICATION, MOTION, OR ENERGIZATION**

## Input identity

The official ROBOTIS repository head was resolved with `git ls-remote` and frozen at:

`9187eca0920458be04d2399906388f55242f81f1`

The exact `link5.stl`, left/right palm STL, URDF and upstream license were retrieved from raw GitHub URLs at that commit. Their SHA-256 hashes are machine-checked by both the generated source-integrity register and `cad/vendor/robotis/vendor-manifest.csv`.

## Generated evidence

- responsive self-contained interactive top-view guide;
- readable 1600 x 950 static SVG;
- three exact URDF positions at q=-11, 0 and +20 mm;
- closest palm-mesh distances of 0.059329, 19.939267 and 59.106467 mm;
- parameterized gripper mass/gravity sensitivity without assigning actual mass;
- seven fail-closed integration holds; and
- corrected mass-ledger ownership: `V0M-014`, `V0M-015`, and `V0M-016`.

The mesh distances are not certified jaw openings and are not substituted for the e-Manual 20-75 mm stroke. Mesh volumes and URDF inertias receive no physical mass credit.

## Automated validation

Executed with the controlled CAD interpreter:

```text
C:\Users\amyle\Documents\New project\.venvs\hr-v0-cad\Scripts\python.exe tools/generate_hr_v0_gripper_integration.py
C:\Users\amyle\Documents\New project\.venvs\hr-v0-cad\Scripts\python.exe tools/check_hr_v0_gripper_integration.py
```

Result:

```text
Generated HR-V0-GRIP-P0.2: exact official source frozen; seven integration holds remain open
HR-V0 gripper integration check passed: exact source frozen, 3 reference poses, 7 holds open
```

## Browser validation

The generated HTML was served locally and inspected in the in-app Chromium browser.

- Desktop: 1440 x 1000 viewport, 1120 px header/main width, 16 px body and 48 px title, no horizontal overflow.
- Narrow: 390 x 844 viewport, 343 px header/main width, 16 px body, 307 px table width, no horizontal overflow.
- Slider: q=20.0 mm produced left/right transforms of -80/+80 px at the declared 4 px/mm display scale.
- A first rendering exposed a collapsed-width defect caused by a compact CSS `min()` declaration. It was corrected to explicit `width` plus `max-width`, regenerated and rechecked.
- A scaled in-SVG label that became too small on narrow screens was removed because the same information is available as normal 16 px page text and the SVG retains its accessible label.

## Release boundary

All `GRH-001` through `GRH-007` holds remain `OPEN`. No complete mechanism manufacturing definition, H104 registration, usable-opening calibration, received mass/COM, guard/receiver, force/current/drop result, fastener/cable/wear release, fabrication authorization, motion permission, functional-safety approval or energization authorization exists.
