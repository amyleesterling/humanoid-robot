# HR-V0 mechanical release area

**PRELIMINARY—NOT RELEASED FOR FABRICATION OR ENERGIZATION**

This directory contains the first native, parametric mechanical source for the bench-mounted HR-V0 handoff demonstrator. It is **quote geometry**, not a fabrication release. The custom parts are intentionally limited to flat 6061-T6 plates that can be waterjet, laser cut, router cut, or conventionally machined.

## Generate the package

From the repository root on Windows:

```powershell
& '..\.venvs\hr-v0-cad\Scripts\python.exe' cad\hr-v0\src\hr_v0_cad.py
```

For a clean environment, install the pinned package from `requirements-cad.txt`. Generated artifacts include STEP, STL, DXF, readable SVG quote drawings, a STEP/GLB assembly-space model, mass estimates, and a machine-readable manifest.

## Controlled custom parts

| Part | Description | Quantity | Material | Current status |
|---|---|---:|---|---|
| MV0-001 | 160 mm upper-link plate | 1 | 4.75 mm nominal 6061-T6 | Quote geometry |
| MV0-002 | 160 mm forearm plate | 1 | 4.75 mm nominal 6061-T6 | Quote geometry |
| MV0-003 | Shoulder-to-column adapter | 1 | 6.35 mm nominal 6061-T6 | Fit coupon required |
| MV0-004 | Bench anchor plate | 2 | 6.35 mm nominal 6061-T6 | Site-dependent |

The assembly uses envelopes for 80/20 40-4040 extrusion and XM540 actuators. Use the untouched manufacturer STEP files in `../vendor/robotis` for final interference checking. The generated assembly is a space claim and mounting concept, not a kinematically constrained assembly.

## Gates before a cutting order

- Print 1:1 paper overlays or cut an inexpensive polymer coupon and physically verify every ROBOTIS PCD against the purchased FR13 frames.
- Confirm the cutting supplier's actual thickness tolerance, hole tolerance, minimum feature and finish.
- Resolve fastener exact parts, strength class, engagement, torque, locking method and witness marking.
- Add and verify hard stops, cable paths, covers, gripper retention and the fixed guard.
- Survey the real Boston bench substrate and select anchors from the substrate and edge-distance evidence.
- Complete the released mechanical calculations and independent mechanical review.

Do not send the generated files as an approved production order.

