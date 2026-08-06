# HR-V0 mechanical release area

**PRELIMINARY—NOT RELEASED FOR FABRICATION OR ENERGIZATION**

This directory contains the first native, parametric mechanical source for the bench-mounted HR-V0 handoff demonstrator. It is **quote geometry**, not a fabrication release. The custom parts are intentionally limited to flat 6061-T6 plates that can be waterjet, laser cut, router cut, or conventionally machined.

## Generate the package

From the repository root on Windows:

```powershell
& '..\.venvs\hr-v0-cad\Scripts\python.exe' cad\hr-v0\src\hr_v0_cad.py
```

For a clean environment, install the pinned package from `requirements-cad.txt`. Generated artifacts include STEP, STL, DXF, readable SVG quote drawings, a STEP/GLB assembly-space model, mass estimates, three interface fit-coupon packages, a guard/catch/cable space study, and `generated/SOURCE-MANIFEST.csv` with SHA-256 hashes for every generated artifact.

## Controlled custom parts

| Part | Description | Quantity | Material | Current status |
|---|---|---:|---|---|
| MV0-001 | 160 mm upper-link plate; H101 output to S102 body-frame interfaces | 1 | 4.75 mm nominal 6061-T6 | Corrected quote geometry; physical fit required |
| MV0-002 | 160 mm forearm plate; H101 input and selected FR12-H104K 24 x 12 candidate pattern | 1 | 4.75 mm nominal 6061-T6 | Do not cut until MV0-FC03 physical fit, fastener stack and load path are released |
| MV0-003 | S102 shoulder-to-column adapter | 1 | 6.35 mm nominal 6061-T6 | Corrected quote geometry; physical fit required |
| MV0-004 | Bench anchor plate | 2 | 6.35 mm nominal 6061-T6 | Site-dependent |

## Controlled nonstructural fit coupon

`MV0-FC01` checks the eight-hole PCD22 through pattern on the received frames. `MV0-FC02` checks the selected four-tapped-hole 32 x 16 mm rectangle on the received FR13-S102K. `MV0-FC03` checks the selected FR12-H104K four-hole subset on a 24 x 12 mm rectangle and records seating plus fastener access. Their generated DXF/STEP/STL and 1:1 A4 SVG files are under `generated/fit-coupons/`. Use only [the PCD22 procedure](../../docs/hr-v0-fit-coupon-procedure-p0.1.md), [the S102 procedure](../../docs/hr-v0-s102-fit-procedure-p0.1.md), and [the gripper architecture/inspection route](../../docs/hr-v0-gripper-architecture-p0.1.md). No coupon is a structural part, tolerance release, thread qualification, or evidence that the final fastener stack is acceptable.

The corrected interface and fastener boundary is [controlled separately](../../docs/hr-v0-joint-interface-fasteners-p0.1.md). The earlier symmetric PCD22 assumption was invalid: H101 output, S102 body-frame, and gripper interfaces are not interchangeable.

## Hard-stop datum study

`generated/hard-stops/` contains the checked J1/J2 coordinate conventions, candidate stop-contact datums and a readable kinematic layout. It deliberately contains no fabricable stop block. The generated mass/energy screen excludes reflected drive inertia and cannot select a bumper or establish impact capacity. See [the hard-stop design basis](../../docs/hr-v0-hard-stop-design-basis-p0.1.md) and [validation procedure](../../docs/hr-v0-hard-stop-validation-p0.1.md).

The assembly uses envelopes for 80/20 40-4040 extrusion and XM540 actuators. Use the untouched manufacturer STEP files in `../vendor/robotis` for final interference checking. The generated assembly is a space claim and mounting concept, not a kinematically constrained assembly.

## Guard, receiver and cable space study

`generated/safety-enclosure/` contains a non-released STEP envelope, readable front/plan guard layout, catch-space assumptions, five cable zones and explicit provisional allowances. The 900 x 400 x 950 mm internal guard space is derived from the 360 mm object-center reach, 35 mm object half-extent, and provisional 25 mm stopping, 25 mm clearance and 5 mm tolerance reservations. Those provisional values are not safety distances or acceptance limits. See [the controlled design basis](../../docs/hr-v0-guard-receiver-cable-p0.1.md).

## Gates before a cutting order

- Execute `INSPECT-MECH-003` with the controlled `MV0-FC01` coupon and received FR13 frames; preserve every per-hole record and photograph.
- Execute `INSPECT-MECH-004` with `MV0-FC02` on both received S102 frames and `INSPECT-MECH-005` on all received kit contents.
- Execute `INSPECT-MECH-008` with `MV0-FC03` on the received FR12-H104K and `INSPECT-GRIP-001` on the allocated RM-X52 mechanism plus its fixed local guard.
- Freeze the full 3D sweep and exact harness, then execute `INSPECT-GUARD-001`, `INSPECT-CABLE-001`, and `TEST-DROP-001`; enlarge the enclosure if measured stopping, payload, tolerance or service volumes exceed the preliminary reservation.
- Confirm the cutting supplier's actual thickness tolerance, hole tolerance, minimum feature and finish.
- Resolve fastener exact parts, strength class, engagement, torque, locking method and witness marking.
- Add and verify hard stops, cable paths, covers, gripper retention and the fixed guard.
- Before any powered stop test, release the backed-up bumper/catch geometry, current/speed/latency bounds, impact acceptance values, guarded fixture and qualified written approval.
- Survey the real Boston bench substrate and select anchors from the substrate and edge-distance evidence.
- Complete the released mechanical calculations and independent mechanical review.

Do not send the generated files as an approved production order.
