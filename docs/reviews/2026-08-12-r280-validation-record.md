# R280 validation record

> **PRELIMINARY - SCRATCH NUMERICAL EVIDENCE ONLY - NOT APPROVED FOR PROCUREMENT, QUOTATION, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION**

R280 generated `HR-V0-J2-STOP-REFINEMENT-EXECUTION-P0.1`, its synchronized interactive guide and configuration reconciliation P0.44. This is bounded numerical/toolchain feasibility evidence, not convergence or capacity evidence.

Exact P0.13 STEP geometry was imported through Gmsh OCC and SHA-bound. Exact entity discovery identified C06 load faces 30/71, hole cylinders 33-38 and rail-root curves 119/208. C07 identified hole cylinders 13-18, 21 split pocket-floor faces, 40 exact pocket-boundary curves and the shared metal-backup planar face. Local Distance/Threshold fields were combined by a Min field, and exact entity nodes—not centroid boxes—bound the loaded and fixed facets.

Three meshes were retained. C06 P2C contains 8,027 vertices and 33,102 tetrahedra; C06 L0 contains 40,399 vertices and 197,167 tetrahedra. Both pass the proposed minimum-SICN quality floor. C07 L0 contains 54,204 vertices and 252,751 tetrahedra but its minimum SICN is 0.052708; it fails the required 0.10 gate and receives no structural result.

The only completed structural case is a C06 L0 P1 diagnostic with 121,197 DOFs. It balances force to 4.97e-14, gives 0.400278 N mm strain energy and 0.005931 mm maximum solution-DOF displacement. Its raw 11.4047 MPa quadrature maximum and fixed-volume zone metrics are explicitly excluded from capacity use and receive no convergence credit.

Two direct sparse P2 attempts were stopped cleanly. The 884,739-DOF L0 attempt exceeded 6.25 GB and ran at least 180 seconds without a result. Even the 162,702-DOF coarse cross-check exceeded 5.05 GB and ran at least 225 seconds without a result. No P2 stress/displacement result exists. The next execution requires a controlled iterative/preconditioned or validated external solver and repaired C07 meshing.

Browser QA, native KiCad regression, final repository validation and staged manifest count are recorded below after staging.

Browser QA: **passed at 1440 x 900 and 390 x 844**. Desktop body/table text measured 17/16 px; mobile measured 16/16 px and the smallest functional text was 16 px. Neither viewport had page-level overflow; all five tables scrolled internally on mobile. The warning and H02-open statement were visible. The temporary tab and server were closed.

Native KiCad: **18/18 passed**.

Post-staging non-`pcbnew` checks: **225/225 passed**.

Final staged master manifest: **7,519 package files**.

R278-H02, H03 nonlinear contact, H04 joined hardware/frame, dynamics, physical correlation, qualified capacity and every work authority remain open.
