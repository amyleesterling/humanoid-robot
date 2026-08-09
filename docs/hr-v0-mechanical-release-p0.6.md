# HR-V0 integrated mechanical release candidate P0.6

> **PRELIMINARY—INTEGRATED CANDIDATE ONLY—NOT RELEASED FOR QUOTATION, FABRICATION, ASSEMBLY, MOTION, OR ENERGIZATION.**

Date: 2026-08-07

Identifier: `HR-V0-MECH-P0.6`

Supporting arm candidate: `HR-V0-ARM-ARCH-P0.7`

Supporting stop basis: `HR-V0-HS-P0.3` / `HR-V0-J2-STOP-P0.1`

## Disposition

P0.6 supersedes P0.5. It retains A00–A07 and the J2 `15..115 deg` command candidate, then integrates the C06/C07 positive-metal stop CAD candidate as `HS-J2-POS`. The stop pair is separately analyzed from the 69-pair continuous body-clearance certificate.

The controlled straight-reference datums remain C0 `(-210,0,0) mm`, J1 `(-210,81.025,500) mm`, J2 `(-210,283.575,500) mm`, G1 `(-210,412.625,500) mm`, and OMAX `(-210,441.025,500) mm`.

Nominal C06/C07 metal contact is `117.999985 deg`; nominal body contact remains `121.643289 deg`. The maximum unselected `0.75 mm` bumper envelope does not contact at the `115 deg` software ceiling. These are analytical configuration facts, not released physical limits.

## Controlled evidence

- `docs/hr-v0-arm-architecture-p0.7.md`
- `docs/hr-v0-hard-stop-design-basis-p0.3.md`
- `cad/hr-v0/generated/arm-architecture-p0.7/`
- `cad/hr-v0/generated/assembly/`
- `cad/hr-v0/mechanical-release-data.csv`
- `tests/forms/hr-v0-mechanical-release-inspection-template.csv`
- `tests/forms/hr-v0-j2-limit-stop-template.csv`
- `tools/generate_hr_v0_arm_architecture.py`
- `tools/check_hr_v0_arm_architecture.py`
- `tools/generate_hr_v0_mechanical_release.py`
- `tools/check_hr_v0_mechanical_release.py`
- `docs/hr-v0-mechanical-parity-p0.1.md`
- `release/hr-v0/mechanical-parity-p0.1/`
- `tools/generate_hr_v0_mechanical_parity.py`
- `tools/check_hr_v0_mechanical_parity.py`

R135 independently confirms the five STEP/DXF profile extents and all thirty nominal hole features. It also identifies eight countersink pairs whose centers agree but whose STEP opening is modeled at `Ø11.40 mm`, the upper limit of the drawing/DXF `Ø11.30 +0.10/-0.00 mm` control. That semantic difference remains an open qualified-review disposition; no supplier may infer nominal or tolerance from STEP alone. Six drawing controls also remain schedule-bound instead of fully displayed on the readable SVGs.

## Remaining release boundary

Bumper selection and characterization; received material, fit and FAI; complete stop tolerance/load/contact analysis; A00 T-slot capacity; fastener installation; cable and guard envelopes; mass/COM/inertia; measured contact, backlash, compliance and stopping overtravel; continuous-duty and thermal tests; physical proof; and qualified mechanical/functional-safety review remain open. J1 and J2-negative stops remain undesigned. The Boston bench/anchor design remains site-specific and unproved.

Automated checks establish repository consistency and nominal analytical evidence only. `EG-005` through `EG-008` remain partial. No fabrication, motion or energization authorization is issued.
