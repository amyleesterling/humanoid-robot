# R209 independent review request

**PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION**

Independently review `HR-V0-RUNTIME-OBS-CARRIER-P0.3` as a candidate correction to the R208 ISO1212 output-current blocker. Do not treat clean ERC/DRC or the project checker as physical acceptance.

Reproduce and challenge:

- the four independent `SN74LVC1G125DBVR` channels and hard-grounded active-low enables;
- the 1.50 kohm / 47.0 kohm ISO-side and 36.5 kohm / 330 kohm GPIO-side networks, including tolerance, temperature, leakage, partial-power and fault cases;
- the 2.424 mA ISO-side and 99.63 uA GPIO-side hard-short screens;
- the 2.518 V buffer-input HIGH floor, 0.400 V LOW ceiling and 2.426 V cable-side source-HIGH screen;
- the 6.180 mA conservative steady 3V3 screen, including the selected delta-ICC interpretation and missing switching current;
- DBV-5 and 0805 land geometry, decoupling placement, planes, return paths, creepage/clearance, EMC and manufacturability;
- exact JFIELD1/JLOGIC1 mapping and parity with R202, R204, R207 and Electrical P1.16;
- OFF, ramp, active, brownout, shutdown, field-only, open, short-to-return, short-to-3V3 and cross-short behavior; and
- the explicit zero-functional-safety-credit boundary and fail-closed software use of invalid observations.

Evidence still required includes authoritative Raspberry Pi 5 header-3V3 external-load limits and RP1 GPIO VIH/VIL, leakage, capacitance, clamps and unpowered-pin behavior; received-part and first-article evidence; installed timing/EMC; fault injection; and qualified electrical review. Record every source revision/date. Do not approve procurement, fabrication, connection, powered testing, motion or energization.
