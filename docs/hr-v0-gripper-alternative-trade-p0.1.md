# HR-V0 source-controlled gripper alternative trade study P0.1

Identifier: **HR-V0-GRIP-ALT-P0.1**  
Status: **PRELIMINARY - PREFERRED EVALUATION CANDIDATE ONLY; NOT SELECTED; NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, MOTION, OR ENERGIZATION**  
Date: 2026-08-08  
Requirements affected: `SYS-001`, `SYS-002`, `GRIP-001`, `GRIP-002`, `MASS-002`, `SAFE-004`, `SAFE-006`

## Decision

Pololu item 3551, **Micro Gripper Kit with Position Feedback Servo**, is the preferred HR-V0 evaluation candidate. It is not the selected gripper and does not supersede `HR-V0-GRIP-P0.2`, the current mechanical candidate, or the authoritative requirement set.

This recommendation is deliberately narrow. It resolves the catalog-source problem better than the present ROBOTIS proposal: the manufacturer supplies an assembled STEP file, a dimensioned drawing, an assembly/user guide and an exact feedback-servo identity. It does not resolve the Project Button adapter, guard, power, control, mass, force, reliability or physical-evidence problems.

The ServoCity `3219-0002-0002` complete kit is retained as a wide-mechanism fallback. The ROBOTIS RM-X52 proposal remains the controlled baseline proposal, but its acquired-source and H104-registration holds remain open.

## Why the task still works

`SYS-002` sets an upper bound: one soft foam object no more than 100 g and no more than 70 mm maximum dimension. It does not require a 70 mm jaw opening. A controlled 25-30 mm foam cube fits the Pololu kit's published 32 mm internal opening and remains within `SYS-002`. The accepted demonstration object must be frozen and measured before test; this statement is task compatibility, not a grip-force or handoff verification.

No human handoff is introduced. The existing guarded, supervised, foam-object-only boundary remains.

## Evidence comparison

| Attribute | Pololu 3551 | ServoCity 3219-0002-0002 | ROBOTIS RM-X52 proposal |
|---|---:|---:|---:|
| Controlled manufacturer assembled CAD | STEP acquired; 3 solids | STEP acquired; 43 solids | public view route only; no acquired export payload |
| Published kit mass | 30 g | 101 g | selection required |
| Published usable opening | 32 mm internal | selection required | selection required |
| Command | hobby-servo PWM | hobby-servo PWM | DYNAMIXEL protocol |
| Position information | separate analog feedback lead | none stated | actuator telemetry only |
| Decision | **preferred evaluation candidate - not selected** | fallback - not selected | controlled proposal - source held |

Source files, hashes, signatures, dates and evidence boundaries are frozen in the two vendor source manifests. The Pololu STEP was parsed as three solids with a `48.3233046 x 62.3000002 x 36.6002866 mm` native-coordinate bounding box. The ServoCity STEP was parsed as 43 solids with a `60.9235229 x 132.0163877 x 54.2000002 mm` native-coordinate bounding box. Those boxes are file facts, not installed envelopes or assembly transforms.

## Mass screen

The nonselected P0.9 X430 integrated arm has an incomplete known moving subtotal of `577.091 g` against the `MASS-002` limit of `750 g`, leaving `172.909 g` before the gripper, adapter, guard, pads, cable and other omitted items.

- Pololu catalog mass screen: `750 - 577.091 - 30 = 142.909 g` remaining before every omitted item.
- ServoCity catalog mass screen: `750 - 577.091 - 101 = 71.909 g` remaining before every omitted item.

These are arithmetic screens, not mass closure. Vendor catalog mass is not received mass, and P0.9 itself remains nonselected and incomplete.

## Mechanical change required

If Pololu 3551 is later selected, it replaces the current H104/ROBOTIS gripper chain with a direct adapter from the two M5x0.8 end taps of the current 20-2040 forearm member to an accepted Pololu mounting pattern. Vendor native coordinates do not define that transform.

The adapter needs controlled source, drawing, material, tolerances, exact fasteners, locking, access, received fit, proof and a merged moving-envelope analysis. A fixed local guard, broad compliant pads, cable retention and service access still have to be designed and verified. No adapter should be quoted or fabricated from this trade study.

## Electrical and controls change required

The preferred candidate creates a new feedback-servo branch:

1. Servo power must be downstream of both actuator-power interruption devices so opening either removes gripper power.
2. A protected 6 V branch is required. Pololu D24V22F6 item 2859 is an evaluation candidate only; its typical current capability depends on input voltage and thermal conditions and is not a released branch rating.
3. Branch fuse, conductors, connectors, regulator carrier, enclosure thermal behavior, inrush, voltage drop and fault-current coordination are `SELECTION REQUIRED`.
4. PWM source, physical pin, voltage amplitude, startup/shutdown state and cable are `SELECTION REQUIRED`.
5. The feedback lead requires a selected protected analog input and a received calibration.
6. E-stop release and manual reset must leave the PWM output in a nonmoving state. Only a separate, deliberate supervised command may move the gripper.

Pololu describes approximate 500 us open and 2400 us closed endpoints and warns that units vary and can buzz or bind at an endpoint. Those values are characterization starting points only. They are not released Project Button commands. The standard FEETECH FS90 V1.0 sheet does not define the modified FS90-FB feedback cable and cannot be used to infer it.

## Selection gate

The candidate may be selected only after all `GAH-001` through `GAH-012` records are evidenced and dispositioned. At minimum, that includes:

- an approved requirement change removing or superseding the solution-specific ROBOTIS wording in `GRIP-002`;
- exact adapter/fastener definition and qualified mechanical review;
- exact protected 6 V, PWM and analog-feedback interfaces plus updated connected ECAD and ERC;
- received identity/metrology, mass/COM/inertia and free-motion/bind data;
- calibrated force, current, drop, wear and cable-retention tests;
- merged guard/envelope evidence and fault-injection showing power removal and no reset-caused motion; and
- independent mechanical, electrical, controls and functional-safety-boundary review.

No purchase has been authorized and no candidate article has been received or tested.

## Primary sources

- Pololu item 3551 [product/specifications](https://www.pololu.com/product/3551/specs), [resources](https://www.pololu.com/product/3551/resources), and [user guide](https://www.pololu.com/docs/0J76/all), accessed 2026-08-08.
- Pololu [Micro Gripper dimension drawing](https://www.pololu.com/file/0J1569/micro-gripper-dimensions.pdf), dated 2018-08-31, accessed 2026-08-08.
- Pololu item 3436 [modified FS90-FB product page](https://www.pololu.com/product/3436) and FEETECH [standard FS90 specification V1.0](https://www.pololu.com/file/0J1435/FS90-specs.pdf), accessed 2026-08-08.
- Pololu item 2859 [D24V22F6 regulator product page](https://www.pololu.com/product/2859), accessed 2026-08-08.
- ServoCity [Servo Driven Gripper Kit 3219-0002-0002](https://www.servocity.com/servo-driven-gripper-kit-servo-included/), including linked assembly, specification and STEP resources, accessed 2026-08-08.

## Release boundary

This is a source-controlled trade study. It closes no requirement, risk, physical inspection, fabrication gate, motion gate or energization gate. Project Button remains **not build-ready**, and energization remains prohibited.
