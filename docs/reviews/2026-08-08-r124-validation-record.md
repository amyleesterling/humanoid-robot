# R124 validation record

Status: **PRELIMINARY - NOT APPROVED FOR FABRICATION, MOTION OR ENERGIZATION**

Date: 2026-08-08

Round: R124
Package: `HR-V0-STOP-BUDGET-P0.1`

## Corrected defect

The active `docs/control.md` limit table still showed J2 `15..125 deg`, contradicting the current firmware, mechanical and narrative binding at `15..115 deg`. The row is corrected and covered by a new fail-closed checker.

The current handoff also pointed to control-panel candidate P0.5 after P0.6 had become the controlled current package. That pointer is corrected; no design approval is implied.

## Controlled results

- J2-positive nominal approach: `118 - 115 = 3 deg`.
- Constant-speed geometric traversal: `300 ms` at `10 deg/s`; `100 ms` at `30 deg/s`.
- `DF-01` 300 ms candidate detection travel: `3 deg` at `10 deg/s`; `9 deg` at `30 deg/s`, before any downstream delay or coast.
- Schneider 24 ms maximum opening-time component screen: `0.240 deg` at `10 deg/s`; `0.720 deg` at `30 deg/s`; no total-stopping or loaded-interruption claim.
- Twelve calculation/hold rows; sixteen blank physical cases, all `NOT EXECUTED` and `NOT AUTHORIZED`.
- J1 minimum, J1 maximum and J2 minimum remain `DESIGN REQUIRED` and motion-prohibiting.

## Validation status

- The R124-specific checker passed: twelve calculation/hold rows, sixteen deliberately blank test cases and the active `15..115 deg` J2 command binding were checked.
- The full non-manifest suite passed `76/76` checks.
- Browser QA passed at `1440 x 1000` and `390 x 844`: no body overflow, minimum visible text `12 px`, and the interactive `30 deg/s` case displayed `100 ms`, `9.000 deg` heartbeat travel and a `6.000 deg` overrun of the nominal approach.
- The intentional fail-closed readiness command returned exit `2`: all twenty-one E0-through-E2 gates remain `partial`.
- The staged release manifest contains `1654` package files and passed the manifest checker. Clean-tree validation is performed after commit; this working record does not claim it early.

`EG-026` remains `open`. No physical time, travel, rail-decay, contactor, stop, guard, PLr/SIL or qualified-validation evidence exists in R124.
