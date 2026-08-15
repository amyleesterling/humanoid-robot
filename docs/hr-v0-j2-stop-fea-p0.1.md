# HR-V0 J2 stop C06 full-part FEA screen P0.1

> **PRELIMINARY - NOT APPROVED FOR PROCUREMENT, QUOTATION, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION**

R271 imports exact P0.10 C06 STEP into Gmsh 4.15.2 and solves three first-order tetrahedral meshes with scikit-fem 12.0.2. The 2 mm mesh contains 9,229 nodes and 39,187 tetrahedra. Under the R270 endpoint-plus-gravity single-rail resultant, the modeled positive-root maximum is 122.205 MPa and the global element maximum is 180.573 MPa; maximum displacement is 0.416 mm. Linear 4× scaling gives 488.822 MPa and fails the interim geometry-rejection threshold.

The result supersedes reliance on the 50.864 MPa beam screen but does not provide qualified convergence or an allowable. Fixed hole surfaces and distributed rail-top loading regularize the actual bolt/contact system. P0.10 remains unselected; nine analysis, physical-correlation and authority holds remain open.

[Interactive R271 evidence](../release/hr-v0/j2-stop-fea-p0.1/index.html)
