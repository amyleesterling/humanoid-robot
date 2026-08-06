# HR-V0 release specification — bench arm

Document ID: HR-REL-V0  
Revision: 0.1  
Status: current engineering baseline; unbuilt and unvalidated

## Capability earned

A fixed, guarded, three-axis bench mechanism repeatedly transfers one soft foam object while proving the proposed power, stop, watchdog, communications, thermal, logging, and test architecture.

## Included configuration

- One shoulder rotation axis, one elbow rotation axis, and one parallel gripper axis.
- Rigid bench mounting and fixed shielding or an approved controlled exclusion boundary.
- External compute, safety-control power, and actuator power in separately protected domains.
- Dual-channel emergency stop, monitored actuator-energy contactors, and an independent heartbeat permit.
- Foam payload only: 100 g and 70 mm maximum.

## Entry conditions

- Released schematic, BOM, mechanical definition, software configuration, and test procedures identify matching revisions.
- Power-off inspection passes before any actuator branch is connected.
- Safety circuit is proven with actuator branches disconnected.

## Acceptance criteria

- Exactly two arm axes and one gripper axis are present and bounded by software limits and mechanical stops.
- Automatic tool-center speed is at most 0.15 m/s; setup motion is hold-to-run and at most 10 deg/s.
- E-stop, heartbeat loss, communications loss, overtemperature, overcurrent, and limit faults reach the defined latched response without automatic restart.
- The mechanism completes 100 fixture handoffs with at least 99 successes, no unsafe fault, and complete logs.
- Structural proof, grip-force, electrical-load, and worst-duty thermal tests pass.

## Required evidence

Approved records for INSPECT-SYS-001, TEST-HAND-001, TEST-SAFE-001 through TEST-SAFE-003, TEST-MECH-001, TEST-THERM-001, TEST-GRIP-001, TEST-POWER-001, and AUDIT-CFG-001.

## Boundary

HR-V0 is not a humanoid body, walking system, toy, human-contact release, or child-accessible device.
