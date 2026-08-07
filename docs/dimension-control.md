# HR-30 Dimension-Control Specification

The top-level CAD assembly shall be driven from a single parameter table. No subassembly may redefine these datums independently.

| Parameter | Symbol | Nominal | Allowed design range |
|---|---|---:|---:|
| Total height | H | 762 mm | 740–800 mm |
| Floor to ankle | Z_A | 45 mm | 40–55 mm |
| Ankle to knee | L_S | 165 mm | 155–175 mm |
| Knee to hip | L_T | 170 mm | 160–180 mm |
| Hip to shoulder | L_TR | 210 mm | 195–225 mm |
| Shoulder to elbow | L_UA | SELECTION REQUIRED | HR-V0 R55 bench candidate is 193.025 mm because of corrected exact frame/adapter offsets; it does not define HR-30 proportions |
| Elbow to wrist | L_FA | 145 mm | 135–155 mm |
| Wrist to fingertip | L_H | 75 mm | 65–85 mm |
| Shoulder-axis spacing | W_S | 220 mm | 210–240 mm |
| Hip-axis spacing | W_H | 125 mm | 115–140 mm |
| Foot length | L_F | 180 mm | 170–195 mm |
| Foot width | W_F | 85 mm | 80–100 mm |

## Packaging zones

- Head: 170 W × 145 D × 155 H mm maximum; camera baseline and ventilation shall not enlarge total height.
- Chest: 240 W × 145 D × 190 H mm maximum; compute is removable from the rear without removing shoulders.
- Pelvis: 175 W × 130 D × 90 H mm maximum; primary restraint attachment is metal-to-metal.
- Hands: 70 W × 45 D × 85 L mm maximum with all pinch points covered.

## CAD deliverables for design freeze

The master assembly shall report total mass, center of mass in neutral and worst reach, inertia tensors by link, swept envelopes, cable minimum-bend radii, tool access, fastener access, hard-stop clearances, guard clearances, and restraint-load paths. A 1:1 dimensioned side/front elevation PDF must be reviewed before detailed joint parts are released.
