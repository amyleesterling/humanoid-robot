# R129 validation record

Status: **PRELIMINARY - NOT APPROVED FOR FABRICATION, MOTION OR ENERGIZATION**

Date: 2026-08-09

Round: R129

Package: `HR-V0-PASSIVE-ARM-RECEIVER-DETAIL-P0.2`

## Controlled result

- Sixteen BOM rows identify exact held guide, contact-layer, joint-hardware and shock candidates while retaining configured rail, retention and attachment selections as open.
- Seven interfaces and twelve fail-closed holds are controlled; four holds are `PARTIAL`, eight are `OPEN`, and none is closed.
- Three STEP/DXF fabrication files are dimensioned hole-free blanks. They are not final machinable parts.
- The receiver review STEP occupies X `-125..125 mm`, Y `-430..430 mm`, and Z `20..320 mm`, leaving nominal guard margins of `75 mm` in X and `20 mm` in Y.
- The nominal backup gap is `9.625 mm`; the nominal residual after the `8.128 mm` MA30M catalog stroke is `1.497 mm`. The tolerance stack remains open.
- R127's retained known-commanded clearance remains `63.106478372 mm`.

## Evidence state

- R129 is a project-owned correction, not an independent qualified review.
- The original 28 R127 physical evidence rows remain `NOT EXECUTED` and `NOT AUTHORIZED`.
- `EG-008` and `EG-009` remain `partial`.
- Browser QA passed at `1440 x 1000` and `390 x 844`: no page-level horizontal overflow, the body text was `17 px` desktop / `16 px` mobile, the smallest visible leaf text was `14 px`, the warning remained visible, and the model-viewer occupied `1080 x 520 px` desktop / `335 x 430 px` mobile. After scrolling the mobile viewer into view, its WebGL canvas rendered the detailed receiver model and the poster state cleared. The console reported no warnings or errors. The temporary viewport override was reset and the temporary tab was finalized.
- All `81/81` non-manifest repository checkers passed using the controlled CadQuery interpreter, except the three native KiCad checkers run with KiCad 10's interpreter.
- Fail-closed readiness check `tools/check_energization_gates.py --through-stage E2 --require-ready` returned the required exit code `2`: `21` applicable gates, `0` closed, `0` open and `21` partial. This is an intentional not-ready result, not a validation failure.
- The deterministic release manifest contains `1,734` package files and is checked after staging and again from the clean committed tree.

No physical result exists in R129.
