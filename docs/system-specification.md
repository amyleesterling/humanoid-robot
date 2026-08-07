# HR-V0 System Specification

Document ID: HR-SYS-001  
Revision: 0.1  
Program baseline: HR-30-SYS-R0.2  
Status: Concept baseline; not a build release

## 1. Mission

HR-V0 shall demonstrate a repeatable, supervised transfer of a lightweight foam block using the same layered architecture intended for the 762 mm HR-30 humanoid. It exists to retire safety, actuator, power, thermal, control, and integration risks before full-body work. HR-V0 dimensions are a joint test article and do not define the final character proportions.

The first scored behavior is:

1. An operator places a 100 g maximum foam block in a fixed, keyed nest.
2. From outside the exclusion zone, the operator commands one prevalidated trajectory.
3. The arm closes the gripper, lifts the block, and presents it to an instrumented receiver fixture.
4. The fixture asserts `receiver_ready`; the gripper releases; the arm returns to park.
5. Any missing heartbeat, limit violation, overcurrent, overtemperature, communication loss, emergency-stop action, or unexpected receiver state causes the defined safe response.

Human-to-robot or robot-to-human handoff is not part of the initial acceptance test. It is a later V0 extension after fixture testing passes.

## 2. Physical envelope

| Parameter | Baseline value |
|---|---:|
| Active axes | shoulder pitch, elbow pitch, parallel gripper |
| Shoulder-to-elbow length | 191.5 mm R54 architecture candidate; NOT RELEASED; final tolerance and structure SELECTION REQUIRED |
| Elbow-to-gripper-frame origin | 118.0 mm R54 architecture candidate; NOT RELEASED; leaves 50.5 mm to 360 mm object-center ceiling; final gripper/TCP transform SELECTION REQUIRED |
| Maximum shoulder-to-object reach | 360 mm |
| Payload | 100 g maximum, soft foam only |
| Payload envelope | 40–70 mm each principal dimension |
| Automatic joint speed | Pose-dependent limit derived from the 0.15 m/s tool-center limit; 30 deg/s is an additional ceiling, not sufficient enforcement by itself |
| Setup joint speed | 10 deg/s maximum, hold-to-run |
| Tool-center linear speed | 0.15 m/s maximum |
| Moving assembly mass | 0.75 kg maximum, excluding shoulder actuator/base |
| Workspace | dry indoor lab, 18–28 °C, noncondensing |
| Duty cycle | 10 cycles followed by thermal inspection; 30 min session maximum until validated |
| Base | rigid bench mount, four M8 fasteners, steel backing plate |

All values are verification targets. CAD mass properties and measured as-built values replace estimates before build release.

## 3. Operating modes

- `POWER_OFF`: actuator rail de-energized.
- `SAFE_OFF`: computer and logs powered; actuator rail de-energized; restart required.
- `SETUP`: trained operator only, hold-to-run, 10 deg/s, no autonomous motion.
- `AUTO_FIXTURE`: exclusion zone clear; only signed, prevalidated trajectories.
- `FAULT`: torque command zero, actuator power removed when required, fault latched.

No unrestricted teleoperation, generated motion, voice-triggered motion, or AI-originated direct actuator command is permitted in V0.

## 4. Safety concept

The emergency stop is a proposed stop-category-0 design for V0: a dual-channel mushroom switch opens a safety relay, which de-energizes two series contactors in the 12 V actuator rail. Computer power remains present for fault logging. The current Electrical V2.1 watchdog permit is wired downstream of the safety outputs and removes actuator power on a lost heartbeat, but heartbeat restoration could reclose that permit while the safety relay remains latched. That restart path is a safety-architecture blocker. A released revision shall make watchdog dropout force a monitored physical-reset cycle, or use another independently reviewed hardware restart interlock; a firmware latch is not credited. The emergency-stop path itself does not depend on Linux, ROS, networking, or the watchdog microcontroller.

The arm shall be surrounded by fixed transparent shielding during fixture tests. The only normal access is with actuator power off. A floor/bench exclusion boundary of at least 600 mm from the maximum swept envelope shall be marked and controlled by the test lead.

The project borrows risk-reduction principles from ISO 10218-1:2025, ISO 10218-2:2025, ISO/TS 15066:2016, and ISO 13850, but this document does not claim compliance or certification. ISO 10218 explicitly does not cover public-access/service-robot use; child-adjacent operation therefore needs a separate standards and regulatory review.

## 5. Success criteria

V0 passes only when:

- every `MUST` requirement in `requirements/requirements.csv` passes its referenced test;
- 100 consecutive fixture handoffs complete with no unsafe fault and at least 99 successful transfers;
- emergency-stop and watchdog stopping tests pass from the worst tested pose and speed;
- no actuator case exceeds the provisional 65 °C test limit and no power conductor exceeds a 20 °C rise over ambient;
- measured joint current and torque margins are reviewed against the as-built mass model;
- the risk register has no open `high` or `critical` residual risk;
- mechanical and electrical reviewers sign the release checklist.

## 6. Configuration control

Every released assembly receives a configuration record containing CAD revision, firmware commit, controller image version, actuator model/serial/firmware, wiring revision, BOM revision, calibration file hash, and completed test report. Parts may not be substituted by appearance or nominal rating alone.

## 7. Explicit exclusions

V0 does not include walking, wheels, batteries, stairs, outdoor use, lifting a person, sharp/hot/liquid payloads, unsupervised operation, open-loop motion, learning on hardware, collision-based exploration, or operation around children.

## 8. Program product baseline

The full product target is HR-30: 762 mm nominal standing height, 740–800 mm configuration tolerance, 10 kg absolute mass ceiling, friendly non-realistic external form, and staged activation culminating in walking. The controlling product definitions are `docs/full-body-specification.md` and `docs/walking-system.md`. HR-30A is bolted to a pedestal; HR-30B/C/D use an engineered overhead restraint. HR-30W removes the tether only after the walking release tests pass and only inside a controlled test area.
