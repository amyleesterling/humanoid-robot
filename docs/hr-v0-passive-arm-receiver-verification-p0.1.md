# HR-V0 passive arm-receiver second-method verification P0.1

**PRELIMINARY - INTERNAL SECOND-METHOD VERIFICATION ONLY - NOT APPROVED FOR FABRICATION, MOTION OR ENERGIZATION**

Document ID: `HR-V0-PASSIVE-ARM-RECEIVER-VERIFY-P0.1`

Date: 2026-08-09

Parent: `HR-V0-PASSIVE-ARM-RECEIVER-P0.1`

Gates: `EG-008` and `EG-009` remain `partial`

## Result

R128 independently reconstructs the three numerical claims most important to the R127 receiver candidate without calling its pose-grid or arithmetic functions:

1. continuous known-body separation from the receiver;
2. nominal fit of the serialized receiver STEP inside the fixed-guard reservation; and
3. ACE-unit conversions and the provisional two-rail arithmetic.

All three are corroborated. This is internal computational evidence, not an independent qualified review or physical result.

## Closed-form envelope verification

The P0.7 arm uses parallel J1 and J2 X axes. For each conservative source-BRep AABB corner on the forearm side, the bench-datum height is:

```text
z(q1,q2) = 500 + J2Y sin(q1)
           + (y - J2Y) sin(q1 + q2)
           + zlocal cos(q1 + q2)
```

The current J1 interval is `-20..70 deg`, so it contains no interior point where `cos(q1) = 0`. A two-variable interior stationary point is therefore impossible. R128 evaluates the exact trigonometric extrema on all four boundaries of the J1/J2 rectangle for every corner of all eleven controlled bodies.

The global result is:

- exact minimum inside the conservative AABB-corner model: `384.142618886 mm`;
- controlling body: `H104_FRAME`;
- controlling corner: `(-20.500000050, 334.100000000, -35.250000017) mm`;
- controlling pose: J1 `-20 deg`, J2 `15 deg`; and
- exact model clearance above the `Z = 320 mm` receiver: `64.142618886 mm`.

R127's released candidate remains the more conservative `383.106478372 mm` lower bound and `63.106478372 mm` clearance. The extra `1.036140514 mm` is not reclaimed. Complete gripper, object, cables, tolerances, deformation and as-built evidence remain outside both proofs.

## Serialized STEP and guard-fit verification

R128 re-imports the issued R127 receiver STEP rather than using generator primitives. Its nominal aggregate bounds are:

| Axis | Receiver STEP | Guard internal limit | Limiting margin |
|---|---:|---:|---:|
| X | `-90..+90 mm` | `-200..+200 mm` | `110 mm` per limiting side |
| Y | `-430..+430 mm` | `-450..+450 mm` | `20 mm` per limiting side |
| Z | `20..320 mm` | `0..950 mm` | `20 mm` bottom; `630 mm` top |

The `20 mm` Y result is the smallest nominal horizontal margin. It is not a released assembly clearance because panels, joints, fasteners, tolerances, guard deformation, access and physical fit are still open.

## Independent arithmetic

Decimal re-derivation gives:

- MA30M catalog energy: `3.502529700 J` each;
- three-unit arithmetic sum: `10.507589100 J`;
- catalog/gravitational-input ratio: `1.984214623`;
- published stroke conversion: `8.128 mm`;
- published impact-velocity conversion: `0.67056..4.45008 m/s`;
- provisional simple-span moment: `210,000 N mm`;
- ideal rail stress: `92.598716846 MPa`; and
- typical-property deflection: `3.951236974 mm`.

These values agree with R127. They remain catalog and idealized screens. Unequal shock/rail sharing, peak force, side load, continued drive, joints, allowables, application approval and proof are unresolved.

## Evidence boundary

R128 closes no R127 hold. In particular:

- the receiver has no selected guides, contact layer, platen material, joints, posts or anchors;
- three joint-stop directions and physical acceptance of the fourth remain open;
- the complete moving body and as-built dynamics remain unknown;
- ACE has not accepted the application;
- all 28 R127 physical evidence rows remain `NOT EXECUTED` and `NOT AUTHORIZED`; and
- no qualified mechanical or functional-safety disposition exists.

## Controlled artifacts

- `cad/hr-v0/generated/passive-arm-receiver-verification-p0.1/`
- `release/hr-v0/passive-arm-receiver-verification-p0.1/index.html`
- `tools/generate_hr_v0_passive_arm_receiver_verification.py`
- `tools/check_hr_v0_passive_arm_receiver_verification_p01.py`

This package confirms internal numerical consistency only. It releases no purchase, cut, part, joint, shock setting, physical test, motion or energization.
