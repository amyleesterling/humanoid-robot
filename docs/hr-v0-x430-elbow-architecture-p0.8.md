# HR-V0 X430 elbow architecture P0.8

> **PRELIMINARY — COMPARISON CANDIDATE ONLY — NOT APPROVED FOR QUOTATION, PROCUREMENT, FABRICATION, ASSEMBLY, MOTION, CONNECTION, OR ENERGIZATION.**

Configuration identifier: `HR-V0-ARM-ARCH-P0.8-X430-CANDIDATE`

Date: 2026-08-08

Status: separately identified comparison branch. P0.7 remains controlled and XM430 is not selected.

## Decision

P0.8 is geometrically credible enough for independent review, but it does not supersede P0.7. It reduces the incomplete known/CAD-estimated moving subtotal from 692.758 g to 577.091 g and leaves 172.909 g below the 750 g ceiling. That is not a mass pass: received FR12 frames, exact fasteners, bumper, complete gripper mechanism, connectors, strain relief and moving harness remain absent from the subtotal, and no assembled mass, center of mass or inertia has been measured.

The candidate X430 elbow screen is 1.104 N·m after the existing 2.25 screening multiplier. Dividing ROBOTIS's 4.1 N·m 12 V stall endpoint by that incomplete demand gives 3.713. This is a **stall-endpoint ratio only**. It is not continuous capacity, safety factor, efficiency, thermal margin, connector evidence or permission to energize.

## Exact-coordinate correction

The first bounding-box interpretation of the FR12-S102 file would have placed its outside face only 19.5 mm from the elbow axis. That interpretation was rejected after checking the exact cylindrical axes and the official OpenMANIPULATOR-X assembly sequence.

The released comparison generator instead registers:

- X430 rear case axes at local `X=±11, Y=-32`, parallel to local `Z`;
- FR12-S102 side axes at local `Y=±11, Z=11`, parallel to local `X`;
- an exact `+21 mm` translation of the S102 local Z coordinate before the common package roll;
- the resulting S102 selected axes at joint-registration `Y=±11, Z=32` before roll; and
- an outside fixed-face offset of 40.5 mm from J2.

The X430 local `+Z` output axis maps to project joint `-X`. The X430/S102 fixed package then receives a common `+90°` roll about J2. FR12-H101 remains at the straight-reference output pose and supplies the moving face at `Y=28 mm`; its selected link axes are `X=±12, Z=±6`.

These registrations are reproducible in `interface-feature-evidence.csv` and `transform-schedule.csv`. They do not replace received-part identity, horn/idler stack measurement, fit inspection or first-article inspection.

## Geometry and stop result

| Quantity | P0.7 | P0.8 candidate |
|---|---:|---:|
| J1 to J2 axis | 202.550 mm | 191.550 mm |
| J2 to G1 frame origin | 129.050 mm | 125.050 mm |
| candidate maximum object center from J1 | 360.000 mm | 345.000 mm |
| provisional J2 positive soft limit | 115° | 115° |
| nominal metal-stop contact | 118° | 117.999991° |
| first sampled nonintentional rigid-body intersection | 122° in P0.7 | 120° in P0.8 |

P08-C01 and P08-C02 use two symmetric integral outer wings. The nominal sampled model has zero nonintentional positive-volume intersection through the 115° soft limit and through the 118° stop target. The next sampled nonintentional intersection occurs at 120°. This is only a rigid, nominal, 0.5° sampled result. Continuous between-sample clearance, tolerances, backlash, compliance, deformation, bumper force/stroke, stopping overtravel, rebound, cable, connector, strain-relief and guard envelopes remain open. The 2° nominal stop-to-next-sample interval is not an accepted uncertainty budget.

## Mass and load comparison

| Item | Result | Evidence boundary |
|---|---:|---|
| P08-C01 fixed-catch adapter | 52.234 g | CAD volume × 2.70 g/cm³; received material and mass open |
| P08-C02 moving-striker adapter | 52.234 g | CAD volume × 2.70 g/cm³; received material and mass open |
| incomplete P0.8 known subtotal | 577.091 g | replaces P0.7 J2 actuator/C06/C07 terms only |
| provisional remaining headroom | 172.909 g | every omitted mandatory item must still fit and be measured |
| incomplete elbow gravity result | 0.491 N·m | CAD-estimated forearm plus legacy gripper/payload allocations |
| 2.25 elbow screen | 1.104 N·m | not a continuous-duty or thermal qualification |
| XM430 12 V stall-endpoint ratio | 3.713 | catalog endpoint only |

P0.8 shortens the candidate object-center reach to 345 mm, which remains within the 360 mm maximum requirement. The first foam-block handoff location still requires a released minimum/working reach and physical verification; a maximum requirement alone does not prove task usability.

## What remains open

The twelve R91 architecture holds remain controlling. P0.8 advances only three to partial:

- `ELBH-002`: native X430/FR12 geometry and transforms now exist, but received fit and acceptance do not;
- `ELBH-007`: nominal positive-stop geometry exists, but bumper, tolerance, load and physical proof do not; and
- `ELBH-008`: a nominal sampled rigid-body sweep exists, but continuous, cable, connector, guard, tolerance and deformation evidence does not.

Complete measured mass/COM/inertia, frame and fastener mass, continuous/cyclic torque, thermal evidence, branch current, connector/conductor/protection evidence, speed/acceleration/stopping tests, structural proof, firmware/calibration binding, electrical-source synchronization, received hardware and qualified mechanical/electrical/controls/functional-safety disposition remain open.

No supplier may quote or fabricate P08-C01 or P08-C02 from the review drawings. They lack a released material lot, tolerance stack, surface/edge controls, fastener stack, FAI plan, bumper definition, load case, proof acceptance and signed work authorization.

## Controlled artifacts

- native integrated review geometry: `cad/hr-v0/generated/elbow-architecture-p0.8/HR-V0_X430_elbow_P0.8_candidate.step`;
- interactive review model: `cad/hr-v0/generated/elbow-architecture-p0.8/HR-V0_X430_elbow_P0.8_candidate.glb`;
- separately identified custom-part STEP candidates and review drawings under `parts/` and the package root;
- exact feature, transform and interface schedules;
- sampled collision and stop sweeps;
- mass/load comparison, hold register and fail-closed package status; and
- reproducible generator `tools/generate_hr_v0_x430_elbow_architecture.py`.

## Primary manufacturer evidence

- ROBOTIS, [XM430-W350-T/R e-Manual](https://emanual.robotis.com/docs/en/dxl/x/xm430-w350/), live page checked 2026-08-08; no formal page revision displayed. Used for 82 g mass, 4.1 N·m / 2.3 A 12 V stall endpoint, 46 rpm no-load endpoint, stall warning and official drawing/source links.
- ROBOTIS, `FR12-H101K` reference drawing, drawing date 2026-01-07, manufacturer download record 312, checked 2026-08-08. Reference only; exact selected axes are also checked in the controlled STEP.
- ROBOTIS, `FR12-S102K` reference drawing, drawing date 2026-01-07, manufacturer download record 318, checked 2026-08-08. Reference only; exact selected axes are also checked in the controlled STEP.
- ROBOTIS, OpenMANIPULATOR-X Assembly Manual, PDF creation/modification 2019-03-25, pages 8–13, checked 2026-08-08. Used to interpret the X430/FR12 assembly relationship; system precedent only.
- ROBOTIS, [OpenMANIPULATOR-X specification](https://emanual.robotis.com/docs/en/platform/openmanipulator_x/specification/), live page checked 2026-08-08; no formal page revision displayed. Feasibility precedent only, not proof for Project Button.

All sources remain subject to received-item identity and configuration control. No manufacturer source approves this Project Button application.
