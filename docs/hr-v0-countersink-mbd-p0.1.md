# HR-V0 countersink model-definition correction P0.1

> **PRELIMINARY - NOT APPROVED FOR QUOTATION, FABRICATION, ASSEMBLY, MOTION, OR ENERGIZATION.**

Identifier: `HR-V0-CSK-MBD-P0.1`

Candidate: `HR-V0-ARM-ARCH-P0.8-CSK-MBD-CANDIDATE`

Controlled source: `HR-V0-ARM-ARCH-P0.7`

## Result

R135 found that all eight P0.7 countersink openings are modeled at the drawing's upper diameter limit, Ø11.40 mm, while the controlled nominal is Ø11.30 +0.10/-0.00 mm with a 90° included angle. The P0.7 STEP also uses a 3.10 mm axial depth. Those two modeled dimensions derive an 87.159469° cone, not 90°.

This package generates four nonselected P0.8 candidate STEP parts with:

- unchanged M5 through hole Ø5.50 mm;
- nominal major diameter Ø11.30 mm;
- nominal axial depth 2.90 mm, derived from the 90° geometry;
- unchanged part bounding boxes, exterior profiles, hole centers and all non-countersink features; and
- separate Ø11.40 maximum-diameter and 3.10 mm maximum-depth screens retained for conservative clearance/residual-material checks.

The candidates add only the material removed by P0.7's larger/deeper countersink. The total calculated mass change across C01/C04/C06/C07 is 0.195715 g at the project screening density of 2.70 g/cm³.

## Configuration boundary

P0.7 remains the controlled architecture. This package does not silently revise its files or downstream hashes. P0.8 cannot be selected until a qualified mechanical reviewer independently verifies the STEP cone geometry, accepts the nominal-versus-limit semantics, reviews fastener seating and directs configuration-control regeneration.

## Evidence

- `release/hr-v0/countersink-mbd-p0.1/part-comparison.csv`
- `release/hr-v0/countersink-mbd-p0.1/feature-certificate.csv`
- `release/hr-v0/countersink-mbd-p0.1/decision-register.csv`
- `release/hr-v0/countersink-mbd-p0.1/finding-register.csv`
- `release/hr-v0/countersink-mbd-p0.1/package-status.json`
- `release/hr-v0/countersink-mbd-p0.1/index.html`
- `cad/hr-v0/generated/countersink-mbd-p0.1/`

## What this does not prove

This bounded correction does not prove manufacturing capability, tolerance, cutter/gauge method, screw-head seating, flushness, received fit, residual strength, fatigue, hard-stop behavior, stopping, guarding or safety. Supplier DFM, FAI, received-lot inspection, proof testing and qualified review remain mandatory.
