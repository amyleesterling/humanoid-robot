# HR-V0 mechanical release area

**PRELIMINARY—NOT RELEASED FOR FABRICATION OR ENERGIZATION**

This directory contains native mechanical sources and correction evidence for the bench-mounted HR-V0 handoff demonstrator. It is not a fabrication release. R53 withdrew `MV0-001` through `MV0-003` and every arm supplier packet. R56 adds `generated/arm-architecture-p0.3/` as the current strengthened exact-coordinate replacement candidate; its adapters, beams and fasteners must not be quoted or fabricated. `MV0-004` remains on its separate bench-survey hold.

## Generate the package

From the repository root on Windows:

```powershell
& '..\.venvs\hr-v0-cad\Scripts\python.exe' cad\hr-v0\src\hr_v0_cad.py
```

For a clean environment, install the pinned package from `requirements-cad.txt`. The old generator retains historical P0.2 files so earlier review evidence remains reproducible; `generated/WITHDRAWN-R53.md` governs those artifacts. Generate the replacement candidate separately with `tools/generate_hr_v0_arm_architecture.py` and validate it with `tools/check_hr_v0_arm_architecture.py`. Its exact-source STEP/GLB, explicit transforms, interface schedule, sampled collision sweep and readable SVG are review evidence only. Fit coupons retain optional STL solely as nonstructural inspection aids.

The current release hold is [HR-V0-MECH-P0.3](../../docs/hr-v0-mechanical-release-p0.3.md). The replacement feasibility layer is [HR-V0-ARM-ARCH-P0.3](../../docs/hr-v0-arm-architecture-p0.3.md). The P0.3 general arrangement intentionally keeps released arm datums blank; the R56 directory contains candidate datums without converting them into released dimensions.

## Controlled custom parts

| Part | Description | Quantity | Material | Current status |
|---|---|---:|---|---|
| MV0-001 | former 160 mm upper-link plate | 1 historical | 4.75 mm nominal 6061-T6 | WITHDRAWN R53; invalid interface architecture; do not quote or fabricate |
| MV0-002 | former 160 mm forearm plate | 1 historical | 4.75 mm nominal 6061-T6 | WITHDRAWN R53; do not quote or fabricate |
| MV0-003 | former S102 shoulder-to-column adapter | 1 historical | 6.35 mm nominal 6061-T6 | WITHDRAWN R53; invalid interface architecture; do not quote or fabricate |
| MV0-004 | Bench anchor plate | 2 | 6.35 mm nominal 6061-T6 | Site hold; bench survey, anchor selection and FAI required |
| MV0-C01 | R54 PCD22-to-member adapter topology | 4 candidate | material/thickness SELECTION REQUIRED | CANDIDATE ONLY; fasteners, tolerances, access and proof open; do not quote or fabricate |
| MV0-C02 | R54 100 mm `20-2040` conservative collision envelope | 2 candidate | orderable route under investigation | Not exact profile CAD; end machining and structural application open; do not quote or fabricate |

The old process decision and supplier screens are retained as historical research in [HR-V0 flat-plate manufacturing P0.1](../../docs/hr-v0-flat-plate-manufacturing-p0.1.md), [Boston fabrication and RFQ route P0.1](../../docs/hr-v0-boston-fabrication-route-p0.1.md), and [withdrawn inquiry packets P0.1](../../docs/hr-v0-fabrication-rfi-p0.1.md). The packet checker must report zero active ZIPs.

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
- Obtain written supplier DFM against the exact drawing and hashes, then inspect one authorized first article under `INSPECT-MECH-009` before any production or powered use.
- Resolve fastener exact parts, strength class, engagement, torque, locking method and witness marking.
- Add and verify hard stops, cable paths, covers, gripper retention and the fixed guard.
- Before any powered stop test, release the backed-up bumper/catch geometry, current/speed/latency bounds, impact acceptance values, guarded fixture and qualified written approval.
- Survey the real Boston bench substrate and select anchors from the substrate and edge-distance evidence.
- Execute `INSPECT-MECH-011` with the exact-bench survey form; obtain facility permission, calculate the complete anchor interface, release numerical proof limits and preserve qualified proof evidence.
- Complete the released mechanical calculations and independent mechanical review.

Do not send any current arm geometry for quotation or fabrication. R54 is an architecture candidate only and no supplier packet is active.
