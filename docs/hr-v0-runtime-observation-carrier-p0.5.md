# HR-V0 power-state-corrected runtime-observation carrier R211 / P0.5 / PCB-P0.4

**PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION**

R211 supersedes P0.4 for current review. P0.4 hard-grounded the active-low OE pins of four `SN74LVC1G125DBVR` devices even though TI recommends a VCC pull-up when high impedance is required through power transitions. P0.5 removes that OE state entirely by using exact active `SN74LVC1G07DBVR` open-drain buffers. Each output has an exact Panasonic `ERJ6ENF1002V` 10.0 kohm pull-up to the same proposed Pi 3V3 rail, followed by the retained 39.0 kohm GPIO fault limiter and 330 kohm carrier-side fail-low bias.

TI specifies the G07 for partial-power-down using Ioff and defines its DBV pin 1 as no-connect. When the carrier 3V3 supply is absent, the G07 output is high impedance and the pull-up source is absent with it; P0.5 therefore removes the prior positive push-pull source into the Pi pin. This is a topology improvement, not proof of Raspberry Pi compatibility.

The current official RP1 public reference defines 3.3 V bank selection and 2/4/8/12 mA drive settings but does not publish Pi 5/RP1 VIH, VIL, leakage, capacitance, clamp or unpowered-pin limits. The current HAT+ specification also requires tolerance of STANDBY with 5 V present and 3.3 V absent. Those limits and the 7.612 mA header-load screen require Raspberry Pi application acceptance and physical power-state testing. All fourteen holds remain open. Every channel remains an ordinary diagnostic with zero functional-safety credit.

No procurement, fabrication, assembly, connection, powered test, motion or energization is authorized.
