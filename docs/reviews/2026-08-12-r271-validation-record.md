# R271 validation record

> **PRELIMINARY - NOT APPROVED FOR PROCUREMENT, QUOTATION, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION**

R271 imported the exact P0.10 C06 STEP into Gmsh 4.15.2 and regenerated first-order tetrahedral meshes at 4, 3 and 2 mm nominal sizes. The finest model contains 9,229 nodes and 39,187 tetrahedra. Its applied-plus-reaction force residual is 2.82 × 10^-12 of the applied resultant.

Two complete regenerations produced byte-identical analysis status, numerical tables, three compressed mesh capsules, finest-mesh VTU and all SVG/PNG plots. The added structural-analysis dependencies are version-pinned in `tools/requirements-structural-analysis.txt`.

The endpoint-plus-gravity single-rail model gives 122.205 MPa positive-root maximum, 180.573 MPa global element maximum and 0.416 mm maximum displacement. These mesh-sensitive maxima are screening values. The final-two-mesh root-maximum change is 7.36%; qualified convergence is explicitly not claimed.

Repository validation passed **215/215** checks. Native KiCad regression passed **18/18** currently detected `pcbnew` checks; R271 changes no ECAD source. The staged master manifest contains **6,799** package files, including this validation record and the pinned structural-analysis dependency list.

Browser QA passed at 1280 × 720 and 390 × 844. Body text was 16 px and table text 14 px; neither viewport had document-level horizontal overflow, wide tables scrolled internally, and both analysis graphics loaded. The temporary viewport override and local server were reset.

No nonlinear C06/C07 contact, bolt/frame model, plasticity, impact, fatigue, physical correlation, qualified acceptance or work authority is claimed.
