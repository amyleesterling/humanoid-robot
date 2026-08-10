# HR-V0 E2 control-only hardware slice P0.4

Status: **PRELIMINARY - NOT APPROVED FOR FABRICATION OR ENERGIZATION**

Identifier: `HR-V0-E2-HW-P0.4`

P0.4 supersedes the P1.14-bound P0.3 slice. R195 directly binds the first control-only commissioning configuration to `Project Button Electrical V3-P1.15-CARRIER-CANDIDATE`, `PCB-P1.0`, `HR-V0-WD-PCBA-DATA-P0.2` and current `HR-V0-WD-CAM-P0.2`. Historical `HR-V0-E2-P115-PARITY-P0.1` remains audit evidence rather than a current dependency.

The configuration retains 23 installed/absent/DNP/selection rows, six exact XT1 position candidates, three source-domain rows and twelve blocking holds. Only the held 24 V control and 5.1 V compute domains may eventually be considered under a separately authorized E2 procedure.

The 12 V actuator source, F0/SD1, F1/F2/F3, all three P0.3 limiter carriers, DXL-STAR-P0.2, U2D2 power path, actuator branches and actuator connectors must remain physically absent or unwired, covered, labelled and proven dead. K1/K2 load poles remain unsourced and unwired.

P0.4 is a configuration input, not an assembly instruction or test authorization. Received identities, RESET/ARM/H1 maps, F24 and relay protection, conductors, enclosure/bonding, watchdog PCBA manufacture, firmware/HIL, instruments/limits, physical actuator exclusion and four-role authorization remain open.

Interactive guide: `release/hr-v0/e2-hardware-p0.4/HR-V0_e2-hardware-guide.html`.
