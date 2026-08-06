# R11 Engineering Correction Calculations

**PRELIMINARY—NOT APPROVED FOR ENERGIZATION**

Date: 2026-08-06  
Scope: controlled correction record for Fable findings B4, B5, B7, M3, M4, M5, M6, and M11.  
Boundary: arithmetic and architecture screening only. This record does not select parts, approve fabrication, claim functional-safety performance, or authorize energization.

All calculated results retain the maturity of their inputs. A correct calculation made from a target or review assumption is still only a target or screen.

## Disposition map

| Finding | Correction in R11 | Closure state |
|---|---|---|
| B4 | arm actuator mass exceeds allocation; leg assembly fails independent mass screen | **open—architecture and controlled mass ledger required** |
| B5 | fixed 4-series battery and fixed rail removed; voltage/chemistry compatibility screened | **open—energy architecture `SELECTION REQUIRED`** |
| B7 | hip-roll direct drive blocked; 8 kg and 10 kg cases calculated | **open—six-axis W0 evidence required** |
| M3 | no-load speed converted through proposed reduction; walking band reduced to 0.10–0.14 m/s | **open—loaded trajectory proof required** |
| M4 | XM540 corrected to 10.6 N·m at 12 V and 4.4 A | corrected in calculation; physical duty proof open |
| M5 | joint-rate/TCP inconsistency calculated; pose-dependent Jacobian limit required | **open—implementation and test required** |
| M6 | XH540 input, speed, radial/axial, and connector boundaries corrected | **open—output support and exact connector selection required** |
| M11 | regeneration, source coordination, and tether assumptions made explicit | **open—hardware architecture and tests required** |

## Primary-source register

| Source | Revision/date recorded | Facts used | Accessed |
|---|---|---|---|
| [ROBOTIS XH540-W270 web manual](https://emanual.robotis.com/docs/en/dxl/x/xh540-w270/) | live web manual; no document revision/date displayed | XH540 mass, input voltage, recommended voltage, stall torque/current, no-load speed, radial and axial load; comparison table also gives XM540 torque/current | 2026-08-06 |
| [ROBOTIS XM540-W270 web manual](https://emanual.robotis.com/docs/en/dxl/x/xm540-w270/) | live web manual; no document revision/date displayed | XM540 mass, stall torque/current, and input voltage | 2026-08-06 |
| [ROBOTIS XM430-W350 web manual](https://emanual.robotis.com/docs/en/dxl/x/xm430-w350/) | live web manual; no document revision/date displayed | XM430 mass used in the current arm-candidate mass screen | 2026-08-06 |
| [ROBOTIS XC430-W240 web manual](https://emanual.robotis.com/docs/en/dxl/x/xc430-w240/) | live web manual; no document revision/date displayed | XC430 mass used in the reviewed 25-axis actuator-mass screen | 2026-08-06 |
| [Mean Well LRS-350 specification](https://www.meanwell.com/Upload/PDF/LRS-350/LRS-350-SPEC.PDF) | `LRS-350-SPEC 2025-09-12` | LRS-350-12 output, overload behavior, peak load, inrush; absence of quantified T50/I²t in the product specification | 2026-08-06 |
| [Mean Well enclosed-type installation manual](https://www.meanwell.com/Upload/PDF/Enclosed_Type_EN.pdf) | 2025-12-17 | generic installation guidance and conductor table; not an LRS-350 protection selection | 2026-08-06 |
| [Mean Well breaker-selection article](https://www.meanwell.com/newsInfo.aspx?c=5&i=765) | 2019-07-31 | breaker selection depends on actual inrush waveform/T50 and breaker proof factor | 2026-08-06 |

The internal Fable review is an independent secondary review, not a manufacturer source. Where its provisional masses or tether values are reproduced below, they are labeled **review assumptions** and are not promoted into selections.

## 1. Arm mass allocation — B4

Current candidate count:

- 6 × XM540 at 0.165 kg = 0.990 kg;
- 4 × XM430 at 0.082 kg = 0.328 kg;
- actuator subtotal = `0.990 + 0.328 = 1.318 kg`.

Allocation residuals:

- against the 1.30 kg two-arm target: `1.300 − 1.318 = −0.018 kg`;
- against the 1.50 kg maximum: `1.500 − 1.318 = 0.182 kg`.

Conclusion: the candidate actuators alone exceed the target and leave only 182 g under the maximum for structure, output bearings/shafts, grippers, harnesses, covers, fasteners, and sensors. The arm allocation fails. R11 does not choose smaller actuators or alter degrees of freedom; that redesign is `SELECTION REQUIRED` and must be justified by task torques, speed, contact limits, and measured duty.

## 2. Leg and whole-robot mass screen — B4

Manufacturer-backed actuator floor:

`12 × 0.165 kg = 1.980 kg`

The independent review added these **non-controlled screening assumptions**:

| Review assumption | Approximate mass |
|---|---:|
| six belt stages | 0.27 kg |
| twelve bearing/shaft sets | 0.36 kg |
| leg structure | 1.3–1.7 kg |
| feet | 0.35 kg |
| harness | 0.25 kg |
| **screened two-leg result** | **4.5–4.9 kg** |

The exact arithmetic depends on what each review bucket includes, and none is a selected BOM line or controlled CAD mass property. The result is retained only as evidence that the 3.40 kg target and 3.80 kg maximum are not closed. In the reviewed 25-axis candidate count, the 1.318 kg arm subtotal already includes two wrist and two gripper XM430 units; adding 1.980 kg for the legs, about 0.130 kg for two 65 g head actuators, and 0.165 kg for the waist actuator gives approximately `3.593 kg`. The exact actuator variants, count, and mass must still be reconciled to the controlled BOM before use.

Required closure evidence: exact configuration BOM, manufacturer mass for every purchased item, CAD material and mass properties, cable/fastener/adhesive allowances, measured prototype masses, link centers of mass, inertia tensors, and a controlled reserve policy. Until then, 8 kg cannot be used as an achieved sizing mass.

## 3. Hip-roll and ankle torque screens — B7

Inputs:

- gravitational acceleration `g = 9.80665 m/s²`;
- target/ceiling mass = 8/10 kg;
- hip lateral moment arm = 0.0625 m, derived from the 125 mm provisional hip width;
- ankle center-of-mass offset = 0.040 m;
- hip dynamic screen = 2×;
- ankle screen = 2× dynamic and 1.5× uncertainty.

Hip roll:

| Case | Static | 2× dynamic screen |
|---|---:|---:|
| 8 kg | `8 × 9.80665 × 0.0625 = 4.903 N·m` | `9.807 N·m` |
| 10 kg | `10 × 9.80665 × 0.0625 = 6.129 N·m` | `12.258 N·m` |

The XH540-W270 ideal stall point is 9.9 N·m at 12 V and 11.7 N·m at 14.8 V. Thus the 8 kg dynamic screen is already 99% of the 12 V ideal stall point, while the 10 kg screen is 105% of the 14.8 V ideal stall point. Losses, temperature, loaded voltage, motion speed, and uncertainty only reduce margin. Direct-drive hip roll is blocked.

Ankle pitch/roll magnitude screen at 40 mm:

| Case | Static | 2× dynamic × 1.5× uncertainty |
|---|---:|---:|
| 8 kg | `8 × 9.80665 × 0.040 = 3.138 N·m` | `9.414 N·m` |
| 10 kg | `10 × 9.80665 × 0.040 = 3.923 N·m` | `11.768 N·m` |

The proposed 1.5:1 reduction gives `11.7 × 1.5 = 17.55 N·m` ideal stall at 14.8 V before belt, bearing, alignment, and compliance losses. It is not a continuous capability. W0 must model and measure hip yaw/roll/pitch, knee pitch, and ankle pitch/roll through stand, weight transfer, single support, step, kneel, rise, controlled stop, and credible disturbance trajectories at both the target and ceiling mass cases.

## 4. XH540 speed and walking band — M3/M6

Manufacturer no-load points:

- at 14.8 V: `46 rpm × 360 / 60 = 276 deg/s` at the motor; after ideal 1.5:1 reduction, `276 / 1.5 = 184 deg/s` at the joint;
- at 12.0 V: `39 rpm × 360 / 60 = 234 deg/s` at the motor; after ideal 1.5:1 reduction, `234 / 1.5 = 156 deg/s` at the joint.

These are unloaded endpoints. A 120 mm step at 0.18–0.20 m/s would consume only 0.60–0.67 s per whole step before double-support and transfer allowances; earlier screens found the resulting swing trajectories marginal against the reduced no-load limit. R11 therefore releases only **0.10–0.14 m/s** for both HR-30D and HR-30W feasibility testing. Even this range requires pose-by-pose loaded speed/torque simulation followed by measured gait trajectory evidence at the actual rail voltage and temperature.

## 5. Actuator voltage and battery compatibility — B5/M6

The XH540-W270 manufacturer input range is 10.0–14.8 V, with 12 V recommended.

| Candidate architecture example | Voltage screen | R11 disposition |
|---|---|---|
| 4-series Li-ion/LiPo direct | 16.8 V full charge | exceeds 14.8 V; incompatible with direct actuator connection |
| 4-series LiFePO4 direct | approximately 14.6 V full charge | may fit upper limit, but loaded end-of-discharge torque/speed and transients are unresolved |
| battery plus regulated actuator rail | converter can set rail within limit | mass, loss, heat, transient response, current, fault behavior, and regeneration unresolved |
| higher-voltage development tether plus on-robot conversion | lowers tether current for a given power | converter, insulation, protection, PE/shield, mass, drag, and regeneration unresolved |
| low-voltage development tether | avoids on-robot high-voltage conversion | high current, voltage drop, connector, conductor, heating, and drag unresolved |

No chemistry, series count, rail voltage, converter, source current, connector, or fuse is selected by this table. Screens shall use the actuator-terminal voltage under worst credible loaded end-of-discharge and transient conditions, not nominal pack voltage.

## 6. HR-V0 XM540 correction — M4

The current official ROBOTIS table gives XM540-W270:

| Supply | Ideal stall torque | Stall current |
|---:|---:|---:|
| 11.1 V | 10.0 N·m | 4.2 A |
| 12.0 V | **10.6 N·m** | **4.4 A** |
| 14.8 V | 12.9 N·m | 5.5 A |

The HR-V0 mechanical document previously stated 9.9 N·m at 12 V, which is the XH540 value. It is corrected to 10.6 N·m at 4.4 A. Against the 3.83 N·m shoulder intermittent screen, the ideal stall ratio is `10.6 / 3.83 = 2.77`. This ratio is not a continuous torque margin or proof factor. Acceptance still requires the actual joint, current limit, duty, actuator-terminal voltage, thermal state, and measured mass properties.

## 7. TCP and joint-rate consistency — M5

Convert the present joint limit:

`30 deg/s × π / 180 = 0.5236 rad/s`

Shoulder-only at the screened 0.36 m payload radius:

`v = 0.36 × 0.5236 = 0.1885 m/s`

This exceeds the 0.15 m/s TCP limit. The compatible shoulder-only rate at that reach is:

`ω = 0.15 / 0.36 = 0.4167 rad/s = 23.87 deg/s`

For a planar two-link screen in the straight horizontal pose, the payload center is 0.36 m from the shoulder and 0.20 m from the elbow. If shoulder and elbow both move at 30 deg/s in the same tangential direction, the Jacobian contributions add:

`v_screen = (0.36 + 0.20) × 0.5236 = 0.2932 m/s`

This is a defined conservative screening pose, not a universal maximum. The controller must enforce TCP speed with the calibrated tool transform and pose-dependent Jacobian for all joint combinations. Closure evidence includes exact TCP datum, calibrated link dimensions, limit implementation outside non-real-time behavior code, command interpolation, startup/reset behavior, stale-command behavior, controlled-stop behavior, and measured worst-case combined-axis tests. E-stop release or manual reset cannot command motion.

## 8. XH540 output-load and connector boundary — M6

Manufacturer output-load values:

- radial load: 40 N applied 10 mm from the horn;
- axial load: 20 N.

Single-support static force:

- 8 kg: `8 × 9.80665 = 78.45 N`;
- 10 kg: `10 × 9.80665 = 98.07 N`;
- 8 kg with a 2× dynamic screen: `156.91 N`.

These foot forces are not identical to actuator-bearing loads; joint geometry can amplify or redirect them. They are already sufficient to show that the leg load path cannot rely on the actuator bearing. Dual-supported output geometry is mandatory unless an alternative is proven against the final radial, axial, moment, shock, and life spectrum.

The connector/contact rating is not closed. The exact housing and contact order codes, wire gauge, crimp tooling, contact resistance, circuit grouping, mating cycles, temperature rise, ambient/bundling derating, and fault-current coordination are `SELECTION REQUIRED`. An approximate “3 A connector” statement is not permitted as a verified limit, and stall current may exceed some candidate contact ratings.

## 9. Mean Well source and protection coordination — M11

The current LRS-350-12 product specification gives:

- 12 V, 29 A, 348 W rated output;
- overload protection at 110–140% of rated output power, hiccup mode with automatic recovery after the fault is removed;
- a separate 150% peak-load statement for up to one second;
- 60 A typical cold-start input inrush at both 115 and 230 VAC.

The product specification does not supply inrush T50/duration, I²t, a quantified output short-circuit time-current curve, or an LRS-350-specific external fuse/breaker selection. The enclosed-product installation manual is generic and does not close QF1 or F0/F1–F3. Mean Well's breaker article itself requires actual inrush waveform/T50 and breaker proof-factor evidence.

Therefore all protection values remain `SELECTION REQUIRED`. Required inputs include prospective source and battery fault current, cable length, conductor material and insulation, ambient, bundling, installation method, connector/contact limits, inrush, duty cycle, load profile, interrupting rating, PE/grounding scheme, and jurisdiction. Software current limiting cannot substitute for branch fault protection.

## 10. Regeneration and controlled stop — M11

No reviewed Mean Well document establishes that the LRS-350 can sink returned actuator energy. Deceleration, gravity, or an external disturbance can raise the DC bus. The following remain `SELECTION REQUIRED`:

- bus clamp, dump resistor, storage, or bidirectional-converter topology;
- clamp threshold and tolerance relative to actuator and source limits;
- energy, peak power, pulse duration, repetition, thermal recovery, and failure mode;
- source reverse-current tolerance and overvoltage/latch behavior;
- contactor timing and DC interruption under a regenerating load;
- controlled-stop availability with loss of source, clamp, communications, or one protection channel.

Test closure requires worst-case measured bus energy and voltage for gait stop, kneel, fall-arrest interaction, driven-joint backdrive, source disconnect, and clamp fault. No contactor, clamp, or source is approved by this record.

## 11. Tether electrical and mechanical screen — M11

The independent review used these assumptions only to expose scale:

- conductor: 8 AWG at 2.1 mΩ/m;
- one-way length: 3–5 m;
- loop length: 6–10 m;
- current: 80 A.

Arithmetic:

- loop resistance = `2.1 mΩ/m × 6–10 m = 12.6–21.0 mΩ`;
- voltage drop = `80 A × 0.0126–0.0210 Ω = 1.008–1.680 V`;
- conductor dissipation = `80² × 0.0126–0.0210 = 80.6–134.4 W`.

These values do not select 8 AWG, 80 A, a 3–5 m tether, or any connector. Actual closure must compare low-voltage/high-current distribution with a higher-voltage tether and on-robot conversion. Electrical evidence includes load and fault current, permissible actuator-terminal voltage, source/converter response, conductor temperature, connector/contact ratings, fuse coordination, transient drop, regeneration, shielding/PE, separation from RS-485, and jurisdiction. Mechanical evidence includes mass per metre, bend stiffness, overhead support, drag force and moment over the whole workspace, strain relief, connector breakaway policy, snag control, and physical separation from the fall-arrest line.

## R11 closure evidence checklist

- controlled BOM/CAD/measured mass and inertia ledger demonstrating reserve;
- six-axis inverse-dynamics cases at target and ceiling masses, including kneel/rise and stop;
- W0 torque/speed/thermal/backlash/efficiency tests at actual loaded rail voltage;
- reduced-joint output sensing and belt-fault evidence;
- dual-supported output structural, bearing, shaft, and life calculations;
- exact actuator connector/contact selection and derating evidence;
- released energy architecture with chemistry, series count, rail, converter, BMS, precharge, disconnect, fuses, contactors, charger interlock, telemetry, and regeneration solution;
- source/fuse/conductor/connector coordination using prospective fault current and installation conditions;
- tether voltage-drop, heating, drag, stiffness, strain-relief, snag, and fall-arrest-separation evidence;
- pose-dependent TCP limiter implementation and worst-case combined-axis tests;
- synchronized BOM, schematics, wire table, connector schedule, software limits, web guide, and controlled source documents.

Until those items close through qualified review and physical evidence, the package remains **PRELIMINARY—NOT APPROVED FOR ENERGIZATION**.
