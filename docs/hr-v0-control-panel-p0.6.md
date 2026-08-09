# HR-V0 control-panel and compute-installation candidate P0.6

> **PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TEST, OR ENERGIZATION.**

Identifier: `HR-V0-CP-P0.6`

Compute installation: `HR-V0-COMPUTE-INSTALL-P0.1`

Date: 2026-08-08

Electrical baseline: `Project Button Electrical V3-P1.14`

## Correction

The P0.5 panel was not large enough to add an honest Raspberry Pi case, U2D2 retention and cable-retention allocation while preserving its protection and selection reserves. P0.6 therefore supersedes P0.5 as the current physical-layout candidate and enlarges only the enclosure/backplate branch:

- enclosure: Hammond `PJ302410RT`, nominal 762 x 610 x 257 mm outside;
- inner panel: Hammond `18P2721`, nominal 685.8 x 533.4 mm; and
- the existing P0.5 component coordinates remain inherited in the upper-left region while a separated right-side compute column and an unallocated lower reserve are added.

The larger enclosure is an exact catalog candidate on hold, not an approved purchase. Its wall/support design, received dimensions, door geometry, modified Type/IP status, thermal behavior, bonding and qualified application review remain open.

## Compute installation candidate

P0.6 adds these exact held candidates:

| Reference | Candidate | Controlled catalog fact | Remaining physical proof |
|---|---|---|---|
| CCASE1 | Waveshare `PI5-CASE-D`, SKU `26087` | metal Pi 5 case; official Active Cooler listed; included bracket for 35 mm guide rail; published outer envelope 90.5 x 87 x 49.5 mm | received hardware identity; Active Cooler-specific assembly clarification; rail offset/retention; grounding/EMC; airflow and thermal test |
| U2D2 | ROBOTIS `902-0132-000` | 48 x 18 x 14.9 mm, 9 g; current units stated as Type-C from August 2025 | received revision/cable; reference-voltage review; physical retention; waveform/no-backfeed/HIL |
| GTM1-3 | HellermannTyton `GTM500C2`, article `130-95000` | nonadhesive screw-mount 0.5-inch Grip Tie base; 63.5 x 25.4 mm | panel fastener/torque; rigid-device and cable-loop application; pull/slip/vibration/abrasion |
| GT1-3 | HellermannTyton `GT.50X80C2`, article `854-44353` | releasable 203.2 x 12.7 mm hook-and-loop strap | compression, overlap, port clearance, service life and qualified application acceptance |

One base/strap pair is allocated around the U2D2 body. Two pairs are allocated for the compute-power and Pi-to-U2D2 cable service loops. HellermannTyton publishes the strap system for cables; it does not publish the rigid U2D2 application. P0.6 therefore takes no retention credit until received-article pull, slip, vibration, abrasion, connector-load and repeated-service tests are accepted.

The current U2D2 e-Manual says the product connects with an enclosed USB cable and that current production changed to Type-C in August 2025. It does not identify the enclosed cable's host connector, length, shielding or outside diameter in the controlled text. R122 separately advances `BOM-070` to an exact held StarTech.com `USB2AC50CM` candidate through `HR-V0-U2D2-USB-P0.1`; no received fit, bend/retention, electrical/EMC/HIL or USB cable route is released.

The compute heartbeat, U2D2 path and every retention candidate retain **zero functional-safety credit**.

## Layout basis

`backplate-layout.csv` controls 26 planning rectangles. All lie inside the nominal 533.4 x 685.8 mm inner-panel boundary. This is a two-dimensional catalog-envelope screen only:

- the dedicated compute column is separated from the inherited device area by `WD2`;
- `DR4` is a 100 mm planning segment of the R123 exact held Phoenix Contact `1207648` unperforated `NS 35/7.5` rail candidate; its end retention remains `SELECTION REQUIRED`;
- CCASE1, the U2D2 retention base and two cable-loop bases have separate envelopes;
- 323.8 x 142.4 mm of added lower area remains visibly unallocated; and
- no hole, cut length, fastener, conductor, cable entry or cable route is released.

The catalog screen does not establish bracket offset, rail engagement, depth, connector overhang, bend radius, duct fill, service-tool access, door closure, heat rise, grounding or EMC.

## Sources

- Hammond `PJ302410RT` product page and drawing, drawing issue 2014-06-13, rechecked 2026-08-08: <https://www.hammfg.com/part/PJ302410RT>
- Hammond current PJRT / 18P compatibility records, rechecked 2026-08-08: <https://www.hammfg.com/electrical/products/accessories/18p>
- Waveshare `PI5-CASE-D` product page and dimension image, no formal revision stated, rechecked 2026-08-08: <https://www.waveshare.com/pi5-case-d.htm>
- ROBOTIS U2D2 e-Manual, no formal revision stated, rechecked 2026-08-08: <https://emanual.robotis.com/docs/en/parts/interface/u2d2/>
- HellermannTyton `GTM500C2`, no formal revision stated, rechecked 2026-08-08: <https://www.hellermanntyton.us/products/130-95000/>
- HellermannTyton `GT.50X80C2`, no formal revision stated, rechecked 2026-08-08: <https://www.hellermanntyton.us/products/854-44353/>

## Required closure evidence

1. Receive and identify every exact candidate, including U2D2 connector revision and every supplied screw/standoff.
2. Obtain written Waveshare clarification or a controlled received-article assembly trial showing `SC1148` installation without invented hardware.
3. Measure the enclosure, panel, case, bracket, ports and cables; update the three-dimensional fit model and hole schedule.
4. Select rail ends, panel fasteners, retention hardware and cable entries; receive and prove the exact USB cable against measured fit, bend, pull, connector-load, thermal, electrical and EMC evidence.
5. Execute unpowered rail-pull, U2D2 slip/pull/vibration, cable-pull, abrasion, access and closed-cover inspections.
6. Resolve metal-case, steel-panel, rail, PE/DC 0 V and shield treatment through the current grounding/bonding package and qualified review.
7. Close duct fill, cable separation, installed current, brownout, blocked-fan, worst-case ambient and calibrated enclosure temperature-rise evidence.
8. Close the applicable procurement, fabrication, electrical, commissioning and functional-safety gates before any work authorization.

Passing repository checks proves source, BOM and coordinate consistency only. It does not prove fit, retention, thermal performance, EMC, functional safety or permission to build or energize.
