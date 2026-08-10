# Sol R12 Findings Rechecked Against R22

> **PRELIMINARY - NOT APPROVED FOR FABRICATION OR ENERGIZATION**

Date: 2026-08-06

Current configuration: `HR-30-SYS-R0.2`, Electrical `V3-P0.4`, firmware `HR-V0-FW-P0.1`, mechanical `HR-V0-MECH-R0.1-PRELIMINARY`

## Scope and independence

This is a project-owned reconciliation, not a new Sol review. Sol's R12 totals remain 18 BLOCKER, 30 MAJOR and 8 MINOR against the historical baseline. Sol has not independently reviewed R13-R22, and this pass cannot close or renumber those findings.

## R22 evidence added

R22 addresses a bounded part of Sol B-003, M-002 and M-004 by defining the missing HR-V0 hard-stop coordinate and load-case framework:

- J1 and J2 coordinate conventions and four candidate stop datums 5 degrees beyond provisional software limits;
- a candidate 50 mm contact radius with exact generated datum coordinates;
- reproducible allocated moving inertias of 0.047264 kg m^2 at J1 and 0.010144 kg m^2 at J2;
- setup, automatic and 12 V no-load-endpoint allocated-mass energy screens;
- three-times-gravity and ideal drive-into-stop force screens;
- explicit exclusion of reflected drive inertia, bumper force/displacement, tolerance, stop latency and repeated-cycle evidence;
- `INSPECT-MECH-006`, guarded incremental `TEST-MECH-002`, and an eight-row `NOT-EXECUTED` evidence template.

The checked ROBOTIS page reports 30 rpm no-load speed and 10.6 N m momentary stall torque at 12 V for XM540-W270 and warns that stall torque differs from continuous/real-world output. R22 uses them only as mutually exclusive screening endpoints.

## Current disposition

| Sol R12 conclusion | R22 status |
|---|---|
| No buildable HR-V0 mechanical definition | **Still open.** Stop coordinate/load cases now exist, but no physical stop bracket, backed-up bumper/catch, fasteners, tolerance stack, guard, cable route, gripper, released assembly or proof evidence exists. |
| Dynamics and hard-stop impact are undefined | **Improved but open.** Allocated-mass cases are reproducible. Effective/reflected inertia, drive persistence, bumper curve, contact stiffness, rebound, fatigue and measured impact remain absent. |
| HR-V0 energization is prohibited/not ready | **Still correct.** The E2 release gate remains unresolved and powered stop testing is explicitly prohibited before qualified written approval. |
| HR-30W walking is plausible but unproved | **Still correct.** R22 is limited to the HR-V0 bench arm and supplies no walking-hardware evidence. |

## Verdict

R22 turns “design hard stops” into an exact evidence-acquisition and validation problem. It does not produce a fabricable stop or permission to move an actuator. Sol's mechanical and energization verdicts remain open.
