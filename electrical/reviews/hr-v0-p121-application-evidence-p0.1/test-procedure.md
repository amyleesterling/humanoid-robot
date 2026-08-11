# HR-V0 P1.21 no-load A1-gating test procedure P0.1

> **PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION**

Identifier: `HR-V0-P121-APP-EVID-P0.1`

Execution state: **NOT EXECUTED - NOT AUTHORIZED**

This procedure is a controlled future-test definition. It shall not be executed until every `AUTH-001` through `AUTH-010` prerequisite is independently verified and a separate written E2 control-only work authorization is issued for the exact configuration.

## Hard boundary

- The actuator source, actuators and main power path shall be physically absent.
- SRA1 output contacts shall be observed only with an approved isolated low-energy continuity fixture.
- K1/K2 power poles shall not switch a load. EDM may be represented only by an approved dry-contact simulator.
- No mains source, installed robot actuator rail, motion, payload or person may be introduced.
- Any unexpected output closure, relay chatter, odor, heat, smoke, unstable trace, instrument overrange, fixture discrepancy or loss of isolation requires immediate source removal, quarantine and nonconformance entry.

## Required order

1. Freeze the exact Git commit, P1.21 native KiCad hash, fixture ECAD/BOM/wiring hashes, firmware hash and received serial/lot identities.
2. Complete and sign all authorization-prerequisite rows.
3. Enter manufacturer-derived numeric limits and approved test points. `SELECTION REQUIRED` is not an executable value.
4. Complete TEST-001 unpowered. Stop on any discrepancy.
5. Apply only the separately authorized current-limited 24 V control source.
6. Execute TEST-002 through TEST-018 in order unless the signed test owner issues a controlled deviation.
7. Capture every required signal on a common time base and preserve raw files before analysis.
8. Mark a test PASS only when every qualitative condition and every selected numerical limit passes. Ambiguous, missing or clipped data are FAIL, not PASS.
9. Remove power, verify zero energy, archive evidence and obtain independent review.

Passing this procedure would provide configuration-specific evidence only. It would not establish functional-safety approval, loaded interruption, stopping distance, guard containment, actuator motion authority or general energization permission.
