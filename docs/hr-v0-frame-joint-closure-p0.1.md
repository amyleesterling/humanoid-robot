# HR-V0 Frame Joint Closure P0.1

**PRELIMINARY—NOT RELEASED FOR PROCUREMENT, FABRICATION, ASSEMBLY, OR ENERGIZATION**

Date: 2026-08-07

Supporting identifier: `HR-V0-FRAME-P0.1`

Parent mechanical coordination candidate: `HR-V0-MECH-P0.2`

## Result

This pass removes the ambiguous `40-4334 and/or 40-4332` frame-joint placeholder. The exact candidate is:

- six 80/20 `40-4334` 40-series four-hole wide gusseted inside-corner brackets;
- twenty-four 80/20 `75-3422` bolt assemblies, four per bracket;
- four horizontal base-corner joints, `FJ-001` through `FJ-004`; and
- two opposed column joints, `FJ-005` and `FJ-006`.

This is an exact catalog candidate on hold, not an application release. No frame may be assembled from this document alone.

## Primary-source basis

The current 80/20 `40-4334` product page identifies a 6063-T6 anodized 40-series gusset with two adjacent holes on each side and specifies four `75-3422` assemblies as suggested mounting hardware. The current `75-3422` page identifies one M8 x 16 mm button-head socket-cap screw and one offset-thread slide-in economy T-nut per assembly. Both pages were rechecked 2026-08-07 and expose no formal document revision.

The 80/20 *University Booklet*, current official PDF found 2026-08-07, gives a 13 N m minimum and 20 N m maximum guide for `75-3422` with `40-4040`. It explicitly treats these values as guidance and says the correct torque must be determined experimentally under the actual joint and assembly conditions. Therefore:

- 13–20 N m is only the controlled trial window;
- the released torque remains `SELECTION REQUIRED`;
- the applied torque tool and calibration must be recorded;
- surface condition, seating, sequence, slip, re-torque and witness marks must be recorded; and
- qualified mechanical review must accept the final joint procedure.

## Candidate allocation and orientation

`bom/hr-v0-frame-joint-schedule.csv` is authoritative for the six joint instances. `FJ-001` through `FJ-004` occupy the four inside plan corners of the 500 x 320 mm base and engage the upper slot faces. `FJ-005` and `FJ-006` are opposed on the column's X-minus and X-plus faces, with bracket planes parallel to YZ. Manufacturer CAD and received-part fit must confirm every claimed mounting orientation and tool-access path before assembly.

## Load screen—not an allowable

The existing controlled structural proof moment is 11.49 N m. For the opposed column-bracket study, using the nominal 40 mm face separation gives:

`11.49 N m / 0.040 m = 287.25 N`

That is the candidate force in the resisting couple. Dividing only for an average screen across the two fasteners on one member side gives 143.63 N per fastener. Neither value is a fastener, T-nut, bracket, extrusion-slot or joint allowable. The calculation omits prying, slip, preload scatter, friction variation, shock, eccentricity, tolerance, fatigue, re-use and the real load distribution.

The same 80/20 booklet publishes generic horizontal-bracket guidance, including a 40-series corner-gusset row, but it does not identify that table as an application rating for this exact six-joint assembly. It may inform the qualified review; it shall not be used as proof that `40-4334` passes.

## Required closure sequence

1. Receive and quarantine the five `40-4040` cuts, six `40-4334` brackets and twenty-four `75-3422` assemblies.
2. Record markings, quantities, pack/lot evidence, damage and manufacturer CAD identity.
3. Dry-fit each joint without applying a release torque; confirm slot engagement, seating and tool access.
4. A qualified mechanical reviewer defines the proof fixture, actual moment/shear cases, acceptance limits and torque trial sequence within the manufacturer guide.
5. Execute `INSPECT-MECH-010` using the controlled form. Record calibrated tool identity, surface condition, torque, sequence, seating, diagonal/perpendicularity, slip, post-proof result and witness marks.
6. Inspect for bracket, screw, T-nut, slot and extrusion damage; quarantine any nonconformance.
7. Freeze the final torque, reuse/replacement rule, inspection interval and signed application disposition in a later controlled revision.

Until all seven steps pass, `BOM-024`, `BOM-025`, `BOM-071`, `MIC-003` and every `FJ-*` joint remain `exact_candidate_hold`.

## Remaining structural holds

This pass does not close the bench anchors, MV0-004 plates, custom-part fasteners, hard stops, guard/catch, cable hardware, measured mass/COM/inertia, shock/fatigue loads, first articles, proof tests or qualified release. It does not authorize fabrication or energization.
