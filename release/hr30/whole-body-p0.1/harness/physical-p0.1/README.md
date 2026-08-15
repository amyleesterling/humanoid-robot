# HR-30 whole-body physical harness P0.1

**PRELIMINARY - PHYSICAL HARNESS ARCHITECTURE ONLY - NOT APPROVED FOR PROCUREMENT, FABRICATION, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION**

This is the first complete physical translation of the HR-30 logical wiring architecture. It binds all **25 joints**, **8 actuator buses**, **58 installed equipment items**, and **667 current ECAD logical terminals** to a controlled harness architecture.

It contains 12 body corridors plus 50 explicit moving-joint power/data loops (62 route segments and 124 route points). Each actuator has a known device-side contact map, a branch-power relationship, a data-link boundary, a moving-loop obligation, retention obligation, derating inputs, and an inspection path.

The architecture now defines one two-conductor power pair per actuator and a serial data chain for each bus. Every actuator input housing receives its own return, VDD, and data contacts. Every inter-actuator outgoing housing populates only the data contacts: GND and VDD cavities remain empty, so no power current is daisy-chained through a preceding actuator connector. This controlled split-harness is the P0.1 construction candidate; crimp tooling, conductor selection, cavity inspection, no-backfeed tests, and fault injection remain required before release.

The 76.08 A figure is only the sum of manufacturer 12 V momentary stall-current endpoints. It is not expected demand, a conductor rating, a fuse value, or permission to power the robot.

Open the [interactive physical harness guide](index.html). Start with `axis-harness-binding.csv`, `route-segment-register.csv`, `connector-contact-map.csv`, and `unresolved-harness-selections.csv`.

No cable cut length, conductor size, protection value, complete connector set, retention hardware, shielding decision, or powered validation is released by this package.
