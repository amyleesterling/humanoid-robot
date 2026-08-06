# HR-30 Walking-System Specification

**PRELIMINARY—NOT APPROVED FOR ENERGIZATION**

Document ID: HR-WALK-001  
Revision: 0.2, R11 correction pass
Program baseline: HR-30-SYS-R0.2  
Status: walking feasibility baseline; actuator, reduction, energy, tether, and connector selections remain open

Controlled arithmetic and source details are in [R11 engineering calculations](r11-engineering-calculations.md).

## Walking mission

HR-30W is intended to start from quiet standing, walk untethered on a level indoor floor, turn, stop, and return to quiet standing without external support. Development proceeds through a slack overhead fall-arrest system and, if selected, a separately managed power/data tether. Neither may carry robot weight during a scored HR-30D trial.

Walking around people—especially children—is not authorized by passing the engineering walking test. That requires separate physical-contact, functional-safety, and operating-site reviews.

## Initial performance envelope

| Metric | HR-30D tethered acceptance | HR-30W untethered acceptance |
|---|---:|---:|
| Surface | level rigid indoor, ±0.5° | same |
| Continuous path | 10 m | 25 m |
| Commanded speed | **0.10–0.14 m/s** | **0.10–0.14 m/s** |
| Minimum step length | 40 mm | 50 mm |
| Maximum nominal step length | 100 mm | 120 mm |
| Step width | 90–140 mm | 90–140 mm |
| Foot clearance | 15 mm minimum | 20 mm minimum |
| Quiet stand | 60 s | 120 s |
| Turn | 90° in ≤6 steps | 90° in ≤5 steps |
| Normal stop | settle within 2 steps | settle within 2 steps |
| Endurance | 10 min cumulative | 30 min cumulative |

The 0.10–0.14 m/s band is a release ceiling, not evidence that the candidate actuator meets the trajectory. No ramps, stairs, carpet transitions, outdoor terrain, running, jumping, or deliberate human contact are part of the first walking release.

## Leg kinematics

Each leg has six active axes:

1. hip yaw;
2. hip roll;
3. hip pitch;
4. knee pitch;
5. ankle pitch;
6. ankle roll.

Provisional commanded ranges are hip yaw ±30°, hip roll ±25°, hip pitch −35° to +45°, knee 0° to 120°, ankle pitch −35° to +30°, and ankle roll ±20°. Mechanical stops sit beyond software limits but before cable, shell, or self-collision. Final ranges come from collision-checked CAD and gait optimization.

## Candidate drivetrain and blocked assumptions

The current test candidate is twelve ROBOTIS XH540-W270-R RS-485 actuators. Hip pitch, knee pitch, and ankle pitch retain a proposed **1.5:1 external timing-belt reduction** (motor:joint) with a dual-supported joint shaft. This stage makes no claim of braking or non-backdrivability. Hip yaw and ankle roll may begin as direct-drive test articles only after their W0 screens close. **Direct-drive hip roll is blocked.** Packaging shall preserve a credible reduction or alternate-actuator path.

The current official ROBOTIS web manual, consulted 2026-08-06, gives these XH540-W270 facts:

| Property | Manufacturer value | Engineering use |
|---|---:|---|
| input voltage | 10.0–14.8 V; 12 V recommended | rail must remain inside limits during steady and transient operation |
| ideal stall torque/current at 12 V | 9.9 N·m / 4.9 A | momentary zero-speed screen only |
| ideal stall torque/current at 14.8 V | 11.7 N·m / 5.9 A | momentary zero-speed screen only |
| no-load speed at 12 V | 39 rpm | 234 deg/s motor; 156 deg/s after ideal 1.5:1 reduction |
| no-load speed at 14.8 V | 46 rpm | 276 deg/s motor; 184 deg/s after ideal 1.5:1 reduction |
| radial load | 40 N at 10 mm from horn | cannot carry single-support load through actuator bearing alone |
| axial load | 20 N | must be included in output-bearing proof |
| mass | 165 g | twelve units total 1.980 kg before structure |

Manufacturer stall and no-load points are mutually exclusive endpoints, not one usable operating point. The proposed 1.5:1 stage gives 17.55 N·m ideal zero-speed joint stall at 14.8 V before losses. Continuous/cyclic torque, speed under load, temperature, backlash, efficiency, impact response, and gait duty cycle require physical characterization at the actual actuator-terminal voltage.

At a 125 mm hip width, a 62.5 mm lateral moment arm produces 4.90 N·m static hip-roll torque at 8 kg and 6.13 N·m at 10 kg. A 2× dynamic screen gives 9.81–12.26 N·m before any added uncertainty factor. That leaves no defensible direct-drive margin against a 9.9 N·m ideal stall point at 12 V and fails the 10 kg case even at 14.8 V. W0 must close all six axes for stand, weight transfer, single support, step, kneel, rise, stop, and disturbance trajectories.

The no-load speed screen also constrains the gait. At 14.8 V the 1.5:1 pitch reduction permits only 184 deg/s unloaded at the joint; at 12 V it permits 156 deg/s. The released 0.10–0.14 m/s band therefore requires trajectory-level proof of loaded joint speed, torque, voltage sag, bus timing, and temperature. Higher speeds are not carried forward.

Every reduced leg joint requires output-side absolute position sensing as the baseline. An alternative is allowed only after demonstrating equivalent detection of belt slip, pulley release, backlash, lost calibration, and motor/output disagreement over the released temperature, load, and motion envelope. Encoder model, mounting, redundancy, accuracy, power-loss behavior, and safety role remain `SELECTION REQUIRED`.

The actuator connector housing, contacts, wire gauge, mating cycle, temperature rise, and derating remain `SELECTION REQUIRED`. No approximate connector current figure is a rating. Exact manufacturer order codes and contact-level evidence are required before comparing connector capacity with joint current or fault current.

Alternative actuator families may be screened, but no alternate is selected. Any mixed family must close voltage compatibility, timing, fault behavior, service, mass, thermal rejection, and spares. Published rated or stall torque alone is insufficient.

## Output support and structure

The manufacturer radial-load value is 40 N at 10 mm from the XH540 horn. Single-support foot force is already about 78.5 N at the 8 kg target and 98.1 N at the 10 kg ceiling before dynamics, lever arm, joint geometry, or impacts. A 2× dynamic screen exceeds 150 N at 8 kg. Therefore every load-bearing leg axis requires a dual-supported output shaft or an independently verified equivalent load path; support is mandatory, not a packaging preference. Bearing, shaft, housing, fastener, and actuator-interface proofs remain required from the final CAD loads.

## Foot and state sensing

- One 6-axis IMU rigidly attached near the pelvis center, sampled at 800 Hz minimum; a second torso IMU is recommended for cross-checking.
- At least four independently calibrated vertical load-sensing points per foot, sampled synchronously at 500 Hz minimum.
- Foot data shall resolve total normal force to ±5 N and center of pressure to ±5 mm over the validated load region.
- Every joint reports position, velocity, current/torque proxy, voltage, temperature, and hardware faults at 250 Hz minimum.
- Foot sole uses a replaceable high-friction compliant layer with a documented friction test and no hidden caster or support.

## Control timing

| Function | Minimum rate | Deadline rule |
|---|---:|---|
| Actuator internal loop | manufacturer internal rate | monitored through response tests |
| Joint command/feedback bus | 250 Hz per leg | two missed frames trigger gait abort |
| IMU acquisition and attitude filter | 800 Hz | timestamp jitter <0.5 ms RMS target |
| Foot force/CoP estimation | 500 Hz | synchronized left/right within 1 ms |
| State estimator | 500 Hz | stale state >6 ms invalid |
| Whole-body stabilizer | 250 Hz | deadline miss latches degraded stop |
| Footstep/gait planner | 50 Hz | never commands actuators directly |
| Hardware fall/safety monitor | 1 kHz | independent of Linux process health |

This is the canonical multi-rate target: 1 kHz safety monitoring; 800 Hz IMU acquisition; 500 Hz state estimation and foot-force processing; 250 Hz stabilization and each segmented joint bus; and 50 Hz non-real-time planning. Faster internal sampling is allowed, but every boundary uses timestamped data and explicit age limits.

The 250 Hz bus rate is not demonstrated capacity. Before integrated gait, a packet budget shall account for every command and response byte, protocol overhead, turnaround time, retries, diagnostics, bus utilization, worst-case jitter, and failure traffic. Physical topology, termination, shielding, isolation, power injection, and any left/right rebalance remain `SELECTION REQUIRED` pending measured harness evidence. RS-485 shall be routed and shielded from actuator-current conductors according to a controlled harness drawing, with a single verified topology and termination plan.

The real-time controller executes state estimation and whole-body stabilization. Raspberry Pi/Linux performs perception, behavior, logging, and non-real-time planning. Linux cannot be the only process maintaining balance.

## Gait state machine

Walking modes execute only inside the canonical `DRIVE_ENABLED` state defined in `docs/control.md`:

`CROUCH_READY -> QUIET_STAND -> WEIGHT_SHIFT -> SINGLE_SUPPORT -> DOUBLE_SUPPORT -> QUIET_STAND`

Any walking mode may request `CONTROLLED_STOP` through a released kneel or stop trajectory while verified control authority remains. Loss of that authority transitions to the applicable latched fault and hardware energy-removal response. `TETHER_ARREST` describes a physical event, not a software-safe state. A walking command carries speed, heading, stop horizon, terrain class, configuration hash, timestamp, sequence number, and timeout. Unknown terrain, stale commands, or configuration mismatch converge to a stop; they do not continue the last velocity indefinitely.

## Fall, stop, and regeneration behavior

An inertial fall predictor monitors attitude, angular rate, support polygon, foot forces, joint tracking, bus health, and supply voltage. It shall declare `FALL_IMMINENT` early enough to retract arms, protect the head, reduce joint stiffness, and request controlled kneel when feasible.

Immediate actuator power removal can itself cause a fall because the candidate joints have no safety brake. Therefore:

- HR-30D relies on the reviewed overhead arrest system during all powered gait work;
- HR-30W is tested inside a padded, access-controlled area with no person inside the fall envelope;
- human-facing walking is blocked until a reviewed solution exists for safe power-loss behavior, which may require joint brakes, retained control power, passive geometry, or another independently validated measure.

The emergency stop still removes hazardous drive energy through hardware. No software claim may weaken that function merely to keep the robot standing.

Actuator deceleration and gravity-driven joint motion can return energy to the DC bus. The present bench-source candidate is not documented as an energy sink. Bus clamp, dump, storage, or bidirectional-converter architecture remains `SELECTION REQUIRED`. Test evidence shall cover worst-case bus rise, source overvoltage/latch behavior, contactor opening, loss of clamp, and whether the released controlled-stop trajectory remains available. A software deceleration limit alone is not regenerative-energy protection.

## Energy system and tether

The actuator rail, tether voltage, battery chemistry, series count, converter, and capacity are all `SELECTION REQUIRED`. The XH540-W270 accepts 10.0–14.8 V and recommends 12 V. A 4-series lithium-ion/LiPo pack reaches 16.8 V when full and is incompatible with direct connection. A 4-series LiFePO4 example may remain below 14.8 V when full, but torque and speed must pass at loaded end-of-discharge voltage. These are architecture screens, not selections.

Any onboard energy system requires cell-level protection and balancing, main fuse, precharge, service disconnect, reviewed drive-energy isolation, independent current/voltage/temperature telemetry, enclosure and strain relief, charger interlock, and chemistry-appropriate transport, charging, and storage procedures. No hand-built loose-cell pack is permitted.

The development tether shall compare low-voltage/high-current distribution with a higher-voltage tether plus on-robot conversion. A prior calculation used 8 AWG, 2.1 mΩ/m, 3–5 m one-way length, and 80 A only as review assumptions; it predicted 1.01–1.68 V loop drop. Those are not released values. Closure requires source and converter transients, maximum and continuous current, voltage drop, fault protection, connector/contact evidence, regeneration behavior, conductor temperature/derating, PE/shield strategy, jurisdiction, tether mass and bend stiffness, overhead support, drag torque, strain relief, and snag prevention. The power/data tether and fall-arrest line shall not create a common single-point hazard.

This document does not authorize procurement, fabrication, energization, or walking near people.
