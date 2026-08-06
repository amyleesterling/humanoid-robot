# Mechanical Concept and Preliminary Load Model

**PRELIMINARY—NOT APPROVED FOR ENERGIZATION**

Status: correction-stage feasibility model. Native HR-V0 R0.1 quote geometry, four custom-part neutral files, preliminary mass properties, reproducible structural screens, three controlled fit-coupon packages, a proposed orderable gripper mechanism allocation, a checked hard-stop kinematic/load-case study, and a generated guard/catch/cable space study now exist. Physical coupon/kit inspection, released production tolerances/drawings, complete mass closure, fabricable hard-stop parts, measured stopping/drop/sweep evidence, exact guard/receiver/harness parts, gripper force/fasteners, bench anchors, proof tests, and mechanical release are not complete. See [the R0.1 mechanical baseline](hr-v0-mechanical-r0.1.md), [joint-interface basis](hr-v0-joint-interface-fasteners-p0.1.md), [gripper architecture](hr-v0-gripper-architecture-p0.1.md), [guard/receiver/cable architecture](hr-v0-guard-receiver-cable-p0.1.md), [hard-stop basis](hr-v0-hard-stop-design-basis-p0.1.md), and [R11 engineering calculations](r11-engineering-calculations.md).

## Geometry

The HR-V0 mechanism is a planar two-link arm mounted to a rigid vertical bench column.

- J1 shoulder pitch: commanded range −20° to +70° from horizontal datum.
- J2 elbow pitch: commanded range 15° to 125° internal angle.
- Upper link, shoulder axis to elbow axis: 160 ±0.5 mm.
- Forearm, elbow axis to gripper datum: 160 ±0.5 mm.
- Payload center: up to 200 mm from elbow and 360 mm from shoulder in the screened horizontal pose.
- Mechanical hard stops shall sit at least 5° beyond software limits and before any cable, connector, or shield contact.
- Each rotating joint requires dual-supported output geometry. Actuator output bearings alone shall not carry cantilevered link loads unless the actuator manufacturer explicitly approves the final force, moment, duty, shock, and life case.

Links are initially specified as flat 4.75 mm nominal 6061-T6 aluminum plates using ROBOTIS FR13-H101K output frames and FR13-S102K actuator-body frames. The interfaces are deliberately asymmetric: H101 output uses the PCD22 clearance pattern, S102 body-frame mounting uses the selected 32 x 16 tapped rectangle, and the proposed FR12-H104K gripper frame uses a selected 24 x 12 mm four-hole subset. `MV0-FC03` physical seating and fastener-access evidence is mandatory; the fastener stack and load path remain unreleased. Polymer parts may be used for fit coupons, covers, cable guides, and gripper fingers, but not as the sole primary shoulder load path in the first build release. See [the joint-interface and fastener basis](hr-v0-joint-interface-fasteners-p0.1.md) and [the gripper architecture](hr-v0-gripper-architecture-p0.1.md).

## Mass budget

| Item | Maximum mass | Center from upstream axis |
|---|---:|---:|
| Upper link hardware | 0.12 kg | 0.08 m from shoulder |
| Elbow actuator + bracket | 0.20 kg | 0.16 m from shoulder |
| Forearm hardware | 0.12 kg | 0.08 m from elbow |
| Gripper assembly | 0.21 kg | 0.16 m from elbow |
| Payload | 0.10 kg | 0.20 m from elbow, 0.36 m from shoulder |

Maximum moving mass from this budget is 0.75 kg, including the 0.10 kg payload and excluding the fixed shoulder actuator/base. The controlled R23 ledger has a 565.4 g known subtotal and only 184.6 g of unresolved headroom for all remaining moving parts. This is an allocation screen, not a measured assembly-mass pass. Each item requires a supplier or CAD source, local center of mass, inertia, configuration revision, and later a measured value. See [the moving-mass closure record](hr-v0-moving-mass-closure-p0.1.md).

## Worst-case static gravity torque

The conservative pose places both links horizontal. Using `g = 9.80665 m/s²`:

`T_shoulder = g × [(0.12×0.08) + (0.20×0.16) + (0.12×0.24) + (0.21×0.32) + (0.10×0.36)] = 1.70 N·m`

`T_elbow = g × [(0.12×0.08) + (0.21×0.16) + (0.10×0.20)] = 0.62 N·m`

Preliminary design checks use 1.5× for commanded acceleration and 1.5× uncertainty, producing intermittent screening values of 3.83 N·m at J1 and 1.40 N·m at J2. These are not continuous-duty ratings or permission to energize.

The current official ROBOTIS web manual, consulted 2026-08-06, publishes the XM540-W270 at **10.6 N·m ideal stall torque and 4.4 A stall current at 12.0 V**. The prior 9.9 N·m statement incorrectly used the XH540 value and has been removed. The ideal stall ratio against the 3.83 N·m shoulder screen is `10.6 / 3.83 = 2.77`, but stall is a momentary zero-speed endpoint, not a continuous available torque or structural safety factor.

Build release requires a duty-cycle/temperature bench test with the actual joint, controlled current limiting, measured actuator-terminal voltage, and final mass properties. If J1 cannot hold the horizontal proof pose below the approved steady current and temperature, the design shall add a counterbalance or change the actuator; current limits shall not simply be raised.

## Tool-center-point speed consistency

The 30 deg/s joint limit is `30 × π / 180 = 0.5236 rad/s`. At the 0.36 m maximum shoulder-to-payload radius, shoulder-only motion would produce:

`v_TCP = r × ω = 0.36 × 0.5236 = 0.188 m/s`

That exceeds the 0.15 m/s tool-center-point (TCP) limit. At full reach, the shoulder-only rate must therefore be no more than:

`ω_shoulder,max = 0.15 / 0.36 = 0.4167 rad/s = 23.9 deg/s`

Combined shoulder and elbow motion can be more restrictive. In the screened straight horizontal pose, using 0.36 m from shoulder to the payload center and 0.20 m from elbow to the payload center, equal-direction motion at 30 deg/s gives a conservative planar Jacobian screen of `(0.36 + 0.20) × 0.5236 = 0.293 m/s`. The controller shall therefore use pose-dependent forward-kinematic/Jacobian rate limiting on the defined TCP; independent per-joint caps are insufficient. The exact TCP datum, tool transform, link calibration, command interpolation, measurement method, and worst-case combined-axis test remain release inputs.

Reset, enable, or E-stop release shall never create motion. TCP limiting applies to commanded, startup, recovery, calibration, and controlled-stop trajectories.

## Output-load boundary

For the walking candidate, the current XH540 manufacturer page lists a 40 N radial load at 10 mm from the horn and a 20 N axial load. An 8 kg single-support load is already approximately 78.5 N static before dynamics or lever arms. Consequently, HR-30 leg axes require dual-supported output shafts or an independently verified equivalent load path. The final bearing arrangement must isolate actuator bearings from prohibited radial, axial, and overturning loads.

The HR-V0 arm requires the same form of proof using the selected actuator's own manufacturer limits; XH540 limits shall not be silently transferred to XM540. Exact actuator variant, horn, bearing, shaft, bracket, fastener, and load spectrum remain controlled selections.

## Structural release calculations still required

- joint-shaft and bearing radial, axial, moment, life, and shock loads;
- plate bending and fastener bearing/tear-out at 3× the maximum permitted operational load;
- base and bench overturning/slip at 3× operational load;
- hard-stop impact at the maximum physically possible speed;
- gripper finger stress and detachment retention;
- fatigue-sensitive holes and printed-part creep;
- shield impact and fastener retention;
- cable forces throughout the envelope;
- tolerance stack, alignment, backlash, and service access;
- correlation of CAD mass properties with measured parts.

Minimum mechanical proof factor is 3.0 against the maximum permitted operational load for non-brittle metal primary structure. This is a project rule, not a standards claim. It does not replace joint-specific fatigue, impact, fastener, bearing, or restraint analysis.

The current hard-stop screen records the allocated-mass energies and candidate 50 mm contact datums but is not a stop-part release. Reflected drive inertia, bumper force/displacement, current persisting during stop-detection latency, rebound, wear, tolerance and repeated-cycle evidence remain required under `INSPECT-MECH-006` and `TEST-MECH-002`.

## Serviceability and pinch control

Route power and data in separate replaceable looms with strain relief at every moving transition. No cable may become a hard stop. Covers shall prevent finger access to belt, gear, and scissor-gripper pinch points. Fasteners in primary joints use documented torque, prevailing-torque nuts or threadlocker as appropriate, and witness marks. Gripper fingers use compliant pads and rounded edges with at least 3 mm radius.

This document does not authorize fabrication, energization, or operation around children.
