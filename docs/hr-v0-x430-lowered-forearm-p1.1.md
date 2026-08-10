# HR-V0 X430 lowered-forearm candidate P1.1

> **PRELIMINARY — NOT APPROVED FOR QUOTATION, PROCUREMENT, FABRICATION, ASSEMBLY, MOTION, CONNECTION, OR ENERGIZATION.**

Configuration identifier: `HR-V0-ARM-ARCH-P1.1-X430-LOWERED-FOREARM-CANDIDATE`

## Decision

P1.1 is a nonselected mechanical comparison. P0.7 remains the controlled architecture, P1.0 remains the prior X430 comparison, and X430 is not selected. No quote, purchase, fabrication, assembly, connection, motion or energization is authorized.

P1.0 improved the X430-to-moving-striker clearance at nominal stop contact to 2.491516 mm, but left only 1.491516 mm for all manufacturing, registration, play, fastener, deformation and measurement effects while preserving a 1.000 mm physical residual. Its local upper M5 boss also left only 1.300 mm nominal countersink-to-profile land, below the existing 2.000 mm project screen.

## Geometry correction

P1.1 changes the forearm-side interface as one rigid subassembly:

- the J2 axis remains at Y=191.550 mm;
- the FR12-H101 moving face and striker origin remain at Y=219.550 mm;
- the FR12 frame holes remain X=±12, Z=±6 mm;
- the forearm 20-2040 member, its two M5 axes, the distal adapter and H104 datum move 7.000 mm downward;
- the member axes become X=0, Z=+3 and −17 mm;
- the moving-adapter base becomes Z=−27…+13 mm;
- the external stop lobes retain their P1.0 world coordinates and nominal contact surface;
- nominal first metal contact remains 117.999977°.

The 11.400 mm maximum countersink envelope now has 4.300 mm nominal land to both the upper and lower profile edges. The closest M5-to-FR12 feature-envelope gap is 5.116 mm. These are nominal design screens; supplier DFM, material, FAI, fit, preload and proof remain open.

## Complete changed-solid certificate

The forearm offset changes four solids, so P1.1 does not reuse P1.0's nine-pair update:

- 30 P0.9 certificates are retained only where both solids remain identical;
- the retained P0.9 summary is SHA-256 bound;
- all 39 pairs involving the changed striker, forearm member, distal adapter or H104 are recomputed;
- the complete commanded-domain certificate still contains 69 pair groups;
- the domain remains J1 −20°…70° and J2 15°…115°;
- the general nominal rigid-solid floor remains 0.750 mm;
- the X430-to-striker pair has a separate 4.750 mm requirement.

Results:

- 140 adaptive interval cells;
- 106 exact B-Rep distance calls;
- 4.798163 mm guaranteed nominal X430-to-striker clearance through the commanded domain;
- 1.313579 mm minimum guaranteed nominal clearance among all 69 pairs.

The certificate excludes manufacturing variation, fasteners, cables, connectors, guards, deformation, compliance and stopping travel.

## Stop-sequencing allocation

Exact nominal results are:

- X430-to-striker clearance at the 115° software limit: **4.875499 mm**;
- X430-to-striker clearance at nominal 118° metal contact: **4.369402 mm**;
- stop-pair gap at 115°: 1.913782 mm;
- required physical residual at contact: **1.500 mm**;
- available combined adverse-variation budget: **2.869402 mm**.

P1.1 allocates acceptance limits as follows:

| Contributor | Maximum adverse contribution |
|---|---:|
| Adapter profile and thickness | 0.250 mm |
| Frame/actuator registration and runout | 0.500 mm |
| Joint play and calibration | 0.500 mm |
| Fastener projection | 0.250 mm |
| Stop deformation and bumper behavior | 0.750 mm |
| Measurement uncertainty | 0.250 mm |
| **Worst-case sum** | **2.500 mm** |

The nominal allocation margin is 0.369402 mm. Every allocation is an **unverified maximum acceptance limit**, not a measured result or accepted tolerance. Failure to demonstrate any individual limit, the worst-case sum, or the 1.500 mm residual rejects P1.1.

## Mass boundary

- P1.1 moving-striker CAD estimate: 58.282 g;
- incomplete known/CAD-estimated moving subtotal: 583.138 g;
- provisional unresolved headroom to the 750 g screen: 166.862 g.

The subtotal omits received fasteners, bumper, complete gripper mechanics, connectors, strain relief and moving harness. Complete assembled mass, COM and inertia remain unmeasured. The 7 mm offset also changes the moving mass distribution, so the prior partial load screen cannot release P1.1.

## Open evidence and rejection conditions

Eight architecture holds remain OPEN and four PARTIAL. P1.1 is rejected unless all of the following are closed against the exact configuration:

1. supplier-accepted material, thickness, profile, finish, edge and inspection definition;
2. calibrated FAI demonstrating the profile, feature positions, thickness and edge lands;
3. exact M5 and M2.5 stacks with received seating, engagement, access, preload, locking and projection evidence;
4. received X430/FR12 registration, runout, play and calibration measurements with uncertainty;
5. complete cable, connector, strain-relief, gripper and guard swept envelopes;
6. accepted structural, impact, prying, fatigue and deformation evidence;
7. selected bumper/retention plus measured stopping, rebound and overtravel;
8. complete mass/COM/inertia and actuator torque/current/thermal evidence;
9. synchronized firmware, electrical and configuration identifiers; and
10. independent mechanical, electrical, controls and functional-safety disposition.

## Controlled evidence

- generator: `tools/generate_hr_v0_x430_lowered_forearm.py`;
- fail-closed checker: `tools/check_hr_v0_x430_lowered_forearm.py`;
- native/generated package: `cad/hr-v0/generated/arm-architecture-p1.1-x430-lowered-forearm/`;
- interactive guide: `release/hr-v0/arm-architecture-p1.1-x430-lowered-forearm/index.html`;
- independent review request: `docs/reviews/2026-08-08-x430-lowered-forearm-p1.1-independent-review-request.md`.

Passing automated CAD checks proves only the stated nominal model and internal allocation arithmetic. It is not fabrication, motion, functional-safety or energization approval.
