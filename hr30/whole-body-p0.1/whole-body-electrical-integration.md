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

This allocation does **not** select eight controller interfaces or release wiring. Exact controller boards/transceivers, isolation, voltage-domain compatibility, direction control, pins, mating connectors, termination, bias, protection, shield/return treatment, grounding, cable type, routing, actuator IDs, bus timing and failure behavior remain **SELECTION REQUIRED**.

The intended harness separates communication from branch-power distribution. A data daisy chain must not connect actuator VDD between independently protected power branches. An exact connector/breakout design and manufacturer-supported implementation must prove that boundary before connection.

## Relationship to KiCad

The historical `project-button-v2` native KiCad package is mixed HR-V0/HR-30 preliminary architecture and is **not synchronized** to this eight-segment whole-body allocation. A new HR-30-only native KiCad reconciliation must bind all 25 axes, selected interface devices, pins, connectors, protection, grounding, cable/shield rules and shutdown behavior. Until that work exists and receives qualified review, this package grants no connection, powered-test, motion, or energization authority.

## Primary manufacturer evidence

The protocol classification is taken from current official ROBOTIS e-Manual pages recorded in `actuator-bus-source-register.csv`, accessed 2026-08-14. The web manuals did not expose an explicit publication revision/date in the verified page content, so that field remains unresolved rather than inferred.
