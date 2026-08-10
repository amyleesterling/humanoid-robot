# R161 independent review request

> **PRELIMINARY - NOT APPROVED FOR SUPPLIER UPLOAD, QUOTATION, PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, MOTION, OR ENERGIZATION**

Please review `HR-V0-DXL-CARRIER-INTEGRATION-P0.1`, `V3-P1.15-CARRIER-CANDIDATE`, and `DXL-STAR-P0.2-CARRIER-CANDIDATE` as unreleased correction candidates.

Check:

1. Every `F1/F2/F3 -> LIM1/LIM2/LIM3 -> INJ1 -> DXL-star -> actuator` positive-net transition and every return terminal.
2. Absence of ambiguous `J1_VDD/J2_VDD/J3_VDD` rail names in the candidate schedules, netlist and PCB.
3. `JC1:2` no-VDD/no-copper behavior and native P0.1/P0.2 star-board geometry parity.
4. Whether four terminal blocks per limiter correctly represent the P0.3 `JIN1/JOUT1` interfaces without implying a built article.
5. The P0.6 reserve-zone and three-board no-overlap screens, including hole datums, cover depth, connector sweep, duct access, thermal and service assumptions.
6. The refusal to turn geometric route screens into cut lengths.
7. All twelve unresolved selections and 24 open acceptance rows.
8. Whether any source/return protection, reverse-energy, grounding/bonding, EMC, harness, workmanship, physical-test or functional-safety obligation is missing.

Do not approve procurement, fabrication, assembly, connection, powered work, motion, energization or functional-safety credit from this review.
