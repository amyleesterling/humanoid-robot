# HR-V0 Raspberry Pi observation interface carrier R204 / P0.1 / PCB-P0.1

**PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION**

R204 issues a native two-layer 65.0 x 56.5 mm passive interface-carrier candidate between the Raspberry Pi 5 40-pin header and R202 `JLOGIC1`. It is deliberately **not** a HAT or HAT+: it has no ID EEPROM, no ID-pin copper and no HAT/HAT+ marking. Only physical pins 15, 16, 17, 18, 20 and 22 have nets or routed copper. Pins 2 and 4 have no 5 V copper; the other 32 positions are also no-net/no-copper.

The exact Pi-side socket candidate is Samtec `ESQ-120-33-G-D`. Its `-33` body/stack dimension is 16.13 mm, close to Raspberry Pi's 16 mm ideal Active Cooler spacing recommendation. That does not release the stack: received case, cooler, socket, standoff, screw, seating and board-strain evidence remain open. Samtec's official layout publishes a 1.02 mm finished drill but no copper-land diameter. The encoded 1.70 mm land is therefore project-controlled and requires fabricator DFM acceptance.

The six-position boundary is Phoenix Contact `MKDS 1/6-3,5`, item `1751280`. Six exact Belden `3051` color/order-code candidates are assigned one-for-one to R202 `JLOGIC1`, but every cut length remains `SELECTION REQUIRED` until the observation carrier has a frozen panel location and routing. The proposed termination is direct-stripped 22 AWG, 5 mm strip, no ferrule, at the manufacturer's 0.22-0.25 Nm range. That process still requires received-terminal qualification, pull testing, exposed-strand acceptance and inspection-tool control.

R202 already contains four exact 10 kohm fail-low pulldowns; R204 intentionally adds none. The pinned Raspberry Pi OS image and publisher SBOM remain controlled by `HR-V0-RPI-OS-SBOM-P0.1`; installation, target inventory, gpiochip path, line ownership, physical readback and HIL remain unexecuted.

Native KiCad ERC and DRC both report zero encoded violations. This proves only source connectivity and annotation. The carrier has zero functional-safety credit. All 10 R204 holds remain open, no Sol R12 blocker closes, and there is no procurement, fabrication, assembly, connection, powered-test, motion or energization authority.
