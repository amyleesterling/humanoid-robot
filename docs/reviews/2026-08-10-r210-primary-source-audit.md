# R210 primary-source audit and correction disposition

**PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION**

R210 independently rechecked the new R209 buffer and resistor assumptions against current official Texas Instruments and Panasonic records. This is a project-owned source audit, not an independent or qualified electrical review.

## Findings

1. **BLOCKER — incorrect DBV land geometry.** R209 encoded five 1.20 x 0.70 mm lands with 2.20 mm between row centers. TI's current DBV0005A example, drawing 4214839/K dated August 2024, specifies five 1.10 x 0.60 mm lands, 0.95 mm pitch, 1.90 mm span along the three-pin row and 2.60 mm between row centers. R209/P0.3 is superseded for current fabrication review.
2. **MAJOR — insufficient GPIO fault-current margin.** R209's 36.5 kohm candidate produced 99.63 uA at 3.6 V and -1% tolerance, leaving only 0.37 uA below TI's 100 uA VOH/VOL characterization point before temperature effects. P0.4 uses exact Panasonic `ERJ6ENF3902V` 39.0 kohm and includes its +/-100 ppm/K TCR over -40 to 125 C, producing a 94.18 uA screen.
3. **VERIFIED — buffer electrical table.** TI SCES223T Rev T specifies VIH 2.0 V and VIL 0.8 V for 3.0–3.6 V, VOH at least VCC-0.1 V and VOL at most 0.1 V at 100 uA, maximum ICC 10 uA, maximum delta-ICC 500 uA for one input at VCC-0.6 V, input capacitance 4 pF, and -40 to 125 C operation. R210 uses those rows without assigning Raspberry Pi GPIO acceptance.

## Corrected analytical screens

- ISO-side hard short: 2.449 mA using 1% tolerance plus +/-100 ppm/K temperature allowance;
- buffer-input HIGH floor: 2.516 V;
- GPIO-side hard short: 94.18 uA using the same allowance;
- cable-side source-HIGH screen: 2.582 V using TI's VCC-0.1 V row; and
- steady 3V3 screen: 6.183 mA excluding switching current.

These corrections close only the two source-encoding defects in the current candidate. DFM, solder process, received components, Raspberry Pi limits, installed timing, EMC, thermal, fault injection and qualified review remain open.

Primary sources:

- Texas Instruments, `SN74LVC1G125`, SCES223T Rev T, including DBV0005A drawing 4214839/K: <https://www.ti.com/lit/ds/symlink/sn74lvc1g125.pdf>
- Texas Instruments active product record: <https://www.ti.com/product/SN74LVC1G125>
- Panasonic `ERJ6ENF3902V` product record: <https://industrial.panasonic.com/ww/products/pt/general-purpose-chip-resistors/models/ERJ6ENF3902V>
