# Sol R12 status after R55 corrected arm candidate

**PRELIMINARY - NOT APPROVED FOR FABRICATION OR ENERGIZATION**

Date: 2026-08-07

Independent review being dispositioned: Sol R12

Project response: R55 / `HR-V0-ARM-ARCH-P0.2`

The Sol summary supplied on 2026-08-07 is the already controlled R12 independent review. It is not a new independent round. R55 is a project-owned correction and is not an approval.

## Material correction

R55 re-audited the R54 arm against manufacturer-coordinate cylinders, current ROBOTIS assembly guidance, controlled 80/20 geometry evidence and a denser collision sweep. It found and corrected three R54 modeling errors: raw XM540 body orientation, use of PCD22 instead of the rectangular link pattern, and horizontal placement of the 20-2040 end-tap pair. It also exposed a nominal adapter/body collision beginning at 122 degrees.

The corrected candidate records a 193.025 mm J1-J2 spacing, 119.525 mm J2-G1 spacing, vertical 20-2040 members, flush M5 countersunk candidate geometry, 221 sampled poses and a provisional 120 degree J2 soft limit. Static thread and member screens pass at candidate level, but adapter countersink pull-through/local stress remains a blocker.

## Sol finding disposition

| Sol concern | R55 state | Still required |
|---|---|---|
| No buildable mechanical definition | Improved, still open | received frame stack, released adapter, exact M2.5/M5 stack, cables, stops, manufacturing drawing, FAI and proof |
| No closed mass/inertia model | Open | received masses, COM/inertia and full allocation closure |
| Unproven continuous joint torque | Open | current/thermal/duty characterization and qualified drivetrain review |
| Insufficient dynamic restraint/stopping | R55 found a 122 degree collision and fails closed at a provisional 120 degree limit | hard stop, measured stopping overtravel and fault tests |
| No executed approved verification | Open | calibrated fixtures, raw records, accountable execution and approval |

R55 closes no procurement, fabrication, assembly, energization or functional-safety gate. HR-V0 remains not build-ready and energization remains prohibited.
