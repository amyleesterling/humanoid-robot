# R193 validation record

> **PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION**

Artifact: `HR-V0-GRIP-CAD-ACQ-P0.2`

Date: 2026-08-10

## Executed source/configuration checks

- The current official ROBOTIS endpoint 690 was followed to public Onshape document `9442f03bd8ccac084fda9dd3`, workspace `039e8dbd53e0782540ea5b0d`.
- The public viewer displayed **ROBOTIS OpenManipulator Chain**, **Main**, **shared via a link and view only**.
- The exact gripper assembly plus five native part-workspace element URLs were opened and their displayed identities recorded.
- Anonymous assembly/part/tab context menus exposed no export action; an unauthenticated document API request returned HTTP 401. No account was used and no payload was acquired.
- A fresh shallow clone of the official ROBOTIS repository resolved to commit `9187eca0920458be04d2399906388f55242f81f1`, commit date 2026-08-05. The two palm STL and link5 STL hashes matched the previously frozen repository evidence; the checked-out URDF differed from the frozen raw artifact only by checkout line endings and receives no new engineering credit.
- The active XM430/OpenMANIPULATOR proposal remained unselected. The XC330 branch remained an alternate prohibited from direct connection to the current rail.
- All six source rows, six element rows, three decision rows and twelve holds passed the fail-closed R193 checker. EG-003 and EG-005 remain partial; EG-028 remains open.
- R192 hold `WRI-H10` was corrected from the erroneous text “1-degree nominal sample” to the executed 5-degree sample. The generated-source manifest was refreshed and the R192 checker passed.

Command/result:

`python tools/check_hr_v0_gripper_cad_source_correction_p02.py`

`HR-V0 gripper CAD source correction P0.2 check passed: 6 sources, 6 native elements, 3 decisions and 12 open holds verified`

## Repository validation

- Initial repository regression rejected five deliberate stale/untracked conditions: R192 generated-source hash, build-traveler source hash, configuration-reconciliation source hash, release manifest and the R192 integration manifest. No failure was suppressed.
- After deterministic source-manifest, configuration-reconciliation and build-traveler regeneration, **136/137** standard-runtime checkers passed; the only remaining expected failure was the release-manifest checker because the new R193 files were not yet staged.
- After final staging and release-manifest regeneration, the complete standard-runtime sweep passed **137/137**.
- All **13/13** native KiCad `pcbnew` checkers passed under KiCad 10.0.5, including the existing zero-violation modeled ERC/DRC boundaries.
- Traceability passed over **81 requirements, 40 risks, 110 procedures and 57 release/walking-document procedure references**.
- BOM validation passed over **91 system items, 17 evaluation-only lines and 18 selection-required groups**.
- CAD validation passed over 4 historical custom-part artifacts, 3 fit coupons, **529 hash-bound generated artifacts** and 17 vendor references, with no active fabrication packet.
- The energization register retained **all 30 gates unresolved: 23 partial and 7 open**. `--require-ready` returned exit 2 as required.
- The final staged release manifest contains **3,339 package files** and passed its dedicated content/hash checker.

## Interactive-guide QA boundary

The HTML checker verifies 16 px body/functional text, 14 px metadata, responsive grid/table overflow controls, required warnings and absence of 11/12 px declarations. The in-app Browser's URL policy blocked the local/data-URL preview, so no live desktop/mobile visual-QA claim is made for R193. The deployed GitHub Pages view remains an explicit follow-up inspection item.

## Boundary

The checks prove source/configuration consistency only. They do not establish an immutable Onshape version, native export, received mechanism, H104 transform, tolerances, material/process, fasteners, complete mass/COM/inertia, cable path, retained guard, force/current/thermal limits, power-loss containment, physical verification, functional-safety performance or qualified acceptance. No requirement, Sol R12 finding or energization gate closes.
