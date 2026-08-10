# R192 validation record

> **PRELIMINARY WRIST-INTEGRATION EVIDENCE ONLY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION**

Artifact: `HR-V0-XC330-WRIST-P0.1`
Date: 2026-08-10

## Executed source and geometry checks

- The ROBOTIS H104 STEP/PDF matched the controlled 229,070/72,806-byte records and SHA-256 values.
- CadQuery imported H104 as one solid with the expected bounds and 4,314.613722 mm3 nominal volume.
- Independent arithmetic reproduced the gripper-to-H104 Rx +90 degree / `(0,4.0,13.5)` mm transform, combined world Rx 270 degree / `(0,327.6,-13.5)` mm transform, object-center world Y 358.6 mm and 1.4 mm nominal reserve.
- Both native bridge STEP files parsed at 1,821.576112005 mm3; both STL companions existed.
- Twelve hole rows reproduced the observed H104 M2-tap axes and transformed S101/U-base PCD16 axes while retaining every fastener as `SELECTION REQUIRED`.
- Seven nominal contact rows reproduced zero positive-volume intersection and zero distance at the intentional contact faces.
- The endpoint-aligned 5-degree sweep covered 399 joint pairs including J1 `-20/+70` and J2 `15/115` degree endpoints; all samples had zero positive intersection against the encoded P0.7 fixed/upper bodies.
- Both integrated STEP files parsed and both GLBs carried valid `glTF` signatures.
- Mass arithmetic reproduced the 9.836511 g bridge-pair screen, 688.961224 g incomplete subtotal and 61.038776 g incomplete headroom.
- All 18 holds remained open, all release booleans remained false, the active ledger still named XM430, and zero requirement/gate/Sol closure was claimed.

Command:

`C:\Users\amyle\Documents\New project\.venvs\hr-v0-cad\Scripts\python.exe tools/check_hr_v0_xc330_wrist_integration_p01.py`

Result:

`HR-V0 XC330 wrist integration P0.1 check passed: exact H104 source, transform chain, 2 bridge parts, 7 nominal contacts, 399 sampled poses, calculations and 18 open holds verified`

## Visual QA

The interactive guide was loaded from a local HTTP origin in the in-app browser. Wide desktop and 390 x 844 mobile layouts were inspected. Both GLBs loaded and rendered coherently. Cards reflowed without horizontal overflow (`scrollWidth == clientWidth`); body/functional text remained 16 px and metadata 14 px; no user-facing text fell below 14 px.

## Repository validation

- The non-`pcbnew` standard sweep passed **136/136** checker programs after correcting the new generator's cross-platform DXF hashing and staging the controlled package.
- The KiCad 10.0.5 `pcbnew` sweep passed **13/13** checker programs.
- CAD validation passed over 4 historical custom-part artifacts, 3 fit coupons, **529 hash-bound generated artifacts** and 17 vendor references while retaining no active fabrication packet.
- Traceability passed over **81 requirements, 40 risks, 110 procedures and 57 release/walking-document references**.
- BOM structure passed over 91 system items and 17 evaluation-only lines while retaining **18 `SELECTION REQUIRED` groups** and no procurement-released complete machine BOM.
- The synchronized release-candidate manifest passed over **3,328 package files**. `EG-002` remains partial until merge and formal acceptance.
- The energization register retained **all 30 gates unresolved: 23 partial and 7 open**.

These digital passes verify modeled source/configuration consistency only. They do not change any physical or energization release state.

## Boundary

The checks do not verify received H104/gripper/bridge identity or dimensions, screw identity/seating/engagement/torque/locking, released bridge material/process/tolerance, static/fatigue strength, complete moving mass/COM/inertia, cable flex/strain relief, retained guarding, continuous collision clearance, grip force, current/thermal behavior, power-loss containment, physical proof, executed verification or qualified acceptance. No requirement, energization gate or Sol R12 blocker closes.
