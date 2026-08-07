# HR-V0 Boston fabrication and custom-metal sourcing

Status: **VERIFIED SOURCING RESEARCH—NOT A RELEASED MANUFACTURING PACKAGE**

Research updated: 2026-08-07

Region: Boston, Massachusetts, USA

## Program input

- A local library makerspace may provide CNC access, but its metalworking capability is not yet known.
- HR-V0 is a light-duty demonstrator for one soft foam object of at most 100 g; it is not a high-payload robot.
- Low force and low mass do not replace fastener definition, first-article inspection, proof loading, hard stops, guarding, stopping tests or qualified review.

## Recommendation

Use flat 4.75 mm and 6.35 mm 6061-T6 plates, catalog ROBOTIS frames and catalog 80/20 brackets. Do not weld or bend the structural parts. The current 2.70 mm candidate holes in `MV0-001`, `MV0-002`, and `MV0-003` are smaller than their plate thickness, so they are **CNC mill/drill RFQ parts**, not laser-finished SendCutSend parts. `MV0-004` may be profile cut only after the real bench survey closes its slot and anchor definition.

This plan does not depend on a library having metal CNC. See the controlled [flat-plate manufacturing decision](hr-v0-flat-plate-manufacturing-p0.1.md).

## Current part-to-process plan

| Controlled part | Qty | Stock/process candidate | Default RFQ route | Hold point |
|---|---:|---|---|---|
| `MV0-001` upper link | 1 | 4.75 mm 6061-T6; CNC profile and drill | Xometry or Protolabs CNC | `MV0-FC01` and `MV0-FC02`, hole tolerance, DFM and FAI |
| `MV0-002` forearm | 1 | 4.75 mm 6061-T6; CNC profile and drill | Xometry or Protolabs CNC | `MV0-FC01` and `MV0-FC03`, hole tolerance, DFM and FAI |
| `MV0-003` shoulder adapter | 1 | 6.35 mm 6061-T6; CNC profile and drill | Xometry or Protolabs CNC | `MV0-FC02`, column interface, DFM and FAI |
| `MV0-004` bench anchor | 2 | 6.35 mm 6061-T6; profile-cut candidate | SendCutSend or Xometry only after survey | Bench substrate, anchor system, slots, DFM and FAI |
| Fit coupons, guard templates, cable mockups | as needed | Approved nonstructural polymer, plywood or acrylic | Library/FabVille candidate | Inspection procedure and material/use restrictions |

The generated files are RFQ geometry only. Do not upload them as a cutting order.

## Verified options

| Route | Verified capability and access | HR-V0 use |
|---|---|---|
| [Boston Public Library KBLIC](https://www.bpl.org/kblic/) | Official information describes STL/PLA printing with a 146 mm cube limit; the service is currently marked temporarily unavailable. No metal CNC capability is documented. | Not a metal route; recheck the actual neighborhood facility. |
| [FabVille, Somerville](https://fabville.org/machines) | Its ShopBot accepts DXF, but the official material list limits it to wood, cardboard, acrylic and other organic materials. | Nonmetal templates, fixtures and guards only. |
| [Artisans Asylum, Allston](https://www.artisansasylum.com/shops/machine) | Official machine-shop listing includes manual/CNC mills and aluminum capability; orientation and tool-specific testing are required. | Nearby supervised CNC/inspection candidate after operator checkout or instruction. |
| [Lowell Makes](https://lowellmakes.com/facilities/machine-shop/) | Official list includes Tormach CNC, knee mill and lathe; checkout is required. | Local self-fabrication fallback if access and inspection capability are documented. |
| [Mill Forge, Norwood](https://millforge.org/facilities/) | Official facilities list manual metal cutting/forming and welding, but does not establish precision aluminum CNC capability. | General fabrication only; not the baseline precision-link route. |
| [SendCutSend 6061](https://sendcutsend.com/materials/6061-aluminum/) | Lists project stock thicknesses but recommends holes no smaller than material thickness. | `MV0-004` profile RFQ candidate after survey. Do not order the current 2.70 mm holes as laser-finished features. |
| [Xometry CNC](https://www.xometry.com/capabilities/cnc-machining-service/) | Supports 6061 and publishes standard metal tolerance of ±0.005 in / ±0.127 mm unless otherwise specified. | Baseline CNC/DFM quotation for `MV0-001` through `MV0-003`; the quote, drawing and FAI govern. |
| [Protolabs precision machining](https://www.protolabs.com/services/cnc-machining/precision-machining-tolerances/) | Publishes standard machined-hole tolerance and drawing-based precision review. | Independent CNC/DFM quotation. |

Current prices are not engineering inputs; they depend on the released geometry, quantity, tolerance, finish, inspection and lead time.

## Library/makerspace capability checklist

Before assigning any metal part, record:

- exact machine make/model, work envelope and operating status;
- written approval for 6061 at 4.75 or 6.35 mm;
- spindle, tooling, workholding, coolant/chip-control and stock rules;
- CAM workflow and accepted source formats;
- class, certification, supervision, reservation, cost and residency rules;
- drawing tolerance the shop accepts and the available calibrated inspection instruments; and
- permission for outside stock, cutting fluid, drilling, reaming, tapping and repeat setups.

Until this evidence exists, use the library only for approved nonmetal fit coupons, fixtures and guard templates.

## Immediate sequence

1. Receive one FR13-H101K, one FR13-S102K and the controlled gripper interface hardware.
2. Execute `INSPECT-MECH-003`, `INSPECT-MECH-004`, and `INSPECT-MECH-008` with the controlled coupons.
3. Freeze the hole diameter/location tolerances from physical evidence and reviewed structural calculations.
4. Complete fastener, hard-stop, cable, guard and bench-anchor definitions.
5. Obtain comparable CNC quotes for the same hashes and revision; obtain a profile-cut quote for `MV0-004` only after bench survey.
6. Obtain supplier DFM acceptance and release a separately controlled first-article candidate.
7. Inspect first articles under `INSPECT-MECH-009`; do not use them in powered assembly until qualified disposition.

No custom welding, bent aluminum, five-axis machining or free-form metal bodywork is required for HR-V0 R0.1. Do not silently convert a quoted process or local machine into an approved fabrication route.

**PRELIMINARY—NOT APPROVED FOR FABRICATION OR ENERGIZATION.**
