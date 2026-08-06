# HR-30 Walking-System Specification

Document ID: HR-WALK-001  
Revision: 0.1  
Program baseline: HR-30-SYS-R0.2  
Status: walking baseline; actuator procurement pending test articles

## Walking mission

HR-30W shall start from quiet standing, walk untethered on a level indoor floor, turn, stop, and return to quiet standing without external support. Development proceeds through a slack overhead tether, but the tether may arrest falls only and may not carry robot weight during scored HR-30D trials.

Walking around people—especially children—is not authorized by passing the engineering walking test. That requires a separate physical-contact, functional-safety, and operating-site release.

## Initial performance envelope

| Metric | HR-30D tethered acceptance | HR-30W untethered acceptance |
|---|---:|---:|
| Surface | level rigid indoor, ±0.5° | same |
| Continuous path | 10 m | 25 m |
| Commanded speed | 0.08–0.15 m/s | 0.10–0.20 m/s |
| Minimum step length | 40 mm | 50 mm |
| Maximum nominal step length | 100 mm | 120 mm |
| Step width | 90–140 mm | 90–140 mm |
| Foot clearance | 15 mm minimum | 20 mm minimum |
| Quiet stand | 60 s | 120 s |
| Turn | 90° in ≤6 steps | 90° in ≤5 steps |
| Normal stop | settle within 2 steps | settle within 2 steps |
| Endurance | 10 min cumulative | 30 min cumulative |

No ramps, stairs, carpet transitions, outdoor terrain, running, jumping, or deliberate human contact are part of the first walking release.

## Leg kinematics

Each leg has six active axes:

1. hip yaw;
2. hip roll;
3. hip pitch;
4. knee pitch;
5. ankle pitch;
6. ankle roll.

Provisional commanded ranges are hip yaw ±30°, hip roll ±25°, hip pitch -35° to +45°, knee 0° to 120°, ankle pitch -35° to +30°, and ankle roll ±20°. Mechanical stops sit beyond software limits but before cable, shell, or self-collision. Final ranges come from collision-checked CAD and gait optimization.

## Candidate drivetrain

Baseline A uses twelve ROBOTIS XH540-W270-R 14.8 V RS-485 actuators for commonality and low moving mass. Hip pitch, knee pitch, and ankle pitch receive a **1.5:1 external timing-belt reduction** (motor:joint) with a dual-supported joint shaft. This stage makes no claim of braking or non-backdrivability. Hip yaw, hip roll, and ankle roll begin direct drive but retain packaging space for 1.5:1 reduction if tests require it.

Published XH540-W270 performance is 11.7 N·m stall torque at 14.8 V; the 1.5:1 stage gives a theoretical 17.6 N·m joint stall value before efficiency loss. Stall torque is never a continuous rating. Acceptance depends on measured continuous torque, temperature, backlash, efficiency, impact response, and gait duty cycle.

The public shorthand for this number is: **17.6 N·m ideal, momentary, zero-speed stall after the proposed reduction. It is not continuous, thermally sustainable, or impact-rated torque.** It may not be used as an available walking-torque value in sizing or acceptance calculations.

Baseline B tests CubeMars AK70-10-class modules at hip/knee if Baseline A cannot meet continuous or impact loads. At 521 g and 8.3 N·m published rated torque, AK70 modules improve dynamic torque control but add several kilograms if used at every joint. Mixing actuator families is permitted only if timing, fault, service, and spare-part costs are accepted at design review.

The ROBOTIS YM070 99:1 actuator is not the baseline despite its published 14.6 N·m continuous torque because its 790–980 g mass would make a twelve-joint leg set incompatible with the HR-30 mass ceiling.

Every externally reduced leg joint requires output-side absolute position sensing as the baseline. A proposed alternative is allowed only after it demonstrates equivalent detection of belt slip, pulley release, backlash, lost calibration, and motor/output disagreement over the full released temperature, load, and motion envelope. Encoder model, mounting, redundancy, accuracy, power-loss behavior, and safety role remain `SELECTION REQUIRED`.

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

This is the canonical multi-rate schedule: 1 kHz safety monitoring; 800 Hz IMU acquisition; 500 Hz state estimation and foot-force processing; 250 Hz whole-body stabilization and each segmented joint bus; and 50 Hz non-real-time planning. Faster internal sampling is allowed, but every boundary uses timestamped data and explicit age limits. No document or implementation may substitute one of these rates for another without a controlled change record.

The 250 Hz bus rate remains a design target, not a demonstrated capacity. Before integrated gait, a packet budget shall account for every command and response byte, protocol overhead, turnaround time, retries, diagnostics, bus utilization, worst-case jitter, and failure traffic. Physical topology, termination, shielding, isolation, power injection, and any left/right bus rebalance remain `SELECTION REQUIRED` pending the measured budget and harness evidence.

The real-time controller executes state estimation and whole-body stabilization. Raspberry Pi/Linux performs perception, behavior, logging, and non-real-time planning. Linux cannot be the only process maintaining balance.

## Gait state machine

Walking modes execute only inside the canonical `DRIVE_ENABLED` state defined in `docs/control.md`:

`CROUCH_READY -> QUIET_STAND -> WEIGHT_SHIFT -> SINGLE_SUPPORT -> DOUBLE_SUPPORT -> QUIET_STAND`

Any walking mode may request `CONTROLLED_STOP` through a released kneel or stop trajectory while verified control authority remains. Loss of that authority transitions to the applicable latched fault and hardware energy-removal response. `TETHER_ARREST` describes a physical event, not a software-safe state. A walking command carries speed, heading, stop horizon, terrain class, configuration hash, timestamp, sequence number, and timeout. Unknown terrain, stale commands, or configuration mismatch converge to a stop; they do not continue the last velocity indefinitely.

## Fall and stop behavior

An inertial fall predictor monitors attitude, angular rate, support polygon, foot forces, joint tracking, bus health, and supply voltage. It shall declare `FALL_IMMINENT` early enough to retract arms, protect the head, reduce joint stiffness, and request controlled kneel when feasible.

Immediate actuator power removal can itself cause a fall because the candidate leg joints have no safety brake. Therefore:

- HR-30D relies on the rated overhead arrest system during all powered gait work;
- HR-30W is tested inside a padded, access-controlled area with no person inside the fall envelope;
- human-facing walking is blocked until a reviewed solution exists for safe power-loss behavior, which may require joint brakes, retained control power, passive knee geometry, or another independently validated measure.

The emergency stop still removes hazardous drive energy through hardware. No software claim may weaken that function merely to keep the robot standing.

## Energy system

HR-30C/D initially use an external current-limited 14.0–14.8 V actuator supply through a managed overhead tether. HR-30W requires an onboard, professionally assembled 4-series battery system with:

- cell-level protection and balancing;
- main fuse at the pack;
- precharge and anti-spark connection;
- service disconnect accessible without removing covers;
- redundant drive-energy contactors or equivalent reviewed isolation;
- pack current, voltage, and temperature telemetry independent of gait software;
- rigid fire-resistant enclosure and strain relief;
- transport, charging, and storage procedure appropriate to the selected chemistry.

No hand-built loose-cell pack is permitted. Pack voltage, capacity, chemistry, and supplier remain a procurement gate after the measured walking power profile exists.
