# HR-V0 task-specific unpowered joint-stack metrology P0.2

> **PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION**

Document ID: **HR-V0-JOINT-MET-P0.2**  
Date: 2026-08-11  
Requirements: `MECH-005`, `MECH-006`, `SAFE-006`, `SAFE-007`, `MASS-002`

## Engineering result

R254 accepts Sol's central evidence finding: HR-V0 still has no received machine or executed measurement evidence. It also corrects the project's own metrology plan. One fixture cannot honestly support all measurements in the R84 campaign.

The successor separates five methods:

1. loose-part depths, faces and feature coordinates on nonmarring free-state supports;
2. assembled axial stack against an externally realized joint axis;
3. external mechanical angle and bidirectional unpowered backlash with independent gravity restraint;
4. both-side envelope scans using low-occlusion supports and controlled re-fixturing; and
5. loose and assembled mass on a tared calibrated balance.

The [interactive guide](../release/hr-v0/joint-stack-metrology-p0.2/index.html) contains the full method, phase, HSI, hold, operation and uncertainty registers. All five methods and 22 operations are `NOT EXECUTED`. All 12 holds are open. The 40 uncertainty inputs are blank and `SELECTION REQUIRED`, so no combined or expanded uncertainty is calculable.

## P0.2 fixture disposition

`HR-V0-JOINT-STACK-FIXTURE-P0.2` remains a mathematically rank-6 nominal locator candidate, but R254 prohibits treating it as a universal measurement fixture:

- it is not applicable to free-state loose-part metrology;
- it is only a conditional support candidate for axial work because it does not realize the joint axis;
- it is only a conditional fixed-S102 datum candidate for angle work because it provides neither a moving reference nor gravity restraint;
- it is not acceptable as the sole scan fixture because it creates occlusion; and
- it is not applicable to mass measurement.

No P0.2 fixture use is authorized. Its material, contact force, restraint, tolerance, local deformation, FAI, received fit, repeatability, uncertainty and qualified-review holds remain open.

## Phased execution boundary

The package separates work so loose-part metrology need not wait for threaded assembly:

- `PH0` acquisition/receiving requires written authority and resolved supplier identity;
- `PHL` loose-part work requires received articles plus accepted instruments, calibration, uncertainty and method-specific supports;
- `PHA` temporary assembly remains prohibited until one exact signed instruction controls screws, depths, spacer placement, torque, locking, reuse and stop-work criteria;
- `PHM` assembled measurements require separate method/fixture acceptance; and
- `PHT` teardown requires evidence completeness and qualified disposition.

Every phase is `NOT AUTHORIZED` and `NOT EXECUTED`. Electrical sources, actuator connections and power equipment remain prohibited throughout this campaign.

## Uncertainty boundary

R84's numerical instrument capabilities remain project-authored provisional screening boundaries, not released part tolerances. R254 does not invent component allocations. Each method now requires explicit inputs for calibration, resolution, repeatability, fixture reseat/support, datum or axis realization, environment, probe/scan/model fit, and operator/processing effects.

The structure follows the uncertainty-component, combination and reporting route in [NIST Technical Note 1297, 1994 edition](https://www.nist.gov/pml/nist-technical-note-1297). Fixture and datum design must receive qualified review against the applicable controlled product definition; [ASME Y14.43-2011 (R2020)](https://www.asme.org/codes-standards/find-codes-standards/y14-43-dimensioning-tolerancing-principles-gages-fixtures) is recorded as a review source, not silently applied as a released acceptance basis.

## Configuration effect

`HR-V0-CONFIG-REC-P0.18` adds this current execution contract and supersedes P0.1 for execution planning only. Historical R84 requirements remain preserved. P0.18 contains 37 current records, 27 supersession records, 82 open holds and 115 open/unexecuted acceptance rows.

R254 closes zero Sol blockers, zero fabrication gates and zero energization prerequisites. It creates a more honest route to the received dimensions, mass and interface evidence needed to address B-003 and B-010.

