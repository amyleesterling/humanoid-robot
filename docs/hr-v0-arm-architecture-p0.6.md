# HR-V0 integrated arm architecture P0.6

> **PRELIMINARY—CANDIDATE GEOMETRY ONLY—NOT RELEASED FOR QUOTATION, FABRICATION, ASSEMBLY, MOTION, OR ENERGIZATION.**

Date: 2026-08-07

Identifier: `HR-V0-ARM-ARCH-P0.6`

Parent release hold: `HR-V0-MECH-P0.5`

## R67 result

P0.6 preserves P0.5's exact A00-A07 geometry and adds a conservative continuous nominal model-space clearance certificate. It corrects the previous reliance on a 0.5-degree sample grid and lowers the candidate J2 command ceiling from 120 to 115 degrees.

The controlled transforms remain:

- J1 at `(-210, 81.025, 500) mm` from A0;
- J1-to-J2 spacing `202.550 mm`;
- J2-to-H104 G1 spacing `129.050 mm`; and
- nominally parallel J1/J2 axes.

These are CAD-candidate coordinates, not as-built measurements.

## Continuous nominal clearance certificate

The adaptive analyzer covers every non-intentional rigid-body pairing across:

- J1 `-20..70 deg`;
- J2 `15..120 deg`;
- 22 fixed-base/upper pairs;
- 28 upper/forearm pairs; and
- 20 fixed-base/forearm pairs.

For each adaptive interval cell, the analyzer computes a center AABB lower bound or exact B-Rep distance and subtracts an additive rigid-body chord-displacement bound for every allowed angle inside the cell. A cell is accepted only when the remaining lower bound is at least `0.75 mm`.

Results:

| Measure | Result |
|---|---:|
| non-intentional pairs | 70 |
| certified leaf cells | 130 |
| exact B-Rep distance calls | 84 |
| required certified clearance | 0.750000 mm |
| minimum conservative lower bound | 0.765783 mm |
| critical exact clearance at J2=120 deg | 0.962813 mm |
| continuous nominal first contact | J2=121.643289 deg |
| first 0.5-degree sampled positive-volume collision | J2=122 deg |

The 40,001-pose sampled exact-boolean sweep remains as independent grid evidence through J2=125 degrees. The continuous result is nominal CAD evidence only; it excludes tolerances, deformation, backlash, compliance, cables, guards, stop hardware, stopping travel, calibration, measurement uncertainty and physical proof.

## Candidate J2 allocation

- software ceiling: `115 deg`;
- candidate backed-up hard-stop datum: `118 deg`;
- software-to-stop allowance: `3 deg`;
- stop-to-nominal-contact separation: `3.643289 deg`;
- reserved nominal collision guard: `1 deg`; and
- remaining candidate physical-uncertainty budget: `2.643289 deg`.

This is not a released limit or stop design. See `docs/hr-v0-hard-stop-design-basis-p0.2.md`.

## Controlled evidence

`cad/hr-v0/generated/arm-architecture-p0.6/` contains the native STEP and GLB assemblies, separate part STEP/DXF artifacts, readable SVG drawings, source/transform/interface/fastener registers, analytical screens, the 40,001-row sampled sweep, the 70-pair continuous summary, the 130-cell certificate, and the candidate stop allocation.

`tools/check_hr_v0_arm_architecture.py` verifies exact artifact membership, source hashes, transforms, pair-group completeness, the certified clearance floor, the numerical contact boundary, the stop-allocation hold, readable warnings and the 18 px minimum drawing body text.

## Reproducibility boundary

The P0.6 generator reproduces its own candidate outputs deterministically under the controlled CadQuery environment. The older whole-package generator `cad/hr-v0/src/hr_v0_cad.py` uses OCC export features that can change timestamps, ordering or generated identifiers between runs; exact legacy bytes remain governed by the release manifest and shall not be described as byte-reproducible without a separately controlled canonicalization pass.

## Remaining release blockers

Received MTR/FAI/fit, supplier DFM, T-slot pullout/slip/prying, received fastener stacks, torque/locking/reuse controls, qualified structural acceptance, complete mass/COM/inertia, physical hard-stop CAD and proof, stopping-overtravel/backlash/compliance/tolerance/uncertainty evidence, cables and strain relief, guard integration, impact/fatigue proof and signed qualified mechanical/functional-safety review remain open.

No procurement, quotation, fabrication, assembly, motion, energization, or functional-safety gate closes in R67.
