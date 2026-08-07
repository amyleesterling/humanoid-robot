# HR-V0 Mechanical Release Coordination P0.2

> **SUPERSEDED BY `HR-V0-MECH-P0.3` (R53). DO NOT USE THE P0.2 ARM DATUMS, MV0-001/MV0-002/MV0-003 GEOMETRY, OR FABRICATION PACKETS.** Exact ROBOTIS STEP coordinates show that the H101 moving frame and S102 bottom body frame do not present the coplanar interfaces assumed here. This file is retained only as configuration history.

**PRELIMINARY—NOT RELEASED FOR FABRICATION, ASSEMBLY, OR ENERGIZATION**

Date: 2026-08-07

Release-coordination identifier: `HR-V0-MECH-P0.2`

Native geometry baseline: `HR-V0-MECH-R0.1-PRELIMINARY`

Flat-plate process basis: `HR-V0-PLATE-RFQ-P0.1`

## Result

P0.2 establishes one explicit mechanical datum and interface contract for the HR-V0 bench demonstrator. It does not convert candidate dimensions into fabrication authority. It makes the remaining work executable and auditable:

- 24 controlled parameters state a nominal value, datum, source, maturity and exact closure evidence;
- 12 mechanical interfaces identify every parent/child boundary and prevent an unspecified fastener or mounting assumption from disappearing inside the assembly;
- 20 assembly component groups join the mechanical arrangement to the system BOM;
- five exact candidate extrusion cuts are enumerated in three controlled schedule rows;
- six exact frame-joint candidates allocate six `40-4332` brackets and twelve `75-3422` assemblies under corrected `HR-V0-FRAME-P0.2`;
- six generated assembly datums create one neutral-pose chain from the bench plane through J1, J2, the gripper frame and maximum permitted object reach;
- a readable SVG general-arrangement drawing exposes dimensions and every fabrication hold; and
- a 20-row unexecuted inspection template provides the physical closure route.

## Defects corrected

### Assembly transforms were not a controlled datum chain

The R0.1 STEP/GLB assembly was explicitly a space model. Its adapter, actuator-envelope and link placements did not resolve to one shoulder datum. P0.2 defines:

| Datum | Candidate coordinate in A0 | Meaning |
|---|---:|---|
| `A0` | `(0, 0, 0)` mm | bench plane and base-plan origin |
| `C0` | `(-210, 0, 0)` mm | column centerline |
| `J1` | `(-166, 0, 500)` mm | shoulder axis |
| `J2` | `(-6, 0, 500)` mm | elbow axis in the neutral horizontal study pose |
| `G1` | `(154, 0, 500)` mm | gripper-frame datum in that pose |
| `OMAX` | `(194, 0, 500)` mm | 360 mm reach ceiling from J1, not a commanded pose |

The CadQuery assembly now uses this chain. The J1 X position is derived from the `C0` column center plus the MV0-003 lower-left coordinate difference `58 - 14 = 44 mm`. The adapter lower-left Z is set so its candidate shoulder datum is 500 mm above A0. J2 and G1 then follow the two 160 mm link centers.

This chain remains a candidate until exact frame stacks, coupons, fasteners and assembled inspection pass. It shall not be copied into motion calibration as measured truth.

### Misleading structural STL files were removed

Regeneration testing found that CadQuery 2.8 produced byte-identical STL files for `MV0-001` and `MV0-002` despite their different distal hole patterns. STEP and DXF preserve the distinct interfaces. Because these four custom parts are metal RFQ/CNC items—not printable structural parts—P0.2 prohibits structural STL rather than publishing an ambiguous mesh. The checker requires exactly DXF and STEP for every `MV0-001` through `MV0-004` part.

The nonstructural fit coupons retain STL only as optional inspection aids. Their controlled dimensional evidence remains DXF/STEP plus the calibrated 1:1 overlays and physical records.

### Bench anchors are horizontal interfaces

The previous assembly view displayed `MV0-004` vertically even though its intended bench slots and frame holes are coplanar. P0.2 rotates the two candidate plates into the bench plane in the assembly model. This is a visualization correction, not an anchor release. The actual bench substrate, site permission, edge distances, bolt/backing arrangement, pull-out, shear and base attachment remain `SELECTION REQUIRED`.

## Candidate assembly sequence

No step below may start until its preceding hold is signed. This is sequencing information, not assembly authorization.

1. Receive and inspect the five exact `40-4040` extrusion cuts: two at 500 mm for the longitudinal base rails, two at 240 mm for the transverse rails, and one at 500 mm for the column.
2. Receive the six `40-4332` brackets and twelve `75-3422` assemblies identified in `bom/hr-v0-frame-joint-schedule.csv`; do not treat catalog identity as application release.
3. Execute the qualified fit/tool-access, torque-development, slip/proof and inspection route in `docs/hr-v0-frame-joint-closure-p0.2.md` and `INSPECT-MECH-010`. The manufacturer 13–20 N m value is a trial guide, not a released torque.
4. Install the column at candidate `C0`; inspect position, perpendicularity and anti-rotation. Do not install actuators.
5. Survey the actual bench and close `MIC-001`/`MIC-002` before cutting or installing `MV0-004`.
6. Execute `MV0-FC01`, `MV0-FC02` and `MV0-FC03` against received and identified ROBOTIS parts.
7. Obtain supplier DFM, freeze tolerances and release only a first-article order for the four custom parts under separate written authorization.
8. Execute `INSPECT-MECH-009` on every first article. Quarantine any deviation.
9. Expand BOM-066 into exact per-interface fasteners after measuring real stacks and available thread depth. Release engagement, preload, torque, retention, cure, reuse and witness-mark criteria.
10. Assemble J1, J2 and the gripper unpowered. Execute the P0.2 datum/interface inspection, moving-mass measurement and full-range cable study.
11. Design and proof the backed-up hard stops, fixed guard, catch, gripper local guard and bench anchoring.
12. Complete the unpowered configuration inspection before any electrical connection.

## Artifact map

| Artifact | Purpose |
|---|---|
| `cad/hr-v0/mechanical-release-data.csv` | controlled parameter and maturity table |
| `cad/hr-v0/mechanical-interface-control.csv` | parent/child mounting and fastener boundary register |
| `cad/hr-v0/mechanical-assembly-components.csv` | mechanical-to-system-BOM assembly schedule |
| `bom/hr-v0-extrusion-cut-schedule.csv` | exact candidate profile cut lengths |
| `bom/hr-v0-frame-joint-schedule.csv` | six exact bracket/hardware instances and orientation/load-screen holds |
| `cad/hr-v0/frame-joint-placement-p0.2.csv` | six bracket-ridge placements, controlled faces and analytic envelope result |
| `docs/hr-v0-frame-joint-closure-p0.2.md` | corrected catalog evidence, geometry, torque-development boundary and proof route |
| `cad/hr-v0/generated/assembly/assembly-datums.csv` | generated coordinate chain |
| `cad/hr-v0/generated/assembly/HR-V0_general-arrangement.svg` | web-readable dimensioned assembly view |
| `cad/hr-v0/generated/assembly/mechanical-release-summary.json` | counts and source hashes |
| `tests/forms/hr-v0-mechanical-release-inspection-template.csv` | unexecuted physical evidence form |
| `tests/forms/hr-v0-frame-joint-receiving-assembly-template.csv` | unexecuted joint receiving, torque and proof form |
| `tools/generate_hr_v0_mechanical_release.py` | deterministic standard-library generator |
| `tools/check_hr_v0_mechanical_release.py` | cross-source fail-closed validation |

## Release holds

The following remain hard blockers:

1. received frame, actuator, gripper and extrusion identities;
2. executed interface coupons and released acceptance tolerances;
3. executed frame-joint fit/torque/slip/proof evidence, exact anchors and every remaining structural fastener;
4. supplier DFM and material/thickness certificates;
5. custom-part first articles and dimensional inspection;
6. measured moving mass, center of mass and inertia;
7. a fabricated, backed-up and proof-tested hard-stop system;
8. exact cable parts and complete unpowered articulation;
9. a frozen guard, catch and receiver based on measured sweep and stopping travel;
10. bench survey and anchor calculations;
11. proof-load, drop/containment and post-test inspection evidence; and
12. qualified mechanical and functional-safety review.

Passing the P0.2 checker means only that these definitions agree with one another. It does not prove fit, strength, safe stopping, containment or permission to fabricate.
