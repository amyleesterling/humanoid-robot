# HR-V0 integrated mechanical release candidate P0.5

> **PRELIMINARY—INTEGRATED CANDIDATE ONLY—NOT RELEASED FOR QUOTATION, FABRICATION, ASSEMBLY, MOTION, OR ENERGIZATION.**

Date: 2026-08-07

Identifier: `HR-V0-MECH-P0.5`

Supporting arm candidate: `HR-V0-ARM-ARCH-P0.6`

Supporting stop basis: `HR-V0-HS-P0.2`

## Disposition

P0.5 supersedes the P0.4 current release hold. It retains the exact-coordinate A00-A07 arm candidate and adds the continuous nominal collision evidence and conservative candidate J2 soft-limit/stop allocation.

This is configuration and analytical closure only. It is not a fabrication or motion release.

## Controlled candidate datums

| Datum | A0 coordinate in straight reference | Status |
|---|---:|---|
| C0 column centerline | `(-210, 0, 0) mm` | base candidate; received squareness/proof open |
| J1 shoulder axis | `(-210, 81.025, 500) mm` | integrated candidate |
| J2 elbow axis | `(-210, 283.575, 500) mm` | integrated candidate |
| G1 H104 frame origin | `(-210, 412.625, 500) mm` | integrated candidate; received gripper stack open |
| OMAX boundary | `(-210, 441.025, 500) mm` | 360 mm J1-relative requirement boundary; actual TCP must remain inside |

The candidate J2 command range is `15..115 deg`. A candidate positive hard-stop datum is `118 deg`. The continuous nominal body certificate covers through `120 deg` and places first nominal contact at `121.643289 deg`. None of these values is a released physical limit.

## Controlled evidence

- `docs/hr-v0-arm-architecture-p0.6.md`
- `docs/hr-v0-hard-stop-design-basis-p0.2.md`
- `cad/hr-v0/generated/arm-architecture-p0.6/`
- `cad/hr-v0/generated/assembly/`
- `cad/hr-v0/mechanical-release-data.csv`
- `cad/hr-v0/mechanical-interface-control.csv`
- `cad/hr-v0/mechanical-assembly-components.csv`
- `tests/forms/hr-v0-mechanical-release-inspection-template.csv`
- `tests/forms/hr-v0-j2-limit-stop-template.csv`
- `tools/generate_hr_v0_arm_architecture.py`
- `tools/check_hr_v0_arm_architecture.py`
- `tools/generate_hr_v0_mechanical_release.py`
- `tools/check_hr_v0_mechanical_release.py`

Automated checks establish artifact consistency, nominal geometry and a conservative rigid-model clearance lower bound. They do not establish as-built material properties, preload, fatigue life, impact behavior, stopping distance, cable/guard clearance, physical suitability, safety integrity or permission to fabricate or energize.

## Remaining release boundary

Before any arm article can be released, the project must close received material/fit/FAI, exact installation and proof data, qualified calculation acceptance, the A00 T-slot load path, the physical hard-stop design and measured stop allocation, cable/guard envelopes, mass/COM/inertia, continuous-duty actuator/thermal behavior, physical proof and qualified mechanical/functional-safety review. The base still requires an exact Boston bench survey, anchor design and proof.

`EG-005` through `EG-008` remain partial. No fabrication or energization authorization is issued.
