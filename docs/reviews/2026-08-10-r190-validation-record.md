# R190 validation record

> **PRELIMINARY FEASIBILITY EVIDENCE ONLY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION**

Artifact: `HR-V0-GRIP-XC330-P0.1`

Date: 2026-08-10

## Executed digital checks

- Official ROBOTIS STEP size and SHA-256 matched the controlled source manifest.
- CadQuery imported 15 manufacturer solids with the expected aggregate bounds.
- Nine custom part STEP files parsed and all nine STL companions existed.
- Closed, middle and open assembly STEP files parsed; all three GLB files carried valid `glTF` signatures.
- Seven kinematic samples reproduced the 40-76 mm hard-jaw and 38-74 mm nominal padded ranges.
- Full travel recalculated to 128.915504 degrees at the 8 mm pitch radius.
- The mass screen reproduced 673.774625 g incomplete subtotal and 76.225375 g incomplete headroom.
- Both ideal force screens reproduced, with explicit rejection of continuous/stall acceptance credit.
- All 15 release holds remained open; all release booleans remained false.
- The active moving-mass ledger still named XM430 and contained no XC330 line.
- The interactive guide rendered at 1280 x 720 with 16 px body text, 14 px metadata, zero horizontal overflow and a visible interactive GLB model.

Command:

`C:\Users\amyle\Documents\New project\.venvs\hr-v0-cad\Scripts\python.exe tools/check_hr_v0_xc330_gripper_feasibility_p01.py`

Result:

`HR-V0 XC330 gripper feasibility P0.1 check passed: official STEP hash/15 solids, 9 native parts, 3 poses, calculations and 15 open holds verified`

## Repository checks

- The first full sweep correctly rejected the candidate because the central generated-CAD source manifest lacked the 32 new package artifacts. The R190 generator now rebuilds that manifest and the CAD checker passes over 478 hashed generated artifacts.
- A later sweep correctly rejected Windows-generated STEP bytes that differed from the staged LF-normalized blobs. The generator now emits deterministic LF STEP, JSON and HTML bytes before hashing.
- The final non-`pcbnew` sweep passed 134/134 checker programs.
- The final native KiCad 10.0.5 `pcbnew` sweep passed 13/13 checker programs.
- The release-candidate manifest passed over 3,255 package files. `EG-002` remains partial because this candidate is not merged or formally accepted.
- `check_traceability.py` passed over 81 requirements, 40 risks, 110 procedures and 57 release/walking-document references.
- `check_energization_gates.py` retained all 30 gates unresolved: 23 partial and 7 open.
- `check_hr_v0_bom.py` passed structurally while retaining 18 `SELECTION REQUIRED` groups and no procurement-released complete machine BOM.

The rejected intermediate sweeps were not reclassified as passes; their findings were corrected before the final sweep.

## Boundary

These are source, geometry, arithmetic and presentation checks. They do not verify tooth strength or form, print quality, frame fit, fasteners, tolerances, guidance, guarding, current, force, thermal behavior, wear, cable flex, power-loss drop behavior, mass/COM/inertia, target hardware, or qualified acceptance. No requirement, Sol R12 blocker or energization gate closes.
