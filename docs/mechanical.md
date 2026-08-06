# Mechanical Concept and Preliminary Load Model

Status: preliminary; CAD and drawing release are not yet present.

## Geometry

The mechanism is a planar two-link arm mounted to a rigid vertical bench column.

- J1 shoulder pitch: commanded range -20° to +70° from horizontal datum.
- J2 elbow pitch: commanded range 15° to 125° internal angle.
- Upper link, shoulder axis to elbow axis: 160 ±0.5 mm.
- Forearm, elbow axis to gripper datum: 160 ±0.5 mm.
- Mechanical hard stops shall sit at least 5° beyond software limits and before any cable, connector, or shield contact.
- Each rotating joint requires dual-supported output geometry; actuator output bearings alone shall not carry cantilevered link loads unless the actuator maker explicitly approves the final load case.

Links are initially specified as 6061-T6 aluminum side plates with transverse spacers. Polymer parts may be used for covers, cable guides, and gripper fingers, but not as the sole primary shoulder load path in the first build release.

## Mass budget

| Item | Maximum mass | Center from upstream axis |
|---|---:|---:|
| Upper link hardware | 0.12 kg | 0.08 m from shoulder |
| Elbow actuator + bracket | 0.20 kg | 0.16 m from shoulder |
| Forearm hardware | 0.12 kg | 0.08 m from elbow |
| Gripper assembly | 0.21 kg | 0.16 m from elbow |
| Payload | 0.10 kg | 0.20 m from elbow, 0.36 m from shoulder |

Maximum moving mass from this budget is 0.75 kg.

## Worst-case static gravity torque

The conservative pose places both links horizontal. Using `g = 9.80665 m/s²`:

`T_shoulder = g × [(0.12×0.08) + (0.20×0.16) + (0.12×0.24) + (0.21×0.32) + (0.10×0.36)] = 1.70 N·m`

`T_elbow = g × [(0.12×0.08) + (0.21×0.16) + (0.10×0.20)] = 0.62 N·m`

Preliminary design checks use 1.5× for commanded acceleration and 1.5× uncertainty, producing required intermittent torques of 3.83 N·m at J1 and 1.40 N·m at J2. These are sizing values, not permission to run continuously at those loads.

The proposed XM540-W270-T is published at 9.9 N·m stall torque at 12 V. Stall torque is not a continuous rating. Build release requires a duty-cycle/temperature bench test with the actual joint, current limiting enabled, and the final mass properties. If J1 cannot hold the horizontal proof pose below the approved steady current and temperature, the design shall add a counterbalance or change actuator; software current limits shall not simply be raised.

## Structural release calculations still required

- joint-shaft/bearing radial and moment loads;
- plate bending and fastener bearing/tear-out at 3× the worst operational load;
- base and bench overturning/slip at 3× operational load;
- hard-stop impact at the maximum physically possible speed;
- gripper finger stress and detachment retention;
- fatigue-sensitive holes and printed-part creep;
- shield impact and fastener retention.

Minimum mechanical proof factor is 3.0 against the maximum permitted operational load for non-brittle metal primary structure. This is a project rule, not a standards claim.

## Serviceability and pinch control

Route power and data in separate replaceable looms with strain relief at every moving transition. No cable may become a hard stop. Covers shall prevent finger access to belt, gear, and scissor-gripper pinch points. Fasteners in primary joints use documented torque, prevailing-torque nuts or threadlocker as appropriate, and witness marks. The gripper fingers use compliant pads and rounded edges with at least 3 mm radius.

