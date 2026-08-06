# HR-30 Full-Body Product Specification

Document ID: HR-PROD-030  
Revision: 0.1  
Program baseline: HR-30-SYS-R0.2  
Status: Product baseline; detailed design not released

## Product intent

HR-30 is a compact social and manipulation research robot with a nominal standing height of **762 mm (30.0 in)**. It should read visually as a small friendly robot, not as a realistic child. Its first useful configuration is stationary: active face/head orientation, waist, two arms, and two soft grippers on a bolted pedestal at the final standing height.

“Child-sized” describes scale only. It does not imply toy classification, unsupervised access, safe physical contact, or permission to operate around children.

Current operating boundary: **adult-operated experimental robotic machinery; not a toy; not approved for unsupervised consumer use.** This is a conservative project rule, not a legal classification, conformity assessment, certification, or permission to energize. Final product classification, jurisdiction, intended user population, and applicable standards remain `SELECTION REQUIRED` before procurement or public operation.

## Controlled envelope

| Property | Target | Hard limit |
|---|---:|---:|
| Overall height, neutral pose | 762 mm | 740–800 mm by configuration |
| Overall mass, tethered | 8.0 kg | 10.0 kg |
| Shoulder width, shell | 250 mm | 280 mm |
| Hip width, shell | 155 mm | 180 mm |
| Maximum arm span | 900 mm | 980 mm |
| Maximum single-arm reach from shoulder axis | 360 mm | 390 mm |
| Maximum hand payload | 100 g in human-facing mode | 250 g guarded engineering mode |
| Automatic hand speed | 0.15 m/s | 0.20 m/s guarded engineering mode |
| External edge radius | 5 mm preferred | 3 mm minimum |
| Nominal center-of-mass height | 410 mm | 460 mm maximum in neutral pose |

Mass above 8 kg consumes fall-energy and actuator margin and requires a formal change review. The 10 kg value is an absolute stop, not a design target.

## Dimension datums

Neutral pose uses the floor plane as Z=0 and the sagittal center plane as X=0.

| Datum | Height above floor |
|---|---:|
| Ankle pitch axis | 45 mm |
| Knee pitch axis | 210 mm |
| Hip pitch axis | 380 mm |
| Waist yaw axis | 425 mm |
| Shoulder pitch axes | 590 mm |
| Neck pan axis | 650 mm |
| Top of shell | 762 mm |

Nominal segment lengths are ankle-to-knee 165 mm, knee-to-hip 170 mm, shoulder-to-elbow 150 mm, elbow-to-wrist 145 mm, and wrist-to-fingertip 75 mm. These are robot proportions, not copied child anthropometry.

## Degrees of freedom

### HR-30A: active upper body, 13 DOF

| Region | Per side | Total | Candidate actuator class |
|---|---|---:|---|
| Head | pan, tilt | 2 | compact X-series, current limited |
| Waist | yaw | 1 | XM540-class |
| Shoulders | pitch, roll | 4 | XM540-class |
| Elbows | pitch | 2 | XM430/XM540 class, decided by V0 data |
| Wrists | rotation | 2 | XM430-class |
| Grippers | parallel open/close | 2 | XM430-class with compliant transmission |

HR-30A is bolted through the pelvis datum to a steel pedestal. Lower-body shells may be fitted for appearance only if they are non-load-bearing and cannot be mistaken for powered legs.

### HR-30B: supported full body, 25 DOF maximum

Each leg adds hip yaw, hip roll, hip pitch, knee pitch, ankle pitch, and ankle roll. Leg joints remain unpowered or mechanically locked until their individual test articles pass. At all times the robot is carried by a rated overhead restraint or rigid support frame that prevents floor impact.

### HR-30C, HR-30D, and HR-30W

Powered stance, tethered dynamic walking, and untethered walking are required successive releases. No upper-body actuator selection is automatically approved for leg service. Leg joint selection is controlled by the walking-system specification and instrumented joint/leg prototypes.

## Appearance and interaction constraints

- The face is stylized and clearly robotic; no photorealistic skin or imitation-child presentation.
- Status is visible from three meters: white/blue ready, amber setup, red fault, and actuator-power-off indication.
- Speakers cannot trigger movement directly.
- Cameras have a physical privacy indicator driven from camera power, not software alone.
- Fingers are broad, compliant, replaceable, and unable to form a narrow scissor point.
- Covers are removable only with tools and cannot expose a powered pinch point during normal operation.

## Capability releases

| Release | Capability | Required restraint |
|---|---|---|
| HR-V0 | one guarded arm, fixture handoff | bench mount + fixed shield |
| HR-30A | two-arm stationary interaction | bolted pelvic pedestal + controlled perimeter |
| HR-30B | full visual body, joint characterization | overhead fall restraint + guarded cell |
| HR-30C | powered supported stance | rated restraint taking full robot weight + guarded cell |
| HR-30D | dynamic level walking | slack overhead fall-arrest tether + guarded cell |
| HR-30W | untethered level walking | controlled access test area; no public or child access |

HR-30W completion is necessary for the program to claim “walks.” A robot carried by the tether, shuffling on a gantry, or supported by a boom does not satisfy that claim.
