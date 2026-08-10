# HR-V0 DYNAMIXEL transport and execution boundary P0.2

**PRELIMINARY—SOURCE CANDIDATE ONLY—NOT APPROVED FOR CONNECTION, FLASHING, FABRICATION, OR ENERGIZATION**

Identifier: `HR-V0-DXL-TRANSPORT-P0.2`

Date: 2026-08-07

Parent firmware candidate: `HR-V0-FW-P0.3`

P0.2 retains the ordered torque-off, discovery, identity/configuration readback, authority-bound synchronous writes, telemetry checks, watchdog handling, and fault-triggered torque removal documented in `hr-v0-dynamixel-transport-p0.1.md`. It corrects the configuration boundary by adding the exact R67 mechanical identifiers and engineering-unit motion envelope.

J2 raw conversion is now bounded by 15° through 115° even if the received actuator raw range is wider. The port remains unopened until all existing selections close and the mechanical-limit binding is explicitly `ACCEPTED-FOR-GUARDED-HIL` with a non-placeholder evidence hash. The committed file intentionally does not meet that condition.

The SDK remains ROBOTIS DYNAMIXEL SDK 4.0.5, tag 4.0.5, upstream commit `2ded684`, released 2026-05-06. All P0.1 primary-source links and physical/HIL evidence requirements remain applicable. No target installation, connection, register write, actuator motion, or functional-safety validation occurred.

`EG-017` remains **partial**.

**PRELIMINARY—SOURCE CANDIDATE ONLY—NOT APPROVED FOR CONNECTION, FLASHING, FABRICATION, OR ENERGIZATION**
