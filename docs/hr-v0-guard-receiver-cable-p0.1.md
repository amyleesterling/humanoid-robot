# HR-V0 guard, receiver and moving-cable architecture P0.1

**PRELIMINARY—SPACE RESERVATION AND EVIDENCE PLAN ONLY. NOT APPROVED FOR FABRICATION OR ENERGIZATION.**

Date: 2026-08-06  
Requirements: `SAFE-004`, `SAFE-010`, `SAFE-011`, `MECH-001`  
Risks: `R-001`, `R-002`, `R-022`, `R-034`

> **R126 role correction:** every P0.1 reference to the floor `receiver` or fixed catch tray means the **object catch only**. `HR-V0-COLLAPSE-ENV-P0.1` shows that its top at `Z=26 mm` is 114 mm below the controlled arm-envelope bottom. It receives zero arm-support, energy, impact or load credit. A separate passive arm receiver or accepted stop-supported resting architecture remains required.

## Protective boundary

HR-V0 powered tests require a fixed enclosure around the entire arm, gripper, receiver and payload-drop region. The preliminary model uses five tool-removable panels—front, rear, left, right and top—plus a fixed catch tray. A panel may be removed only after the applicable service disconnect is open, absence of actuator energy is verified, and restart is controlled. No door switch or guard interlock is selected or credited. During a test, all panels are installed and the separate 600 mm controlled exclusion boundary remains in force.

The emergency stop, RESET and ARM controls remain outside the enclosure. RESET and ARM do not command motion. A camera may observe the enclosed test, but a camera is not a protective device.

## Preliminary envelope derivation

The generated study uses the current shoulder datum 500 mm above the bench and the controlled 360 mm maximum shoulder-to-object-center reach. The 70 mm maximum object dimension contributes a 35 mm worst-direction half-extent.

| Term | Value | Status |
|---|---:|---|
| Maximum object-center reach | 360 mm | controlled requirement; must be inspected |
| Maximum object half-extent | 35 mm | derived from the 70 mm object ceiling |
| Stopping-travel space reservation | 25 mm | **provisional; not measured** |
| Guard-clearance space reservation | 25 mm | **provisional; access-probe selection required** |
| Build/calibration/tolerance reservation | 5 mm | **provisional; stack not closed** |
| Preliminary radial envelope | 450 mm | derived space claim only |

`360 + 35 + 25 + 25 + 5 = 450 mm`.

This produces a preliminary 900 mm internal width and 950 mm internal height. Internal depth is provisionally 400 mm. These dimensions reserve space; they are not safety distances or acceptance limits. The released enclosure must use the measured union of three-dimensional swept volume, stopping travel for every permitted mode and fault, maximum payload extent, cable/service volumes, build and calibration tolerance, and the selected minimum clearance. If any measured term exceeds the reservation, the enclosure grows.

Generated evidence under `cad/hr-v0/generated/safety-enclosure/` includes:

- a readable front/plan SVG;
- a non-fabrication-release STEP envelope;
- the 14-row assumption table; and
- five moving-cable datum zones.

## Catch and receiver

The preliminary catch space is 820 x 320 mm with 50 mm walls under the guarded workspace. The modeled 3 mm bottom and 6 mm panel values are provisional geometry only. Exact material grade, sheet thickness, support spacing, frame, fasteners, edge treatment, fire behavior, cleaning, impact capacity and retention are `SELECTION REQUIRED`.

The two operational receiver nests remain adjustable and `DESIGN REQUIRED` until the released pickup/place poses and inverse-kinematic solutions are frozen. The catch must remain effective even if a nest, pad or payload is absent. It must contain the controlled 100 g foam object after commanded opening, gripper fault and actuator-power loss from every released pose. It is not credited to contain an actuator, metal link or other detached high-energy component; the outer guard and mechanical retention/proof design must address those hazards separately.

Execute `TEST-DROP-001` with the controlled record template. Reference foam construction, dimensions, mass tolerance, release heights, trial count, rebound/slide limits and damage criteria remain `SELECTION REQUIRED`.

## Moving-cable zones

The dashed route in `HR-V0_cable_route_datums.svg` is a centerline space study, not a harness drawing. It divides the route into:

1. `CR-001`: fixed base entry to the J1 service loop;
2. `CR-002`: upper-link neutral route zone;
3. `CR-003`: J2 service loop;
4. `CR-004`: forearm neutral route zone; and
5. `CR-005`: gripper pigtail to its first retained clamp.

The upper-link and forearm studies reserve a line from local x = 35 to 125 mm at local z = +28 mm, just beyond the 22 mm link half-width. The out-of-plane coordinate, bundle diameter and final clamps remain open. The 50 mm hard-stop contact-radius study is a keep-out warning, not a cable-loop radius.

Before actuator connection, freeze the exact cable and connector parts, conductor functions, bundle diameter, manufacturer minimum bend radius, allowable torsion/tension, clamp family/spacing, strain relief, abrasion sleeve, mass allocation and service method. Articulate the exact unpowered assembly through every individual and combined mechanical-limit case under `INSPECT-CABLE-001`. No cable may carry connector load, rub an edge, enter the hard-stop or guard-contact path, obstruct service access, or become the first motion limit.

## Required closure evidence

1. Complete 3D kinematic/swept-volume model for the frozen assembly, gripper, payload and harness.
2. Measured maximum stopping travel for controlled stop, E-stop, watchdog loss, communication loss and relevant faults in every worst pose.
3. Released access probe, clearance, measurement uncertainty and acceptance rationale.
4. Exact panel/frame/fastener/receiver materials and calculations, including impact and retention.
5. Executed `INSPECT-GUARD-001`, `INSPECT-CABLE-001`, and `TEST-DROP-001` records.
6. Guard and receiver proof/impact evidence plus post-test inspection criteria.
7. Site footprint, bench survey, anchoring and service-isolation approval.
8. Qualified mechanical and functional-safety review of the frozen configuration.

The preliminary envelope may be used for site planning and collision-study development only. It is not a cutting list, panel drawing, purchase specification, safety distance, or permission to connect an actuator.
