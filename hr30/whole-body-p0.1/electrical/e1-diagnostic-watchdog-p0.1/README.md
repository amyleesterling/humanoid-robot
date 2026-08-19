# HR-30 E1 diagnostic watchdog P0.1

**PRELIMINARY - DIAGNOSTIC ONLY - ZERO SAFETY CREDIT - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION OR ENERGIZATION**

This package contains a native KiCad schematic and routed 40 x 25 mm two-layer diagnostic adapter using the exact TI TPS3431SDRBR candidate. It observes MOTION_WD_HEARTBEAT, forces the controller permit input low, and exposes WDO_N/ENOUT only at local test pads. JIO1 contacts 4, 6, 7 and 8 are physically absent from the fixture cable. It contains no actuator interface or actuator-power path.

The open CWD pin and high SET1 select TI's 1360/1600/1840 ms minimum/typical/maximum preset. Native ERC/DRC validate encoded connectivity only. The board/cable are unbuilt, HIL is unexecuted, the circuit receives zero functional-safety credit, and every work authority remains false.
