# R201 independent review request

**PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION**

Review `HR-V0-RUNTIME-OBS-IF-P0.1` as a diagnostic-only electrical evaluation candidate. Do not infer a PCB, harness, Raspberry Pi pin allocation, safety function or work authorization.

1. Open the root and all four child sheets under `electrical/kicad/hr-v0-runtime-observation-interface-p0.1/` with KiCad 10.0.5 or a documented compatible version. Reproduce ERC and the netlist independently.
2. Trace `SR1_STATUS`, `SRA1_STATUS`, `K1_STATUS` and `K2_STATUS` from their current P1.15 source terminals through every RTHR, RSENSE, CIN, shunt, ISO1212 pin, output resistor, pulldown and connector terminal.
3. Verify ISO1212DBQ pins against TI SLLSEY7G Rev G and challenge the proposed `SAFETY_0V` field / `COMPUTE_0V` logic boundary, floating SUB treatment, logic brownout state and absence of channel-to-channel isolation within each two-channel device.
4. Recalculate every `load-budget.csv` result. Treat TI current limits and IDEC's 7 mA catalog value as documented screens, not received-product evidence.
5. Challenge the SR1 calculation for Y32's 20 mA ceiling, 5 V maximum internal drop, 0.1 mA residual current, H1 voltage range, exact received H1 current and useful brightness.
6. Challenge the 2.70 kohm K1/K2 wetting loads against Schneider's 5 mA / 17 V minima, contact contamination/bounce/life, resistor tolerance, temperature and fault cases.
7. Review TI's Type-3 EMC table and layout guidance. The catalog application results do not qualify the Project Button board, cable, enclosure or grounding system.
8. Confirm no output can command, restore, latch or preserve motion and no diagnostic channel receives functional-safety credit.
9. Confirm all ten holds remain genuinely open and identify any missing selection, calculation, physical test or common-cause case.
10. Review the interactive guide at `release/hr-v0/runtime-observation-interface-p0.1/index.html` for legibility, correct source links and faithful correspondence to the native source.

Return findings by severity with exact sheet/reference/terminal/net, primary-source support, proposed correction and closure evidence. Do not approve fabrication, connection, powered testing, motion or energization.
