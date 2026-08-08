# HR-V0 gripper architecture P0.2

Document ID: **HR-V0-GRIP-P0.2**

Source-control pass: **R71**

Status: **PRELIMINARY - NOT APPROVED FOR FABRICATION, MOTION, OR ENERGIZATION**

Requirement links: `GRIP-001`, `GRIP-002`, `SAFE-004`, `SAFE-006`, `MASS-002`

## Controlled candidate

HR-V0 uses one proposed ROBOTIS `XM430-W350-T` actuator and the gripper mechanism subset allocated from the orderable `OpenMANIPULATOR-X Frame Set RM-X52`, ROBOTIS SKU `905-0023-000`. The exact allocation is controlled in `bom/hr-v0-gripper-kit-contents.csv`; the parent kit contains other manipulator parts and its complete shipping mass must not be assigned to the gripper.

The manufacturer publishes a 20-75 mm gripper stroke for OpenMANIPULATOR-X. Project Button's controlled object envelope is 40-70 mm in each principal dimension; the exact released grip axis and installed padded opening remain unverified. The project does not claim the manufacturer's whole-manipulator 500 g payload as a gripper force or HR-V0 payload rating. The object mass remains no more than 100 g.

## Exact official geometry now controlled

R71 freezes the current official ROBOTIS OpenMANIPULATOR source at exact commit `9187eca0920458be04d2399906388f55242f81f1`. The controlled folder contains:

- `link5.stl`, the fixed gripper-carrier collision/visual mesh;
- `gripper_left_palm.stl` and `gripper_right_palm.stl`;
- `open_manipulator_x.urdf`, including the two prismatic palm joints; and
- the upstream `LICENSE`.

Hashes and exact raw URLs are recorded in `cad/vendor/robotis/vendor-manifest.csv` and repeated in the generated source-integrity register. `cad/hr-v0/generated/gripper-integration-p0.2/HR-V0_gripper-reference-viewer.html` is a responsive interactive top-view guide derived from the exact mesh vertices and official URDF axes. The static SVG, source register, three checked poses, parameterized mass/load table and seven integration holds are in the same folder.

This advances source traceability, not fabrication readiness. The public files are triangulated collision/visualization meshes and a simulation URDF, not complete native manufacturing drawings for the crank, rods, bushes, rails, brackets, pads, fasteners or guard. No mesh volume is converted to mass. The URDF's one-gram palm inertias are explicitly treated as placeholders and receive no physical mass credit.

The URDF puts the left and right joint origins at X=81.7 mm and Y=+/-21.0 mm, uses opposing Y axes, and limits each joint to -11 through +20 mm. Exact mesh checks give 0.059329 mm, 19.939267 mm and 59.106467 mm closest palm-mesh distance at the lower, neutral and upper URDF positions. These values are not certified jaw openings and are not substituted for the published 20-75 mm stroke. The received mechanism, installed pads and object range must be measured and reconciled.

## Distal mechanical interface

The controlled ROBOTIS `FR12-H104K.stp` supports a selected four-hole subset on a 24 x 12 mm rectangle on the frame broad face. Generated `MV0-FC03` files provide a nonstructural fit check. Execute `INSPECT-MECH-008` against the received frame and record all four positions, flat seating, fastener access and photographs.

The exact transform between the received H104 interface and the official URDF `link5` parent frame is not yet proven. `GRH-002` therefore blocks merging the reference gripper into the controlled P0.7 arm assembly for collision or fabrication credit. The exact fastener part, length, grade, engagement, torque, locking, process tolerance, guard clearance and structural proof remain `SELECTION REQUIRED`.

## Guard and human-contact boundary

The crank arm, link rods, rail blocks, actuator/frame interface and their reachable pinch or shear zones require a fixed local cover. Only the two broad compliant object-contact pads may enter the receiver opening. The outer fixed shield and 600 mm controlled test boundary remain mandatory. HR-V0 performs fixture-to-fixture foam-block transfer only; a person must never offer a hand or receive the object from the powered mechanism.

The guard CAD, material, thickness, attachment, access-probe choice, retained clearances, swept envelope and removal-interlock policy remain `DESIGN REQUIRED`. `INSPECT-GRIP-001` cannot pass until those items are frozen and the received mechanism is assembled in the exact controlled configuration. The R71 mesh envelope is a guard-design input, not a released guard.

## Force and power-off validation

Do not derive grip force from XM430 stall torque. `TEST-GRIP-001` must measure force across the released object range with a calibrated load cell and must establish the lowest current limit that retains the reference 100 g foam object through the released motion. The force/current acceptance value remains `SELECTION REQUIRED` until the reference foam, permanent-compression/tear criterion, retention acceleration, repeatability sample count and margin are released.

Power-off and commanded-open tests must show where the object falls and confirm that a fixed receiver or catch contains it. No powered gripper test may begin before the guard, receiver, current ceiling, catch tray and abort rules are approved for the controlled fixture.

## Mass and load closure

The gripper actuator belongs in `V0M-014`; the mechanism, pads, guard and retention belong in `V0M-015`; and gripper fasteners, connector, cable and moving-harness share belong in `V0M-016`. This corrects P0.1's stale `V0M-011` / `V0M-012` references.

The active P0.7 ledger has a 692.758 g known/CAD-estimated subtotal against the 750 g screen, leaving 57.242 g for **all** unresolved moving frames, hardware, bumper, gripper mechanics and cables. The nonselected R70 relief study would increase that incomplete headroom to 115.225 g, but it is not the controlled geometry. `gripper-mass-load-sensitivity.csv` shows incremental gravity terms for parameterized gripper mass at the ledger radii; it does not assign actual mass or reserve the total headroom for the gripper. Every received item must be weighed and reconciled against the assembled measurement without omission or double counting.

## Open integration holds

The machine-readable `gripper-integration-holds.csv` keeps all seven items open:

1. complete mechanism manufacturing definition or received dimensional metrology;
2. H104-to-URDF carrier registration;
3. usable opening calibration with pads installed;
4. measured mass, center of mass and inertia closure;
5. released guard and receiver;
6. calibrated force/current and power-off/drop behavior; and
7. exact fasteners, cable route, strain relief and wear evidence.

## Evidence required to close

1. Received-kit record for all `GKC-001` through `GKC-020` rows.
2. Executed `MV0-FC03` physical-fit record and approved H104-to-carrier transform plus fastener/tolerance stack.
3. Complete mechanism definition from manufacturer evidence or controlled received-part metrology.
4. Released guard and receiver CAD with access, retention and drop tests.
5. Measured mechanism, guard, cable and assembled-gripper mass/COM evidence.
6. Calibrated grip-force/current/foam-compression results across the released range.
7. Power-off containment, cable-flex, wear, fastener-retention and proof evidence.
8. Independent qualified mechanical and electrical review of the frozen configuration.

## Primary manufacturer evidence

- ROBOTIS OpenMANIPULATOR-X specification, rechecked 2026-08-07: https://emanual.robotis.com/docs/en/platform/openmanipulator_x/specification/
- ROBOTIS OpenMANIPULATOR-X assembly instructions, rechecked 2026-08-07: https://emanual.robotis.com/docs/en/platform/openmanipulator_x/assembly/
- ROBOTIS official OpenMANIPULATOR repository, exact source commit retrieved 2026-08-07: https://github.com/ROBOTIS-GIT/open_manipulator/tree/9187eca0920458be04d2399906388f55242f81f1
- ROBOTIS OpenMANIPULATOR-X Frame Set RM-X52, SKU `905-0023-000`, rechecked 2026-08-06: https://www.robotis.us/openmanipulator-x-frame-set-rm-x52/
- ROBOTIS XM430-W350 e-Manual, rechecked 2026-08-06: https://emanual.robotis.com/docs/en/dxl/x/xm430-w350/
- Controlled manufacturer files and hashes: `cad/vendor/robotis/vendor-manifest.csv`.

The architecture and test method may inform HR-30, but the full-body hand geometry, mass, reach, fall behavior and human-facing risks require a separate change-impact review and validation.
