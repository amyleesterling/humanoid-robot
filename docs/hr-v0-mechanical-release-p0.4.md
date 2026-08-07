# HR-V0 integrated mechanical release candidate P0.4

**PRELIMINARY - INTEGRATED CANDIDATE ONLY - NOT RELEASED FOR QUOTATION, FABRICATION, ASSEMBLY, MOTION, OR ENERGIZATION**

Date: 2026-08-07

Identifier: `HR-V0-MECH-P0.4`

Supporting arm candidate: `HR-V0-ARM-ARCH-P0.5`

## Disposition

P0.4 supersedes the P0.3 state in which the current arm datums were deliberately blank. It integrates P0.5's exact-coordinate column, shoulder support, arm, and H104 candidate into the base/frame coordination package. The generated general arrangement, datum schedule, release tables, inspection template, release metadata, and native arm assembly now agree on J1, J2, G1, A00-A07, and the provisional joint limits.

This is a configuration closure, not a fabrication release. Native CAD and dimensioned candidate drawings exist, but the evidence chain still stops before material receipt, FAI, complete fastener installation control, physical fit, structural proof, continuous collision proof, hard-stop validation, cables/guard integration, and qualified acceptance.

## Controlled candidate datums

| Datum | A0 coordinate in straight reference | Status |
|---|---:|---|
| C0 column centerline | `(-210, 0, 0) mm` | base candidate; received squareness/proof open |
| J1 shoulder axis | `(-210, 81.025, 500) mm` | integrated candidate |
| J2 elbow axis | `(-210, 283.575, 500) mm` | integrated candidate |
| G1 H104 frame origin | `(-210, 412.625, 500) mm` | integrated candidate; received gripper stack open |
| OMAX boundary | `(-210, 441.025, 500) mm` | controlled 360 mm J1-relative requirement boundary; actual TCP must remain at or inside |

The provisional J2 command range is `15 to 120 degrees`. A 40,001-pose sampled study extends to `125 degrees` only to expose the nominal contact boundary at `122 degrees`; those outside-limit poses are not command authorization.

## Reproducible evidence

- `tools/generate_hr_v0_arm_architecture.py` and `tools/check_hr_v0_arm_architecture.py`
- `cad/hr-v0/generated/arm-architecture-p0.5/`
- `tools/generate_hr_v0_mechanical_release.py` and `tools/check_hr_v0_mechanical_release.py`
- `cad/hr-v0/generated/assembly/`
- `cad/hr-v0/mechanical-release-data.csv`
- `cad/hr-v0/mechanical-interface-control.csv`
- `cad/hr-v0/mechanical-assembly-components.csv`
- `tests/forms/hr-v0-mechanical-release-inspection-template.csv`
- `tests/forms/hr-v0-robotis-interface-closure-template.csv`

The automated checks establish artifact consistency and deterministic candidate geometry only. They do not establish material properties, fastener preload, safety factor, fatigue life, collision clearance between samples, stopping distance, physical suitability, or permission to fabricate or energize.

## Remaining release boundary

Before a qualified reviewer can release any arm article, the project must close the open evidence listed in `docs/hr-v0-arm-architecture-p0.5.md`, including the A00 T-slot load path and A07 received H104/RM-X52/HN12-I101 assembly. The base still requires an exact Boston bench survey, anchoring design, received frame-joint fit, developed torque, slip/prying proof, and qualified disposition. The guard, catch, cable route, hard stops, motion limits, mass/COM/inertia, actuator continuous-duty/thermal performance, and proof-test fixtures remain unresolved.

`EG-005` through `EG-008` remain partial. No fabrication or energization authorization is issued.
