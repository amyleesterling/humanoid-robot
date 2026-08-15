# R203 independent review request

**PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION**

Review `HR-V0-RUNTIME-OBS-PINMAP-P0.1` as a source-level, diagnostic-only Raspberry Pi 5 GPIO allocation candidate. It carries zero functional-safety credit and does not authorize procurement, harness construction, connection, powered test, motion or energization.

Please independently reproduce and challenge:

1. the physical-pin, BCM GPIO, signal and polarity mapping for heartbeat GPIO17 and observation GPIO22/GPIO23/GPIO24/GPIO25;
2. consistency among `JLOGIC1`, the electrical schedules, the allocation CSV, host config, host tests, release metadata, guide and handoff;
3. the requirement that `enable_jtag_gpio=1` is prohibited for this allocation and that all other boot-overlay/alternate-function conflicts are resolved on the exact target image;
4. the fail-closed treatment of `gpio_chip_path`, OS/kernel/libgpiod identity and runtime line ownership as `SELECTION REQUIRED`;
5. Raspberry Pi reset/high-impedance behavior, pulls, 3.3 V-only GPIO limits, current constraints and back-power/sequencing risk against the cited official records;
6. whether active-high observation polarity is preserved from ISO1212 output through the Pi input without creating a false safe-state interpretation;
7. connector, contact, wire, shield, return, strain-relief, routing, creepage/clearance and enclosure evidence still needed for a buildable harness;
8. the distinction between diagnostic observation and credited safety action, including whether any single GPIO, daemon or host failure can be mistakenly treated as motion permission;
9. preflight exit 78 with 36 current holds and the absence of any route to motion authority while a selection remains open; and
10. the responsive web guide at desktop and narrow-mobile widths, including 16 px body, 14 px secondary and 12 px absolute minimum text rules.

Do not close Sol R12 or an energization gate from source checks alone. Require target readback, physical measurements, fault injection, qualified electrical review and configuration-specific authorization before changing any evidence state.
