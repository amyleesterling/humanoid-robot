# R191 validation record

> **PRELIMINARY INTERFACE EVIDENCE ONLY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION**

Artifact: `HR-V0-GRIP-XC330-P0.2`

Date: 2026-08-10

## Executed source and geometry checks

- Four archived manufacturer files matched controlled byte sizes and SHA-256 values.
- CadQuery imported the official XC330 as 15 solids and FPX330-S101 as one solid with expected bounds.
- The two exact frame transforms independently reproduced 0.000000 mm represented-axis residual and 0.000000000 mm3 positive-volume interference against the actuator.
- Seven project-owned custom STEP files parsed and all seven STL companions existed.
- Closed, mid and open assembly STEP files parsed; all three GLBs carried valid `glTF` signatures.
- The module 0.8 / 20-tooth / 20-degree involute arithmetic, 8.0 mm pitch radius and 0.150 mm pair-backlash candidate reproduced.
- Three poses reproduced the 40-76 mm hard and 38-74 mm nominal padded ranges plus 128.915504 degrees full travel.
- Mass arithmetic reproduced 679.124713 g incomplete subtotal and 70.875287 g incomplete headroom with all exclusions preserved.
- All 16 holds remained open, all release booleans remained false, the active ledger still named XM430, and zero requirement/gate/Sol closure was claimed.

Command:

`C:\Users\amyle\Documents\New project\.venvs\hr-v0-cad\Scripts\python.exe tools/check_hr_v0_xc330_gripper_interface_p02.py`

Result:

`HR-V0 XC330 gripper interface P0.2 check passed: 4 official source hashes, exact two-frame registration, 7 native parts, 3 poses, involute geometry, calculations and 16 open holds verified`

## Visual QA

The interactive guide was loaded from a local HTTP origin in the in-app browser. Wide desktop and 390 x 844 mobile layouts were inspected. The GLB rendered coherently; summary cards reflowed to one column on mobile; body/functional text remained 16 px and metadata 14 px; no user-facing text fell below 14 px.

## Repository validation

- The non-`pcbnew` standard sweep passed **135/135** checker programs.
- The KiCad 10.0.5 `pcbnew` sweep passed **13/13** checker programs.
- CAD validation passed over 4 historical custom-part artifacts, 3 fit coupons, **510 hash-bound generated artifacts** and 17 vendor references while retaining no active fabrication packet.
- Traceability passed over **81 requirements, 40 risks, 110 procedures and 57 release/walking-document references**.
- BOM structure passed over 91 system items and 17 evaluation-only lines while retaining **18 `SELECTION REQUIRED` groups** and no procurement-released complete machine BOM.
- The synchronized release-candidate manifest passed over **3,299 package files**. `EG-002` remains partial until merge and formal acceptance.
- The energization register retained **all 30 gates unresolved: 23 partial and 7 open**.

These digital passes verify modeled source/configuration consistency only. They do not change any physical or energization release state.

## Boundary

The checks do not verify received dimensions or fit, screw identity/seating/engagement/torque/locking, tolerance stack, material or print process, tooth-root form/strength/life, guide wear, guarding, grip force, current, thermal behavior, cable flex, power-loss containment, mass/COM/inertia, physical proof or qualified acceptance. No requirement, energization gate or Sol R12 blocker closes.
