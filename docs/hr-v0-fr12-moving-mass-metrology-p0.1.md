# HR-V0 FR12 moving-subassembly mass metrology P0.1

> **PRELIMINARY — UNPOWERED MEASUREMENT ROUTE ONLY — NOT APPROVED FOR PURCHASE, ASSEMBLY, FABRICATION, MOTION, CONNECTION, OR ENERGIZATION.**

Identifier: `HR-V0-FR12-MASS-MET-P0.1`

Date: 2026-08-08

Requirements/procedures: `MASS-002`, `INSPECT-MECH-007`, `INSPECT-MECH-016`, `REVIEW-MASS-002`

Parent comparison: `HR-V0-ARM-ARCH-P1.1-X430-LOWERED-FOREARM-CANDIDATE`

Open input addressed: `LOAD-OPEN-01`

## Decision

R96 correctly excluded the FR12-H101 frame, idler and moving hardware because no accepted mass distribution exists. R97 defines how to obtain that evidence without promoting a storefront field or nominal STEP volume into a received mass.

The official ROBOTIS US product page reports `0.10 lb` for the complete FR12-H101K Set, which includes an HN12-I101 Set, frame, bolts and spacer rings. The official HN12-I101 product page reports `0.20 lb` for that included sub-kit. Whether those rounded fields are shipping database values, placeholders or another commerce convention, they cannot both establish the installed physical mass hierarchy. Both are therefore **rejected for mass, COM and inertia credit**.

`LOAD-OPEN-01` remains open. No physical article has been purchased, received, assembled or measured.

## Exact geometry evidence

The controlled manufacturer `fr12_h101.stp` is SHA-bound in the generated source register. CadQuery imports it as one solid with:

| Frame-only property | Result |
|---|---:|
| Volume | 2,854.117032 mm³ |
| Uniform-geometry centroid | X=0.000000, Y=20.046637, Z=0.000000 mm |
| Bounding box | X ±20.5; Y −2.5..28.0; Z ±12.0 mm |
| Maximum B-Rep vertex radius about J2 X | 29.904013 mm |
| Conservative bounding-box corner radius | 30.463092 mm |

These results describe the frame geometry only. They exclude HN12-I101, output-side moving hardware, installed bolts/spacers, manufacturing variation and any temporary-assembly stack. The bounding-box radius is a geometry support input, not an as-built subassembly envelope.

## Physical article route

No new inferred order code is introduced. The existing evaluation boundary already contains:

- `EVA-010 / BOM-018`: one proposed ROBOTIS OpenMANIPULATOR-X Frame Set RM-X52, SKU `905-0023-000`, containing FR12/HN12 articles and gripper-mechanism parts; and
- `EVA-004 / BOM-007`: one proposed ROBOTIS XM430-W350-T, SKU `902-0124-000`.

After separate program-owner purchase approval, one FR12-H101 and one HN12-I101 may be segregated from the received RM-X52 kit for unpowered measurement. The XM430 may be used only as a temporary unpowered fit article after the screw/engagement/spacer/torque/locking/reuse hold closes. This allocation does not select X430 for the released architecture and must not consume or double-count gripper articles.

## Required measurements

The generated plan has twelve operations and two hard holds. At minimum:

1. Freeze the exact commit, received identities, kit allocation and unpowered work scope.
2. Inventory and photograph every loose item before allocation.
3. Establish received-source parity against the controlled STEP/drawing.
4. Qualify a calibrated balance with no worse than 0.01 g readability, accepted range, traceability, tare stability, repeatability and uncertainty. Readability alone is not accuracy.
5. Record at least ten raw readings each for the frame, idler/output moving hardware, installed fastener/spacer group, and later the complete temporarily assembled moving subset.
6. Do not assemble until exact screw length, engagement, spacer, torque, locking, reuse and teardown instructions are signed.
7. Reconcile the assembled result to the sum of the loose groups within accepted combined uncertainty.
8. Measure every as-built Y/Z extremum about the physical J2 axis and add expanded coordinate uncertainty.
9. Measure Y and Z COM with an accepted two-reaction fixture or another qualified method. For supports separated by `L`, the projected COM from support A is `R_B L / (R_A + R_B)` after fixture tare; the surveyed support-to-J2 datum and uncertainty must then be applied.
10. Obtain qualified mechanical/metrology disposition before replacing `LOAD-OPEN-01`.

The blank result and thirty-reading raw templates remain `NOT EXECUTED`:

- `tests/forms/hr-v0-fr12-moving-subassembly-measurement-template.csv`;
- `tests/forms/hr-v0-fr12-mass-repeat-template.csv`.

## Conservative calculation route

For accepted upper mass `m_upper` and as-built upper radial envelope `r_upper`, including their approved uncertainty contributions:

`Ixx_upper = m_upper × r_upper²`

`gravity_moment_upper = m_upper × g × r_upper`, using `g = 9.80665 m/s²`.

These are rigorous support bounds only when every moving item is inside the measured envelope and counted in the upper mass. They may be conservative enough for a load screen, but they do not supply reflected rotor/gear inertia, compliance, drive persistence, dynamic impact, bumper behavior or continuous actuator capability. A qualified reviewer must decide whether the bounds are acceptable for the intended calculation.

The frame STEP may support a measured-mass-scaled uniform-density frame inertia only after received-source parity and material/distribution uniformity are accepted. Mixed idler/bearing/fastener hardware may not inherit the frame distribution.

## Evidence package

- `cad/hr-v0/generated/fr12-moving-mass-metrology-p0.1/frame-geometry-audit.json`
- `cad/hr-v0/generated/fr12-moving-mass-metrology-p0.1/commerce-weight-conflict.csv`
- `cad/hr-v0/generated/fr12-moving-mass-metrology-p0.1/evaluation-article-allocation.csv`
- `cad/hr-v0/generated/fr12-moving-mass-metrology-p0.1/received-measurement-plan.csv`
- `cad/hr-v0/generated/fr12-moving-mass-metrology-p0.1/mass-radius-bound-sensitivity.csv`
- `cad/hr-v0/generated/fr12-moving-mass-metrology-p0.1/source-register.csv`
- `cad/hr-v0/generated/fr12-moving-mass-metrology-p0.1/package-status.json`
- `release/hr-v0/fr12-moving-mass-metrology-p0.1/index.html`

## Primary sources

- [ROBOTIS FR12-H101K Set](https://www.robotis.us/fr12-h101k-set/), live page checked 2026-08-08; SKU, included components and `0.10 lb` commerce field; no formal revision displayed.
- [ROBOTIS HN12-I101 Set](https://www.robotis.us/hn12-i101-set/), live page checked 2026-08-08; SKU, included components and `0.20 lb` commerce field; no formal revision displayed.
- [ROBOTIS X430 model reference](https://docs.robotis.com/docs/dxl/model_reference/x_series/xh_series/xh430-v210/), live page checked 2026-08-08; official FR12-H101 drawing/STEP links. The controlled reference drawing is dated 2026-01-07.

## Release boundary

This package closes no mass, COM, inertia, torque, stop, structure, fabrication or energization gate. It authorizes no purchase or physical work. P0.7 remains the controlled unreleased geometry; P1.1 and X430 remain unselected. `LOAD-OPEN-02` through `LOAD-OPEN-10` are unaffected.
