# HR-V0 Boston fabrication and custom-metal sourcing

Status: **VERIFIED SOURCING RESEARCH - NOT A RELEASED MANUFACTURING PACKAGE**

Research updated: 2026-08-07
Region: Boston, Massachusetts, USA

## Program input

- HR-V0 is a light-duty demonstrator for one soft foam object of at most 100 g; low payload does not replace tolerances, inspection, proof loading, hard stops, guarding, stopping tests or qualified review.
- The local library's metalworking capability is unknown. The plan does not depend on it.
- No welding or custom bent structural aluminum is currently required.

## Controlled recommendation

Use flat 4.75 mm and 6.35 mm 6061-T6 plates, catalog ROBOTIS frames and catalog 80/20 brackets. The current 2.70 mm candidate holes in `MV0-001`, `MV0-002`, and `MV0-003` must be CNC drilled/milled. Quote either one-stop CNC or a deliberately hole-free profile blank followed by qualified secondary machining. `MV0-004` remains on site hold until the real bench survey closes its slot and anchor definition.

See the controlled [flat-plate manufacturing decision](hr-v0-flat-plate-manufacturing-p0.1.md), [fabrication-route supplement](hr-v0-boston-fabrication-route-p0.1.md), and machine-readable route register.

## Current part-to-process plan

| Controlled part | Qty | Stock | Permitted quotation route | Hold point |
|---|---:|---|---|---|
| `MV0-001` upper link | 1 | 4.75 mm 6061-T6 | One-stop CNC, or `PROFILE_ONLY_RFQ` blank plus qualified secondary CNC/drill | `MV0-FC01` and `MV0-FC02`, hole tolerance, DFM and FAI |
| `MV0-002` forearm | 1 | 4.75 mm 6061-T6 | One-stop CNC, or `PROFILE_ONLY_RFQ` blank plus qualified secondary CNC/drill | `MV0-FC01` and `MV0-FC03`, hole tolerance, DFM and FAI |
| `MV0-003` shoulder adapter | 1 | 6.35 mm 6061-T6 | One-stop CNC, or `PROFILE_ONLY_RFQ` blank plus qualified secondary CNC/drill | `MV0-FC02`, column interface, DFM and FAI |
| `MV0-004` bench anchor | 2 | 6.35 mm 6061-T6 | Site hold; profile cutting or one-stop CNC only after survey | Bench substrate, anchor system, slots, DFM and FAI |
| Fit coupons, guard templates, cable mockups | as needed | Approved nonstructural material | Library or prototype-shop candidate | Inspection procedure and material/use restrictions |

The generated files are RFQ geometry only. Final-geometry DXFs must not be uploaded to a profile-only supplier as a cutting order.

## Current official-source capability screen

All pages below were rechecked 2026-08-07 and exposed no formal document revision unless stated.

| Route | Current published capability | Controlled HR-V0 use |
|---|---|---|
| [Boston Public Library KBLIC](https://www.bpl.org/kblic/) and [Teen Central](https://www.bpl.org/services-central-library/teen-central/) | Checked pages document CAD/software, MakerBot/PLA and related maker resources. No suitable structural-metal machining capability was documented. | Design/nonstructural aids only on current evidence; excluded from the structural-metal route. |
| [FabVille, Somerville](https://fabville.org/) | Current page describes free open-shop/lab-manager support and says its focus is education and prototyping rather than small-scale manufacturing. | Prototype/training candidate only; exact current machine and material policy require direct confirmation. |
| [Artisans Asylum, Allston](https://www.artisansasylum.com/home) | Current page lists Machine Shop, Metal Shop and CNC Plasma Cutter resources at 96 Holton Street. It does not publish the exact machine, tolerance or availability needed here. | Nearby capability-confirmation, training, secondary-machining or inspection candidate; no job is assumed accepted. |
| [SendCutSend 6061](https://sendcutsend.com/blog/6061-t6-aluminum-laser-cutting-service/) | Advertises 6061-T6 profile cutting and gives 0.170 inch as an example minimum hole, larger than the current 2.70 mm holes. | Hole-free profile-blank quote candidate only; secondary machining remains mandatory. |
| [Xometry CNC](https://www.xometry.com/capabilities/cnc-machining-service/) | Advertises 6061 CNC machining, DFM feedback and inspection options. | One-stop CNC/DFM quotation candidate; exact quote, drawing and FAI govern. |
| [Protolabs aluminum CNC](https://www.protolabs.com/services/cnc-machining/aluminum/) | Advertises 6061-T651 CNC machining and published machining tolerances. | Independent one-stop quotation candidate; T651 versus current T6 callout requires explicit disposition. |

Current prices are not engineering inputs; they depend on the frozen geometry, quantity, tolerance, finish, inspection and lead time.

## Makerspace capability checklist

Before assigning any metal part, record:

- exact machine make/model, work envelope and operating status;
- written approval for 6061 at 4.75 or 6.35 mm;
- spindle, tooling, workholding, coolant/chip-control and stock rules;
- CAM workflow and accepted source formats;
- class, certification, supervision, reservation, cost and residency rules;
- drawing tolerance the shop accepts and available calibrated inspection instruments; and
- permission for outside stock, cutting fluid, drilling, reaming, tapping and repeat setups.

Until this evidence exists, use a library or makerspace only for approved nonmetal aids or capability discussions.

## Immediate sequence

1. Receive the controlled ROBOTIS interface hardware and execute `INSPECT-MECH-003`, `INSPECT-MECH-004`, and `INSPECT-MECH-008`.
2. Freeze finished hole diameter/location tolerances from physical evidence and reviewed calculations.
3. Complete fastener, hard-stop, cable, guard and bench-anchor definitions.
4. Obtain comparable one-stop CNC and/or controlled two-process quotes for the same hashes and revision; obtain any `MV0-004` quote only after bench survey.
5. Obtain supplier DFM acceptance and qualified review of the selected route.
6. Release a separately controlled one-first-article authorization.
7. Execute `INSPECT-MECH-009`; do not use the article in powered assembly until signed disposition.

**PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY OR ENERGIZATION.**
