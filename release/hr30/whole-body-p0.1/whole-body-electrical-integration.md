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

Current official ROBOTIS manuals now close only the actuator-side pin order and listed connector piece parts: RS-485 pin 1 GND, 2 VDD, 3 DATA+, 4 DATA- using the EHR-04/B4B-EH-A family; XC330 TTL pin 1 GND, 2 VDD, 3 DATA using EHR-03/B3B-EH-A; both list SEH-001T-P0.6 contacts and 21 AWG DYNAMIXEL wire. This allocation does **not** select eight controller interfaces or release wiring. Exact controller boards/transceivers, isolation, voltage-domain compatibility, direction control, controller pins/connectors, assembled cables, termination, bias, protection, shield/return treatment, grounding, application conductor sizing, routing, actuator IDs, bus timing and failure behavior remain **SELECTION REQUIRED**.

The P0.1 candidate uses one separately protected power branch per bus segment, not 25 independently protected actuator feeds. Axes listed on one bus may share that segment VDD; no cable or breakout may connect VDD between different protected segments. Exact branch analysis, connector/breakout design and physical no-backfeed verification remain required before connection.

## Relationship to KiCad

The historical `project-button-v2` native KiCad package is mixed HR-V0/HR-30 preliminary architecture and is **not synchronized** to this eight-segment whole-body allocation. A new HR-30-only native KiCad reconciliation must bind all 25 axes, selected interface devices, pins, connectors, protection, grounding, cable/shield rules and shutdown behavior. Until that work exists and receives qualified review, this package grants no connection, powered-test, motion, or energization authority.

## Primary manufacturer evidence

The protocol classification is taken from current official ROBOTIS e-Manual pages recorded in `actuator-bus-source-register.csv`, accessed 2026-08-14. The web manuals did not expose an explicit publication revision/date in the verified page content, so that field remains unresolved rather than inferred.
