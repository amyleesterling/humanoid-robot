# HR-V0 mechanical release area

**PRELIMINARY—NOT RELEASED FOR FABRICATION OR ENERGIZATION**

This directory contains the first native, parametric mechanical source for the bench-mounted HR-V0 handoff demonstrator. It is **quote geometry**, not a fabrication release. The custom parts are intentionally limited to flat 6061-T6 plates that can be waterjet, laser cut, router cut, or conventionally machined.

## Generate the package

From the repository root on Windows:

```powershell
& '..\.venvs\hr-v0-cad\Scripts\python.exe' cad\hr-v0\src\hr_v0_cad.py
```

For a clean environment, install the pinned package from `requirements-cad.txt`. Generated artifacts include STEP, STL, DXF, readable SVG quote drawings, a STEP/GLB assembly-space model, mass estimates, a PCD22 fit-coupon package, and `generated/SOURCE-MANIFEST.csv` with SHA-256 hashes for every generated artifact.

## Controlled custom parts

| Part | Description | Quantity | Material | Current status |
|---|---|---:|---|---|
| MV0-001 | 160 mm upper-link plate | 1 | 4.75 mm nominal 6061-T6 | Quote geometry |
| MV0-002 | 160 mm forearm plate | 1 | 4.75 mm nominal 6061-T6 | Quote geometry |
| MV0-003 | Shoulder-to-column adapter | 1 | 6.35 mm nominal 6061-T6 | Fit coupon required |
| MV0-004 | Bench anchor plate | 2 | 6.35 mm nominal 6061-T6 | Site-dependent |

## Controlled nonstructural fit coupon

`MV0-FC01` is a 38 mm outside-diameter coupon with eight candidate 2.70 mm holes on a 22 mm pitch circle. The generated DXF/STEP/STL and 1:1 A4 SVG are under `generated/fit-coupons/`. Use them only with [the controlled unpowered inspection procedure](../../docs/hr-v0-fit-coupon-procedure-p0.1.md). The coupon checks the received FR13-H101K and FR13-S102K broad-face pattern; it is not a structural part, tolerance release, or evidence that the final fastener stack is acceptable.

The assembly uses envelopes for 80/20 40-4040 extrusion and XM540 actuators. Use the untouched manufacturer STEP files in `../vendor/robotis` for final interference checking. The generated assembly is a space claim and mounting concept, not a kinematically constrained assembly.

## Gates before a cutting order

- Execute `INSPECT-MECH-003` with the controlled `MV0-FC01` coupon and received FR13 frames; preserve every per-hole record and photograph.
- Confirm the cutting supplier's actual thickness tolerance, hole tolerance, minimum feature and finish.
- Resolve fastener exact parts, strength class, engagement, torque, locking method and witness marking.
- Add and verify hard stops, cable paths, covers, gripper retention and the fixed guard.
- Survey the real Boston bench substrate and select anchors from the substrate and edge-distance evidence.
- Complete the released mechanical calculations and independent mechanical review.

Do not send the generated files as an approved production order.
