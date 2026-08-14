# HR-30 actuator-interface carriers P0.1

**PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, MOTION OR ENERGIZATION**

This package advances the whole humanoid's eight actuator buses from pin-level blocks to two dimensioned native KiCad PCB placement candidates. Carrier A contains four complete ISOW1432 RS-485 application channels. Carrier B contains one complete ISOW1432 channel and three SN74LVC1T45 translator channels. Both boards are 82 x 42 x 1.6 mm, use six copper layers, retain data-only field connectors, and include exact footprints, board outlines, placement, ratsnest and SVG inspection outputs.

The RS-485 channels include TI-required local bypassing, separate VISOOUT/VISOIN and GND2/GISOIN ferrites, an SM712 bus-protection candidate, and a default-open 120-ohm termination configuration. The TTL channels include dual-rail bypassing, a receive-default direction pulldown, 33-ohm series candidate, TPD1E10B06 ESD candidate and a DNP idle pull-up.

An automated via-in-pad route was generated during development and rejected after KiCad reported shorts and clearance failures. Those tracks and vias are not retained. The native boards intentionally preserve the unrouted ratsnest and deterministic lane reservations so the remaining work is visible. DRC output is evidence, not approval. Copper routing, isolation geometry, enclosure fit, cable retention, surge/miswire behavior, timing, waveform integrity, EMC, thermal performance and every powered test remain open.

Open `index.html` for the readable interactive guide.
