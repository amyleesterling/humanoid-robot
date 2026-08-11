# R212 independent review request

**PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION**

Independently review `V3-P1.17-OBSERVATION-P0.5-CANDIDATE` and `HR-V0-CONFIG-REC-P0.2` as a configuration correction, not as electrical, fabrication or safety approval.

1. Reconstruct P1.15 and P1.17 from their generators. Confirm all 79 core component definitions and every core terminal/net/status/evidence field are identical and that OBS1/PIOBS1 are the only additions.
2. Compare OBS1 JFIELD1/JLOGIC1 against the native P0.5 connector schedule and PIOBS1 JOBS1/JPI1 against the passive Pi carrier. Confirm every omitted Pi header position remains no-net/no-copper in the native carrier.
3. Recalculate and verify every binding hash. Confirm release metadata, configuration maps, supersession records, BOM boundary and review ledger all identify P0.5 as current and P0.2-P0.4 as historical.
4. Challenge the decision to retain P1.15 as the direct watchdog/core binding while using P1.17 as the synchronized system view. Require exact parity evidence for every downstream watchdog, E2, BOM, CAM and harness consumer.
5. Review all seven affected gates and reject any implied closure. In particular, obtain authoritative Pi limits, close observation BOM quantities, exact harness lengths, DFM, first article, physical power-state/fault tests and the zero-safety-credit common-cause boundary.

Do not authorize procurement, fabrication, assembly, connection, powered testing, motion or energization from R212.
