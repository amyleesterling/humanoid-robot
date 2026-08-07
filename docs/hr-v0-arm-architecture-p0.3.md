# HR-V0 strengthened arm architecture P0.3

**PRELIMINARY - CANDIDATE GEOMETRY ONLY - NOT RELEASED FOR QUOTATION, FABRICATION, ASSEMBLY, OR ENERGIZATION**

Date: 2026-08-07

Identifier: `HR-V0-ARM-ARCH-P0.3`

Parent hold: `HR-V0-MECH-P0.3`

## R56 result

P0.3 supersedes R55/P0.2. It preserves the corrected XM540/S102 registration, ROBOTIS rectangular frame pattern and vertical 20-2040 links while replacing the thin adapter and incomplete fastener stack:

1. Adapter nominal thickness is `9.525 mm` (3/8 inch) with a project finished acceptance range of `9.0 to 10.0 mm`. The maximum 3.10 mm countersink therefore leaves at least 5.90 mm of finished material instead of P0.2's 1.6625 mm nominal residual.
2. Westfield `WF2563` is the exact M5 x 20 A2 stainless ISO 10642 candidate. Its live product record gives a 9.43 to 10.07 mm head diameter, 2.669 to 3.100 mm head height and 3 mm drive. At the 10.0 mm adapter maximum it retains a 10.0 mm geometric engagement screen in the 20-2040 M5 end tap.
3. Westfield `WF2339` M2.5 x 16 A2 stainless ISO 4762 screws and `WF1254` M2.5 A2 DIN 934 nuts are exact candidates for the three frame/adapter interfaces. The modeled maximum stack leaves 1.8 mm, or four nominal 0.45 mm pitches, beyond the nut before screw-length tolerance. Received stack measurement remains mandatory.
4. A regenerated 221-pose, 0.5-degree sweep retains first nominal forearm-adapter/J2-body contact at 122.0 degrees. The 120.0-degree ceiling remains provisional; no motion range is released.

## Candidate datums

| Datum | Candidate value | Status |
|---|---:|---|
| J1 axis | `(0,0,0)`, direction +X | coordinate candidate |
| J1 H101 link face | `Y=32.0000 mm` | exact vendor face; physical stack open |
| J2 S102 link face | `Y=151.0500 mm` | exact vendor face after package roll |
| J2 axis | `Y=202.5500 mm` | candidate; 202.55 mm from J1 |
| J2 H101 link face, straight reference | `Y=234.5500 mm` | requires -90-degree output offset relative to the rolled body package |
| G1 H104 origin | `Y=331.6000 mm` | candidate; leaves 28.4000 mm to the 360 mm object-center ceiling |

The adapter remains a `48 x 40 mm` 6061-T651 machining candidate. Exact raw-stock order code, certified minimum properties, grain direction, flatness, finish, dimensional tolerances, local conical-contact model, fatigue treatment and first article remain open.

## Static screen boundary

The thicker adapter increases the calculated shoulder/elbow gravity allocations to 1.858/0.498 N m and the existing 2.25 screening cases to 4.180/1.122 N m. No continuous actuator capability is inferred.

At the 208.98 N no-friction-credit M5 couple force:

- the minimum-residual punching-shear demand is 2.0499 MPa;
- average pressure over the minimum-head annulus is 4.5347 MPa;
- M5 end-thread inferred shear capacity is 6,856.9 N, a 32.8 demand ratio; and
- 20-2040 strong-axis bending stress is 1.8429 MPa against the product page's 172.37 MPa published yield value.

Kaiser Aluminum's `Sheet Coil & Plate Alloy 6061`, Rev. 05/06, reports 276 MPa as a **typical** T6/T651 yield value. The generated 77.7 and 60.9 comparison ratios are therefore indicative screens only, not factors of safety or allowables. Certified minimum properties, accepted local FEA or equivalent, preload/prying/fatigue/impact analysis and physical proof remain required.

## Controlled evidence

`cad/hr-v0/generated/arm-architecture-p0.3/` contains native STEP, interactive GLB, readable SVG, candidate part STEP files, transform/interface/fastener schedules, the 221-row sweep, tool-access screen, joint-load screen and machine-readable summary. `tools/check_hr_v0_arm_architecture.py` fails closed on the source hashes, 9.0 mm finished minimum, exact candidate order codes, 120/122-degree collision boundary, typical-property caveat and unresolved physical proof.

Current primary records, all accessed 2026-08-07:

- Kaiser Aluminum `Sheet Coil & Plate Alloy 6061`, Rev. 05/06: https://online.kaiseraluminum.com/depot/PublicProductInformation/Document/1015/Kaiser_Aluminum_6061_Sheet_Coil_and_Plate.pdf
- Westfield `WF2563`: https://www.westfieldfasteners.co.uk/Bolts-Screws-Metric/Socket-Head-Csk-Allen-Screw-M5x20-A2-Stainless.html
- Westfield `WF2339`: https://www.westfieldfasteners.co.uk/Bolts-Screws-Metric/Socket-Head-Cap-Screw-M2.5x16-A2-Stainless.html
- Westfield `WF1254`: https://www.westfieldfasteners.co.uk/Metric-Nuts/Hex-Nut-M2.5-A2-Stainless.html
- Westfield DIN 934 guide, current download with no document revision exposed: https://www.westfieldfasteners.co.uk/Standards/Nut_Hex_M.pdf

## Release blockers

- received XM540/H101/S102 horn, idler and axial-stack fit;
- received WF2339/WF1254 stack, screw-length tolerance, protrusion and 5 mm tool access;
- released torque, anti-galling/locking, witness-marking and reuse rules for every M2.5 and M5 fastener;
- adapter exact raw stock, certificate, 9.0 to 10.0 mm finished thickness, countersink inspection, local analysis and FAI;
- supplier confirmation and received gauge/depth inspection of the 20-7047 end-tap service;
- continuous between-sample collision proof including exact cables, connectors, guard, stop and gripper;
- a physical hard stop and measured fault stopping overtravel below the 122-degree collision pose;
- received mass/COM/inertia, joint-slip, preload, fatigue, impact and cycle proof; and
- qualified mechanical review plus every applicable electrical, control and safety gate.

R56 creates no supplier packet and closes no procurement, fabrication, assembly, energization or functional-safety gate.
