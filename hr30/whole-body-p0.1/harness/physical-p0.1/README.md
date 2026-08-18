# HR-30 whole-body physical harness P0.1

**PRELIMINARY - PHYSICAL HARNESS ARCHITECTURE ONLY - NOT APPROVED FOR PROCUREMENT, FABRICATION, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION**

This is the first complete physical translation of the HR-30 logical wiring architecture. It binds all **25 joints**, **8 actuator buses**, **64 installed equipment items**, and **667 current ECAD logical terminals** to a controlled harness architecture.

It contains 12 body corridors plus 50 explicit moving-joint power/data loops (62 route segments and 124 route points). All 62 registered routes are also exported as named editable STEP solids and as one interactive GLB in a recognizable 762 mm body context. Those rods are route centerlines—not selected cable diameters, bundle clearances, or bend-radius releases. Each actuator has a known device-side contact map, a branch-power relationship, a data-link boundary, a moving-loop obligation, retention obligation, derating inputs, and an inspection path.

The architecture now defines one two-conductor power pair per actuator and a serial data chain for each bus. Every actuator input housing receives its own return, VDD, and data contacts. Every inter-actuator outgoing housing populates only the data contacts: GND and VDD cavities remain empty, so no power current is daisy-chained through a preceding actuator connector. This controlled split-harness is the P0.1 construction candidate; crimp tooling, conductor selection, cavity inspection, no-backfeed tests, and fault injection remain required before release.

Every moving actuator-power pair now ends at a fixed-side panel transition: igus CF130.03.02.UL enters Molex 430250200 with 430300001 contacts, mates to panel-mount 430200200 with 430310001 contacts, and continues through a restrained Alpha Wire 3051 pigtail to JST EH. Direct CF130-to-JST crimping is rejected. The exact 25 transition candidates are in `actuator-power-transition-register.csv`; CF130 core OD, bracket/fastener CAD, pigtail length, crimp qualification, derating, pull, temperature-rise and flex tests remain open.

The 71.88 A figure is only the sum of manufacturer 12 V momentary stall-current endpoints for the current 25-axis allocation. It is not expected demand, a conductor rating, a fuse value, or permission to power the robot.

Manufacturer-interface review is now configuration-bound. ROBOTIS publishes the actuator pinouts, but its 21 AWG cable statement conflicts with JST's EH catalog limit of AWG 22 for `SEH-001T-P0.6`, and ROBOTIS's `EHR-03` / `EHR-04` names differ from JST's `EHR-3` / `EHR-4` catalog table. These are not silently normalized: both remain open procurement blockers in `manufacturer-interface-discrepancy-register.csv`. U2D2 is retained only as a single-segment commissioning candidate, and the 10 A U2D2 Power Hub is rejected for whole-body or leg power aggregation.

Open the [interactive physical harness guide](index.html). Start with the whole-body route model, `route-cad-register.csv`, `axis-harness-binding.csv`, `route-segment-register.csv`, `connector-contact-map.csv`, and `unresolved-harness-selections.csv`.

No cable cut length, conductor size, protection value, complete connector set, retention hardware, shielding decision, or powered validation is released by this package.

<!-- HR30-DUTY-THERMAL-P01-START -->
## Duty/thermal successor

The [route-specific duty/thermal successor](../duty-thermal-screen-p0.1/index.html) now fills the bounded torque-producing RMS and peak component for every entry in this package's derating register and groups the 25 pairs by physical power corridor. Total normal RMS, fault current, ambient, hot derating and physical tests remain open.
<!-- HR30-DUTY-THERMAL-P01-END -->
