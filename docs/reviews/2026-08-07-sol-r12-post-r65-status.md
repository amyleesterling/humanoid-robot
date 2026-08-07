# Sol R12 finding status after R65

Date: 2026-08-07

Current configuration: `HR-30-SYS-R0.2`, Electrical `V3-P1.8`, firmware `HR-V0-FW-P0.2` with `HR-V0-DXL-TRANSPORT-P0.1`

Status: **PRELIMINARY—NOT APPROVED FOR CONNECTION, FABRICATION, FLASHING, OR ENERGIZATION**

This is a project-owned reconciliation of the existing independent Sol R12 review after R65. It is not a new Sol review and is not counted as one.

## Corrected source gap

Sol accurately reported that the earlier candidate had no DYNAMIXEL transport or execution layer. R65 adds a pinned Protocol 2.0 SDK adapter and a fail-closed controller that:

- refuses to open a port while any device, received identity, calibration, profile or physical-limit selection is unresolved;
- commands torque off to the expected set before discovery and to every discovered ID before accepting the bus;
- requires an exact ID/model set plus register readback with torque off;
- writes a zero-jump start target, current/profile bounds and Bus Watchdog before torque enable;
- binds writes to fresh supervisor authority and one trajectory identity; and
- removes torque after authority, packet, watchdog, hardware-error, current, voltage or temperature failure.

The source suite now contains 43 executable tests across the supervisor and watchdog packages. Nine transport HIL cases remain explicitly `NOT EXECUTED`.

## Findings that remain open

R65 does not make HR-V0 buildable or energizable. It does not close the Sol R12 blockers concerning buildable mechanical definition, functional-safety allocation and validation, stopping time/distance, DC contactor duty, PE/grounding, mass/inertia closure, continuous torque and thermal evidence, power-loss response, dynamic restraint, battery/power architecture, or received hardware.

For the transport specifically, the following remain unresolved:

1. target operating-system/Python image and exact installed SDK artifact/hash;
2. stable serial device path, U2D2 hardware/USB revision and retained cable;
3. received actuator model numbers, firmware versions, IDs and torque-off register captures;
4. assembly-specific zero, direction, scale, raw range and start tolerance;
5. profile, current, voltage and temperature limits established by guarded tests;
6. external branch current, connector temperature, regeneration and protection evidence;
7. target timing, process crash, packet fault, USB interruption, brownout and actuator reboot HIL;
8. stopping-time and no-resume evidence on the accepted mechanism; and
9. independent controls, electrical and qualified functional-safety review.

All 30 energization gates remain unchanged: **0 closed, 22 partial, 8 open**. `EG-017` remains partial. No SDK was installed on a target, no port was opened, no device was connected, and no mechanism was energized.

## Independent-review request

Use `docs/reviews/2026-08-07-firmware-p0.2-independent-review-request.md` against the exact candidate commit. Reviewers must reproduce source checks, audit the SDK API and signed encoding, inspect torque-off/identity/configuration/authority ordering, and keep target execution and all physical HIL evidence separate from source-model results.

**PRELIMINARY—NOT APPROVED FOR CONNECTION, FABRICATION, FLASHING, OR ENERGIZATION**
