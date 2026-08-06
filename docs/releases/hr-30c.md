# HR-30C release specification — powered stance

Document ID: HR-REL-30C  
Revision: 0.1  
Status: future gate; detailed design and test evidence not released

## Capability earned

The restrained full body supports its static weight through both feet, holds quiet standing, and performs controlled left/right weight shifts. It does not walk.

## Included configuration

- HR-30B full body with only individually qualified leg axes enabled.
- Rated overhead restraint attached throughout testing and a guarded, access-controlled cell.
- Synchronized pelvis IMU, foot-force sensing, joint feedback, real-time state estimation, and independent fall/safety monitoring.
- External current-limited 14.0–14.8 V power separated into left-leg, right-leg, and upper-body domains.

## Entry conditions

- HR-30B acceptance is approved.
- Walking-verification W0 simulation/test articles and W1 restrained single-leg testing pass.
- Restraint proof, sensor calibration, joint limits, power-loss response, controlled-kneel strategy, and fault procedures are approved.

## Acceptance criteria

- Feet carry 100% of measured static robot weight during the scored hold; the restraint remains connected but supplies no sustained support.
- Quiet standing is maintained for 120 seconds without stepping, single support, deadline failure, thermal/current limit violation, or invalid sensor state.
- The robot completes 100 commanded bilateral weight shifts while keeping both feet in contact and remaining within released force, center-of-pressure, attitude, and joint-tracking bounds.
- Loss of the Linux planner, stale state, missed control deadline, low supply, invalid foot sensor, or E-stop produces the released restrained response and a latched restart-required state.
- Commands, feedback, safety states, restraint load, and configuration are logged for the complete trial.

## Required evidence

Planned W2 records traced to STANCE-001 through STANCE-004: TEST-STANCE-001 through TEST-STANCE-003 and AUDIT-STANCE-001, plus sensor calibration, restraint-load trace, thermal/current logs, fault-injection results, and configuration audit. These records do not exist until the corresponding tests and audit are completed and approved.

## Boundary

HR-30C does not authorize stepping, single-support balance, dynamic walking, slack-tether gait, untethered operation, or people inside the fall zone.
