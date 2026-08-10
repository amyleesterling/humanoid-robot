# HR-V0 integrated arm architecture P0.5

**PRELIMINARY - CANDIDATE GEOMETRY ONLY - NOT RELEASED FOR QUOTATION, FABRICATION, ASSEMBLY, OR ENERGIZATION**

Date: 2026-08-07

Identifier: `HR-V0-ARM-ARCH-P0.5`

Parent release hold: `HR-V0-MECH-P0.4`

## R66 result

P0.5 closes the source-geometry gaps at both ends of the P0.4 arm candidate without claiming physical acceptance. The deterministic native package now represents the 40-4040 column, `MV0-C05` shoulder support, rolled J1/J2 XM540/S102 packages, H101 output frames, two vertical 20-2040 members, standard `MV0-C01` adapters, the H104-specific `MV0-C04` adapter, and the exact H104 frame.

All eight project interfaces `A00` through `A07` have explicit coordinates and candidate hardware. J1 is placed at `(-210, 81.025, 500) mm` from A0. The nominal J1-J2 spacing is `202.550 mm`; J2 to the H104 frame origin is `129.050 mm`. The nominal J1 and J2 axes are parallel. These are CAD candidate coordinates, not measured assembly results.

## Newly defined interfaces

- `MV0-C05`: `48 x 80 x 9.525 mm` nominal S102-to-40-4040 side-slot support. Four `2.70 mm` candidate holes use exact S102 STEP axes at `X=+/-16, Z=+/-8 mm`; two `8.50 mm` candidate column holes are at `X=0, Z=+/-30 mm`.
- `MV0-C04`: `48 x 40 x 9.525 mm` nominal H104-to-20-2040 adapter. Its four `2.70 mm` candidate holes derive from exact H104 STEP cylinder axes. In the adapter frame they are `(-11,+8)`, `(+11,+8)`, `(-12,-6)`, and `(+12,-6) mm`.
- `A00`: exact-candidate `80/20 17-8520` M8 x 20 screws and `13035` M8 roll-in T-nuts join `MV0-C05` to the front slot of a `40-4040` column. Catalog compatibility and a separate manufacturer mounting precedent are recorded; project pullout, slip, prying, installation torque, anti-galling, and proof remain unresolved.
- `A07`: exact-candidate `MISUMI SCB2.5-20` screws and `Accu HNN-M2.5-A2` locknuts join `MV0-C04` to the H104. Received fit, torque, retention, reuse, tool access, and proof remain unresolved.

The FR12-H104K product boundary requires the `HN12-I101` idler set when used with XM430. That item is already allocated within the proposed RM-X52 parent kit in `bom/hr-v0-gripper-kit-contents.csv`; the received kit still must be reconciled before assembly.

## Evidence package

`cad/hr-v0/generated/arm-architecture-p0.5/` contains:

- combined native STEP and interactive GLB assemblies;
- separate `MV0-C01`, `MV0-C04`, `MV0-C05`, and 20-2040 STEP parts;
- controlled SVG drawings and DXF profiles for the three custom adapter/support geometries;
- `interface-feature-evidence.csv` with exact controlled STEP hashes and selected axes;
- `interface-schedule.csv`, `transform-schedule.csv`, fastener and tool-access schedules;
- dimensional/FAI controls and analytical screens; and
- a 40,001-row two-axis collision sweep.

The sweep samples J1 from `-20` to `70 degrees` and J2 from `15` to `125 degrees` in `0.5-degree` increments. It finds no positive modeled intersection through the provisional J2 ceiling of `120 degrees`. The first nominal contact occurs at `122 degrees`, and 1,267 outside-limit poses are marked collision. The conservative rotated-AABB broad phase cannot omit an exact contact at a sampled pose, but the study is not continuous proof and excludes cables, guards, stop hardware, manufacturing variation, compliance, and stopping travel.

## Primary-source basis

Sources were accessed 2026-08-07 and are recorded with release effects in `cad/vendor/arm-interface-source-register.csv`:

- 80/20 40-4040: https://8020.net/40-4040.html
- 80/20 17-8520: https://8020.net/17-8520.html
- 80/20 13035: https://8020.net/13035.html
- 80/20 40006-BP mounting precedent: https://8020.net/40006-bp.html
- ROBOTIS FR12-H104K: https://robotis.us/fr12-h104k-set/
- ROBOTIS FR13-S102K: https://robotis.us/fr13-s102k-set/

The controlled ROBOTIS PDFs identify FR12-H104K drawing date 2017-08-31 and FR13-S102K drawing date 2026-01-07. Controlled STEP hashes, not visual interpretation of the drawings, establish the candidate hole-axis coordinates.

## Release blockers

P0.5 does not authorize quotation or fabrication. It still requires received material certificates and dimensions, supplier DFM, separately authorized first articles, complete fastener stack measurements, developed torque/locking/reuse rules, received H104/S102/column fit, T-slot pullout/slip/prying proof, qualified structural acceptance, cables and strain relief, continuous collision proof, backed-up physical hard stops, measured stopping overtravel and uncertainty margin, guard integration, physical proof testing, and signed qualified mechanical disposition.

No procurement, fabrication, assembly, motion, energization, or functional-safety gate closes in R66.
