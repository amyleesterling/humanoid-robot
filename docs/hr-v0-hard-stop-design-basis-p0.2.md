# HR-V0 Hard-Stop Design Basis P0.2

> **PRELIMINARY—NOT APPROVED FOR FABRICATION OR ENERGIZATION.** This document records a candidate allocation, not a released stop design or motion limit.

Date: 2026-08-07

Mechanical candidate: `HR-V0-MECH-P0.5`

Arm candidate: `HR-V0-ARM-ARCH-P0.6`

Requirement: `SAFE-007`, `MECH-006`

## Disposition

P0.2 supersedes the numerical J2-positive allocation in P0.1. P0.1 used obsolete arm geometry, a 125-degree provisional software limit, and a 130-degree study datum. Those values shall not be used for the current arm.

P0.6 establishes the following nominal model facts for the exact-coordinate candidate:

- all 70 non-intentional body pairs are continuously certified to retain at least 0.75 mm nominal model-space separation over J1 `-20..70 deg` and J2 `15..120 deg`;
- the certificate's lowest conservative lower bound is `0.765783 mm`;
- the critical exact B-Rep clearance at J2 `120 deg` is `0.962813 mm`;
- the numerically located first nominal contact is J2 `121.643289 deg`; and
- the 0.5-degree sampled sweep first reports positive-volume intersection at J2 `122 deg`.

The continuous certificate closes the between-sample question for the nominal rigid CAD bodies only. It excludes manufacturing and assembly tolerances, actuator/frame compliance, backlash, deformation, cables, guards, stop hardware, payload variation, stopping travel, calibration error, measurement uncertainty, and physical proof.

## J2-positive candidate allocation

| Boundary | Candidate value | Meaning |
|---|---:|---|
| software ceiling | `115.000000 deg` | provisional maximum command; not released |
| backed-up hard-stop datum | `118.000000 deg` | candidate physical contact datum; no stop CAD exists |
| nominal first CAD contact | `121.643289 deg` | numerical model result, not an as-built limit |
| software-to-stop allowance | `3.000000 deg` | must exceed worst stopping overtravel under every released case |
| stop-to-nominal-contact separation | `3.643289 deg` | total nominal separation after stop contact |
| reserved nominal collision guard | `1.000000 deg` | candidate reserve that may not be consumed |
| remaining candidate physical-uncertainty budget | `2.643289 deg` | maximum combined stack before any additional qualified margin |

Both independent inequalities must close with measured, signed evidence:

1. `worst stopping overtravel <= 3.000000 deg`; and
2. `backlash + compliance + build tolerance + calibration error + measurement uncertainty + any other accepted physical term <= 2.643289 deg`.

The values above are ceilings, not acceptance targets. A qualified mechanical and functional-safety review may require a larger guard, a lower software limit, or a different stop datum. Restoration, reset, ARM, software restart, or heartbeat restoration must never bypass the released limit or resume an old motion target.

## Boundaries not allocated

J1 minimum/maximum and J2-negative physical-stop datums remain `DESIGN REQUIRED`. The historical `-25/+75 deg` J1 and `10 deg` J2-negative study datums have not received a continuous collision, cable, guard, tolerance, or stopping-travel closure and are not released.

## Required stop architecture

The physical concept remains a replaceable energy-absorbing element backed by a positive metal catch. The stop shall attach to the fixed structural load path and contact an approved metal region of the moving link. It shall not load a cable, connector, actuator plastic cover, guard, cosmetic panel, or unapproved actuator-case feature.

The following remain `DESIGN REQUIRED` or `SELECTION REQUIRED`:

- exact stop and catch geometry, contact radius, material, fasteners, retention, adjustment and inspection access;
- bumper manufacturer/order code, force-displacement and energy data, temperature range, aging, cycle life and replacement rule;
- released current, speed, acceleration, jerk, payload, duty cycle, detection latency and fault cases;
- effective/reflected inertia, impact waveform, rebound, repeated-cycle and drive-into-stop loads;
- load-path, fastener, bearing, prying, fatigue, deformation and parent-structure calculations;
- cable and guard envelopes through the complete stopping and tolerance envelope; and
- numerical acceptance limits and qualified mechanical/functional-safety approval.

## Evidence required to close the allocation

1. Freeze one exact configuration commit and receive the controlled actuator, frames, links, adapters, fasteners, cables and guard interfaces.
2. Inspect the unpowered assembly, establish encoder zero, and measure the stop datum, first interference, backlash, compliance and build tolerance with calibrated equipment.
3. Select the current/speed/acceleration/jerk and payload cases; measure effective inertia and coast/down behavior in a guarded single-axis fixture.
4. Complete the stop CAD, tolerance stack and load calculations using current manufacturer data for every selected part.
5. Execute `INSPECT-MECH-013` and the J2 limit/stop record for every released direction, speed, payload, temperature, voltage and fault case.
6. Preserve synchronized command, position, current, voltage, displacement, force if applicable, high-speed video, calibration and post-test inspection records.
7. Demonstrate both allocation inequalities above and close every nonconformance.
8. Obtain signed qualified mechanical and functional-safety dispositions for the exact configuration.

Source evidence:

- `cad/hr-v0/generated/arm-architecture-p0.6/continuous-clearance-analysis.json`
- `cad/hr-v0/generated/arm-architecture-p0.6/continuous-clearance-summary.csv`
- `cad/hr-v0/generated/arm-architecture-p0.6/continuous-clearance-cells.csv`
- `cad/hr-v0/generated/arm-architecture-p0.6/hard-stop-allocation.csv`
- `tests/forms/hr-v0-j2-limit-stop-template.csv`

No powered motion, fabrication, or energization is authorized by this design-basis document.
