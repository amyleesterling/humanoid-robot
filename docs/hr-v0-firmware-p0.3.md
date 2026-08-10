# HR-V0 firmware P0.3 implementation candidate

**PRELIMINARY—NOT APPROVED FOR CONNECTION, FLASHING, FABRICATION, OR ENERGIZATION**

Identifier: `HR-V0-FW-P0.3`

System baseline: `HR-30-SYS-R0.2`

Date: 2026-08-07

P0.3 corrects the cross-domain motion-limit mismatch found after R67. The mechanical candidate allocates J2 to a 115° software ceiling, but P0.2 still carried a 125° supervisor maximum. The current source binds both supervisor command screening and DYNAMIXEL engineering-to-raw conversion to `HR-V0-MECH-P0.5`, `HR-V0-ARM-ARCH-P0.6`, and `HR-V0-HS-P0.2`, with J2 limited to 15° through 115°.

This is not a released limit. The committed configuration records `CANDIDATE-NOT-RELEASED` and `SELECTION REQUIRED` acceptance evidence. That state, unresolved configuration/kinematic hashes, missing start tolerances, missing received calibration, and the other existing transport selections independently keep motion inhibited and the serial port unopened.

## Controlled correction

- `HR-V0-SUP-P0.2` replaces the stale 125° J2 command envelope with 115° and requires exact mechanical revision identifiers plus an accepted evidence hash before `selections_closed` can become true.
- `HR-V0-ACT-P0.2` carries the same exact mechanical binding and checks engineering-unit envelopes before raw conversion; a raw range large enough to reach 120° cannot bypass the 115° ceiling.
- `HR-V0-DXL-TRANSPORT-P0.2` retains the P0.1 transport/register behavior and adds this mechanical-limit binding at its configuration boundary.
- Tests reject stale 120° configuration, revision mismatch, missing limit evidence, and J2 commands above 115°, while accepting exactly 115° only in an explicitly frozen test fixture.

## Evidence boundary

The 115° value is a candidate derived from nominal CAD and the R67 allocation. Before a guarded HIL configuration can use it, the acceptance-evidence hash must identify reviewed as-built calibration, actual hard-stop geometry, measured stopping overtravel, backlash, compliance, tolerance, uncertainty, cable and guard clearance, and the accepted configuration. No code path assigns functional-safety credit to this limit.

`EG-017` remains **partial**. No target SDK was installed, no port was opened, no actuator was connected, and no HIL or motion test was executed.

**PRELIMINARY—NOT APPROVED FOR CONNECTION, FLASHING, FABRICATION, OR ENERGIZATION**
