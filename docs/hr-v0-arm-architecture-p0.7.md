# HR-V0 integrated arm architecture P0.7

> **PRELIMINARY—CANDIDATE GEOMETRY ONLY—NOT RELEASED FOR QUOTATION, FABRICATION, ASSEMBLY, MOTION, OR ENERGIZATION.**

Date: 2026-08-07

Identifier: `HR-V0-ARM-ARCH-P0.7`

Parent hold: `HR-V0-MECH-P0.6`

Stop basis: `HR-V0-HS-P0.3` / `HR-V0-J2-STOP-P0.1`

## R69 result

P0.7 preserves the exact A00–A07 axis chain and integrates C06/C07 twin-rail positive-stop candidate geometry at `HS-J2-POS`. The controlled axis coordinates remain J1 `(-210,81.025,500) mm`, J1–J2 `202.550 mm`, and J2–G1 `129.050 mm` with parallel nominal J1/J2 axes.

The continuous nominal certificate covers 69 non-intentional rigid-body pairs over J1 `-20..70 deg` and J2 `15..120 deg`. The C06/C07 stop pair is the sole new intentional contact and is separately analyzed; it is not silently discarded.

| Measure | Result |
|---|---:|
| non-intentional pairs | 69 |
| certified leaf cells | 135 |
| exact B-Rep distance calls | 99 |
| required certified clearance | 0.750000 mm |
| minimum conservative lower bound | 0.765783 mm |
| critical body clearance at J2=120 deg | 0.962813 mm |
| continuous nominal first body contact | J2=121.643289 deg |
| first sampled body collision | J2=122 deg |
| nominal C06/C07 metal contact | J2=117.999985 deg |
| body clearance at metal contact | 2.114900 mm |

The stop has two symmetric external load paths and a separate maximum bumper envelope. It does not rely on the actuator cover or a cable as a stop. The nominal CAD results do not include received tolerances, deformation, backlash, compliance, reflected inertia, cables, guards, stopping travel, calibration error or measurement uncertainty.

## Controlled artifacts

`cad/hr-v0/generated/arm-architecture-p0.7/` contains the integrated STEP/GLB, C01–C07 part STEP/DXF sources, readable SVG drawings, interface/transform schedules, the 40,001-pose exact-boolean sweep, the 69-pair continuous certificate, stop contact STEP/GLB, stop approach/tolerance/load registers, and six stop drawing controls.

`tools/check_hr_v0_arm_architecture.py` verifies exact artifact membership, source hashes, transforms, the separate intentional-stop boundary, clearance floors, target contact, bumper-envelope non-intrusion at the software limit, tolerance/load evidence, unresolved bumper selection and readable warnings.

## Release boundary

No part is released. MTR, DFM, FAI, received fit, complete fastener installation controls, stop/parent-structure analysis, bumper selection, cable and guard definition, physical contact/stopping tests, proof load, fatigue/impact evidence, and qualified mechanical/functional-safety review remain open. J1 and J2-negative physical stops remain undesigned.

No procurement, quotation, fabrication, assembly, motion, energization or functional-safety gate closes in R69.
