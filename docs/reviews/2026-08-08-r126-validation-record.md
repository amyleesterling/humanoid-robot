# R126 validation record

Status: **PRELIMINARY - NOT APPROVED FOR FABRICATION, MOTION OR ENERGIZATION**

Date: 2026-08-08

Round: R126

Package: `HR-V0-COLLAPSE-ENV-P0.1`

## Controlled result

- Eleven known moving B-Reps are continuously bounded for arbitrary no-stop-credit J1/J2 rotations.
- Known B-Rep radius: `338.740914 mm`.
- Controlled mass-ledger radius: `360.000000 mm`.
- Guard radial reservation: `450.000000 mm`.
- Unallocated radial residual: `90.000000 mm`.
- Known X extent: `-42.000000 to +42.000000 mm` inside the `-200 to +200 mm` guard depth.
- Controlled Z extent: `140.000000 to 860.000000 mm` inside the `0 to 950 mm` guard height.
- P0.3 floor-tray top: `Z 26.000000 mm`, leaving a `114.000000 mm` gap below the controlled arm envelope.

The floor tray is corrected to `OBJECT CATCH ENVELOPE ONLY` with zero arm-support, energy or load credit. A separate arm receiver and the missing physical stops remain design blockers.

## Evidence state

- Eight guard-fit rows and five role-disposition rows are controlled.
- Eighteen metrology records remain `NOT EXECUTED` and `NOT AUTHORIZED`.
- Complete gripper, object, cable, tolerance, deformation, stopping, rebound and physical evidence are excluded.
- `EG-008` and `EG-009` remain `partial`.

## Automated validation

- Full non-manifest repository suite: `78 / 78` checks passed.
- Intentional readiness test through E2: `21` applicable gates remain `partial`; `--require-ready` returned the required fail-closed exit code `2`.
- Release manifest: `1,679` controlled package files; checker result recorded before commit.
- Clean-tree manifest result is recorded after commit.

No physical result exists in R126.

## Interactive-guide QA

- Chromium viewport checks completed at `1440 x 1000 px` and `390 x 844 px`.
- No horizontal document overflow was detected at either viewport.
- The smallest measured visible user-facing text was `14 px`; body copy is `17 px` with `1.55` line height.
- The floor-tray layer control hid the tray and its gap annotation together, avoiding a misleading residual line.
- The local `model-viewer` module was defined and the GLB asset returned HTTP `200` with `7,055,124` bytes.
- Headless Chromium did not report the WebGL model as loaded. The reviewed page therefore uses a legible SVG poster fallback and makes no claim that headless 3D rendering was validated.
