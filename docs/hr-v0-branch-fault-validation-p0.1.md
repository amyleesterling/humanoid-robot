# HR-V0 branch fault and no-backfeed validation P0.1

> **PRELIMINARY - NOT APPROVED FOR FABRICATION, ASSEMBLY, CONNECTION, MOTION, OR ENERGIZATION**

Date: 2026-08-09

Applies to: Electrical V3-P1.14; `F0`, `F1`, `F2`, `F3`, `FSR1`, `FSR2`, `SD1`, `KP1`, `KP2`, `INJ1`, `U1`, `J1`, `J2`, and `J3`

Status: executable evidence schema only; all physical results and authorization remain open

## Decision

R157 supplies the previously missing evidence location for energization gate `EG-024`. It defines 24 exact-reference cases for unpowered isolation, low-energy control faults, guarded protection faults, output backfeed, regenerative pulses, redundant interruption, and no-motion recovery.

It does **not** select fuse values, conductors, fault energy, source limits, test equipment, acceptance thresholds, or contactor duty. It does not authorize a direct short, connection to the robot supply, actuator motion, or energization. Gate `EG-024` remains `open` until every applicable row is executed against a frozen configuration, raw evidence is accepted, nonconformances are closed, and qualified reviewers sign the result.

## Controlled evidence

- Matrix: `electrical/hr-v0-branch-fault-matrix-p0.1.csv`
- Blank execution record: `tests/forms/hr-v0-branch-fault-validation-template.csv`
- Interactive guide: `release/hr-v0/branch-fault-validation-p0.1/index.html`
- Machine check: `tools/check_hr_v0_branch_fault_validation_p01.py`

- `A - UNPOWERED`: 8 cases
- `B - LIMITED ENERGY`: 5 cases
- `C - GUARDED FAULT FIXTURE`: 8 cases
- `D - CONFIGURED DISTRIBUTION`: 3 cases

## Mandatory sequence

1. Complete Stage A with every energy source physically absent and prove live-dead-live instrument function using an approved method.
2. Complete Stage B only on separately protected, current-limited interface fixtures. The actuator source and robot mechanism remain absent.
3. Complete Stage C only after `EG-014` coordination inputs, exact protection/harness identities, prospective fault energy, enclosure, remote switching, guarding, instruments, emergency response, and qualified test authorization are accepted. A direct uncontrolled short across the robot source is prohibited.
4. Complete Stage D only after the preceding cases and their nonconformances are accepted. Programmable loads/emulators precede any restrained actuator article.
5. Every recovery check must prove that clearing a fault, releasing/resetting E-stop, restoring a branch, or rebooting ordinary control cannot itself command motion. A separate deliberate command remains mandatory.

## Fail-closed acceptance rule

Blank or `SELECTION REQUIRED` numeric thresholds are not permission to improvise. Before execution, the controlled test plan must state exact source serials, source limit/foldback/sink behavior, fuse and holder order codes, conductor and connector identities, loop impedance, fault energy, instrument ranges/bandwidth/calibration, remote switching rating, guards, PPE/emergency response, thermal limits, clearing limits, rail-decay/stopping limits, sample rate, uncertainty, and named authorized roles.

Any unexpected upstream energization, cross-branch energization, connector/conductor/holder damage, uncontrolled arc, source instability, automatic restart, motion command, lost diagnostic, exceeded limit, missing trace, or ambiguous configuration is a failed test and blocks progression.

## Sol R12 disposition

This is a project-owned correction to the Sol R12 architecture-only protection and missing executed-evidence findings. It is not a new Sol review, physical proof, independent approval, or functional-safety validation. The original 18 BLOCKER / 30 MAJOR / 8 MINOR totals are not changed by this pass.

## Release state

All 24 cases are `NOT EXECUTED`. Gate `EG-024` remains `open`. HR-V0 remains not ready for fabrication, assembly, connection, motion, or energization; HR-30W remains a later feasibility program.
