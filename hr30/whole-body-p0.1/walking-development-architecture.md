# HR-30 standing and walking-development architecture P0.1

**PRELIMINARY - CONFIGURATION AND PACKAGING CAD ONLY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, POWERED TESTING, MOTION, OR ENERGIZATION**

The whole body has six commanded axes per leg: hip yaw/roll/pitch, knee pitch, and ankle pitch/roll. Hip pitch reserves 1.5:1, knee and roll axes reserve 2.0:1, and ankle pitch reserves 2.5:1 timing reductions with dual-supported 12 mm outputs and output encoders. Each foot is 90 x 145 mm with four-corner force sensing and a replaceable compliant sole. The active tether-first planning dynamics mass is 10.465 kg with neutral COM Z=0.346 m; these are candidate-volume and allocation values, not measured properties. The separate 11.930 kg onboard-envelope case retains rejected-pack packaging evidence and is not an active power configuration.

Control layers are: embedded actuator current/velocity loops; a deterministic local motion controller for joint interpolation, state estimation, support-polygon checks and limits; a separately powered watchdog/permit path with zero safety credit until validated; and a Raspberry Pi/OpenAI conversational layer that can request only named behaviors. Loss or staleness of the conversational layer never becomes a motion request.

Development sequence:

1. **S0 — unpowered/suspended:** verify axes, hard stops, cable sweep, mass, COM, encoder sign and restraint clearances.
2. **S1 — individually powered/suspended:** one joint at a time under current and travel limits; characterize torque, decay, regeneration and thermal behavior.
3. **S2 — restrained double support:** feet on force plates, overhead restraint carrying no nominal weight; establish stand preparation and power-loss capture.
4. **S3 — weight transfer:** slow lateral/fore-aft COM shifts within a measured support margin; no foot lift.
5. **S4 — tethered step initiation:** unload one foot, lift <=10 mm, replace it at the same location, then arrest and inspect.
6. **S5 — tethered capture steps:** predeclared <=50 mm steps on a level guarded surface with stopping and recovery envelopes.
7. **S6 — repeated tethered walking:** only after thermal, power, bus-latency, state-estimation and restraint results close.
8. **S7 — untethered walking:** future program gate; prohibited by P0.1.

The fall-restraint architecture is a rated overhead gantry, swivel, energy-limiting element and torso/pelvis harness attached to a dedicated structural interface. It must prevent head/floor contact throughout the development envelope without becoming a lifting command or destabilizing tether. Exact working-load limit, dynamic arrest load, attachment geometry and qualified inspection remain selection required.

<!-- HR30-POSE-P01-START -->

## Articulated P0.1 pose set

The package now carries 8 generated full-body configurations rather than prose-only stages, including mirrored lift and capture-step candidates for both legs. Joint targets are in `pose-joint-targets.csv`; transformed COM, support polygons, foot clearance and placement are in `pose-support-metrics.csv`; and each pose has STEP and GLB geometry. The minimum primary-foot COM margin in this set is **23.1 mm**. This is a rigid-link kinematic screen using provisional inertial data—not a zero-moment-point, contact-force, compliance, actuator, trajectory or balance validation.

| Pose | Stage | Support | COM margin | Swing clearance | Forward placement |
|---|---:|---|---:|---:|---:|
| Neutral double support | S2 | DOUBLE | 35.8 mm | 0.0 mm | 0.0 mm |
| Crouched double support | S2 | DOUBLE | 37.7 mm | 0.0 mm | 0.0 mm |
| Left weight transfer | S3 | DOUBLE | 23.1 mm | 0.0 mm | 0.0 mm |
| Right foot lift | S4 | L SINGLE | 23.2 mm | 6.8 mm | 1.0 mm |
| Right capture-step candidate | S5 | L SINGLE | 23.4 mm | 17.2 mm | 40.7 mm |
| Right weight transfer | S3 | DOUBLE | 24.6 mm | 0.0 mm | 0.0 mm |
| Left foot lift | S4 | R SINGLE | 24.7 mm | 6.8 mm | 1.0 mm |
| Left capture-step candidate | S5 | R SINGLE | 24.9 mm | 17.2 mm | 40.7 mm |

<!-- HR30-POSE-P01-END -->

<!-- HR30-COLLISION-P01-START -->

## Nominal self-collision result

All 8 articulated poses have zero common volume across every checked nonadjacent link pair. The smallest nominal clearance is **10.00 mm**. Pairs below 5.0 mm remain packaging holds; the complete pair register is `whole-body-collision-register.csv`. Tolerance, covers, cables, tracking error and physical motion are not validated.

<!-- HR30-COLLISION-P01-END -->
