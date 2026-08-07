# R68 validation record

> **PRELIMINARY—NOT APPROVED FOR FABRICATION OR ENERGIZATION.** Passing source checks do not establish physical suitability, safety integrity, or permission to build or energize.

Date: 2026-08-07

Candidate branch: `codex/review-ledger-handoff`

Products: `HR-V0-FW-P0.3`, `HR-V0-SUP-P0.2`, `HR-V0-ACT-P0.2`, `HR-V0-DXL-TRANSPORT-P0.2`, `HR-V0-LIMITS-P0.1`

## Corrected inconsistency

The R67 mechanical allocation reduced the candidate J2 software ceiling to 115°, but the active supervisor configuration still allowed 125°. R68 replaces that stale value and creates one exact limit-set binding shared by supervisor selection closure and DYNAMIXEL engineering-to-raw conversion. The binding identifies `HR-V0-MECH-P0.5`, `HR-V0-ARM-ARCH-P0.6`, and `HR-V0-HS-P0.2`.

The committed configuration remains fail closed. Its release state is `CANDIDATE-NOT-RELEASED`, its acceptance-evidence SHA-256 is `SELECTION REQUIRED`, its configuration and kinematic hashes are unresolved, and received actuator identity, device, calibration, profiles, raw bounds, voltage, temperature, current and start-tolerance inputs remain unresolved.

## Executable evidence

- 47 firmware source tests pass, including 36 supervisor/actuator/transport tests.
- Exactly 115° passes only in an explicitly frozen guarded-HIL fixture.
- 115.001° is rejected at both command-screening and raw-conversion boundaries.
- Stale 120° envelopes, stale P0.5 arm identifiers, stale supervisor/actuator configuration identifiers, malformed/missing acceptance hashes and unreleased binding states fail closed.
- The repository actuator configuration still refuses to open the serial port.
- Existing reset/ARM, target invalidation, authority-loss, watchdog, telemetry and torque-off tests continue to pass.

## Repository validation

All 23 automated checker entry points pass within their stated preliminary boundaries. Native KiCad validation remains ERC/DRC clean where previously recorded; this correction changes no ECAD. The deterministic release manifest includes the R68 files and passes after regeneration.

The intentional energization readiness check remains nonzero: 30 gates total, 0 closed, 22 partial, and 8 open. Through E2, all 21 applicable gates remain partial.

## Unclosed evidence

R68 does not provide an as-built hard stop, measured stopping time or overtravel, calibration, backlash/compliance/tolerance/uncertainty closure, cable/guard clearance, received hardware, target installation, HIL, qualified functional-safety allocation, or signed review. It closes no fabrication, connection, motion, or energization gate.
