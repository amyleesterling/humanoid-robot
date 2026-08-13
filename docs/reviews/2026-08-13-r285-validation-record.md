# R285 validation record

> **PRELIMINARY - TARGETED CURVED-MESH METHOD EVIDENCE ONLY - NOT APPROVED FOR PROCUREMENT, QUOTATION, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION**

## Result

R285 passes as **bounded targeted curved-mesh method evidence only**. It does not close R279-C02, R278-H02, structural convergence, capacity, safety, or any work-authority gate.

## Executed validation

- Repository-wide HR-V0 standard checker sweep: **237 / 237 PASS**.
- Master release manifest: **8,081 staged payload entries**, regenerated and verified.
- `git diff --check` and staged whitespace check: **PASS**.
- Exact target-feature identity: **12 surfaces and 46 owner-boundary curves**, with no missing or extra records.
- Three fresh-process targeted-remesh runs: **3 / 3 PASS** for the bounded sampled screen; all 17 retained NPZ arrays are identical between runs.
- Each run: **22,078 vertices**, **92,455 Tet10 elements**, and **127,226 unique edges**, with zero shared-edge conflicts.
- Global linear SICN: minimum **0.17901949697693917**; **4 / 92,455** elements below 0.20.
- Independently reconstructed curved-Jacobian samples:
  - Q4: **1,017,005** points, zero wrong/zero and zero normalized-floor failures.
  - Q6: **1,386,825** points, zero wrong/zero and zero normalized-floor failures.
  - Q8: **2,866,105** points, zero wrong/zero and zero normalized-floor failures.
- Feature, remesh, disposition, and configuration source/release mirrors: **byte-identical** and manifest-clean.
- Interactive guide visual QA:
  - desktop **1280 x 720**: minimum rendered text **16 px**, no root horizontal overflow;
  - mobile **360 x 812**: minimum rendered text **16 px**, no root horizontal overflow, all three tables contained by their horizontal-scroll wrappers.

## Independent audit

An independent raw-evidence audit reconstructed the target set, Tet10 topology, SICN histogram, and Q4/Q6/Q8 Jacobian results without trusting the summary registers. It found no discrepancy and accepted R285 for bounded method-only integration.

The audit also confirmed the evidence demonstrates repeatability only in the recorded **Gmsh 4.15.2 / OCC 7.8.1** environment. Cross-platform and randomized-seed robustness remain unverified. Independent and qualified acceptance gates remain open in the controlled configuration.

## Explicitly unverified

- exact B-Rep surface-deviation limits and complete facet-to-OCC mapping;
- exact-zone clipped histograms and measure conservation;
- full-domain curved-Jacobian positivity beyond finite Q4/Q6/Q8 sampling;
- loaded-area, resultant, centroid, and moment preservation;
- structural solution, multilevel convergence, GCI, singularity trends, and physical correlation;
- contact, joined-hardware, dynamic, material, DFM/FAI, and guarded physical-test closure;
- capacity, safety credit, procurement, fabrication, assembly, connection, powered testing, motion, or energization authority.
