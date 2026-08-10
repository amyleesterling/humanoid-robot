# HR-V0 firmware source candidate P0.4

> **PRELIMINARY—SOURCE CANDIDATE ONLY—NOT APPROVED FOR CONNECTION, MOTION, OR ENERGIZATION.**

Date: 2026-08-07

Identifier: `HR-V0-FW-P0.4`

Supervisor: `HR-V0-SUP-P0.3`

Actuator configuration: `HR-V0-ACT-P0.3`

Transport: `HR-V0-DXL-TRANSPORT-P0.3`

Mechanical binding: `HR-V0-LIMITS-P0.2` / `HR-V0-MECH-P0.6` / `HR-V0-ARM-ARCH-P0.7` / `HR-V0-HS-P0.3`

## R69 result

P0.4 preserves the candidate J2 engineering envelope of `15..115 deg` and updates every supervisor/actuator binding identifier to the current mechanical/stop package. It does not accept the new CAD evidence automatically. The committed binding remains `CANDIDATE-NOT-RELEASED` and the acceptance-evidence hash remains `SELECTION REQUIRED`; selection closure therefore remains false and the transport refuses to open a serial port.

The mechanical stop is an analytical candidate only. Before the binding can be accepted for guarded HIL, the exact as-built configuration, calibration, hard-stop contact, bumper, stopping, backlash, compliance, tolerance and uncertainty evidence must be independently accepted and hashed. Device path, actuator identities, kinematic/configuration hashes, raw conversion, voltage/temperature/current limits and profiles remain unresolved.

No target was flashed, no actuator was connected, and no HIL or powered motion was performed. Source tests and reproducible build evidence are not functional-safety approval or permission to energize.
