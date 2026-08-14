# HR-30 actuator-interface carriers P0.1

**PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, MOTION OR ENERGIZATION**

This package advances the whole humanoid's eight actuator buses to two dimensioned, routed native KiCad PCB candidates. Carrier A contains four complete ISOW1432 RS-485 application channels. Carrier B contains one complete ISOW1432 channel and three SN74LVC1T45 translator channels. Both boards are 82 x 42 mm, use six copper layers, retain data-only field connectors, and regenerate from the source tool.

KiCad 10 verifies schematic ERC at 0 errors / 0 warnings and both boards at 0 DRC violations / 0 unconnected pads. The deterministic route uses four internal signal layers with 0.15 mm general traces, 0.20 mm return/power-related traces, and 0.35/0.15 mm through vias. Five native all-copper rule areas preserve 4.0 mm isolation moats across the ISOW1432 barriers. The native boards bind the manufacturer-published JLC06161H-3313 nominal 1.6 mm six-layer candidate; the published copper/dielectric buildup totals 1.5384 mm before solder mask.

The machine-readable Gerber, Excellon, IPC-D-356, position and board-statistics outputs are fabrication candidates for inspection and DFM quotation only. They are explicitly not released for ordering. DRC completion does not establish independent design acceptance, controlled impedance, enclosure fit, cable retention, surge/miswire behavior, timing, waveform integrity, EMC, thermal performance, fault safety or permission for any powered test.

Open `index.html` for the interactive layer-by-layer guide.
