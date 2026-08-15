# HR-V0 joint measurement definition P0.1

> **PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION**

Document ID: **HR-V0-JOINT-MEAS-DEF-P0.1**  
Date: 2026-08-11  
Parents: `HR-V0-JOINT-MET-P0.2`, `HR-V0-LOT-A-INQUIRY-P0.2`

## Result

R256 turns the broad HSI labels in the metrology plan into exact, source-bound reference features and received-article measurement definitions. It derives 79 planar/cylindrical feature records from the controlled XM540, FR13-H101K and FR13-S102K STEP files and binds them to 18 measurement characteristics covering HSI-003 through HSI-014 and the mass-only portions of HSI-017/018.

The [interactive guide](../release/hr-v0/joint-measurement-definition-p0.1/index.html) includes:

- the exact controlled joint-stack geometry with feature-point markers;
- a six-plane axial-reference index;
- source-derived H101/S102 attachment-pattern views;
- exact one-based source face indices, transformed points, axes/normals, radii, areas and geometric signatures;
- received-result, raw-evidence, uncertainty and approval fields that remain blank; and
- all 20 HSI rows with explicit closure boundaries.

## What the numbers mean

The package reproduces nominal source geometry only. For example, it records a 53.000000 mm H101 outer-plane separation, a 48.000000 mm S102 outer-plane separation, and a 2.500000 mm nominal clearance on each side when those source planes are compared. Those values are not tolerances, received measurements, acceptance criteria or proof of fit.

Every provider must still:

1. identify the exact received article and match each received feature to the source reference;
2. report mismatches rather than silently substituting a nearby surface;
3. disclose support, datum, fit, filtering and outlier methods;
4. preserve raw points/scans/readings, transforms and residuals;
5. supply a numeric uncertainty budget; and
6. leave acceptance to a named qualified reviewer using configuration-specific limits.

Geometry alone does not establish thread identity, hole function, fastener allocation, manufacturer-supported use or continuous-duty suitability. STEP volume is explicitly prohibited as accepted mass or inertia evidence.

## HSI coverage

- HSI-001/002 remain receiving and identity records.
- HSI-003..006 now have exact plane and axis candidates for J1/J2 received and assembled axial measurement.
- HSI-007/008 require registered multi-orientation scan evidence; the configured cable and guard remain outside this package.
- HSI-009..012 have exact cylindrical source-pattern references, but manufacturer function allocation remains open.
- HSI-013/014 have exact fixed/moving external plane references, but the zero-angle convention and external measurement method remain open.
- HSI-015/016/019/020 remain external because the harness, guard, bumper/retention and selected fabrication topology do not exist.
- HSI-017/018 gain direct-balance result definitions only; stop-load-path, COM and effective/reflected inertia remain external.

## Configuration effect

`HR-V0-CONFIG-REC-P0.20` supersedes P0.19 as the configuration record only. It contains 39 current records, 31 supersession records, 109 open holds and 142 blank/unexecuted acceptance rows.

R256 closes zero Sol R12 blockers. It supplies no received evidence, method acceptance, tolerance release, build release, qualified approval, functional-safety credit or work authority.
