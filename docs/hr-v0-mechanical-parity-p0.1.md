# HR-V0 mechanical nominal-file parity P0.1

> **PRELIMINARY - NOT APPROVED FOR QUOTATION, FABRICATION, ASSEMBLY, MOTION, OR ENERGIZATION.**

Identifier: `HR-V0-MECH-PARITY-P0.1`

Round: R135

Controlled architecture: `HR-V0-ARM-ARCH-P0.7`

## Outcome

An independent parser and STEP inspection now reconcile all five current custom parts. All five STEP bounding profiles match the controlled DXF extents at zero reported delta. Thirty DXF hole entities have exact nominal STEP-cylinder matches. Eight countersink entities match position but expose an important semantic difference: DXF/drawing nominal diameter is 11.30 mm while STEP uses the allowed 11.40 mm upper limit. C07's STEP contains the controlled 1.000 mm face recess. Each of the twenty-six source inspection controls is bound to its readable drawing and source row.

## Important limitation discovered

C04/C05/C06/C07 are not conventional fully dimensioned fabrication drawings. Six controls are schedule-bound rather than fully displayed on their readable SVGs. C06/C07 DXFs are intentionally pre-fillet construction profiles while STEP controls the R2 finished solid. C01/C04/C06/C07 STEP countersink openings are modeled at the upper diameter limit rather than nominal. A provider must not machine from STEP or DXF alone, and a qualified reviewer must decide whether to remodel the STEP solids at nominal and whether conventional released drawings are required.

## Controlled evidence

- [Interactive parity guide](../release/hr-v0/mechanical-parity-p0.1/index.html)
- `release/hr-v0/mechanical-parity-p0.1/profile-parity.csv`
- `release/hr-v0/mechanical-parity-p0.1/feature-parity.csv`
- `release/hr-v0/mechanical-parity-p0.1/drawing-control-coverage.csv`
- `release/hr-v0/mechanical-parity-p0.1/finding-register.csv`
- `release/hr-v0/mechanical-parity-p0.1/package-status.json`

## Release boundary

Nominal file parity closes no physical or authorization gate. Material certification, provider DFM, manufacturing capability, FAI, received fit, fastener/T-slot capacity, stop loads, complete mass/COM/inertia, continuous duty, guard/cable geometry, proof, fatigue, impact, stopping, functional-safety validation and qualified release remain open. No contact, upload, quotation, fabrication, assembly, motion or energization is authorized.
