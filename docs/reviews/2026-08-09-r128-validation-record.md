# R128 validation record

Status: **PRELIMINARY - NOT APPROVED FOR FABRICATION, MOTION OR ENERGIZATION**

Date: 2026-08-09

Round: R128

Package: `HR-V0-PASSIVE-ARM-RECEIVER-VERIFY-P0.1`

## Controlled result

- Closed-form minimization of all conservative source-BRep AABB corners gives `Z = 384.142618886 mm`.
- The controlling H104 corner and J1/J2 boundary pose exactly reproduce R127's sampled minimum.
- R127's retained continuous lower bound remains `383.106478372 mm`, `1.036140514 mm` below the analytic result.
- The retained receiver clearance remains `63.106478372 mm`; no margin is reclaimed.
- Re-imported receiver STEP bounds are X `-90..90 mm`, Y `-430..430 mm`, and Z `20..320 mm`.
- Nominal guard margins are `110 mm` in X and `20 mm` in Y.
- Decimal ACE and rail calculations reproduce R127 to the stated precision.

## Evidence state

- R128 is internal second-method corroboration, not independent qualified review.
- All twelve R127 hold groups remain open.
- All 28 physical evidence rows remain `NOT EXECUTED` and `NOT AUTHORIZED`.
- `EG-008` and `EG-009` remain `partial`.
- Browser QA passed at `1440 x 1000` and `390 x 844`: no page-level horizontal overflow, the smallest visible leaf text was `14 px`, both angle sliders were present, the warning remained visible, the controlling-corner readout updated from `384.143 mm` to `615.855 mm` when J1 moved from `-20 deg` to `20 deg`, and the console reported no warnings or errors. The temporary viewport override was reset and temporary tabs were finalized.
- All `80/80` non-manifest repository checkers passed using the controlled CadQuery interpreter, except the three native KiCad checkers run with KiCad 10's interpreter.
- Fail-closed readiness check `tools/check_energization_gates.py --through-stage E2 --require-ready` returned the required exit code `2`: `21` applicable gates, `0` closed, `0` open and `21` partial. This is an intentional not-ready result, not a validation failure.
- The deterministic release manifest contains `1,709` package files and is checked after staging and again from the clean committed tree.

No physical result exists in R128.
