# HR-V0 Q4X box physical-layout candidate P0.1

> **PRELIMINARY - DIMENSIONAL REVIEW CANDIDATE ONLY - NOT APPROVED FOR PROCUREMENT, FABRICATION, DRILLING, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION**

Artifact: **HR-V0-Q4X-BOX-LAYOUT-P0.1**

Round: **R185**

Date: **2026-08-10**

## Outcome

R185 converts R184's incomplete enclosure-layout row into a dimensioned panel-layout candidate and a precise drilling hold. It corrects the `14F0907` short side from the R184 value of 174.75 mm to the manufacturer drawing/STEP value of 174.498 mm. The panel is represented as 174.498 x 222.250 x 3.175 mm with four 6.350 mm catalog holes on 158.750 x 209.550 mm centers.

The proposed 150.000 mm Phoenix `1207650` rail is centered on the panel. Its nominal end clearance is 12.249 mm per side. Two `CLIPFIX 35` brackets, one 6.2 mm PTCB, six 5.2 mm terminal bodies and two 2.2 mm end covers sum to a 60.800 mm catalog-width envelope, leaving 56.849 mm nominal panel-edge clearance per side when centered. These are arithmetic and catalog-geometry screens, not installed-fit proof.

## Why the gland holes remain blank

LAPP publishes the exact `53111000` M12x1.5 gland geometry, 8 mm thread length, 16.6 mm body diameter and 3.5-7 mm cable range. It also publishes the `53119000` M12x1.5 locknut as 17 mm across flats, 18.7 mm across corners and 5 mm thick. The checked manufacturer records do not publish a Project Button through-bore tolerance or safe coordinate through the molded `PJ1084T` wall.

R185 therefore releases no bore diameter and no G1/G2 coordinates. The received enclosure must be surveyed for flat wall, ribs, bosses, feet, hinge/latch interference and local thickness. The received rail must likewise establish the realized slot offset before fastener coordinates exist. Qualified mechanical/electrical review must then accept the drilling drawing, hardware stack, torque, edge treatment, ingress/thermal consequences and inspection plan.

## Controlled artifacts

- dimension, source, layout, vendor-hash and hold registers: `test-equipment/hr-v0/q4x-box-layout-p0.1/`;
- review-native SVGs and proxy CAD source: `cad/hr-v0-q4x-box-layout-p0.1/`;
- blank received-article inspection form: `tests/forms/hr-v0-q4x-box-layout-inspection-p0.1.csv`; and
- interactive guide: `release/hr-v0/q4x-box-layout-p0.1/index.html`.

## Review effect

All twelve `QLH-*` holds remain open. R185 closes no Sol R12 blocker, no energization gate and no physical-work authorization. `EG-025` remains open and `EG-026` remains partial. The package provides a better review target; it is not a drill template or assembly instruction.
