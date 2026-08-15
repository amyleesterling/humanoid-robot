# R281 validation record

> **PRELIMINARY - NUMERICAL SOLVER FEASIBILITY ONLY - NOT APPROVED FOR PROCUREMENT, QUOTATION, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION**

R281 generated `HR-V0-J2-NUMERICAL-BACKEND-P0.1`, synchronized component evidence, an interactive guide and configuration reconciliation P0.45. This validates a bounded numerical execution route only; it does not execute the R279 multi-level convergence study.

C06 P2C solves 162,702 displacement DOFs using Jacobi-preconditioned conjugate gradient. A first run with requested `rtol=1e-10` returned CG info zero but its independently recomputed residual was 1.013611e-10 and failed the unchanged 1e-10 gate. A rerun requested 5e-11 and passed after 2,754 iterations with a postcomputed residual of 5.457531e-11 and normalized full-force imbalance of 2.713841e-13.

The previous C07 HXT L0 mesh failed quality at minimum SICN 0.052708. Exact P0.13 geometry and local size fields were held fixed while Gmsh Delaunay algorithm 1 plus Netgen optimization was screened. The resulting L0 mesh has minimum SICN 0.111805 and 0.007040% of elements below 0.20, passing the R279 limits of 0.10 and 0.1%.

On the bounded C07 P2C mesh, the metal-perimeter case passed after 2,590 iterations with postcomputed residual 8.996679e-11. The pocket-floor case initially returned CG info zero but failed at 3.476235e-10. One bounded true-residual correction solve reduced it to 5.173165e-11; normalized full-force imbalance is 3.413253e-13. Both the failed and accepted attempts are retained.

Every result is a single coarse straight-sided P2-displacement feasibility solve. No stress/capacity claim is made. Curved geometry, L0-L3 convergence, registered section resultants, GCI/order, singularity trends, independent solver verification, H03 nonlinear contact, H04 joined hardware/frame, dynamics and physical correlation remain open.

Browser QA, native KiCad regression, final repository validation and staged manifest count are recorded below after staging.

Browser QA: **passed at 1440 x 900 and 390 x 844**. Desktop body/table text measured 17/16 px; mobile measured 16/16 px and the smallest functional text was 16 px. Neither viewport had page-level overflow; all four tables scrolled internally on mobile. The warning and H02-open statement were visible. The temporary tab and server were closed.

Native KiCad: **18/18 passed** using the KiCad 10.0.5 Python runtime. This was a regression sweep; R281 does not change native ECAD source.

Pre-staging non-`pcbnew` checks: **225/226 passed** in the controlled CadQuery environment. The only failure was the expected release-manifest rejection of the new, not-yet-staged R281 package. A first general-runtime attempt lacked CadQuery; rerouting to the project's controlled CAD environment cleared every CAD-dependent check and is recorded as runtime routing, not a design defect.

Post-staging non-`pcbnew` checks: **226/226 passed** in the controlled CadQuery environment.

Final staged master manifest: **7,593 package files** before this validation-record finalization; the manifest was regenerated after this text was staged so its recorded hash and final file count remain controlling.
