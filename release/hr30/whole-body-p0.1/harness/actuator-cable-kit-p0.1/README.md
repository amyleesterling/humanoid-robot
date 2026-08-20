# HR-30 actuator cable kit P0.1

**PRELIMINARY - UNBUILT ACTUATOR CABLE-KIT CANDIDATE - NOT APPROVED FOR PROCUREMENT, FABRICATION, CONNECTION, POWERED TESTING, MOTION OR ENERGIZATION**

This package defines all 25 actuator-power branches as a moving igus CF130.03.02.UL pair ending at a fixed, panel-mounted Molex Micro-Fit 3.0 transition, followed by a restrained Alpha Wire 3051 pigtail into the JST EH actuator housing. Direct CF130-to-JST crimping is rejected. All eight actuator buses now bind to the proposed PDU_COMMON_RET single-point reference: each actuator references the star through its own branch return; every inter-actuator GND and VDD cavity remains empty so the data harness cannot become a parallel motor-current return. Five RS-485 carrier channels are isolated; the three TTL channels are not. Common-mode, TTL margin, regeneration, open-return faults, received fit, crimp, derating, temperature rise, flex life and every physical work authority remain open.
