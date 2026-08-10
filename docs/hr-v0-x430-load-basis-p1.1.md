# HR-V0 X430 moving-load basis P1.1

> **PRELIMINARY — NOT APPROVED FOR QUOTATION, PROCUREMENT, FABRICATION, ASSEMBLY, MOTION, CONNECTION, OR ENERGIZATION.**

Configuration identifier: `HR-V0-ARM-LOAD-P1.1-X430-CANDIDATE`

## Decision

This package supplies the missing analytical update for the 7 mm forearm offset in `HR-V0-ARM-ARCH-P1.1-X430-LOWERED-FOREARM-CANDIDATE`. It does not select P1.1 or X430, close mass/COM/inertia, establish an actuator rating, release a proof load, or authorize work.

The calculation deliberately separates four evidence classes:

1. exact nominal CAD properties using a specified candidate density;
2. catalog mass scaled over a nominal collision envelope;
3. program mass or point allocations used only for sensitivity;
4. unresolved physical items excluded from numeric totals.

Program allocations are not converted into received measurements or upper bounds.

## Source binding

The calculation is SHA-256 bound to:

- the R95 P1.1 architecture summary;
- the R95 full-arm STEP;
- the P1.1 geometry generator; and
- the controlled 80/20 evidence record containing the 20-2040 line mass.

The J2 axis remains Y=191.550 mm and the member-side moving subassembly remains Z=−7.000 mm.

## Component evidence

| Component | Evidence class | Mass | J2-axis inertia input |
|---|---|---:|---:|
| P11-C02 striker | Exact nominal CAD + 2.70 g/cm³ candidate density | 58.281708 g | 0.000076278897 kg·m² |
| 50 mm 20-2040 member | Catalog mass + uniform collision-envelope estimate | 38.216050 g | 0.000164330632 kg·m² |
| Distal H104 adapter | Exact nominal CAD + 2.70 g/cm³ candidate density | 46.987410 g | 0.000409625573 kg·m² |
| Complete gripper | Program allocation at the H104 datum | 210.000000 g | 0.003294165525 kg·m² point model only |
| Maximum soft payload | Requirement point model at nominal object center | 100.000000 g | 0.002359590250 kg·m² point model only |
| FR12-H101/idler | Unresolved physical item | SELECTION REQUIRED | SELECTION REQUIRED |
| Fasteners, bumper, connectors and moving harness | Unresolved physical items | SELECTION REQUIRED | SELECTION REQUIRED |

The three known nominal/estimated components total **143.485169 g** and 0.000650235102 kg·m² about J2. Placing each known mass at the farthest point of its nominal geometry gives a 0.000921987948 kg·m² support bound.

Adding the 210 g gripper and 100 g payload point allocations produces a **453.485169 g incomplete reference** with:

- 0.006303990877 kg·m² point-model inertia; or
- 0.006575743723 kg·m² using the known-geometry support bound plus the two point allocations.

Neither is a complete upper bound. The gripper's extent and own inertia, FR12-H101/idler, fasteners, bumper, connectors and harness are absent.

## Gravity envelope

The exact reference-point calculation is sampled every 0.25° through J2=15°…115°. For each component it applies:

`M = m g (y cos q − z sin q)`

The maximum absolute incomplete-reference gravity moment is **0.483257699 N·m at 15°**. The existing project screen produces:

- 2.25× gravity input: 1.087329823 N·m;
- 3× proof-screen input on that 2.25× case: **3.261989468 N·m**.

These multipliers are analytical inputs, not accepted safety factors, proof loads or actuator requirements. Missing mass can increase the result.

## Stop-load sensitivities

Exact B-Rep reconstruction finds four symmetric nominal contact solutions at a common **45.604835001 mm** radius from J2 at 117.999977°.

If one rail carries the entire static-equivalent moment, the incomplete proof-screen input corresponds to **71.527272672 N** at that radius. This is not a capacity claim. Tolerance may produce single-rail contact, while compliance can change the contact radius and force distribution.

The package also publishes:

- 1, 3, 5 and 10 N·m moment-to-force sensitivities;
- kinetic-energy sensitivities at 5, 10, 20, 30 and 180°/s; and
- average `energy / stroke` forces at 0.5, 1 and 2 mm.

Energy divided by stroke is an average, not a peak impact force. The 180°/s row is an endpoint sensitivity, not a command. Reflected rotor/gear inertia, efficiency, backlash, compliance, drive persistence, bumper dynamics, rebound and controller latency remain absent.

## Ten inputs still open

1. FR12-H101/idler mass, COM and inertia;
2. selected moving fasteners, bumper, connectors, guides, strain relief and harness;
3. complete gripper mass distribution and payload retention;
4. released speed, acceleration, duty and trajectory limits;
5. reflected rotor/gear inertia, efficiency, backlash and compliance;
6. bumper stiffness, damping, stroke, retention, temperature and life;
7. two-rail contact distribution, tolerance, friction and local stress;
8. continuous/cyclic actuator torque, current and temperature;
9. accepted material allowables, fatigue method, proof multiplier and procedure; and
10. measurement uncertainty.

These inputs block complete mass/COM/inertia, stop load, structural release, X430 selection and worst-duty validation.

R98 adds `HR-V0-X430-DUTY-P0.1`, a configuration-specific instrumented evidence route for input 8. It does not close the input: all seven powered stages are blocked, all acceptance values remain `SELECTION REQUIRED`, and no physical result exists.

## Controlled evidence

- generator: `tools/generate_hr_v0_x430_load_basis.py`;
- fail-closed checker: `tools/check_hr_v0_x430_load_basis.py`;
- evidence package: `cad/hr-v0/generated/arm-load-basis-p1.1-x430/`;
- interactive guide: `release/hr-v0/arm-load-basis-p1.1-x430/index.html`;
- independent review request: `docs/reviews/2026-08-08-x430-load-basis-p1.1-independent-review-request.md`.

Passing the checker proves only internal source binding and arithmetic. It is not fabrication, structural, motion, functional-safety or energization approval.
