# HR-30 whole-body electrical integration P0.1

**PRELIMINARY - CONFIGURATION AND PACKAGING CAD ONLY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, POWERED TESTING, MOTION, OR ENERGIZATION**

## What changed

The 25-axis candidate population is not one electrical protocol. The nineteen selected `-R` XH540/XM540/XM430 candidates are assigned to five RS-485 half-duplex segments. The six XC330 candidates are assigned to three TTL half-duplex segments. Every axis appears exactly once in `actuator-bus-axis-binding.csv`.

| Segment | Protocol | Axes | Role |
|---|---:|---:|---|
| RS-LLEG / RS-RLEG | RS-485 | 6 + 6 | independently serviceable left and right legs |
| RS-LARM / RS-RARM | RS-485 | 3 + 3 | proximal arms only |
| RS-WAIST | RS-485 | 1 | waist yaw |
| TTL-LDIST / TTL-RDIST | TTL | 2 + 2 | wrist and gripper on each side |
| TTL-HEAD | TTL | 2 | head pan and tilt |

## Physical implementation boundary

Current primary manufacturer documentation closes the actuator-side pin order and listed connector piece parts: RS-485 pin 1 GND, 2 VDD, 3 DATA+, 4 DATA-; TTL pin 1 GND, 2 VDD, 3 DATA. It also closes the STM32H743ZIT6 LQFP144 UART package pins, five ISOW1432DFMR isolated RS-485 device pinouts, three SN74LVC1T45DCKR 3.3/5 V translator pinouts, and eight exact JST GH data-only field connector candidates. The field connectors intentionally contain reference and data only, with no actuator-VDD contact. PCB layout/passives, assembled cables, actuator power-injection breakout, termination, bias, protection, shield/return treatment, grounding, application conductor sizing, routing, actuator IDs, bus timing, EMC and failure behavior remain **SELECTION REQUIRED**.

The P0.1 candidate now allocates one separately protected power feed per actuator. Axes listed on one bus share only reference and data; they do not share VDD. Standard ROBOTIS X3P/X4P cables include VDD and therefore require a custom/de-pinned data-only construction or breakout. Exact protection values, connector/breakout design and physical no-backfeed verification remain required before connection.

## Relationship to KiCad

The HR-30-only native KiCad project now binds all 25 axes and the eight sourced pin-level interface candidates across nineteen populated sheets with ERC 0/0. That is encoded connectivity and annotation evidence only. Carrier PCB passives/layout, protection, grounding, cable/shield rules, timing, shutdown behavior and physical fault validation remain open, so this package grants no connection, powered-test, motion, or energization authority.

## Primary manufacturer evidence

The protocol classification is taken from current official ROBOTIS e-Manual pages recorded in `actuator-bus-source-register.csv`, accessed 2026-08-14. The web manuals did not expose an explicit publication revision/date in the verified page content, so that field remains unresolved rather than inferred.
