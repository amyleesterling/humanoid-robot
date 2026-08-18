# HR-30 whole-body harness P0.1

**PRELIMINARY - NOT APPROVED FOR CONNECTION, FABRICATION, MOTION OR ENERGIZATION**

This package turns the 25-axis electrical allocation into eight explicit protected bus branches, 25 actuator drops, 33 connector boundaries, 14 controlled harness assemblies and 12 located full-body corridors. It also accounts for every installed equipment item and every current KiCad logical terminal so the missing physical definitions are visible rather than silently omitted. Current primary documentation now closes the candidate STM32 package pins, five isolated RS-485 and three TTL interface-device pinouts, exact controller-side data-only connector families, and actuator-side pin order. Cable assemblies, conductor sizing, protection, termination, shielding, retention, flex life and physical validation remain **SELECTION REQUIRED**.

The 76.08 A figure is only the arithmetic sum of published 12 V momentary stall-current endpoints. It is not expected operating current and must not be used as a fuse, conductor, connector or source rating. A U2D2 Power Hub is limited to 10 A aggregate and is rejected for whole-body or leg power aggregation. U2D2 is retained only as an external single-segment commissioning candidate. The installed geometry instead reserves two four-channel carriers for eight simultaneous independent interfaces; their pin-level device and connector candidates are defined, while the PCB and assembled harness remain unreleased.

The controller data boundary contains reference and data only; it deliberately has no actuator-VDD contact. Standard ROBOTIS X3P/X4P cable families include VDD, so the exact power-injection breakout/cable construction and no-backfeed verification remain open.
