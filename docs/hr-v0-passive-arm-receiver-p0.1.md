# HR-V0 passive arm-receiver candidate P0.1

**PRELIMINARY - NOT APPROVED FOR FABRICATION, MOTION OR ENERGIZATION**

Document ID: `HR-V0-PASSIVE-ARM-RECEIVER-P0.1`

Date: 2026-08-09

Controlled parents: `HR-V0-ARM-ARCH-P0.7`, `HR-V0-COLLAPSE-ENV-P0.1`, `HR-V0-GUARD-P0.3`, `HR-V0-POWERLOSS-P0.1`

Gates: `EG-008` and `EG-009` remain `partial`

## Decision

Proceed with a raised, guided passive receiver platen inside the fixed guard. The candidate contact surface is at `Z = 320 mm`, below the present known commanded-workspace lower bound and `180 mm` above the R126 full-collapse-envelope bottom. The original P0.3 floor tray remains the separate object catch at `Z = 26 mm`.

This is the first controlled arm-receiver geometry. It is not a fabrication release or an accepted impact system. The complete gripper, object, cables, contact material, linear guides, joints, peak load, physical stops and test evidence remain open.

## Commanded-workspace separation

The generator evaluates conservative AABB corners for the eleven known P0.7 moving B-Reps over:

- J1: `-20 to +70 deg`;
- J2: `15 to 115 deg`; and
- grid: `0.25 deg`, or `144,761` two-axis poses.

The sampled minimum is `Z = 384.142619 mm`, controlled by the H104 frame at J1 `-20 deg`, J2 `15 deg`. A radial Lipschitz bound deducts `1.036141 mm` for motion between adjacent grid points, producing a continuous known-geometry lower bound of:

```text
Zknown,commanded >= 383.106478 mm
```

The proposed receiver top therefore has `63.106478 mm` nominal separation from the known commanded geometry. That residual is not a released clearance: the complete gripper, object, cables, tolerance, backlash, deformation, stopping and as-built metrology may consume it.

## Candidate geometry

The receiver consists of:

- one `180 X x 800 Y x 6 Z mm` guided moving platen;
- one `180 x 800 x 10 mm` compliant-contact allocation above it;
- two `840 mm` 80/20 `20-2040` fixed rails with their 40 mm axis vertical;
- four support-post envelopes at X `+/-60 mm`, Y `+/-420 mm`;
- three vertical ACE `MA30M` evaluation-candidate shock absorbers at Y `-300/0/+300 mm`; and
- four unselected linear-guide envelopes at X `+/-70 mm`, Y `+/-350 mm`.

The platen and pad occupy X `-90..+90 mm`, Y `-400..+400 mm`, and finish at `Z = 320 mm`. They fit inside the current X `-200..+200 mm`, Y `-450..+450 mm` guard reservation. Exact finished parts, joints and mounting interfaces are not defined.

## Absorber screen

The current ACE Controls `MA30M` page, accessed 2026-08-09, publishes:

- `31 in-lb/cycle` energy capacity;
- `0.32 in` stroke;
- `0.5..31 lb` effective-weight range;
- `2.2..14.6 ft/s` impact-velocity range; and
- an integrated positive stop.

Three units give an arithmetic catalog total of `10.507589 J`, or `1.984215` times the R125 `5.295591 J` gravitational-only allocation. A simple equal mass share is `0.250 kg` per unit, above the published `0.226796 kg` minimum.

Those comparisons do not approve the application. The actual effective mass includes platen coupling; actual contact velocity is unknown and may fall below the published range; load sharing, adjustment, side load, temperature, cycles, failure behavior and continued drive remain unproved. ACE document `21_22_0019`, Stand 03.2021, Issue 05.2022, permits parallel units but requires the actual mass, impact velocity, propelling force/torque, cycle rate and unit count for sizing. It also requires axial force application and additional safety elements where failure could cause injury. Written ACE application acceptance is therefore mandatory before selection.

## Preliminary subframe screen

A deliberately provisional `2,000 N` vertical platen input is split ideally between two simply supported 840 mm rails. Using the live 20-2040 page's `Ix = 4.5357 cm4` gives:

- `1,000 N` per rail;
- `210,000 N mm` maximum simple-span moment;
- `92.598717 MPa` nominal bending stress; and
- `500 N` ideal reaction at each rail end.

Using `E = 68.9 GPa` as a typical modulus gives `3.951237 mm` nominal center deflection. The live product page's `172.37 MPa` yield value is only a comparison point, not a project allowable. The `2,000 N` input is not an accepted peak or proof load. Unequal sharing, local platen contact, shock reaction, guides, brackets, posts, base/guard transfer, anchors, fatigue and impact remain open.

## Required closure evidence

Twelve fail-closed hold groups remain:

1. complete gripper/object/cable geometry;
2. as-built mass, COM, inertia, friction, backlash and contact velocity;
3. ACE application acceptance and received absorber identity;
4. exact guided-platen design and failure containment;
5. selected compliant contact material and characterized force-travel behavior;
6. platen local strength, edges, fasteners and fatigue;
7. rail, joint, post, base and anchor load-path proof;
8. complete bidirectional J1/J2 stops;
9. guard access, pinch, rebound and final-rest proof;
10. continued-drive, regeneration, elastic and detached-part cases;
11. executed FAI, metrology, drop/backdrive and fault tests; and
12. qualified mechanical and functional-safety disposition plus written work authorization.

All 28 physical-evidence rows remain `NOT EXECUTED` and `NOT AUTHORIZED`. `EG-008` and `EG-009` remain partial.

## Primary sources

- [ACE MA30M current product page](https://www.acecontrols.com/us/products/automation-control/miniature-shock-absorbers/ma30-to-ma900/ma30m.html), accessed 2026-08-09; no formal page revision exposed.
- [ACE MA30-MA900 operating and mounting instructions](https://www.acecontrols.com/media/msimages/pdf/ACE_MA30-MA900_Operating-Mounting_EN_21_22_0019.pdf), document `21_22_0019`, Stand 03.2021, Issue 05.2022; accessed 2026-08-09.
- [80/20 20-2040 product page](https://8020.net/20-2040.html), accessed 2026-08-07; no formal page revision exposed.

## Controlled artifacts

- `cad/hr-v0/generated/passive-arm-receiver-p0.1/`
- `tests/forms/hr-v0-passive-arm-receiver-template-p0.1.csv`
- `release/hr-v0/passive-arm-receiver-p0.1/index.html`
- `tools/generate_hr_v0_passive_arm_receiver.py`
- `tools/check_hr_v0_passive_arm_receiver_p01.py`

This package releases no purchase, cut, joint, shock setting, receiver part, test, motion or energization.
