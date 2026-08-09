# R155 independent engineering review request

Review `HR-V0-DXL-PROT-EVAL-P0.1` as an evaluation candidate only.

Please independently:

1. Verify every TPS259461LRPWR pin, ILM row, UVLO/OVLO threshold limit and required capacitor/layout instruction against TI `SLVSGA8B`.
2. Challenge the 1.65 kohm and 3.32 kohm current-threshold corner screens, including resistor tolerance and temperature behavior.
3. Confirm that TPS25946 does not limit OUT-to-IN current while enabled and that rejecting TPS25947 is correct for the presently modeled regenerative path.
4. Verify Pololu item 3771's exact setpoint, tolerance, resistance, relative-average-power and pulse-use limitations; do not infer a permissible pulse-energy envelope.
5. Challenge the 0.084 V worst-case static nuisance margin against source tolerance/ripple, measurement uncertainty, line/load transients and received variation.
6. Review the post-K2 shunt location against K1/K2 opening, actuator capacitance, wiring inductance, source behavior and simultaneous-axis regeneration.
7. Verify JST VH boundary identity separately from the downstream JST EH 3 A application conflict.
8. Open all five native KiCad sheets, rerun ERC, inspect all 104 terminals and compare KiCad source, BOM, interface map, calculations, tests and interactive exports.
9. Identify missing PCB, thermal, fuse, conductor, harness, EMC, HIL, failure-mode and functional-safety evidence.
10. Confirm that no candidate entered the robot BOM, Electrical V3-P1.14 or a released firmware external-current value.

Return prioritized BLOCKER / MAJOR / MINOR findings with exact references and primary-source evidence. Do not approve procurement, fabrication, assembly, connection, motion or energization.
