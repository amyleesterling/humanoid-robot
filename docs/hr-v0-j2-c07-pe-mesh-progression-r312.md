# HR-V0 J2 C07 numerical handoff through R312

**PRELIMINARY - NOT APPROVED FOR PROCUREMENT, QUOTATION, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION**

R311 found and corrected a method flaw in the R308/R309 exact-facet evaluator. Distance to an underlying OCC surface is not proof that a point lies inside that surface's exact trimmed face. The corrected test requires every quadratic boundary node to satisfy both the distance tolerance and exact trimmed-face containment.

The corrected R311 result is 112,399 uniquely mapped facets, 247 unmapped facets, zero multiply mapped facets, and 32 failure clusters across 24 exact trimmed faces. It supersedes R308's earlier complete-map count, R309's zero-distance containment inference, and R310's underconstrained seven-face imprint candidate.

R312 then executed one preregistered 24-face analysis-only imprint against all 21 R297 volumes. The operation preserved all 21 one-to-one zone mappings, the fused pocket-edge volume, total material exactly, each zone's volume within 8.99e-16 relative error, bounding boxes exactly, and centers of mass within 7.11e-15 mm. It nevertheless failed the frozen topology criterion: only 8 of 24 exact target signatures remained one face with one exterior owner. The R312 candidate is rejected.

The current disposition is:

- R307 remains bounded finite Q4/Q6/Q8 method evidence only.
- R311 is the current exact trimmed-face ownership result.
- R312 is a rejected topology candidate; no successor mesh may inherit acceptance from it.
- A future method must distinguish exact geometric coverage from topology-signature identity and must be separately preregistered before execution.
- R279-C02, structural fields, convergence, H02, capacity, physical correlation, qualified acceptance and every work authority remain open.

No physical part geometry was changed and no mesh or structural solve was executed in R311 or R312.
