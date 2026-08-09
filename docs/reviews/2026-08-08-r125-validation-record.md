# R125 validation record

Status: **PRELIMINARY - NOT APPROVED FOR FABRICATION, MOTION OR ENERGIZATION**

Date: 2026-08-08

Round: R125

Package: `HR-V0-POWERLOSS-P0.1`

## Controlled result

R125 selects passive containment as the HR-V0 power-loss strategy while selecting no receiver material, part or rating. No actuator hold, friction, cable tension, software, `DF-01`, controlled stop or operator intervention receives credit.

The controlled moving-mass allocation is `0.750 kg`; the maximum recorded shoulder radius is `0.360 m`. The configuration-independent vertical excursion bound is `0.720 m`, so the gravitational-only allocation input is:

`0.750 kg × 9.80665 m/s² × 0.720 m = 5.295591 J`.

The value excludes continued drive, regeneration, stored energy, detached hardware, receiver behavior, uncertainty and an accepted factor. It is not an impact prediction, guard rating, receiver rating or proof energy.

## Evidence state

- Twelve bound/hold rows and ten strategy rows are controlled.
- Seventy-two physical cases cover a 3-by-3 pose grid, two payload states and four energy-loss causes.
- Every physical case remains `NOT EXECUTED` and `NOT AUTHORIZED`.
- A 3-by-3 grid is explicitly not continuous all-pose proof.
- `EG-009` remains `partial`.
- Browser QA passed at `1440 x 1000` and `390 x 844`: no page overflow, minimum visible text `14 px`, correct interactive update from `0.500 kg` / `0.250 m` to `2.452 J`, and the partial-gate warning remained visible.
- The complete non-manifest repository suite passed `77/77` checks.
- The intentional readiness command through E2 returned exit `2`: all twenty-one applicable gates remain `partial`.
- The staged deterministic release manifest contains `1664` package files and passes its checker.

Clean-tree validation is performed after commit. No physical result exists in R125.
