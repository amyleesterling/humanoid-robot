# R156 independent engineering review request

Review `HR-V0-DXL-PROT-CARRIER-P0.1` as an evaluation carrier candidate only.

Please independently:

1. Audit the custom RPW footprint against the official TI RPW0010A package and land drawing, including the compound corner lands, 5/6 power lands, mask, paste, courtyard and assembly orientation.
2. Verify every U1 pad/net and all connector polarity against TI `SLVSGA8B` and the controlled terminal schedule.
3. Verify all exact passive order codes, voltage/power/tolerance/temperature characteristics and DC-bias implications against current manufacturer records.
4. Challenge the two-parallel-1-uF output choice using received capacitance, DC bias, temperature, tolerance and actual actuator/interconnect transients.
5. Review the four-layer layout, 3 mm power corridors, fine-pitch escapes, ground/via topology and the explicit absence of via-in-pad against TI guidance and an actual fabricator's process.
6. Verify the J1/J2 1.65 k and G1 3.32 k variant control, marking and traveler requirements.
7. Confirm that ITIMER is open and SPLYGD/FLT are unpulled observation points with zero safety or motion credit.
8. Confirm that TPS25946 does not bound OUT-to-IN current and that the external shunt, source, K1/K2, fuse and simultaneous-axis regenerative-energy questions remain open.
9. Rerun KiCad ERC/DRC, compare the native source, controlled source, BOM, terminal schedule, board, CAM outputs, web guide and manifests.
10. Review the ten test methods and sixteen hold groups for missing current, transient, thermal, connector, EMC, backfeed, HIL, failure-mode, inspection and acceptance evidence.

Return prioritized BLOCKER / MAJOR / MINOR findings with exact sheet, reference, pad/net and primary-source evidence. Do not authorize supplier upload, quotation, procurement, fabrication, assembly, connection, motion or energization.
