# HR-V0 gripper orderable-subassembly acquisition correction

Document ID: **HR-V0-GRIP-ACQ-P0.2**
Date: 2026-08-08
Parent: `HR-V0-GRIP-CAD-ACQ-P0.1`
Requirements: `GRIP-002`, `MECH-005`, `MASS-002`
Verification: `AUDIT-GRIP-002`
Status: **PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, MOTION, OR ENERGIZATION**

## Correction

ROBOTIS currently offers `FR12-G101GM Set`, SKU `903-0256-300`, as a **gripper frame set** for the DYNAMIXEL X430 series. The manufacturer's package list contains `FR12-E170GM` x1, `FR12-E171GM` x1, `WB M2x3` x12, `FHS M2.5x14` x6 and spacer ring x6. It explicitly excludes the idler. For XH430/XM430, ROBOTIS requires the separate `HN12-I101 Set`, SKU `903-0240-000`.

That evidence does not establish that FR12-G101GM contains the complete HR-V0 mechanism. The page does not enumerate the two palms, two link rods, four flange bushes, crank arm, two rail blocks, left/right rail brackets, pads, cable, guard, complete fastener allocation, assembly mates, tolerances, installed mass or H104 transform controlled by the current design. The official drawing index exposed by the product link did not provide a matching `FR12-G101GM`, `FR12-E170GM` or `FR12-E171GM` file during the 2026-08-08 verification.

Therefore:

- FR12-G101GM is **rejected as the sole HR-V0 gripper-mechanism source**.
- HN12-I101 is an exact required supplement if that frame-set route is ever reconsidered, but it is not selected or released.
- The proposed RM-X52 parent-kit route remains the current acquisition candidate because it enumerates the complete mechanism subset in `bom/hr-v0-gripper-kit-contents.csv`.
- No purchase, cart, order, supplier contact, assembly or powered work is authorized.

The controlled comparison is `bom/hr-v0-gripper-acquisition-candidate-p0.1.csv`. The source claims and their limits are in `references/gripper/robotis-gripper-orderable-source-register-p0.1.csv`.

## Receiving and metrology hold

If a program owner later authorizes purchase of the retained exact parent kit, it must remain quarantined until `INSPECT-GRIP-001` reconciles every labeled and unlabeled article to the kit register. Before integration, `AUDIT-GRIP-002` must establish:

1. complete mechanism part count and identity;
2. native or measured geometry and model-to-article residuals;
3. all six H104-to-carrier transform quantities and tolerances;
4. installed mass, local center of mass and moving envelope;
5. exact fastener, thread, engagement, torque, locking and reuse definition;
6. usable opening, cable routing and service access;
7. fixed guard and compliant contact-pad definition; and
8. physical force/current, wear, retention and power-off-drop evidence.

Every numerical result remains **SELECTION REQUIRED** until controlled physical evidence and qualified mechanical review are accepted.

## Primary-source record

- ROBOTIS, [FR12-G101GM Set](https://www.robotis.us/fr12-g101gm-set/), live web page with no displayed document revision, accessed 2026-08-08.
- ROBOTIS, [HN12-I101 Set](https://www.robotis.us/hn12-i101-set/), live web page with no displayed document revision, accessed 2026-08-08.
- ROBOTIS, [DYNAMIXEL-X compatibility chart](https://en.robotis.com/service/compatibility_table.php?cate=dx), live chart with no displayed document revision, accessed 2026-08-08.
- ROBOTIS, [Frame drawing index](https://en.robotis.com/service/downloadpage.php?ca_id=7030), live index with no displayed document revision, accessed 2026-08-08.
- ROBOTIS, [OpenMANIPULATOR-X assembly page](https://emanual.robotis.com/docs/en/platform/openmanipulator_x/assembly/), live e-Manual page with no displayed page revision, accessed 2026-08-08.

Commerce price, stock and weight fields are deliberately excluded from engineering selection, mass and availability credit.

## Release boundary

This correction prevents an incomplete frame set from being mistaken for a buildable gripper. It closes no `GRH-*` hold and does not make HR-V0 buildable or ready to energize. `GRH-001`, `GRH-002`, `MECH-005`, `MASS-002`, guarding, grip-force characterization, physical verification, qualified review and every work authorization remain open.
