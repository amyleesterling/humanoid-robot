# HR-V0 Boston fabrication and custom-metal sourcing

**PRELIMINARY - SOURCING RESEARCH ONLY - NOT APPROVED FOR PROCUREMENT, QUOTATION, FABRICATION, ASSEMBLY, OR ENERGIZATION**

Research updated: 2026-08-08

Region: Boston, Massachusetts, USA

Identifier: `HR-V0-FAB-SRC-P0.5`

Current geometry input: `HR-V0-ARM-ARCH-P0.7` / `HR-V0-J2-STOP-P0.1` / R69

Controlled route register: `cad/hr-v0/manufacturing/hr-v0-r69-fabrication-route-register.csv`

## Configuration correction

The earlier version of this page named `MV0-001`, `MV0-002`, and `MV0-003` as current custom parts. R53 withdrew those parts because their coplanar-frame assumption was wrong. They remain historical only and must not be quoted, cut, or uploaded to a supplier.

The current R69 arm candidate uses:

- one `MV0-C01` standard adapter and one H104-specific `MV0-C04` candidate;
- one `MV0-C05` S102-to-40-4040 support candidate, `48 x 80 x 9.525 mm` nominal;
- one `MV0-C06` moving striker adapter and one `MV0-C07` fixed catch adapter with a controlled face step, both analytical stop candidates;
- one 100 mm and one 50 mm 80/20 `20-2040` extrusion candidate, each with the proposed `20-7047` two-hole M5 end-tap service; and
- catalog ROBOTIS frames and current exact fastener candidates recorded in `HR-V0-ARM-ARCH-P0.7`.

The H104 and S102 source axes and C06/C07 stop geometry are explicit candidates, but bumper selection, received fit, T-slot capacity, complete cable/guard envelope, stop load/contact/tolerance closure, stopping-overtravel margin, bench anchor, supplier DFM, FAI, proof testing, and qualified mechanical acceptance remain open. The parent `HR-V0-MECH-P0.6` release hold remains in force.

## R90 material and process correction

An earlier research note suggested `4.75 mm` (`0.187 in`) SendCutSend plate. That thickness is incompatible with every current C01/C04/C05/C06/C07 part. P0.7 controls nominal thickness at `9.525 mm` with a `9.00..10.00 mm` finished range. **Do not upload, quote, order or substitute 4.75 mm stock.**

SendCutSend's current official pages list `0.375 in` 6061-T6 and countersinking, but the published process evidence does not close this design:

- published accuracy is `+/-0.015 in` (`+/-0.381 mm`), while P0.7 requires locations/profile down to `+/-0.05 mm`, C06 rail datums at `+/-0.025 mm`, and C07 rail coplanarity `<=0.03 mm`;
- its standard M5 90-degree countersink table uses a `10 mm` major diameter, while C01/C04/C06/C07 require `11.30 +0.10/-0.00 mm` and a received-head functional check;
- the current controlled stock candidate is traceable 6061-T651 with an MTR, not an unreviewed T6 substitution; and
- C07 requires a controlled `1.000 +/-0.05 mm` face step and retained surface/coplanarity map.

SendCutSend is therefore excluded as a finished-part route. A deliberately oversized `9.53 mm` profile blank followed by qualified secondary CNC remains only a research contingency; no current profile-only upload artifact exists, and no datum transfer, traceability method or supplier pair is released.

## Recommended Boston-area route

Use catalog ROBOTIS/80/20 hardware wherever the current candidate permits it. For C01/C04/C05/C06/C07, obtain written DFM from a one-stop high-requirement 3-axis CNC supplier only after a qualified reviewer accepts the P0.7 drawing and stop controls. Xometry is the primary capability-inquiry candidate and Protolabs is the alternate; neither default portal tolerance is sufficient by itself, so every critical drawing control, material certificate and first-article report must receive explicit written acceptance. C06/C07 require one datum-controlled stop review, and C07 requires controlled face-step/coplanarity capability.

Artisans Asylum's current machine-shop page identifies a Bridgeport CNC mill in Allston. That makes it a useful local capability, fixture, training or secondary-inspection candidate, but does not establish accepted material, CAM/workholding, operator availability, the P0.7 tolerances, calibrated CMM capability or responsibility for an FAI. It is not the current first-article supplier route.

The Boston Public Library pages checked for this research document design, software, and PLA resources but no suitable structural-aluminum machining capability. FabVille describes education and prototyping rather than production. Neither is a current structural-metal supplier route.

## R75 fixed-guard sourcing route

`HR-V0-GUARD-P0.3` now freezes 80/20 `20-2020`, `14201`, and `75-3581` as exact catalog candidates and Plaskolite TUFFAK GP clear nominal 6 mm as the exact sheet-grade candidate. The 16 profile cuts can be configured directly through 80/20 or an authorized distributor. Obtain one written configuration that lists every cut length, quantity and unmachined-end condition; do not substitute a visually similar 20 mm extrusion or mixed T-slot series.

Obtain the TUFFAK GP sheet from a supplier that will state Plaskolite manufacturer, TUFFAK GP clear grade, nominal thickness, actual stock-sheet identification and traceability on the quote and packing documents. A generic “polycarbonate” line item is not acceptable. The thirteen P0.3 sheet values are enclosure envelopes, not released finished dimensions, so no machine-panel cut plan may be issued from them. Exact supplier/SKU, thickness tolerance, final fit and cut capability remain `SELECTION REQUIRED`.

R76 `HR-V0-GUARD-RET-P0.1` excludes the drill-through `20-2496` route from the current retention baseline and records `12004` only as a nonselected continuous-gasket evaluation candidate for nominal 3 mm outer panels. Its eleven-length packing result is a stock screen before kerf, not a purchase list. A separately approved evaluation may obtain traceable sample stock and an exact fit/impact fixture only after its drawings and test energy are released; it may not order finished machine panels.

Artisans Asylum remains a local capability candidate for supervised fit-up, deburring, measurement or fixture work after the drawings and work authorization exist. It is not assumed to accept the job or provide certified structural inspection. No library or makerspace is authorized to drill panels, assemble the frame, or modify guard parts from the current candidate.

## Current part-to-process plan

| Current item | Candidate quantity | Candidate process | Current action | Hold point |
|---|---:|---|---|---|
| `MV0-C01` adapter | 1 | One-stop 3-axis CNC from accepted drawing/STEP/DXF | Capability/DFM inquiry only after qualified drawing review | Material/MTR acceptance, supplier DFM, separate first article, FAI and proof |
| `MV0-C04` H104 adapter | 1 | One-stop 3-axis CNC from accepted drawing/STEP/DXF | Capability/DFM inquiry only after qualified drawing review | Received H104 fit, material/MTR, DFM, separate first article, FAI and proof |
| `MV0-C05` shoulder support | 1 | One-stop 3-axis CNC from accepted drawing/STEP/DXF | Capability/DFM inquiry only after qualified drawing review | Received S102/40-4040 fit, T-slot proof, material/MTR, DFM, separate first article and FAI |
| `MV0-C06` moving striker | 1 | One-stop 3-axis CNC from accepted STEP/DXF/control schedule | Capability/DFM inquiry only after qualified stop review | STOP-001/002/005, MTR, FAI, complete contact/load/tolerance and proof evidence |
| `MV0-C07` fixed catch | 1 | One-stop 3-axis CNC including controlled face step | Capability/DFM inquiry only after qualified stop review | STOP-003/004/005, step/coplanarity CMM, bumper/retention, load and proof evidence |
| C01/C04/C05/C06/C07 profile blanks | 5 total | Oversized 9.53 mm blank only, then qualified secondary CNC | Research contingency only; direct finished-part route excluded and no controlled upload artifact exists | Separate oversized blank artifacts, T6/T651 disposition, traceability, datum/fixture plan, finished-feature capability and FAI |
| 80/20 `20-2040`, 100 mm | 1 | Catalog cut plus `20-7047` two-hole M5 end-tap service | Written supplier configuration/DFM confirmation only | Received length, squareness, end-tap location/depth, thread-gauge result and joint proof |
| 80/20 `20-2040`, 50 mm | 1 | Catalog cut plus `20-7047` two-hole M5 end-tap service | Written supplier configuration/DFM confirmation only | Same as 100 mm member |
| Bench anchor | 2 candidate | Selection required after actual bench survey | Site survey only | Substrate, edge distance, access, anchor system, pull-out basis, slots, DFM, FAI and proof |
| Fit/guard/cable aids | as needed | PLA, plywood, foam, or other approved nonstructural material | Prototype only | Must not enter a primary load path or be mistaken for released guarding |

## Capability screen

All pages were checked 2026-08-07; no formal revision was exposed unless the page itself stated one.

| Candidate | Published evidence | Controlled use |
|---|---|---|
| [Artisans Asylum, Allston](https://www.artisansasylum.com/shops/machine) | Current page lists a Bridgeport CNC mill and requires tool testing for members/day-pass users. | Local capability, fixture, training, finishing, or supplemental inspection inquiry. Required material, workholding/CAM, operator, tolerance and calibrated-metrology evidence remain unverified. |
| [Xometry CNC](https://www.xometry.com/capabilities/cnc-machining-service/) | Current page lists aluminum 6061, technical drawings, inspection/material-certification options, `+/-0.005 in` default metal tolerance and tighter drawing-defined capability. | Primary one-stop capability-inquiry candidate after qualified drawing review. Written precision, material/MTR and FAI acceptance is mandatory; no quote, supplier selection, or work authorization exists. |
| [Protolabs aluminum CNC](https://www.protolabs.com/services/cnc-machining/aluminum/) | Current pages list 6061-T651 and precision/network machining with drawing-defined tolerances and inspection options. | Alternate one-stop high-requirement candidate after qualified drawing review. Exact factory/network route, material, FAI and quoted tolerances govern. |
| [SendCutSend 6061/countersinking](https://sendcutsend.com/services/countersinking/) | Current page lists 0.375 in 6061-T6 and countersinking at `+/-0.015 in`; its M5 table uses a 10 mm major diameter. | Excluded as the finished-part route. Oversized blank research only; no active profile-only artifact, T651/MTR disposition or secondary datum chain exists. |
| [80/20 20-2040](https://8020.net/20-2040.html) | Current profile page offers the proposed two-hole M5 x 0.8 end-tap service. | Catalog member/service candidate subject to written configuration confirmation and received inspection. |
| [Boston Public Library KBLIC](https://www.bpl.org/kblic/) | Checked pages document maker/design resources, not suitable structural-metal machining. | Design and nonstructural prototype aids only on current evidence. |
| [FabVille, Somerville](https://fabville.org/) | Current page describes education, prototyping, and open-shop support. | Training/prototyping candidate only; not a released structural-part route. |

## Evidence required before any first article

1. Qualified mechanical acceptance of the P0.7 C01/C04/C05/C06/C07 drawings, stop controls, tolerances, material specification, provisional MTR threshold, load cases, and analytical method.
2. Received-fit closure of the H104, S102 and 40-4040 interfaces, bumper selection, and complete adapter/support/stop configuration.
3. Supplier written DFM against the exact repository commit, file names, SHA-256 values, quantity, material, process, tolerances, finish, certificate, and FAI requirements.
4. A separately signed authorization for one first article only. A quote or portal upload is not authorization.
5. Completed `tests/forms/hr-v0-arm-adapter-fai-template.csv` and received-fit evidence using calibrated instruments.
6. Released installation torque, anti-galling, locking, reuse, witness-mark, proof, and nonconformance rules.
7. Physical joint proof, slip/backlash, cycle/impact, cable/guard, hard-stop, and stopping-overtravel evidence.
8. Signed qualified mechanical disposition and every applicable electrical/functional-safety gate before powered use.

The robot's light 100 g foam-object payload reduces the design load case; it does not remove these controls or make an untested moving arm safe around children.

**PRELIMINARY - SOURCING RESEARCH ONLY - NOT APPROVED FOR PROCUREMENT, QUOTATION, FABRICATION, ASSEMBLY, OR ENERGIZATION**
