# HR-V0 Frame Joint Correction P0.2

**PRELIMINARY—NOT RELEASED FOR PROCUREMENT, FABRICATION, ASSEMBLY, OR ENERGIZATION**

Date: 2026-08-07

Supporting identifier: `HR-V0-FRAME-P0.2`

Parent mechanical coordination candidate: `HR-V0-MECH-P0.3` (base/frame evidence only; arm geometry withdrawn)

## Result

R49 supersedes `HR-V0-FRAME-P0.1`. Manufacturer geometry and an analytic member-envelope check exposed three physical defects in P0.1:

1. 80/20 `40-4334` has a 76 mm overall span and two fastener positions 40 mm apart on each leg. The project `40-4040` profile exposes one slot per 40 mm face. It is therefore incompatible with this single-face joint topology. This is a project inference from current manufacturer dimensions, not an 80/20 application approval.
2. Two 320 mm transverse rails centered at `X=±210` intersected the two 500 mm longitudinal rails centered at `Y=±160` in four 40 x 40 x 40 mm volumes.
3. The 500 mm upright centered at `Z=270` began at `Z=20` and intersected the left base rail through `Z=20..40`. The proposed X-face column-bracket orientation also did not align to the transverse rail's top slot.

The corrected exact candidate on hold is:

- two 500 mm longitudinal `40-4040` rails centered at `Y=-140` and `Y=140` mm;
- two 240 mm transverse `40-4040` rails centered at `X=-210` and `X=210` mm;
- one 500 mm `40-4040` upright centered at `X=-210`, from `Z=40` through `Z=540` mm;
- a 500 x 320 mm outside base envelope with square-cut members that meet only at faces;
- six `40-4332` two-hole gusseted inside-corner brackets; and
- twelve `75-3422` bolt assemblies, two per bracket.

No part is released for procurement or assembly. Received-part fit, driver access, load capacity, actual torque, slip/proof and qualified disposition remain open.

## Current official evidence

The following official 80/20 sources were accessed and rechecked 2026-08-07. Their live pages expose no formal revision identifier.

- `40-4040`: 40 x 40 mm 40-series profile with one open T-slot on each of four faces, 6063-T6, and compatibility with 40-series fasteners.
- `40-4332`: 40-series two-hole gusseted inside-corner bracket, 6063-T6 anodized, nominal 40 x 40 x 6 mm legs, 36 mm face width, 8.30 mm holes, and two suggested `75-3422` assemblies.
- `40-4334`: 40-series four-hole wide bracket, 76 mm overall width and two positions 40 mm apart on each leg. It is recorded as rejected for this topology.
- `75-3422`: one `13-8316` M8 x 16 BHSCS plus one `3838` offset-thread slide-in economy T-nut.
- *The Basics of Building T-Slot—University Booklet*: 13–20 N m guide for `75-3422` with `40-4040`, with the limitation that actual torque must be determined experimentally for the real joint conditions.

The catalog geometry does not establish an application allowable, torque, proof load, impact capacity, fatigue life, or permission to assemble.

## Six controlled placements

`cad/hr-v0/frame-joint-placement-p0.2.csv` is the machine-readable placement contract.

| Joint | Ridge coordinate / axis | Controlled faces |
|---|---|---|
| `FJ-001` | `(-190,-120,20)`, Z | left-transverse X+ / rear-longitudinal Y+ |
| `FJ-002` | `(-190,120,20)`, Z | left-transverse X+ / front-longitudinal Y− |
| `FJ-003` | `(190,-120,20)`, Z | right-transverse X− / rear-longitudinal Y+ |
| `FJ-004` | `(190,120,20)`, Z | right-transverse X− / front-longitudinal Y− |
| `FJ-005` | `(-210,-20,40)`, X | column Y− / left-transverse top |
| `FJ-006` | `(-210,20,40)`, X | column Y+ / left-transverse top |

The 36 mm bracket face centered on a 40 mm profile face produces a nominal 2 mm geometric edge-clearance screen on each side. That screen does not prove actual bracket-body, gusset, fastener, socket, driver, wrench, hand or assembly access. Those checks remain `SELECTION REQUIRED` and must be executed on controlled received parts before assembly.

## Analytic interference check

`tools/check_hr_v0_frame_joints.py` treats the five members as axis-aligned 40 mm envelopes. It requires:

- rear/front rails: `X=-250..250`, `Y=-160..-120` and `Y=120..160`, `Z=0..40`;
- left/right rails: `X=-230..-190` and `X=190..230`, `Y=-120..120`, `Z=0..40`; and
- upright: `X=-230..-190`, `Y=-20..20`, `Z=40..540`.

All intended joints share a boundary face but have no positive-volume member overlap. This closes only the earlier envelope collision. It does not model extrusion corner radii, real bracket/gusset volume, screw insertion, tool sweep, tolerance accumulation, burrs, slot details, anchor plates or deflection.

## Load screen—not an allowable

The controlled proof-moment study value remains 11.49 N m. For either column bracket, using a conservative nominal 20 mm leg arm:

`11.49 N m / 0.020 m = 574.5 N`

If two opposed brackets shared that moment perfectly, the nominal value would be 287.25 N per bracket. Neither number is a force allocation or allowable. The calculation omits prying, preload, friction, eccentricity, tolerance, shock, fatigue, redistribution after slip, extrusion-slot capacity and the actual restraint/load path. It defines a lower-bound fixture-sizing input for qualified analysis and proof planning only.

## Required closure sequence

1. Receive and quarantine the five `40-4040` cuts, six `40-4332` brackets and twelve `75-3422` assemblies.
2. Reconcile markings and received dimensions against the current official drawings; retain lot/pack and photograph evidence.
3. Dry-fit every `FJ-*` placement unpowered and without claiming a release torque. Record bracket-body, gusset, screw, T-nut and tool access.
4. A qualified mechanical reviewer defines the actual load cases, fixture, proof factors, numeric acceptance limits and trial sequence.
5. Execute `INSPECT-MECH-010` with calibrated tools and the controlled form.
6. Record seating, torque sequence, diagonal/perpendicularity, slip, post-proof condition, witness marks, damage and nonconformances.
7. Freeze the accepted torque, replacement/reuse rule, inspection interval and qualified application disposition in a later controlled revision.

Until all steps pass, `BOM-024`, `BOM-025`, `BOM-071`, `MIC-003` and every `FJ-*` joint remain `exact_candidate_hold`.

## Remaining holds

This correction does not close bench anchors, anchor plates, custom-part fasteners, hard stops, guard/catch, cable hardware, measured mass/COM/inertia, shock/fatigue loads, first articles, physical proof, functional-safety allocation or qualified release. It does not authorize fabrication or energization.
