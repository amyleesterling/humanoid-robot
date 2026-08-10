# HR-V0 stopping-distance and response-budget screen P0.1

Status: **PRELIMINARY - CALCULATION SCREEN ONLY - NOT APPROVED FOR MOTION OR ENERGIZATION**

Document ID: `HR-V0-STOP-BUDGET-P0.1`

Date: 2026-08-08
Parent configuration: `HR-V0-MECH-P0.6` / `HR-V0-ARM-ARCH-P0.7` / `HR-V0-HS-P0.3`

## Correction

The active control narrative still displayed the obsolete J2 `15-125 deg` range even though R68 bound the current supervisor and actuator configuration to `15-115 deg`. This pass corrects `docs/control.md` to `15-115 deg` and adds a fail-closed checker so an active-document regression to 125 degrees is rejected.

The 125-degree value remains legitimate only in historical or explicitly outside-limit collision sweeps. It is not a command limit.

## J2-positive arithmetic

The current nominal candidate places the J2-positive software ceiling at `115 deg` and metal backup at `118 deg`. The geometric approach is therefore exactly `3 deg`.

For a constant initial angular speed `w`, the most time available before nominal metal contact is:

`t = 3 deg / w`

This gives only a bounding screen:

- at the provisional setup ceiling of `10 deg/s`, `t = 300 ms`;
- at the provisional automatic ceiling of `30 deg/s`, `t = 100 ms`.

Those values are not released response-time limits. They do not include input sensing, safety-relay logic, output-contact operation, contactor operation, rail decay, actuator electronics, stored energy, braking/coast, load, compliance, backlash, build tolerance, calibration error or measurement uncertainty.

## Important watchdog result

The ordinary `DF-01` heartbeat candidate allows up to `300 ms` for detection before downstream delays. At `10 deg/s`, detection alone consumes the entire `3 deg` approach. At `30 deg/s`, it corresponds to `9 deg`, exceeding the approach by `6 deg` before any relay, contactor, rail-decay or mechanical term.

This is not a newly created defect in a credited safety function: `DF-01` already has **zero safety credit**. The calculation makes the consequence explicit. The fixed guard, receiver, hard stops and credited-candidate safety functions must be assessed with `DF-01` failed. The project must not cite heartbeat timing as proof that the J2-positive stop will not be reached.

Schneider's current component record gives a maximum `24 ms` opening-time datum for the held `LC1D25BD`. That corresponds to `0.240 deg` at `10 deg/s` or `0.720 deg` at `30 deg/s`. It is only one component term and does not establish loaded DC interruption suitability or total robot stopping time.

## Missing stop directions

J1 minimum, J1 maximum and J2 minimum still have no selected independent positive-stop geometry. Their response distance and time remain `SELECTION REQUIRED`, and no motion release is possible in those directions. `HR-V0-STOP-REGION-P0.1` defines the required received-article measurements before a topology can be selected.

## Physical evidence required

The exact accepted configuration must record, from one synchronized timebase:

1. initiating input transition;
2. safety-relay output transition;
3. each contactor coil command and pole state;
4. actuator-rail decay through the released no-torque threshold;
5. joint position and velocity until motion stops;
6. payload, pose, supply, temperature and fault case;
7. residual travel, worst endpoint and measurement uncertainty; and
8. guard, hard-stop and first-interference reconciliation.

The blank sixteen-case record is `tests/forms/hr-v0-stopping-time-template-p0.1.csv`. No row is executed or authorized.

## Controlled sources

- `cad/hr-v0/generated/arm-architecture-p0.7/j2-positive-stop-analysis.json`
- `firmware/supervisor/actuator-config.json`
- `docs/hr-v0-contactor-application-p0.1.md`
- `safety/hr-v0-safety-function-allocation.csv`
- `controls/hr-v0-stopping-budget-p0.1.csv`
- `tests/forms/hr-v0-j2-limit-stop-template.csv`

Passing `tools/check_hr_v0_stopping_budget_p01.py` proves only configuration consistency and arithmetic. `EG-026` remains open until controlled physical testing and independent qualified review close the complete stopping function.

**PRELIMINARY - NOT APPROVED FOR FABRICATION, MOTION OR ENERGIZATION.**
