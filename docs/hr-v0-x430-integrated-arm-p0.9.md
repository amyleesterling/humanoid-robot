# HR-V0 X430 integrated-arm comparison P0.9

> **PRELIMINARY — NOT APPROVED FOR QUOTATION, PROCUREMENT, FABRICATION, ASSEMBLY, MOTION, CONNECTION, OR ENERGIZATION.**

Configuration identifier: `HR-V0-ARM-ARCH-P0.9-X430-INTEGRATED-CANDIDATE`

## Decision

P0.9 is a complete shoulder-column-to-gripper-frame nominal CAD comparison, not a selected architecture. P0.7 remains controlled and XM430 is not selected. P0.9 does not authorize a quote, purchase, fabrication, assembly, connection, motion or energization.

This correction responds to the persistent Sol R12 finding that P0.8 supplied an isolated elbow comparison rather than a buildable machine. P0.9 joins the controlled P0.7 column, shoulder support, XM540 J1 and upper-link package to the corrected X430/FR12 J2 coordinates. It adds full-arm collision evidence, adaptive continuous nominal clearance, and explicit fastener/tolerance closure requirements. It still lacks the physical evidence necessary to select or build the branch.

## Exact integrated geometry

- J1 axis to J2 axis: **191.550 mm**.
- J2 axis to G1 H104 origin: **125.050 mm**.
- candidate object-center screen from J1: **345.000 mm**.
- X430 rear-case axes: local Z at X=±11 mm, Y=-32 mm.
- FR12-S102 registration: selected side axes plus a local Z shift of +21 mm, giving the 40.5 mm fixed-face offset established in P0.8.
- FR12-H101 moving face: 28 mm from J2 with selected link axes at X=±12 mm, Z=±6 mm.

The integrated STEP and GLB contain fifteen named/ordered solids: column, shoulder support, J1 package, upper-link package, corrected J2 package, forearm and H104 frame. Intentional frame/actuator assembly interfaces remain excluded only by exact named pair. The model does not contain connectors, cable service loops, strain relief, gripper mechanics, guard, bumper or manufacturing variation.

## Collision and continuous-clearance evidence

The full-arm sampled sweep contains **9,464** poses across J1 −20°…70° and J2 15°…118° at 1° increments. No positive nonintentional volume occurs through the 115° provisional software limit.

Sampling is not used as between-pose proof. The separate adaptive certificate covers every nonintentional solid pair over J1 −20°…70° and J2 15°…115°:

- 69 pair groups;
- 130 certified leaf cells;
- 85 exact B-Rep distance calls where bounding-box evidence was insufficient;
- required nominal clearance: 0.750 mm;
- minimum guaranteed nominal clearance: **0.862928 mm**;
- critical pair: X430 body versus moving striker adapter.

The certificate applies only to the exact nominal rigid solids through the software limit. It excludes tolerances, fastener projections, connectors, cables, strain relief, guards, deformation, compliance, stopping travel and received-part variation. It is not a physical-clearance, motion or safety approval.

## Positive stop

The nominal model reaches first metal contact at **117.999977°**, with a 115° provisional software limit. This is coordinate evidence only. No bumper is selected; no worst-case tolerance stack, stop load, local stress, fastening proof, stopping time, rebound, overtravel or as-built contact measurement exists. The nominal 3° interval is not a released stopping allowance.

## Mass and actuator screen

The arithmetic remains the P0.8 incomplete screen:

- incomplete known/CAD-estimated subtotal: **577.091 g**;
- provisional headroom to the 750 g ceiling: **172.909 g**;
- incomplete elbow 2.25× gravity screen: **1.104 N·m**;
- XM430 12 V relationship: **3.713 stall-endpoint ratio only**.

That is not mass closure or actuator selection. Received FR12 frames, exact fasteners, bumper, complete gripper mechanism, connectors, strain relief and moving harness remain absent. Assembled mass, center of mass and inertia are unmeasured. Continuous/cyclic torque, efficiency, temperature, speed, current, voltage drop and stopping performance are unproved.

## Fastener and tolerance controls

Four stack definitions now state the closure evidence without inventing order codes:

1. FR12-S102 to P09-C01: M2.5 interface, no bottoming, manufacturer-approved engagement, head/access clearance.
2. FR12-H101 to P09-C02: M2.5 through/nut concept, full nut engagement, moving-envelope and tool-access control.
3. 20-2040 to P09-C01/C02: M5 end-tap concept, flush seating, engagement, bottoming and edge-distance control.
4. X430 to FR12 frames: official accessory compatibility, received horn/idler seating, axial play/runout and cable-pinch evidence.

Every exact fastener remains **SELECTION REQUIRED**. The adapter thickness tolerance, frame hole/thread true position, stop-wing profile/clocking, joint axial play/runout and cable/guard swept envelope also remain **SELECTION REQUIRED**. Closing them requires controlled supplier drawings, received metrology, DFM, calibrated FAI, access trials, torque/preload rules, slip/prying/impact/fatigue analysis and physical proof.

## Hold disposition

The twelve R91 architecture holds remain. P0.9 leaves eight OPEN and four PARTIAL:

- `ELBH-002` exact-coordinate integration: PARTIAL;
- `ELBH-007` positive hard stop: PARTIAL;
- `ELBH-008` collision/cable/guard sweep: PARTIAL for nominal solids only;
- `ELBH-009` structural interfaces: PARTIAL because closure requirements now exist, but no stack or proof is accepted.

No hold is closed. Complete mass/COM/inertia, continuous/cyclic actuator performance, external current/protection, physical stop/stopping, cable/guard/tolerance geometry, structural proof, firmware/calibration binding, electrical synchronization and qualified architecture disposition remain prerequisites.

## Controlled evidence

- generator: `tools/generate_hr_v0_x430_integrated_arm.py`;
- fail-closed checker: `tools/check_hr_v0_x430_integrated_arm.py`;
- native/generated package: `cad/hr-v0/generated/arm-architecture-p0.9-x430/`;
- interactive guide: `release/hr-v0/arm-architecture-p0.9-x430/index.html`;
- independent review request: `docs/reviews/2026-08-08-x430-integrated-arm-p0.9-independent-review-request.md`.

The package must be independently reviewed and then supported by received hardware, calibrated measurements and controlled physical tests before any supersession or work authorization may be considered.
