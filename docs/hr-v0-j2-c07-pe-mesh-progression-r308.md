# HR-V0 J2 C07 numerical handoff through R308

**PRELIMINARY - NOT APPROVED FOR PROCUREMENT, QUOTATION, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION**

R307 successfully executed the single CAD-resident candidate frozen in R306/R307. The live OCC pipeline regenerated all 1,244,636 R300 linear tetrahedra, node coordinates, connectivity, SICN values and exact-zone codes identically. It then ran `HighOrder` once on C07-MATRIX with `force=false`, `niter=1`, restored all 239,848 mapped corners, preserved Tet10 tags/connectivity and produced zero failed Q4/Q6/Q8 samples. Maximum optimizer corner movement before restoration was 0.0238589699 mm; recorded post-restoration error was 0.0 mm.

R308 then applied the mandatory frozen exact exterior-facet test. It stopped fail-closed because 77 of 112,646 exterior facets mapped to no exact OCC face; 112,569 mapped uniquely and none mapped multiply. Therefore surface-deviation, per-face-area and load-patch credit was not awarded.

The correct disposition is:

- R307 remains bounded sampled-Jacobian method evidence.
- R307 is not selected for structural execution.
- R279-C02 remains false.
- The next permitted work is a preregistered localization of the 77 unmapped facets, preserving the exact 1e-7 mm node-face membership tolerance.
- Full-domain positivity, structural fields, convergence, H02, capacity, physical correlation and every work authority remain open.

No geometry, mesh field, tolerance or optimizer setting was tuned after observing R308.
