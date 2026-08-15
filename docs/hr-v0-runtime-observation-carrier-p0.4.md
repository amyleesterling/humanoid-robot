# HR-V0 source-audited buffered runtime-observation carrier R210 / P0.4 / PCB-P0.3

**PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION**

R210 supersedes P0.3 for current review. The R209 electrical architecture is retained, but its project-owned DBV land pattern was not equal to TI drawing 4214839/K: R209 encoded 1.20 x 0.70 mm lands on 2.20 mm row spacing, while TI's current example specifies 1.10 x 0.60 mm lands on 2.60 mm row spacing. P0.4 corrects that native footprint and preserves the four independent `SN74LVC1G125DBVR` channels, connector numbering, field networks, board outline, mounting datums, planes and isolation corridor.

P0.4 also replaces the 36.5 kohm GPIO series candidate with exact Panasonic `ERJ6ENF3902V` 39.0 kohm. The R209 99.63 uA hard-short result left only 0.37 uA below TI's 100 uA output-level characterization point before temperature effects. R210 includes 1% resistance tolerance and +/-100 ppm/K over -40 to 125 C: the ISO-side short screen is 2.449 mA, the GPIO-side screen is 94.18 uA, the buffer-input HIGH floor is 2.516 V, the cable-side source-HIGH screen is 2.582 V, and the conservative steady 3V3 screen is 6.183 mA. These are analytical component screens, not Raspberry Pi acceptance.

Pi 5 header-source capability, RP1 GPIO thresholds/leakage/clamps, installed capacitance and timing, back-power, DFM, assembly, EMC, thermal, received-part, first-article, fault-injection and qualified-review evidence remain open. Every observation is an ordinary diagnostic with zero functional-safety credit. All fourteen holds remain open and no procurement, fabrication, connection, powered test, motion or energization is authorized.
