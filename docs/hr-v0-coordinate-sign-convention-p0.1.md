# HR-V0 coordinate and sign convention P0.1

> **PRELIMINARY - NOT APPROVED FOR FABRICATION, MOTION, CONNECTION, OR ENERGIZATION.**

Date: 2026-08-09

Identifier: `HR-V0-FRAME-CONV-P0.1`

Controlled inputs: `HR-V0-MECH-P0.6`, `HR-V0-ARM-ARCH-P0.7`, `HR-V0-ACT-P0.3`, `HR-V0-SUP-P0.3`

## Result

The HR-V0 assembly, kinematics, load calculations, controls and metrology now share one right-handed base convention:

- `A0_BASE_CENTER` is centered on the nominal base footprint at the bench plane.
- `+X` points to the robot's right, from the rear/operator side facing the front.
- `+Y` points toward the robot's front.
- `+Z` points upward from the bench.
- `J1_LOCAL` is at `A0 + (-210.000, 81.025, 500.000) mm`.
- `J2_ZERO` is at `J1_LOCAL + (0.000, 202.550, 0.000) mm`.
- `G1_H104_ZERO` is at `J1_LOCAL + (0.000, 331.600, 0.000) mm` with the controlled H104 straight-reference `Rx=180 degrees` orientation.

`J1` and `J2` positive engineering motion follows the right-hand rule about local `+X`. At each geometric zero, its outgoing link lies on local `+Y`; increasing engineering angle moves that direction toward local `+Z`. J2 zero is a geometry datum only and is outside the candidate `15..115 degree` command range.

## Legacy guard-layout correction

The historical guard P0.2/P0.3 summary names `x=depth`, `y=width`, and `z=height`. That axis swap is useful for rectangular layout dimensions but has determinant `-1` relative to the right-handed A0 basis. It is therefore renamed `G0_LEGACY_LAYOUT` and prohibited for rotations, cross products, torque, inertia, kinematics or controls.

The successor `G0_RH` origin remains the vertical projection of J1 on the bench, at `A0 + (-210.000, 81.025, 0.000) mm`, but its axes are parallel to A0. Historical dimensions map as:

- `x_depth legacy -> G0_RH +Y`
- `y_width legacy -> G0_RH +X`
- `z_height legacy -> G0_RH +Z`

No existing guard geometry or dimension is silently reinterpreted as a rigid transform. The next guard revision must encode `G0_RH` explicitly and retain the mapping for traceability.

## Raw actuator boundary

The P0.7 manufacturer-package transform records that each XM540 native local `+Z` output axis maps to project joint `-X`. This fact does not establish whether increasing DYNAMIXEL position readback produces positive or negative project engineering motion on an assembled device.

For J1, J2 and the gripper, exact received model/firmware identity, raw direction, raw scale, raw zero, raw limits and start tolerance remain `RECEIVED CALIBRATION REQUIRED` or `SELECTION REQUIRED`. The blank six-record calibration form requires two independent mechanical/metrology references for every axis. Until an accepted evidence hash binds those results, firmware must continue to refuse port opening and motion authority.

The gripper engineering coordinate means verified usable object opening in millimetres. Positive means a larger verified opening. Published stroke or mesh distance is not substituted for received usable-opening calibration.

## Mirroring boundary

HR-V0 has one bench arm and no left/right mirrored joint. No actuator direction may be synthesized by mirroring HR-V0 data. HR-30 must release a separate world/body/left/right frame, joint-sign, zero-pose and raw-polarity convention. `CFG-002` continues to require any polarity or mirrored-joint mismatch to inhibit drive enable and latch a recorded fault.

## Controlled artifacts

- `cad/hr-v0/generated/coordinate-convention-p0.1/frame-register.csv`
- `cad/hr-v0/generated/coordinate-convention-p0.1/transform-register.csv`
- `cad/hr-v0/generated/coordinate-convention-p0.1/joint-sign-register.csv`
- `cad/hr-v0/generated/coordinate-convention-p0.1/legacy-layout-mapping.csv`
- `cad/hr-v0/generated/coordinate-convention-p0.1/mirroring-register.csv`
- `cad/hr-v0/generated/coordinate-convention-p0.1/coordinate-convention-holds.csv`
- `cad/hr-v0/generated/coordinate-convention-p0.1/source-register.csv`
- `cad/hr-v0/generated/coordinate-convention-p0.1/coordinate-convention-summary.json`
- `cad/hr-v0/generated/coordinate-convention-p0.1/HR-V0_coordinate-sign-convention.svg`
- `tests/forms/hr-v0-coordinate-calibration-template-p0.1.csv`
- `release/hr-v0/coordinate-convention-p0.1/index.html`
- `tools/generate_hr_v0_coordinate_convention.py`
- `tools/check_hr_v0_coordinate_convention_p01.py`

All ten holds remain open. Nothing here establishes physical datum location, actuator polarity, calibration, collision clearance, stopping behavior, gripper geometry, functional-safety performance, or permission to fabricate, connect, move or energize.
