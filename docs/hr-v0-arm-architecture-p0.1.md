# HR-V0 exact-coordinate arm architecture P0.1

**PRELIMINARY—CANDIDATE GEOMETRY ONLY—NOT RELEASED FOR QUOTATION, FABRICATION, ASSEMBLY, OR ENERGIZATION**

Date: 2026-08-07

Identifier: `HR-V0-ARM-ARCH-P0.1`

Parent correction hold: `HR-V0-MECH-P0.3`

## Result

R54 supplies a geometrically coherent replacement candidate for the invalid P0.2 flat-arm assumption. It does not yet release a buildable arm.

The candidate uses the locally controlled manufacturer-coordinate ROBOTIS XM540, FR13-H101K, FR13-S102K and FR12-H104K STEP files. J1 remains in the manufacturer orientation. The J2 actuator and S102 body frame are deliberately rolled +90 degrees about the common X output axis. This makes the S102 outside broad face oppose the J1 H101 outside broad face. A -90 degree J2 output reference offset returns the J2 H101 and forearm to the project +Y straight-reference direction.

The resulting candidate datums are:

| Datum | Project coordinate / transform | Status |
|---|---:|---|
| J1 axis | `(0, 0, 0)`, direction `+X` | candidate datum |
| J1 H101 outside face | `Y = 32.0 mm`, normal `+Y` | exact vendor geometry; connection open |
| J2 S102 outside face | `Y = 140.0 mm`, normal `-Y` | exact vendor geometry after `Rx(+90°)`; connection open |
| J2 axis | `(0, 191.5, 0)`, direction `+X` | architecture candidate |
| J2 H101 straight reference | `T(0,191.5,0) · Rx(0°)` | requires `-90°` output offset relative to J2 body |
| G1 H104 frame origin | `(0, 309.5, 0)`, `Rx(180°)` | frame-transform candidate; 50.5 mm remains to the 360 mm object-center ceiling |

The J1/J2 axis dot product is exactly `1.0`, giving a mathematical angular difference of `0°` in the candidate source. This is a CAD identity check, not an as-built alignment tolerance or inspection result.

## Candidate structural route

The upper link uses a 100 mm member and the forearm uses a 50 mm member. Both use:

- two candidate `48 × 36 × 4 mm` adapter plates;
- the manufacturer broad-face PCD22 geometry where explicitly identified;
- 80/20 `20-2040` as a conservative `40 × 20 mm` collision envelope; and
- the official two-hole M5 end-tap service only as an orderable route under investigation.

The current 80/20 product page, accessed 2026-08-07, identifies `20-2040` as a 20 × 40 mm, 6063-T6, six-slot 20-series profile; publishes `Ix = 4.5357 cm^4`, `Iy = 1.2133 cm^4`, and `0.0428 lb/in`; and offers a two-hole `M5 × 0.80`, 22.23 mm-deep end-tap option. The project does not yet control exact cross-section CAD or end-tap coordinates. The generated beam is therefore a conservative collision envelope, not invented manufacturer geometry.

No adapter material, finished thickness, tolerance, manufacturing process, M2.5/M5 fastener, thread engagement, torque, retention method, or structural capacity is released.

## Machine-checked evidence

`tools/generate_hr_v0_arm_architecture.py` generates:

- a combined exact-source/candidate STEP assembly;
- an interactive GLB;
- two native candidate-part STEP files;
- explicit 4 × 4 transform, interface and collision-sweep schedules;
- a web-readable SVG; and
- a machine-readable geometry, mass and load summary.

`tools/check_hr_v0_arm_architecture.py` fails closed on vendor hashes, transform values, axis parallelism, artifact membership, warning text, interface status and the sampled collision schedule.

Twenty-three poses from 15° through 125° in 5° increments show zero positive solid intersection between the candidate moving forearm group and the fixed upper-arm/J2 group. This is only a sampled self-collision screen. It excludes cable/connector envelopes, tools, guards, stops, base/column geometry, gripper mechanism, continuous interpolation between samples, compliance and tolerances.

## Updated screening loads

Using the existing 0.75 kg allocation buckets at the R54 candidate radii gives:

`T_J1 = 1.762 N·m`

`T_J2 = 0.478 N·m`

Applying the existing `1.5 × 1.5 = 2.25` screening multiplier gives `3.965 N·m` at J1 and `1.075 N·m` at J2. These are configuration screens only. They do not establish continuous actuator capacity, thermal life, gearbox life, frame strength, joint impact capacity, or permission to energize.

The 100 mm upper profile and 50 mm forearm profile masses are estimated from the current official product-page weight as `76.432 g` and `38.216 g`. One candidate adapter is `17.655 g` using a 2.70 g/cm³ density assumption. The upper and forearm member-plus-adapter screens are `111.741 g` and `73.525 g` before fasteners. Received masses, actual material certificates, local centers of mass and inertia remain mandatory.

## Controlled artifacts

| Artifact | Purpose |
|---|---|
| `cad/hr-v0/generated/arm-architecture-p0.1/HR-V0_arm_architecture_candidate.step` | exact-coordinate combined review assembly |
| `cad/hr-v0/generated/arm-architecture-p0.1/HR-V0_arm_architecture_candidate.glb` | interactive review model |
| `cad/hr-v0/generated/arm-architecture-p0.1/HR-V0_arm_architecture_candidate.svg` | readable transform/dimension view |
| `cad/hr-v0/generated/arm-architecture-p0.1/transform-schedule.csv` | explicit homogeneous transforms |
| `cad/hr-v0/generated/arm-architecture-p0.1/interface-schedule.csv` | fail-closed interface/fastener boundary |
| `cad/hr-v0/generated/arm-architecture-p0.1/collision-sweep.csv` | sampled self-collision results |
| `cad/hr-v0/generated/arm-architecture-p0.1/architecture-summary.json` | hashes, dimensions, axis proof, mass/load screen and open items |
| `cad/hr-v0/generated/arm-architecture-p0.1/parts/` | native candidate topology; not supplier geometry |

## Release blockers

Before this candidate can replace the P0.3 hold as a buildable mechanical release, all of the following remain required:

1. freeze controlled exact `20-2040` cross-section/end-machining evidence or substitute a fully defined structural member;
2. select adapter material, thickness, tolerance, finish and manufacturing process from stress, deflection, fatigue, impact and corrosion evidence;
3. release every fastener order code, grade, length, engagement, washer/nut stack, torque and retention rule;
4. prove assembly and service tool access without relying on impossible internal nut access;
5. add exact cable, connector, strain-relief and bend/twist envelopes to a continuous joint-space sweep;
6. reconcile hard stops, guard/catch, column/J1 support and gripper mechanism to the same transform model;
7. execute received-part fit, FAI, mass/COM/inertia, joint-slip, proof, impact and cycle tests;
8. update the immutable mechanical release and supplier packet only after independent qualified mechanical review; and
9. retain all electrical, control and functional-safety energization gates independently.

The P0.2 parts and RFI packets remain withdrawn. R54 creates no active supplier packet and closes no fabrication or energization gate.
