# R127 validation record

Status: **PRELIMINARY - NOT APPROVED FOR FABRICATION, MOTION OR ENERGIZATION**

Date: 2026-08-09

Round: R127

Package: `HR-V0-PASSIVE-ARM-RECEIVER-P0.1`

## Controlled result

- `144,761` two-axis grid poses cover the current J1 `-20..70 deg` and J2 `15..115 deg` command domain using conservative source-BRep AABB corners.
- Sampled known-geometry minimum: `384.142619 mm`.
- Between-grid continuous deduction: `1.036141 mm`.
- Continuous known commanded-workspace lower bound: `383.106478 mm`.
- Candidate receiver top: `320.000000 mm`.
- Nominal known-geometry residual: `63.106478 mm`.
- Three ACE MA30M evaluation candidates provide `10.507589 J` arithmetic catalog capacity, `1.984215` times the gravitational-only allocation.
- A provisional 2,000 N subframe screen gives `92.598717 MPa` nominal rail stress and `3.951237 mm` typical-property deflection; neither is an allowable pass.

The receiver is now a controlled design candidate rather than a missing concept. Complete geometry, application approval, guides, contact layer, load path, stops and physical evidence remain open.

## Evidence state

- Twelve closure holds are open and block fabrication, motion and energization.
- Twenty-eight physical records remain `NOT EXECUTED` and `NOT AUTHORIZED`.
- `EG-008` and `EG-009` remain `partial`.

## Browser QA

- The local interactive guide returned HTTP `200` and rendered at both `1440 x 1000` and `390 x 844` CSS-pixel viewports.
- Neither viewport produced page-level horizontal overflow.
- The smallest visible leaf text measured `14 px`; body copy is `17 px`.
- The interactive `<model-viewer>` element was present and visible. Its GLB returned HTTP `200` with `7,221,932` bytes.
- Browser console inspection returned no warnings or errors.
- The static SVG front-elevation remains the non-WebGL explanatory fallback.

## Repository regression and readiness

- All `79 / 79` non-manifest repository checkers passed with the required CadQuery or KiCad 10 runtime.
- The E0-through-E2 readiness check found all `21` applicable gates `partial`, returned the required exit code `2`, and reported `NOT READY`.
- The staged release manifest contains `1,697` package files and passed its consistency checker.
- The post-commit clean-tree manifest result is reported in the R127 handoff after commit because recording it here would itself change the package hash set.

No physical result exists in R127.
