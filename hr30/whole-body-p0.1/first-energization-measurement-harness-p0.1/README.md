# HR-30 first-energization measurement harness P0.1

**PRELIMINARY - UNBUILT MEASUREMENT HARNESS - ZERO SAFETY CREDIT - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, WALKING OR ENERGIZATION**

This package replaces the earlier generic DAQ-end labels with a complete NI-side cable candidate. Eight separate Alpha Wire 5610B2201 twisted pairs carry the sixteen analog conductors from panel J1O-J8O to two NI-9229 modules through NI-9976 plugs and NI-9971 backshells. No analog signal or return is shared. The independent battery-slate cable maps JTTL.1 to NI-9924 terminal 14 / NI-9401 DIO0, JTTL.2 to terminal 1 / COM, its drain to SH, and leaves terminal 15 empty; NI ferrite 782803-01 is required adjacent to the module.

The package also corrects ambiguous instrumentation names: channel 6 is the PNOZ `HARDWIRED_PERMIT`, and channels 7/8 are K1/K2 coil voltages rather than unspecified “coil or mirror” points. The exact HR-30 logical nodes are selected, but the robot and source panels still lack released guarded, source-proximal, short-protected diagnostic terminals. The cable assemblies are unbuilt, inspections and calibration are unexecuted, FER-G11 remains open, and no work authority follows.
