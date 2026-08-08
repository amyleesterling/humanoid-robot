# HR-V0 controlled object and handoff evidence package P0.1

Identifier: **HR-V0-OBJ-CTRL-P0.1**
Status: **PRELIMINARY - TEMPLATES NOT EXECUTED; NOT APPROVED FOR PROCUREMENT, ASSEMBLY, MOTION, TESTING, OR ENERGIZATION**
Date: 2026-08-08
Requirements: `SYS-002`, `SAFE-011`, `VER-001`
Procedures: `INSPECT-OBJ-001`, `TEST-HAND-001`

## Purpose

This package synchronizes the retained object baseline across the requirement, verification registry and evidence forms. It makes the 40 mm minimum impossible to omit from a future gripper or handoff decision. It does not select or create the physical object.

## Controlled requirement

The test uses one serialized soft-foam object. Accepted mass including measurement uncertainty must be no more than 100 g. Each of the three accepted principal dimensions including measurement uncertainty must be between 40 mm and 70 mm inclusive.

The exact object still requires a controlled product/material/lot or a separately accepted fabrication definition. Its grip axis, contact faces, conditioning, support method, dimensional measurement force, sampling, instruments, uncertainty, damage criteria and permanent-set limit remain `SELECTION REQUIRED`. Foam compressibility shall not be used to claim compliance with an undersized gripper.

## Fail-closed sequence

1. Freeze the exact candidate object identity, material, lot and nominal geometry.
2. Release the conditioning and low-force measurement method, including contact geometry and force.
3. Calibrate the mass and dimensional instruments and approve the uncertainty method.
4. Mark the object ID, principal axes, grip axis and intended contact faces without changing its behavior.
5. Execute `INSPECT-OBJ-001`; attach raw readings, uncertainty calculation, photographs and qualified acceptance.
6. Confirm the same object ID, configuration commit, software hashes, gripper, nests, catch, guard and trajectory before `TEST-HAND-001`.
7. Record all 100 attempted cycles individually with synchronized logs and video.
8. Repeat the object inspection and teardown inspection; disposition every deviation before any pass claim.

If identity, calibration, uncertainty, configuration, synchronization or required evidence is missing, the result is invalid rather than assumed passing.

## Acceptance logic

- Exactly 100 cycles must be attempted and recorded.
- At least 99 transfers must satisfy the released cycle-success definition.
- Zero unsafe faults are permitted.
- Zero payload escapes from the released catch/guard are permitted.
- The same accepted serialized object must be used for all cycles.
- Every cycle must resolve to raw controller/fault/telemetry logs and synchronized video.
- Pre- and post-test object condition must meet separately released damage and permanent-set limits.

One unsuccessful transfer is not automatically an unsafe fault, but it must remain contained, fully evidenced and dispositioned. Nothing in this package relaxes stop, guard, catch, gripper, motion, thermal, electrical or qualified-authorization gates.

## Current evidence state

The object-metrology form contains twelve blank or open records. The handoff form contains 100 `NOT EXECUTED` cycle rows. The summary form contains released arithmetic criteria but no actual counts or disposition. No object has been selected, acquired, marked, measured or accepted; no handoff cycle has been run.

## Release boundary

This is a definition and evidence-control package. It closes a documentation mismatch only. It does not close `SYS-002`, `SAFE-011`, `VER-001`, `INSPECT-OBJ-001`, `TEST-HAND-001`, `EG-008`, `EG-028`, `EG-029` or any energization gate. Qualified mechanical, controls, test and safety review remain required before physical execution.
