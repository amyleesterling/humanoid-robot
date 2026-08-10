# Mechanical Concept and Preliminary Load Model

> **R98 OVERRIDING ARCHITECTURE/LOAD HOLD:** `HR-V0-ARM-ARCH-P0.7` remains the controlled unreleased geometry and its custom-metal route remains held. The nonselected P1.1 comparison preserves the R95 geometry and R96 incomplete load basis. `HR-V0-FR12-MASS-MET-P0.1` defines an unexecuted physical mass-property route for `LOAD-OPEN-01`; `HR-V0-X430-DUTY-P0.1` defines an unexecuted instrumented route for `LOAD-OPEN-08` with all seven powered stages blocked. The gripper, FR12 measured properties, hardware/harness, complete COM/inertia, drive/reflected inertia, bumper, accepted continuous torque/thermal limits and measured dynamics remain unresolved. P1.0/P1.1 and X430 are unselected; P0.7 is not superseded and no purchase or external work is authorized.

> **R70 CURRENT BOUNDARY:** The historical P0.2 flat-arm architecture and R54/P0.1 through R67/P0.6 arm candidates remain superseded. `HR-V0-ARM-ARCH-P0.7` remains the controlled geometry with integrated A00-A07 plus HS-J2-POS, a 40,001-pose body sweep, a continuous nominal clearance certificate for 69 non-intentional rigid-body pairs through J2=120 degrees, and a separately analyzed twin-rail positive-stop contact. `HR-V0-MASS-REDUCTION-P0.1` adds four nonselected subtractive relief candidates; it does not supersede P0.7. `HR-V0-MECH-P0.6` remains the release hold. No adapter, support, beam, fastener, bumper, motion limit or supplier packet is released.

**PRELIMINARY—NOT APPROVED FOR ENERGIZATION**

Status: correction-stage feasibility model. Exact vendor-coordinate arm source, explicit integrated transforms, an interactive candidate model, controlled C01/C04/C05/C06/C07 drawings/DXFs, a same-interface relief study, preliminary mass properties, reproducible structural screens, continuous nominal body-clearance evidence, analytical positive-stop geometry, controlled fit-coupon packages, an exact-revision gripper collision/kinematic reference, a proposed orderable gripper mechanism allocation, and guard/catch/cable space studies now exist. Received MTR/FAI, qualified analytical acceptance, T-slot capacity, received fastener stacks, torque/locking/reuse rules, physical coupon/kit inspection, complete gripper manufacturing definition and H104 registration, complete mass closure, selected bumper, measured stopping/drop/sweep evidence, exact guard/receiver/harness parts, gripper force/fasteners, bench anchors, continuous-duty/thermal evidence, proof tests, and mechanical release are not complete. See [the R69 arm architecture candidate](hr-v0-arm-architecture-p0.7.md), [the R96 P1.1 load basis](hr-v0-x430-load-basis-p1.1.md), [the R97 FR12 metrology route](hr-v0-fr12-moving-mass-metrology-p0.1.md), [the R98 X430 duty route](hr-v0-x430-duty-characterization-p0.1.md), [the R70 mass-reduction study](hr-v0-mass-reduction-study-p0.1.md), [the P0.6 mechanical hold](hr-v0-mechanical-release-p0.6.md), [joint-interface basis](hr-v0-joint-interface-fasteners-p0.1.md), [gripper architecture](hr-v0-gripper-architecture-p0.2.md), [guard/receiver/cable architecture](hr-v0-guard-receiver-cable-p0.1.md), and [hard-stop basis](hr-v0-hard-stop-design-basis-p0.3.md).

## Current exact-coordinate candidate

R69 preserves the controlled XM540-to-S102 registration and parallel reference J1/J2 axes. J1 is at `(-210,81.025,500) mm` from A0. Candidate J1-to-J2 spacing is 202.550 mm; H104 G1 is 129.050 mm beyond J2 and 331.600 mm from J1, reserving 28.400 mm to the 360 mm object-center ceiling. The upper/forearm members are 100/50 mm vertical `20-2040` envelopes between candidate 9.525 mm adapters. An adaptive certificate covers all 69 non-intentional nominal rigid-body pairs through J2=120° with at least 0.75 mm conservative lower-bound clearance and locates first nominal body contact at 121.643289°. The separately analyzed C06/C07 twin-rail stop contacts at nominal J2=117.999985° while the body retains 2.114900 mm clearance. The candidate software ceiling remains 115°. Bumper selection, cables, guards, stopping overtravel, backlash, compliance, manufacturing variation, deformation and physical tolerances remain excluded.

The R69 partial screen is 2.018 N·m shoulder gravity and 0.515 N·m elbow gravity; after the 2.25 screening multiplier, 4.541 N·m and 1.158 N·m. It uses current C01/C04/C06/C07/member CAD estimates but still uses legacy elbow/gripper/payload allocations and omits frames, fasteners, cables and final gripper mechanics, so it is incomplete and may rise. The member/thread/adapter screens are indicative only; typical material values are not allowables. Certified properties, local contact/prying, preload, fatigue, impact and physical proof remain open.

## Historical P0.2 geometry — withdrawn

The following P0.2 geometry is retained only to explain earlier calculations. It must not be fabricated or used as the current arm definition.

- J1 shoulder pitch: commanded range −20° to +70° from horizontal datum.
- J2 elbow pitch: historical commanded range 15° to 125° internal angle; **withdrawn and prohibited for the current candidate**.
- Upper link, shoulder axis to elbow axis: 160 ±0.5 mm.
- Forearm, elbow axis to gripper datum: 160 ±0.5 mm.
- Payload center: up to 200 mm from elbow and 360 mm from shoulder in the screened horizontal pose.
- Historical 5° hard-stop rule: **withdrawn**. The current unreleased allocation is a 115° software ceiling and 118° positive metal contact, governed by `HR-V0-HS-P0.3`.
- Each rotating joint requires dual-supported output geometry. Actuator output bearings alone shall not carry cantilevered link loads unless the actuator manufacturer explicitly approves the final force, moment, duty, shock, and life case.

Links are initially specified as flat 4.75 mm nominal 6061-T6 aluminum plates using ROBOTIS FR13-H101K output frames and FR13-S102K actuator-body frames. The interfaces are deliberately asymmetric: H101 output uses the PCD22 clearance pattern, S102 body-frame mounting uses the selected 32 x 16 tapped rectangle, and the proposed FR12-H104K gripper frame uses a selected 24 x 12 mm four-hole subset. `MV0-FC03` physical seating and fastener-access evidence is mandatory; the H104-to-official-URDF transform, fastener stack and load path remain unreleased. Polymer parts may be used for fit coupons, covers, cable guides, and gripper fingers, but not as the sole primary shoulder load path in the first build release. See [the joint-interface and fastener basis](hr-v0-joint-interface-fasteners-p0.1.md) and [the gripper architecture](hr-v0-gripper-architecture-p0.2.md).

## Mass budget

| Item | Maximum mass | Center from upstream axis |
|---|---:|---:|
| Upper link hardware | 0.12 kg | 0.08 m from shoulder |
| Elbow actuator + bracket | 0.20 kg | 0.16 m from shoulder |
| Forearm hardware | 0.12 kg | 0.08 m from elbow |
| Gripper assembly | 0.21 kg | 0.16 m from elbow |
| Payload | 0.10 kg | 0.20 m from elbow, 0.36 m from shoulder |

Maximum moving mass from this budget is 0.75 kg, including the 0.10 kg payload and excluding the fixed shoulder actuator/base. R69’s controlled C01/C04/C06/C07/member estimates plus the two actuator masses and payload produce a 692.758 g subtotal, leaving only 57.242 g before frames, fasteners, bumper, gripper mechanics and moving cables. The upper and forearm buckets are already exceeded. R70's nonselected relief set would reduce the incomplete subtotal to 634.775 g and raise provisional headroom to 115.225 g, but does not account for or measure the missing items. This remains a mass-budget blocker, not a measured pass. See [the moving-mass closure record](hr-v0-moving-mass-closure-p0.1.md).

## Historical P0.2 static gravity torque — superseded by the R57 candidate screen

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
