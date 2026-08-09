# HR-V0 continuous collapse-envelope and receiver-role correction P0.1

**PRELIMINARY - NOT APPROVED FOR FABRICATION, MOTION OR ENERGIZATION**

Document ID: `HR-V0-COLLAPSE-ENV-P0.1`

Date: 2026-08-08

Controlled parents: `HR-V0-ARM-ARCH-P0.7`, `HR-V0-GUARD-P0.3`, `HR-V0-POWERLOSS-P0.1`

Gates: `EG-008` and `EG-009` remain `partial`

## Result

The current 450 mm radial guard reservation contains the controlled known rigid-body and mass-ledger radius inputs. The current P0.3 floor tray does not reach the arm's controlled collapse envelope and therefore cannot be credited as an arm receiver.

It is reclassified as an **object-catch envelope only**, with zero arm-support, energy, impact or load credit. A separate passive arm receiver and complete bidirectional hard stops remain `DESIGN REQUIRED`.

## Continuous no-stop-credit method

J1 and J2 use parallel project X axes. Rotation about X preserves every point's X coordinate and its radial distance from the relevant X axis.

For each J1-moving known B-Rep, the checker takes the maximum Y-Z radius of its axis-aligned bounding-box corners about J1. That radius continuously contains the shape under an arbitrary full J1 revolution.

For each J2-moving known B-Rep, the checker takes:

```text
continuous shoulder radius <= J1-to-J2 axis distance
                            + component radius about J2
```

This triangle-inequality construction continuously contains the component for arbitrary J1 and J2 rotations. It does not depend on software limits, actuator holding, friction or the incomplete stop set.

The eleven controlled known moving B-Reps produce:

- known continuous B-Rep radius: `338.740914 mm`;
- known invariant X extent: `-42.000000 to +42.000000 mm`;
- moving-mass ledger radius: `360.000000 mm`; and
- controlling current input radius: `360.000000 mm`.

## Guard-fit screen

`HR-V0-GUARD-P0.3` reserves a 450 mm radial Y-Z cylinder about J1, uses an internal X range of `-200 to +200 mm`, places J1 at `Z = 500 mm`, and provides `Z = 0 to 950 mm` internal height.

The controlling 360 mm input gives:

| Boundary | Controlled input | Guard boundary | Residual |
|---|---:|---:|---:|
| Radial reservation | 360 mm | 450 mm | 90 mm |
| Negative X | -42 mm | -200 mm | 158 mm |
| Positive X | +42 mm | +200 mm | 158 mm |
| Bottom Z | 140 mm | 0 mm | 140 mm |
| Top Z | 860 mm | 950 mm | 90 mm |

These are pass results for the controlled known inputs only. The 90 mm minimum residual is unallocated. It is not a safety distance and may be consumed by the complete gripper mechanism, object geometry, cables, strain relief, tolerance, backlash, deformation, stopping, rebound and measurement uncertainty.

## Receiver-role defect

The P0.3 floor tray starts above the bottom frame and has a nominal top at:

```text
20 mm frame height + 6 mm tray thickness = Z 26 mm
```

The controlled arm-envelope bottom is:

```text
500 mm J1 height - 360 mm controlled radius = Z 140 mm
```

The tray top is therefore `114 mm` below the controlled arm envelope. No controlled rigid arm point is expected to contact that tray. Missing gripper or cable geometry may not be used to invent arm-support credit.

The floor tray remains useful only as an object-catch envelope pending its own material, retention, drop, rebound and access evidence.

## Still-required arm containment

Power-loss containment still requires all of the following for the exact as-built configuration:

- J1 minimum and maximum physical stops;
- J2 minimum physical stop and physical acceptance of the current positive-stop candidate;
- a separate passive arm receiver or an accepted stop-supported final-rest architecture;
- exact receiver contact geometry, compliant element, material and retention;
- complete force, travel, rebound, fatigue and load-path acceptance;
- complete gripper/object/cable geometry and continuous swept/collapse envelope;
- as-built mass, center of mass, inertia, tolerance, backlash and deformation;
- gravitational, continued-drive, regeneration, stored-energy and detached-part cases;
- physical metrology, backdrive/drop/fault tests and qualified review; and
- stable inaccessible recovery without re-energization or spontaneous restart.

The eighteen-row metrology form remains entirely `NOT EXECUTED` and `NOT AUTHORIZED`.

## Controlled artifacts

- `cad/hr-v0/generated/power-loss-envelope-p0.1/collapse-envelope-summary.json`
- `cad/hr-v0/generated/power-loss-envelope-p0.1/collapse-envelope-components.csv`
- `cad/hr-v0/generated/power-loss-envelope-p0.1/guard-fit-screen.csv`
- `cad/hr-v0/generated/power-loss-envelope-p0.1/receiver-role-disposition.csv`
- `cad/hr-v0/generated/power-loss-envelope-p0.1/HR-V0_collapse-envelope-review.step`
- `cad/hr-v0/generated/power-loss-envelope-p0.1/HR-V0_collapse-envelope-review.glb`
- `tests/forms/hr-v0-collapse-envelope-metrology-template-p0.1.csv`
- `release/hr-v0/collapse-envelope-p0.1/index.html`
- `tools/generate_hr_v0_collapse_envelope.py`
- `tools/check_hr_v0_collapse_envelope_p01.py`

This package is a continuous nominal geometric screen. It releases no receiver part, guard clearance, stop, fabrication, motion or energization.
