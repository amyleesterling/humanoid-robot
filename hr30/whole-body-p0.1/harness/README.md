# HR-30 whole-body harness P0.1

**PRELIMINARY - NOT APPROVED FOR CONNECTION, FABRICATION, MOTION OR ENERGIZATION**

This package turns the 25-axis electrical allocation into eight explicit protected bus branches, 25 actuator drops, 33 connector boundaries, 14 controlled harness assemblies and 12 located full-body corridors. It also accounts for every installed equipment item and every current KiCad logical terminal so the missing physical definitions are visible rather than silently omitted. Current primary documentation now closes the candidate STM32 package pins, five isolated RS-485 and three TTL interface-device pinouts, exact controller-side data-only connector families, and actuator-side pin order. Cable assemblies, conductor sizing, protection, termination, shielding, retention, flex life and physical validation remain **SELECTION REQUIRED**.

The 76.08 A figure is only the arithmetic sum of published 12 V momentary stall-current endpoints. It is not expected operating current and must not be used as a fuse, conductor, connector or source rating. A U2D2 Power Hub is limited to 10 A aggregate and is rejected for whole-body or leg power aggregation. U2D2 is retained only as an external single-segment commissioning candidate. The installed geometry instead reserves two four-channel carriers for eight simultaneous independent interfaces; their pin-level device and connector candidates are defined, while the PCB and assembled harness remain unreleased.

The controller data boundary contains reference and data only; it deliberately has no actuator-VDD contact. Standard ROBOTIS X3P/X4P cable families include VDD, so the exact power-injection breakout/cable construction and no-backfeed verification remain open.

<!-- HR30-DISTRIBUTED-POWER-HARNESS-P01-START -->
## Distributed actuator-power successor

The [interactive distributed-power guide](distributed-power-harness-successor-p0.1/index.html) rejects the physically impossible one-jacketed-cable-per-axis bundle. Six local protected nodes feed exact Alpha Wire 12-, 4-, and 2-core candidate trunks with an explicit protected pair for every one of the 25 axes. All six trunk diameter screens fit, and all six now bind to the dimensioned tangent guides in the whole-body route CAD. Protection devices, breakout ECAD, guard and collision sweeps, thermal validation and every powered-work authority remain open.
<!-- HR30-DISTRIBUTED-POWER-HARNESS-P01-END -->

<!-- HR30-POWER-ROUTE-GUIDES-P01-START -->
## Neutral whole-body power-route envelopes

The [neutral power-route guide](power-route-guides-p0.1/index.html) retains six editable tangent 3D centerlines as fixed-pose planning evidence. The continuous whole-limb cable/rigid-guard topology is rejected; use the articulated-power-harness successor for moving joints.
<!-- HR30-POWER-ROUTE-GUIDES-P01-END -->

<!-- HR30-DUTY-CURRENT-P01-START -->
## Bounded current-duty envelope

The [interactive duty-current envelope](duty-current-envelope-p0.1/index.html) converts the frozen 25-axis whole-body control commands into 50 Hz torque-producing current equivalents and per-axis/per-bus peak, P95, RMS and mean evidence. Active gripping, idle current, losses, transients, regeneration, faults, robustness and thermal correlation remain open, so the result does not release wires, connectors, protection or a source.
<!-- HR30-DUTY-CURRENT-P01-END -->

<!-- HR30-DUTY-THERMAL-P01-START -->
## Route-specific duty and thermal planning

The [interactive duty/thermal screen](duty-thermal-screen-p0.1/index.html) binds the two frozen whole-body sequence traces to all 25 routed actuator power pairs, eight electrical buses and every reserved power corridor. It supplies bounded torque-current drop/loss and bundle test cases, while keeping total normal current, CF130 resistance, hot ampacity, faults, protection and all powered work open.
<!-- HR30-DUTY-THERMAL-P01-END -->

<!-- HR30-ARTICULATED-POWER-HARNESS-P01-START -->
## Articulated power harness

The [articulated power-harness candidate](articulated-power-harness-p0.1/index.html) rejects a rigid whole-limb cable guard. It defines 25 passive tap-board envelopes, 45 four-conductor flat-cable joint crossings, and separate rigid-link/flexible-joint guard solids. Every protected pair remains electrically independent. Full-pose collision, bend/torsion life, termination, derating and physical validation remain open.
<!-- HR30-ARTICULATED-POWER-HARNESS-P01-END -->
