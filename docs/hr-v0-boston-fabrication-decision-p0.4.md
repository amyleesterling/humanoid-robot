# HR-V0 Boston fabrication route P0.4

> **PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION.**

Identifier: `HR-V0-BOSTON-FAB-ROUTE-P0.4`

Review round: R217

Date: 2026-08-11

## Decision

The five current custom aluminum parts have a credible fabrication route, but no provider has accepted the work and no external action is authorized. P0.4 replaces the stale P0.3 configuration boundary with the exact current chain:

- `HR-V0-ARM-ARCH-P0.8-DWG-INTEGRATED-CANDIDATE`;
- `HR-V0-MECH-BOM-BIND-P0.2`;
- `HR-V0-MECH-MFG-REVIEW-P0.1`; and
- `HR-V0-FAB-INPUT-P0.1`.

The package binds five current repository inputs by SHA-256. It does not copy or reinterpret the manufacturing geometry.

## Route ranking

- **Kontrast4D, Salem:** primary local capability-inquiry candidate. Its current official capability specification lists 6061, 3/4/5-axis machining, called-out CMM-verified features to +/-0.0005 inch and first-article reports on request. Exact T651 stock, the MTR chain, all 26 controls, 30 FAI operations and the C07 surface map still require written acceptance.
- **Protolabs:** primary online capability-inquiry candidate. Its current official pages list 6061-T651, suitable aluminum machining envelopes and FAI/dimensional/CMM/material-certification options. The exact factory/network path and every high-requirement feature remain unaccepted.
- **Xometry:** secondary online candidate. Its published default is 6061-T6x best available rather than guaranteed T651, but it documents custom material review, formal/CMM/FAI/build-and-hold inspection and quote-time material traceability. Those options must be explicitly selected and accepted; they are not implied.
- **Artisans Asylum, Allston:** training, fixturing and non-credit prototype route. Its official pages list aluminum machining, a Bridgeport CNC mill and an M3X CNC mill with required training/tool testing. Published access does not establish an accepted operator, calibration, CMM/FAI, material traceability or structural first-article capability.
- **Boston Digital Fabrication, Allston:** local commercial capability screen only. It publishes a three-axis CNC knee mill and lathe, but no numerical tolerance, exact T651, MTR, CMM or FAI evidence sufficient for release.
- **Boston Public Library:** excluded for the five structural metal parts. Current official pages document CAD/design support and MakerBot printing, not controlled metal CNC machining. It remains useful for learning and plastic mockups.

## Corrected design inputs

P0.3 incorrectly described payload and motion as wholly unknown. R173 already corrected that record. P0.4 carries the real draft boundary forward:

- soft foam object, measured mass including uncertainty no greater than 100 g and 40-70 mm on each principal dimension;
- TCP speed no greater than 0.15 m/s in every released pose;
- automatic joint command no greater than 30 deg/s, subject to lower pose-dependent limits; and
- hold-to-run setup motion no greater than 10 deg/s.

Duty spectrum, acceleration, jerk, emergency deceleration, restraint/fall cases, safety factors, C05 joint proof, C06/C07 stop loads, material traceability and executed FAI remain open.

## Controlled next action

1. A named qualified mechanical reviewer dispositions the current R215 drawings, loads, interfaces and DFM questions.
2. A separate, signed capability-only inquiry selects one local and one online candidate. Initial contact carries no geometry unless the authorization explicitly lists exact file names and hashes.
3. The candidate responds in writing against exact material, process, all drawing controls, inspection, segregation and nonconformance questions.
4. A separate one-part-per-geometry first-article authorization may be considered only after the response is accepted.
5. Received parts remain segregated until MTR, all 30 FAI operations, fit, mass, structural proof and qualified acceptance are complete.

## Artifacts

- `release/hr-v0/boston-fabrication-route-p0.4/route-comparison.csv`
- `release/hr-v0/boston-fabrication-route-p0.4/source-register.csv`
- `release/hr-v0/boston-fabrication-route-p0.4/configuration-binding.csv`
- `release/hr-v0/boston-fabrication-route-p0.4/input-reconciliation.csv`
- `release/hr-v0/boston-fabrication-route-p0.4/capability-inquiry-register.csv`
- `release/hr-v0/boston-fabrication-route-p0.4/capability-inquiry-authorization-template.csv`
- `release/hr-v0/boston-fabrication-route-p0.4/index.html`

Published capability evidence is not provider selection, program acceptance, quotation, procurement, fabrication or safety evidence.

**PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION.**
