# HR-V0 buffered runtime-observation carrier R209 / P0.3 / PCB-P0.2

**PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION**

R209 supersedes the P0.2 direct ISO1212-to-harness output candidate with a buffered P0.3 native KiCad derivative. The four field channels, both isolation barriers, connector numbering, board outline, mounting datums and field-side copper remain controlled. Each ISO output now reaches its own `SN74LVC1G125DBVR` input through 1.50 kohm and is biased low by 47.0 kohm. Each buffer output reaches the existing JLOGIC1 signal through 36.5 kohm and is biased low by 330 kohm.

The component-level calculation is constrained to a proposed 3.0-3.6 V interface envelope. It bounds the R208 ISO hard-short defect at 2.424 mA and creates a 0.518 V minimum input-HIGH screen against TI's 2.0 V threshold. The downstream 36.5 kohm resistor limits a 3.6 V hard short to 99.63 uA. This is a design correction, not physical or Raspberry Pi acceptance. Pi 5 header-source limits, RP1 GPIO thresholds/leakage/clamps, installed capacitance/timing, back-power, EMC, thermal and fault-injection evidence remain open.

Each active-low OE pin is hard-connected to `COMPUTE_0V`; software cannot enable or bypass the buffers. Observations remain ordinary diagnostics with zero functional-safety credit. Unknown, invalid or unavailable observations must inhibit ordinary heartbeat/motion authority, and reset or power restoration cannot command motion. All 14 holds and all physical acceptance evidence remain open.
