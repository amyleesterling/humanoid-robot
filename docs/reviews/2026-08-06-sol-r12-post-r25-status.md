# Sol R12 findings rechecked against R25

**PRELIMINARY—NOT APPROVED FOR FABRICATION OR ENERGIZATION.**

This is a project-owned status reconciliation, not a new Sol review. Sol's R12 totals remain 18 BLOCKER, 30 MAJOR and 8 MINOR against the historical 62-requirement baseline. Sol has not independently reviewed R13-R25. The current package has 67 draft requirements and 73 registered verification procedures.

## What R25 changes

R25 addresses the evidence structure around Sol findings M-006, M-007 and M-030 without claiming closure:

- `SAFE-010` requires the fixed enclosure to remain beyond the complete released swept, stopping, payload and tolerance union;
- `SAFE-011` requires the catch to contain the 100 g foam object after command, fault or power loss;
- `MECH-001` requires controlled moving-cable routes, bend/twist/tension limits, strain relief and stop/pinch/guard clearance;
- generated native artifacts reserve a 900 x 400 x 950 mm internal guard volume, an 820 x 320 x 50 mm catch space, and five cable zones;
- the 25 mm stopping, 25 mm clearance, 5 mm tolerance, 6 mm panel and 3 mm tray values are explicitly provisional planning inputs;
- three unexecuted record templates cover ten guard cases, ten cable-zone/pose cases and six drop cases; and
- the CAD checker now validates those source artifacts, assumptions, warnings and unexecuted records.

Repository CAD validation passes with four custom parts, three fit coupons, 41 hashed generated artifacts and 11 controlled ROBOTIS references. Traceability resolves 67 requirements, 40 risks and 73 procedures.

The controlled gate checker still reports 21 applicable gates through E2 with 0 closed. Because R25 supplies preliminary guard evidence for EG-008, the distribution becomes 14 partial and 7 open. This is progress in documentation maturity, not permission to connect or energize an actuator.

## R12 conclusions after R25

| R12 conclusion | R25 status |
|---|---|
| HR-V0 is not build ready | **Still correct.** The required guard/catch/harness evidence is now structured, but exact parts, support/frame, fasteners, measured stopping/drop/sweep, physical inspection and proof do not exist. |
| HR-V0 energization is prohibited | **Still correct.** No applicable E0-E2 gate is closed and no powered physical evidence was added. |
| Cable routing lacks geometric verification | **Improved but open.** Five zones and a complete-range inspection route exist; exact cable, connector, clamp, loop, bend/twist/tension limits and executed articulation evidence do not. |
| Guard thickness, mounting and clearance are undefined | **Improved but open.** A space reservation and derived terms exist; the actual safety distance, material, frame, attachment, access probe, impact and retention design remain unresolved. |
| Arm/gripper power-off drop behavior is unbounded | **Improved but open.** Catch geometry and six controlled cases exist only as unexecuted templates. Backdrive trajectories, release height, rebound and containment are unmeasured. |
| HR-30W walking is plausible but unproved | **Still correct.** R25 is HR-V0 containment work and supplies no full-body drivetrain, energy-loss, restraint or walking evidence. |

## Closure boundary

Complete the frozen 3D sweep; measure stopping travel in every worst pose/fault; select the access probe and minimum clearance; design exact panels, frame, fasteners, catch and service isolation; freeze the complete harness; execute unpowered guard/cable inspections and approved drop tests; perform impact/retention proof; and obtain qualified review. The preliminary STEP envelope is for planning and collision development only.

R25 does not approve procurement, fabrication, actuator connection, energization or operation around people.
