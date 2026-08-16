# HR-30 motion controller P0.1

**PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION OR ENERGIZATION**

This package is the editable six-sheet KiCad schematic and routed 82 x 42 mm six-layer PCB candidate for the deterministic STM32H743 local motion layer. It binds all eight actuator-bus UART groups to the two carrier connectors, implements a fixed 3.3 V converter candidate, and includes MCU supply, VCAP, analog rail, reset, boot, SWD, hardwired status and structured-action interfaces.

The connector mapping is an explicit project-owned interface: contact 1 is controller ground, contact 2 is controller 5 V and contact 3 is controller 3.3 V on both carrier connectors. No carrier contact carries actuator VDD. The prior PE7/PE8/PE9 package-number defect is corrected to LQFP144 pins 58/59/60.

The schematic is ERC 0/0. The PCB is deliberately blocked with 112 DRC violations and 2 unconnected items; the complete native report is retained in `validation/hr30-motion-controller-p0.1-drc.rpt`. The layout is not fabrication-ready. The MCU does not implement a validated safety function. No output authorizes ordering, fabrication, assembly, connection, powered testing, motion or energization.
