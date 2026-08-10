# HR-V0 same-interface mass-reduction study P0.1

> **PRELIMINARY—FEASIBILITY STUDY ONLY—NOT APPROVED FOR FABRICATION, MOTION, OR ENERGIZATION.**

Document ID: `HR-V0-MASS-REDUCTION-P0.1`

Parent configuration: `HR-V0-ARM-ARCH-P0.7`

Date: 2026-08-07

## Purpose

R69 exposed that the known or CAD-estimated moving subtotal was already 692.758 g, leaving 57.242 g below the 750 g ceiling before the ROBOTIS frames, fasteners, bumper, cables, guides and complete gripper mechanism were counted. P0.1 tests whether useful mass can be removed without changing the controlled J1/J2/G1 coordinates, plate thickness, fastener axes or positive-stop contact geometry.

The study defines four subtractive candidates:

| Candidate | Parent | Parent estimate | Candidate estimate | Reduction |
|---|---|---:|---:|---:|
| MV0-C01R | MV0-C01 | 46.987 g | 32.791 g | 14.196 g |
| MV0-C04R | MV0-C04 | 46.987 g | 32.791 g | 14.196 g |
| MV0-C06R | MV0-C06 | 70.265 g | 55.952 g | 14.313 g |
| MV0-C07R | MV0-C07 | 66.870 g | 51.593 g | 15.277 g |
| **Four-part total** |  | **231.110 g** | **173.127 g** | **57.983 g** |

Values are CAD volume multiplied by 2.70 g/cm³. They are estimates, not received-part evidence. The exact stock, certificate, finish, tolerance and measured mass remain required.

## Preserved configuration

The candidates retain:

- the P0.7 J1/J2/G1 coordinates and link lengths;
- nominal 9.525 mm plate thickness and 9.0 mm finished minimum;
- every controlled M2.5 interface-hole axis;
- both M5 member-end axes and countersink envelopes;
- C06/C07 twin rail widths, top datums and fixed-catch face recess;
- the candidate fastener interfaces.

Each candidate was produced by subtracting solids from its exact P0.7 parent. Exact B-Rep comparison reports zero candidate volume outside the parent within `0.000010 mm³`. This proves the relieved parts cannot introduce new nominal rigid-body collision volume. It does not prove manufactured clearance, cable/guard clearance or deformation clearance.

The nominal positive-stop first-contact result remains 117.999985° and the nominal metal gap at the 115° software ceiling is unchanged. Bumper selection, tolerance accumulation, stopping travel, impact, rail load sharing and physical contact-mark evidence remain open.

## Screening result

The smallest nominal study ligaments are:

- M5 countersink to outer profile: 2.300 mm;
- M5 countersink to central relief: 1.300 mm;
- M2.5 hole to central relief: 3.650 mm;
- M2.5 hole to outer profile: 4.650 mm.

The conservative row-force/net-strip, M2.5 edge-tear and average-bearing calculations pass the project’s analytical screens. They explicitly omit prying, installed preload, local plate bending, stress concentration, notch sensitivity, frame bearing, fatigue, impact, manufacturing tolerance and proof correlation. They are not allowables and do not release the geometry.

## Mass disposition

If the four relieved candidates replaced their parents, the known/CAD-estimated subtotal would become 634.775 g and provisional unresolved headroom would rise to 115.225 g. `MASS-002` remains blocked because the unresolved items have neither selected geometry nor measured mass. The new headroom is not a reserve that may hide omitted parts.

Selection requires independent mechanical review, exact material/stock control, an accepted local-analysis method, prototype FAI and received fit, measured mass/COM, physical proof, stop-impact validation and qualified disposition. Until then the controlled configuration remains P0.7 C01/C04/C06/C07.

## Controlled evidence

- `cad/hr-v0/generated/mass-reduction-p0.1/mass-reduction-summary.json`
- `cad/hr-v0/generated/mass-reduction-p0.1/candidate-mass-comparison.csv`
- `cad/hr-v0/generated/mass-reduction-p0.1/exact-subset-proof.csv`
- `cad/hr-v0/generated/mass-reduction-p0.1/stop-contact-compatibility.csv`
- `cad/hr-v0/generated/mass-reduction-p0.1/ligament-and-load-screen.csv`
- `cad/hr-v0/generated/mass-reduction-p0.1/interface-preservation.csv`
- `cad/hr-v0/generated/mass-reduction-p0.1/parts/`
- `tools/generate_hr_v0_mass_reduction_study.py`
- `tools/check_hr_v0_mass_reduction_study.py`

No file in this study authorizes quotation, machining, assembly, proof loading, motion or energization.
