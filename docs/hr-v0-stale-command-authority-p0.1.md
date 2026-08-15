# HR-V0 stale-command and restart authority correction P0.1

> **PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION**

Artifact: `HR-V0-STALE-AUTH-P0.1`

Configuration: `HR-V0-SUP-P0.3` / `HR-V0-E2-SEQ-P0.1` / `HR-V0-E2-HW-P0.4`

Review/control round: R196

## Correction

The existing E2 form observed SR1, SRA1, K1, K2 and the physically absent actuator bus. It did not require synchronized evidence of the supervisor state, active trajectory store or torque-enable request. That made `E2-SL-019` ambiguous: K1/K2 may be on after the valid RESET then distinct ARM sequence even though motion authority must still be absent.

`tests/forms/hr-v0-e2-software-authority-template-p0.1.csv` now binds all twenty E2 logic cases to the software-authority observations. In `E2-SL-019`, the expected state after a complete valid hardware re-arm is:

- contactor power path: ON;
- supervisor state: `ARMED`;
- active trajectory: `NONE`;
- torque-enable request: `FALSE`; and
- replay of the pre-drop sequence: `REJECTED`.

The supervisor source already invalidates `active_command` on every fault and retains the monotonic sequence number. R196 adds an executable regression proving that a pre-drop command replay remains rejected after fault acknowledgement, RESET and distinct ARM; only a new sequence can request torque.

## What this proves

The source-level model and automated regression encode the intended authority separation. RESET and ARM do not create a trajectory or torque request. Power-path restoration and motion permission are separate states.

## What this does not prove

The new evidence form is unexecuted. It does not prove the deployed host image, hardware observations, actuator behavior, bus behavior, timing, contactor state, stopping performance, guard containment or functional-safety integrity. The ordinary supervisor and heartbeat diagnostic retain zero safety credit. Physical E2/HIL execution, configuration hashes, synchronized traces, independent witness and qualified review remain required. No finding, requirement or energization gate closes.
