# HR-V0 gripper architecture P0.1

**PRELIMINARY—NOT APPROVED FOR FABRICATION OR ENERGIZATION.**

Requirement links: `GRIP-001`, `GRIP-002`, `SAFE-004`, `SAFE-006`, `MASS-002`

## Controlled candidate

HR-V0 uses one proposed ROBOTIS `XM430-W350-T` actuator and the gripper mechanism subset allocated from the orderable `OpenMANIPULATOR-X Frame Set RM-X52`, ROBOTIS SKU `905-0023-000`. The exact allocation is controlled in `bom/hr-v0-gripper-kit-contents.csv`; the parent kit contains other manipulator parts and its complete shipping mass must not be assigned to the gripper.

The manufacturer publishes a 20–75 mm gripper stroke for OpenMANIPULATOR-X. Project Button requires only the 20–70 mm reference-object range; it does not claim the manufacturer's whole-manipulator 500 g payload as a gripper force or HR-V0 payload rating. The project payload remains one soft foam object no heavier than 100 g.

## Distal mechanical interface

The received ROBOTIS `FR12-H104K.stp` supports a selected four-hole subset on a 24 x 12 mm rectangle on the frame broad face. The candidate is rotated on `MV0-002` so the 12 mm spacing is longitudinal and the 24 mm spacing is transverse. Generated `MV0-FC03` DXF, STEP, STL and 1:1 A4 overlay files provide a nonstructural fit check.

This selection is not a fabrication release. Execute `INSPECT-MECH-008` against the received frame and record all four positions, flat seating, fastener access and photographs. Exact fastener part, length, grade, engagement, torque, locking, process tolerance, guard clearance and structural proof remain `SELECTION REQUIRED`.

## Guard and human-contact boundary

The crank arm, link rods, rail blocks, actuator/frame interface and their reachable pinch or shear zones require a fixed local cover. Only the two broad compliant object-contact pads may enter the receiver opening. The outer fixed shield and 600 mm controlled test boundary remain mandatory. HR-V0 performs fixture-to-fixture foam-block transfer only; a person must never offer a hand or receive the object from the powered mechanism.

The guard CAD, material, thickness, attachment, access-probe choice, retained clearances, swept envelope and removal interlock policy remain `DESIGN REQUIRED`. `INSPECT-GRIP-001` cannot pass until those items are frozen and the received mechanism is assembled in the exact controlled configuration.

## Force and power-off validation

Do not derive grip force from XM430 stall torque. `TEST-GRIP-001` must measure force across the released object range with a calibrated load cell and must establish the lowest current limit that retains the reference 100 g foam object through the released motion. The force/current acceptance value remains `SELECTION REQUIRED` until the reference foam, permanent-compression/tear criterion, retention acceleration, repeatability sample count and margin are released.

Power-off and commanded-open tests must show where the object falls and confirm that a fixed receiver or catch contains it. No powered gripper test may begin before the guard, receiver, current ceiling, catch tray and abort rules are approved for the controlled fixture.

## Mass and configuration closure

All mechanism pieces, pads, guard, fasteners, cable and strain relief belong in `V0M-011` or `V0M-012`. Every received item must be weighed and reconciled against the assembled gripper measurement without omission or double counting. The present 750 g moving-assembly screen has only provisional headroom and is not a pass.

## Evidence required to close

1. Received-kit record for all `GKC-001` through `GKC-020` rows.
2. Executed `MV0-FC03` physical-fit record and approved fastener/tolerance stack.
3. Released guard and receiver CAD with access, retention and drop tests.
4. Measured mechanism, guard, cable and assembled-gripper mass/COM evidence.
5. Calibrated grip-force/current/foam-compression results across the released range.
6. Power-off containment, cable-flex, wear, fastener-retention and proof evidence.
7. Independent qualified mechanical and electrical review of the frozen configuration.

## Primary manufacturer evidence

- ROBOTIS OpenMANIPULATOR-X specification, rechecked 2026-08-06: https://emanual.robotis.com/docs/en/platform/openmanipulator_x/specification/
- ROBOTIS OpenMANIPULATOR-X assembly instructions, rechecked 2026-08-06: https://emanual.robotis.com/docs/en/platform/openmanipulator_x/assembly/
- ROBOTIS OpenMANIPULATOR-X Frame Set RM-X52, SKU `905-0023-000`, rechecked 2026-08-06: https://www.robotis.us/openmanipulator-x-frame-set-rm-x52/
- ROBOTIS XM430-W350 e-Manual, rechecked 2026-08-06: https://emanual.robotis.com/docs/en/dxl/x/xm430-w350/
- Controlled manufacturer drawing, STEP and assembly-manual hashes: `cad/vendor/robotis/vendor-manifest.csv`.

The architecture and test method may inform HR-30, but the full-body hand geometry, mass, reach, fall behavior and human-facing risks require a separate change-impact review and validation.
