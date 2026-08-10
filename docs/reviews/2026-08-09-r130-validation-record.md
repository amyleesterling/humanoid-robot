# R130 validation record

Status: **PRELIMINARY - NOT APPROVED FOR FABRICATION, MOTION OR ENERGIZATION**

Date: 2026-08-09

Round: R130

Package: `HR-V0-RECEIVER-GUIDE-IF-P0.1`

## Controlled result

- The R129 `FAB-REC-003` 20 x 50 mm guide tab is formally rejected because it cannot cover the current documented 53 x 40 mm K2 mounting pattern in either orientation.
- `FAB-REC-004` is a 73 x 80 mm vertical-face, 40 mm-reach, 6.35 mm-wall hole-free right-angle planning envelope. It is not a final machinable part.
- Twelve catalog-coordinate rows, 24 controlled candidate centers and ten fail-closed holds are recorded; two holds are `PARTIAL`, eight are `OPEN`, and none is closed.
- The nominal bracket mass is `0.142242635 kg`; four brackets plus the R129 platen total `3.037850541 kg`. Pads, fasteners, shock moving parts and any application-effective moving mass remain excluded.
- The interface review assembly occupies X `-125..125 mm`, Y `-400..400 mm`, and Z `184.125..310.475 mm`.
- The configured rail identity, received manufacturer CAD, thread depth, final holes, fasteners, fixed/floating arrangement, application acceptance, structural proof and machining definition remain open.

## Evidence state

- The dedicated deterministic package checker passed: 12 catalog rows, 24 controlled centers and ten fail-closed holds.
- R130 is a project-owned correction, not an independent qualified review.
- The igus supplier RFI is an UNSENT draft and no supplier response exists.
- `EG-008` and `EG-009` remain `partial`.
- Browser QA passed at `1440 x 1000` and `390 x 844`: no page-level horizontal overflow, the body text was `17 px` desktop / `16 px` mobile, the smallest visible leaf text was `14 px`, and the warning remained present. The model viewer occupied `1080 x 520 px` desktop and `335 x 430 px` mobile; its WebGL canvas rendered the receiver-guide model at both sizes. The console reported no warnings or errors. The temporary viewport override was reset and the temporary tab was finalized.
- All `82/82` non-manifest repository checkers passed using the controlled CadQuery interpreter, except the three native KiCad checkers run with KiCad 10's interpreter.
- Fail-closed readiness check `tools/check_energization_gates.py --through-stage E2 --require-ready` returned the required exit code `2`: `21` applicable gates, `0` closed, `0` open and `21` partial. This is an intentional not-ready result, not a validation failure.
- The deterministic release manifest contains `1,754` package files and is checked after staging and again from the clean committed tree.

No physical result exists in R130.
