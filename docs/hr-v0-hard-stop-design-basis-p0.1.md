# HR-V0 Hard-Stop Design Basis P0.1

> **R53 HOLD:** The P0.2 arm datums and link geometry are superseded. Energy/load calculations below are historical screens only until replacement J1/J2 transforms, inertia, speeds and stop geometry are released.

**PRELIMINARY - KINEMATIC AND LOAD-CASE DEFINITION ONLY. NOT RELEASED FOR FABRICATION OR ENERGIZATION.**

Date: 2026-08-06

Mechanical baseline: `HR-V0-MECH-R0.1-PRELIMINARY`

Requirement: `SAFE-007`

Generated evidence: `cad/hr-v0/generated/hard-stops/`

## Purpose

Define an auditable coordinate convention, candidate stop datums, and the minimum load cases required before designing the physical J1/J2 stop brackets. This document does not select a bumper, bracket material, fastener, contact shape, or permitted impact energy.

## Coordinate convention and candidate datums

The provisional software limits remain J1 `-20 to +70 deg` and J2 internal angle `15 to 125 deg`. A candidate mechanical datum is placed 5 degrees outside each software limit:

| Stop | Software boundary | Candidate mechanical datum | Layout convention |
|---|---:|---:|---|
| `HS-J1-MIN` | -20 deg | -25 deg | J1 angle from horizontal +X, counter-clockwise positive |
| `HS-J1-MAX` | +70 deg | +75 deg | J1 angle from horizontal +X, counter-clockwise positive |
| `HS-J2-MIN` | 15 deg internal | 10 deg internal | layout ray = 180 deg - internal angle |
| `HS-J2-MAX` | 125 deg internal | 130 deg internal | layout ray = 180 deg - internal angle |

The generated study uses a 50.0 mm moving-contact radius. At that radius the four ideal contact points are recorded in `hard-stop-datums.csv`. These are kinematic datums, not hole coordinates. Final stop faces must account for measured encoder zero, calibration error, 0.25 deg published actuator backlash, frame/link tolerances, bracket compliance, bumper compression, stopping travel, temperature, wear and service adjustment. The required 5 degree separation must remain after the worst-case stack is applied.

## Candidate architecture

Each joint requires two independently retained, body-fixed stop blocks that contact a metal region of the moving link at approximately 50 mm radius. The stop blocks shall attach to the fixed load path—J1 adapter/column structure or J2 upper-link/S102 structure—without using a cable, connector, actuator housing, plastic rear cover, guard, or removable cosmetic cover as the stop.

The preferred concept is a replaceable energy-absorbing bumper backed by a positive metal catch. The bumper handles ordinary low-energy contact; the metal catch prevents overtravel if the bumper is missing, permanently compressed or fractured. Neither element is selected. A production design needs full contact geometry, retained adjustment, anti-rotation, accessible inspection, replacement interval, fastener proof and proof that no stop load is transferred through an unapproved actuator case feature.

## Reproducible allocated-mass screen

The present mass allocation gives:

- J1 moving inertia: `0.047264 kg m^2`;
- J2 moving inertia: `0.010144 kg m^2`.

These values model each allocated mass as a point at its published screening radius. They exclude actuator reflected rotor/gear inertia, frame/harness inertia, compliance, backlash impact and the final gripper geometry.

With `E = 0.5 I omega^2`:

| Case | J1 allocated-mass energy | J2 allocated-mass energy |
|---|---:|---:|
| setup speed, 10 deg/s | 0.000720 J | 0.000154 J |
| auto speed, 30 deg/s | 0.00648 J | 0.00139 J |
| XM540 12 V no-load endpoint, 30 rpm | 0.233 J | 0.0501 J |

The current ROBOTIS XM540-W270 e-Manual was checked 2026-08-06. It reports 30 rpm no-load speed and 10.6 N m stall torque at 12 V, and explicitly distinguishes stall torque from continuous or real-world output. Those endpoints do not occur simultaneously and are not permitted operating targets.

The no-load endpoint screen is incomplete because reflected drive inertia is not published. For illustration only, absorbing the allocated-mass energy through 2 mm of constant-force stroke would require average forces of approximately 117 N at J1 and 25 N at J2. Real peak force depends on the bumper force-displacement curve, damping, contact stiffness, reflected inertia and impact waveform. The 2 mm value is not a selected bumper stroke.

## Static and drive-into-stop cases

At 50 mm radius:

- three times the allocated J1 gravity torque, `3 x 1.70 N m`, produces 102 N tangential force;
- three times the allocated J2 gravity torque, `3 x 0.62 N m`, produces 37.2 N; and
- the published 12 V ideal stall endpoint, `10.6 N m`, corresponds to 212 N before dynamic amplification.

The physical stop and its upstream load path must survive the released combination of resting gravity, impact, commanded current during detection latency, rebound and repeated cycles. A 3x static proof factor cannot be applied blindly to an unknown elastomer impact; the qualified reviewer must approve the final load cases and test factors.

## Evidence required before stop-part CAD

1. Receive and assemble the controlled H101/S102 joint hardware without power and establish the exact fixed/moving planes.
2. Measure encoder zero, link datum, backlash, available swept space, cable envelope and guard envelope.
3. Select the maximum permitted current, speed, acceleration, jerk and stop-detection latency for setup and automatic modes.
4. Measure joint coast/down behavior and effective inertia using a guarded joint article; do not infer reflected inertia from link mass.
5. Select a bumper from a current manufacturer force/energy curve and record temperature, aging, cycle and mounting limits.
6. Design the backed-up metal catch, bracket, fasteners and parent load path for every released load case.
7. Release a dimensional tolerance stack demonstrating software-limit separation and clearance before cable, connector, shield or self-contact.
8. Execute `INSPECT-MECH-006`, then the guarded incremental `TEST-MECH-002`; preserve raw angle, speed, current, force/displacement, high-speed video and post-test inspection evidence.
9. Obtain qualified mechanical and safety review before any actuator-powered stop test.

No powered motion is authorized by this design-basis document.
