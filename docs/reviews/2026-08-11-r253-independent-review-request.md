# R253 independent mechanical/metrology review request

> **PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION**

Please independently review `HR-V0-JOINT-STACK-FIXTURE-P0.2` and `HR-V0-CONFIG-REC-P0.17`. This is a design-evidence review, not a request to approve fabrication or physical work.

## Required review

1. Confirm or reject the finding that P0.1's six coplanar frictionless point contacts have constraint-matrix rank 3 and are not a complete locating scheme.
2. Reproduce P0.2's normalized `[n, (r × n)/48 mm]` matrix, rank 6, singular values, and condition number `9.373695`.
3. Review the A1/A2/A3, B1/B2, and C1 surface/coordinate assignments against the controlled S102 STEP.
4. Confirm that zero nominal intersection volume and positive XM540/H101 clearance support only a nominal rigid-CAD claim.
5. Assess whether datum-B and datum-C edge contacts are mechanically acceptable or require alternate surfaces/features.
6. Define the analysis and evidence required for contact material, force, local stress/deformation, friction, stability, anti-lift restraint, tolerances, accessibility, burrs and wear.
7. Determine whether the seating sequence and restraint remain kinematic or introduce redundant hard contacts and inconsistent loading.
8. Review the XM540 `-T` title/SKU/TTL versus `-R` package-table conflict and confirm the written supplier evidence required before purchase.
9. Review the temporary screw, washer/index, spacer, mounting-depth, torque, locking and reuse holds against current ROBOTIS documentation.
10. State the exact DFM, FAI, measurement-system, physical-fit, repeatability and uncertainty evidence required before one unpowered session could be separately authorized.

For each finding, provide severity, artifact/row/feature, factual basis, required correction, closure evidence, reviewer role, and whether it blocks purchase, fixture fabrication, temporary assembly, or the unpowered session. Do not grant powered, motion, functional-safety or energization credit.
