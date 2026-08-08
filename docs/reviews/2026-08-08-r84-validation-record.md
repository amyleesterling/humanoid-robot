# R84 validation record - unpowered J1/J2 acquisition and metrology

Date: 2026-08-08

Product: `HR-V0-JOINT-MET-P0.1`

Parents: `HR-V0-MECH-EVAL-P0.1`, `HR-V0-STOP-REGION-P0.1`

Status: **PRELIMINARY - UNPOWERED METROLOGY ONLY - NO PURCHASE, ASSEMBLY-USE, MOTION OR ENERGIZATION RELEASE**

## Correction

R84 converts the R83 physical-interface register from a generic “receive and measure” dependency into a controlled acquisition and laboratory traveler. It also corrects the impossible combination of an encoder-zero measurement with an unpowered procedure: `HSI-013/014` now use an external mechanical angle datum, while encoder calibration remains separately authorized powered work.

## Executed source validation

- `tools/generate_hr_v0_joint_stack_metrology.py` completed successfully;
- `tools/check_hr_v0_joint_stack_metrology.py` passed;
- six exact articles are allocated: two XM540-W270-T, two FR13-H101K and two FR13-S102K;
- eighteen operation rows remain `NOT EXECUTED` or `NOT AUTHORIZED`;
- eight hold points remain `OPEN`;
- six instrument classes remain unselected or on hard hold;
- `HSI-001..020` remain `OPEN - NOT EXECUTED`;
- the raw-record template contains one `NOT-EXECUTED` seed row;
- purchase authorization is false;
- temporary threaded assembly authorization is false;
- power or motion authorization is false;
- the SVG parses and preserves 18 px body / 36 px title text controls; and
- the responsive HTML source preserves a 16 px minimum body control and the required warnings/filter routes.

The complete repository sweep passed all `34` non-manifest checkers. Traceability reports `81` requirements, `40` risks and `105` controlled procedures. The staged release manifest contains `938` package files and passed its content/hash checker before commit.

The R83 CadQuery generator was rerun after correcting `HSI-013/014`. Its complete 6,411-pose/131-certificate calculation and checker passed with the same 5.743912 mm conservative nominal lower bound and all twenty physical inputs open.

## Manufacturer-source verification

Current ROBOTIS product and e-Manual records were rechecked 2026-08-08. They support the exact H101/S102 SKUs and kit contents, use of the H101 idler, thrust-washer/index alignment, spacer use, screw-length-versus-mounting-depth check, and cable untangling caution. The current HNX540-C101 record states that its HN13-C101 clamping horn is not compatible with FR13-H101K.

No numeric Project Button assembly torque was found in the cited current manufacturer instructions. R84 therefore retains exact screw allocation, temporary torque, locking and reuse as a signed hard hold rather than inventing values.

## Boundary

This is source and plan validation only. No purchase authorization, purchase order, received article, calibration certificate, fixture approval, temporary assembly instruction, physical measurement, uncertainty budget, photograph, raw point cloud, nonconformance disposition or qualified acceptance exists.

R84 closes zero HSI rows and zero release gates. The package is not a build release and does not permit assembly use, connection, encoder readout, motion, fabrication or energization.

## Remote clean-clone validation

The pushed branch was cloned independently from GitHub at commit `2b17b1ca2978f6b9c447c6b3df0fd9e503f040bd`. In that remote clone:

- all `34` non-manifest repository checkers passed;
- `tools/check_hr_v0_release_manifest.py --require-clean` passed for `938` package files;
- the manifest checker reported the exact cloned commit above; and
- the temporary clone and its exact-path `safe.directory` entry were removed after validation.

This validates source/configuration reproducibility only. It supplies no physical article, qualified review, fabrication, motion or energization evidence.
