# HR-V0 P1.21 protected-routing segregation hardware P0.1

> **PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION**

Identifier: `HR-V0-P121-SEGREGATION-HW-P0.1`

Review round: R241

Date: 2026-08-11

## Result

R241 replaces the undocumented idea of an internal wire-duct divider with a separate, exact catalog candidate: Phoenix Contact `CD 25X25`, item `3240187`, a PVC base-and-cover duct with a 25 x 25 x 2000 mm catalog envelope. The current official US product page was rechecked on 2026-08-11.

The proposed `WD5` planning envelope is x=54.0..423.8 mm and y=10.0..35.0 mm. It is 369.8 mm long, stays inside the 533.4 x 685.8 mm usable backplate, leaves a nominal 10 mm gap to DR1 and 20 mm to the device region, and intersects WD2 only in an explicitly held 40 x 25 mm junction zone.

Existing 40 x 40 mm `DUCT-A` item `3240189` stock cannot supply WD5: WD1-WD4 already consume 1979.2 mm of the 2000 mm article, leaving 20.8 mm before kerf. A separate 3240187 article would leave 1630.2 mm before kerf after the planning piece. This is not a cut plan or purchase release. The application quantity of one is not the manufacturer packing/minimum-order quantity of 24.

## Source facts and boundaries

Phoenix Contact publishes 327 mm2 usable cross-section and an example of ten 3.4 mm-diameter cables at 60 percent fill for item 3240187. Project Button has not selected the seven conductors' exact family, gauge, outside diameter, insulation, bend, termination or derating conditions. The catalog example therefore does not close duct fill or thermal loading.

No current reviewed primary source establishes an internal divider or a released WD5-to-WD2 T-junction for this application. Exact breakout, rib removal, edge treatment, cover access, retaining clips, fastening, labels, separation and mixed WD2 occupancy remain `SELECTION REQUIRED`.

The duct body is a routing candidate, not a safety component. It receives no safety credit and no numeric functional-safety separation is claimed.

Primary sources:

- [Phoenix Contact CD 25X25 item 3240187](https://www.phoenixcontact.com/en-us/products/wiring-duct-cd-25x25-3240187), official US page accessed 2026-08-11.
- [Phoenix Contact CD 40X40 item 3240189](https://www.phoenixcontact.com/en-us/products/wiring-duct-cd-40x40-3240189), official US page accessed 2026-08-11.

## Configuration result

`BOM-096` records the exact 3240187 candidate on hold. `HR-V0-CONFIG-REC-P0.5` supersedes P0.4 only as the current reconciliation and covers 96 BOM groups. P0.4 remains an immutable R223 snapshot. P1.15 remains current; P1.21 remains unaccepted.

Nine R241 holds and eight blank inspections remain open. No conductor, junction, cut, fastener, label, received article, installation, physical result, qualified review or work authorization exists.
