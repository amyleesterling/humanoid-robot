# HR-V0 gripper native-source correction

Document ID: **HR-V0-GRIP-CAD-ACQ-P0.2**

Date: 2026-08-10

Parents: `HR-V0-GRIP-CAD-ACQ-P0.1`, `HR-V0-GRIP-ACQ-P0.2`, `HR-V0-GRIP-SRC-ROUTE-P0.4`

Requirements: `GRIP-002`, `MECH-005`, `MASS-002`

Verification: `AUDIT-GRIP-002`

Status: **PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION**

## Correction

The R72 statement that ROBOTIS download endpoint 690 terminated at an error page is historical. On 2026-08-10 the current official [OpenMANIPULATOR-X assembly page](https://emanual.robotis.com/docs/en/platform/openmanipulator_x/assembly/) linked endpoint `https://www.robotis.com/service/download.php?no=690`; its returned publisher HTML redirected to the public Onshape document:

`https://cad.onshape.com/documents/9442f03bd8ccac084fda9dd3/w/039e8dbd53e0782540ea5b0d/e/6f08aa8ac3d3e5b3054f7782`

The public viewer identified the document as **ROBOTIS OpenManipulator Chain**, workspace **Main**, shared by link and view only. It exposed a native gripper assembly plus separate Gripper Base, Bolts, Horn, Link and Palm workspaces. Their exact document/workspace/element identifiers are frozen in `cad/hr-v0/gripper-cad-source-correction-p0.2/onshape-element-register.csv`.

This corrects source availability, not build readiness. The link points to a mutable workspace rather than an immutable Onshape version. Anonymous view-only context menus did not expose an export command, and the unauthenticated document API returned HTTP 401. No STEP, Parasolid, drawing, feature history, material, tolerance, mass, fastener release or configuration-frozen native assembly was acquired.

## Controlled evidence now available

- The exact Onshape gripper assembly element is `ff13f6a0595abaecccea4081`; its public instance tree showed 57 instances and named the actuator, gripper parts and fastener instances.
- The five relevant native part-workspace elements and displayed part identities are source-bound in the element register.
- The official ROBOTIS GitHub commit `9187eca0920458be04d2399906388f55242f81f1`, dated 2026-08-05, remains frozen under `cad/vendor/robotis/open-manipulator-9187eca/`. Its palm/link5 meshes and URDF are reference geometry and kinematics only, not manufacturing CAD or physical-mass evidence.
- The official assembly page supplies assembly context and the current source link. It does not declare the mutable workspace to be a Project Button fabrication release.

## Configuration decision

The active `XM430-W350-T` / proposed OpenMANIPULATOR-X mechanism baseline is unchanged. It remains the preferred closure route only because it is consistent with current `GRIP-002` and avoids an unreviewed electrical/firmware branch change. It is not selected for purchase or assembly.

The XC330 branch remains an alternate feasibility study. The official [XC330-T288 e-Manual](https://emanual.robotis.com/docs/en/dxl/x/xc330-t288/) gives 6.5-12.0 V operation and 11.1 V recommended. The current [Mean Well GST280A12 specification](https://www.meanwell.com/Upload/PDF/GST280A/GST280A-SPEC.PDF) gives the 12 V model a +/-5% voltage tolerance, so the source may reach 12.6 V before application, wiring, transient and regeneration effects. Therefore the existing nominal 12 V actuator rail cannot be declared a direct XC330 supply. Selecting XC330 would require a separate source/regulator/protection/regen design and per-actuator current-scaling changes before any connection.

Neither branch is buildable. `configuration-decision.csv` records the current decision without changing the BOM, requirement, electrical baseline or firmware configuration.

## Closure route

1. Obtain an immutable Onshape version URL and publisher-authorized export of the complete gripper assembly and individual parts, or execute the already controlled received-kit metrology route.
2. Preserve original filenames, units, coordinate frames, version identity, license, byte counts and SHA-256 values.
3. Reconcile the export to the public assembly instance list and the exact received RM-X52 contents; identify every substituted or absent item.
4. Establish the complete H104-to-carrier transform, fastener stack, tolerances, material/process, moving envelope, cable route, mass/COM/inertia and fixed guard.
5. Execute receiving, dimensional, force/current/thermal, power-loss, wear, drop, collision and access-probe procedures with raw evidence.
6. Obtain independent configuration review and qualified mechanical/electrical/functional-safety dispositions before any applicable release gate may change.

## Remaining boundary

All twelve holds in `hold-register.csv` remain open. This correction closes only the stale claim that the official source link is broken. It does not close `GRH-001`, `GRH-002`, `GRIP-002`, `MECH-005`, `MASS-002`, any Sol R12 finding or any energization gate. No supplier was contacted, no account was used, no file was exported, no article was ordered or received, and no physical verification was executed.
