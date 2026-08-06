# HR-V0 Boston Fabrication and Custom-Metal Sourcing

Status: **VERIFIED SOURCING RESEARCH—NOT A RELEASED MANUFACTURING PACKAGE**

Research date: 2026-08-06
Region: Boston, Massachusetts, USA

## Recorded program input

- A local library makerspace may provide CNC access, but its metalworking capability is not yet known.
- HR-V0 is a light-duty demonstrator. Its controlled task remains moving one soft foam object of at most 100 g; it is not being sized as a high-payload robot.
- Low force and low mass reduce the required structure, but they do not replace fastener definition, first-article inspection, proof loading, hard stops, guarding, or stopping tests.

## Recommendation

Make the first HR-V0 structure from flat 4.75 mm and 6.35 mm 6061-T6 plates, catalog ROBOTIS frames, and catalog 80/20 brackets. Do not weld or bend the structural 6061 parts. Quote identical released geometry at SendCutSend and Xometry, then use a local shop for fit-checking, inspection, deburr, or a genuinely three-dimensional operation only when needed.

This approach does **not** depend on the local library having a metal-capable CNC machine.

## Current part-to-process plan

| Controlled part | Qty | Stock/process candidate | Default route | Why this route |
|---|---:|---|---|---|
| `MV0-001` upper link plate | 1 | 4.75 mm / 0.187 in 6061-T6, flat profile cut | SendCutSend quotation | Two-dimensional profile; no pocket, bend, or weld is required. |
| `MV0-002` forearm link plate | 1 | 4.75 mm / 0.187 in 6061-T6, flat profile cut | SendCutSend quotation | Same process and stock as `MV0-001`; quote together from one controlled revision. |
| `MV0-003` shoulder adapter | 1 | 6.35 mm / 0.250 in 6061-T6, flat profile cut | SendCutSend plus local fit inspection | Flat plate; physical FR13 and extrusion fit still govern hole release. |
| `MV0-004` bench anchor plate | 2 | 6.35 mm / 0.250 in 6061-T6, flat profile cut | Hold until bench survey, then quote | Plate outline exists, but the actual bench substrate and anchor hardware are unresolved. |
| Fit coupons, guard templates, cable-routing mockups | as needed | PLA, plywood, acrylic, or other approved nonmetal stock | Library/FabVille candidate | Appropriate use of a router/laser/3D printer even if metal is prohibited. |

The generated files are quote geometry only. Do not upload them as a cutting order until the fit coupon and drawing review gates close.

## Verified options

| Route | Verified capability and access | HR-V0 use |
|---|---|---|
| [Boston Public Library KBLIC](https://www.bpl.org/kblic/) | Current official information describes STL/PLA 3D printing, with a 146 mm cube limit; the service is currently marked temporarily unavailable. No metal CNC capability is documented. | Not a metal route. Recheck the exact neighborhood library/makerspace before assuming otherwise. |
| [FabVille, Somerville](https://fabville.org/machines) | ShopBot accepts DXF and related 2D formats, but its official material list limits the machine to wood, cardboard, acrylic and other organic materials. Community open shop is free. | Polymer guards, templates and fixtures; not 6061 structure. |
| [Artisans Asylum, Allston](https://www.artisansasylum.com/shops/machine) | Official precision machine shop lists manual/CNC mills and aluminum capability. It is self-service: orientation and tool-specific testing are required. [Membership/day-pass terms](https://www.artisansasylum.com/memberships) currently list day passes and monthly access. | Best nearby hands-on option for supervised drilling, countersink, fit correction, metrology and one-off adapters after checkout or private instruction. |
| [Lowell Makes](https://lowellmakes.com/facilities/machine-shop/) | Official machine-shop list includes Tormach CNC, knee mill and lathe; each requires checkout. [Membership](https://lowellmakes.com/membership/) is adult-only with onboarding. | Lower-cost local self-fabrication fallback if travel is practical. |
| [Mill Forge, Norwood](https://millforge.org/facilities/) | Official facilities list includes manual metal cutting/bending/rolling and welding. Its published CNC equipment does not establish precision aluminum milling. Training/certification applies. | Thin guards/enclosures and general assembly, not the baseline precision link route. |
| [SendCutSend](https://sendcutsend.com/materials/6061-aluminum/) | Official 6061-T6 stock list includes 0.187 in (about 4.75 mm) and 0.250 in (6.35 mm). It accepts [DXF, STEP and other listed formats](https://sendcutsend.com/faq/what-file-formats-do-you-accept/) and publishes typical 2–4 day production before shipping. Its 6061 page does not list bending, so none is assumed. | Primary source for flat link, adapter and anchor plates. Capture the actual quote and DFM result before purchase. |
| [Xometry](https://www.xometry.com/capabilities/sheet-cutting/metal-laser-cutting/) | Official sheet-cutting service accepts 3D CAD and DXF/drawings; published 6061-T6 stock spans the project thicknesses. [CNC service](https://www.xometry.com/capabilities/cnc-machining-service/precision-cnc-machining/) supports small-batch 6061 work. | Comparison quote for flat plates and preferred fallback for pockets, bearing seats or other 3D features. |
| [Protolabs](https://www.protolabs.com/services/cnc-machining/cnc-milling/design-guidelines/) | Official CNC guidance supports 6061 and standard neutral CAD formats. Its [formed-sheet guidance](https://www.protolabs.com/services/sheet-metal-fabrication/forming/) limits published formed 6061-T6 thickness to 0.134 in and requires manual review. | Independent CNC/DFM quote, not the 4.75 mm bent-6061 route. |

Current prices are not frozen engineering inputs; each depends on geometry, quantity, tolerance, finish, inspection and lead time.

## Library/makerspace capability checklist

If the user’s local library is different from KBLIC, record all of these before assigning a part:

- exact machine make/model, work envelope and operating status;
- written approval for 6061 aluminum at 4.75 or 6.35 mm;
- spindle, tooling, workholding, coolant/chip-control and stock rules;
- supported CAM workflow and whether staff accept STEP/DXF or require staff-generated CAM;
- required class, certification, supervision, reservation duration, cost and residency/card rules;
- tolerance staff will accept for the actual drawing and available inspection instruments; and
- permission for outside stock, cutting fluid, reaming, tapping and repeat setups.

Until this evidence exists, use a library router only for polymer fit coupons, fixtures and guard templates.

## Quote package and first-article evidence

Every request for quote needs:

1. unique part number, revision, units, quantity and preliminary status;
2. STEP and DXF generated from the same native source with recorded checksums;
3. controlled drawing specifying 6061-T6, thickness, holes, datums/tolerances, deburr and edge break;
4. explicit **NO WELDING** and **NO BENDS** for HR-V0 R0.1;
5. any thread, countersink or insert callout including depth;
6. vendor DFM report, selected process, live lead time/price, quote expiry and material/inspection options; and
7. first-article inspection for thickness, critical dimensions, hole location, burrs, flatness, fit and measured mass.

If a future bend is unavoidable, record alloy/temper, grain direction, radius, vendor bend rules and post-bend property implications. 6061-T6 is less forgiving in bending than common sheet-metal alloys; the safest V0 structure is flat plates plus bolted catalog brackets.

## Immediate purchasing sequence

1. Buy one FR13-H101K and one FR13-S102K manufacturer frame.
2. Make the controlled nonstructural `MV0-FC01` PCD22 coupon from its generated DXF or STL; use polymer, acrylic, or plywood before considering metal.
3. Execute `INSPECT-MECH-003` against both received frames and preserve the per-hole CSV record, scale measurements, hashes, and photographs; revise CAD through configuration control if needed.
4. Complete the missing fastener, hard-stop, cable, guard and bench-anchor design.
5. Obtain comparable SendCutSend and Xometry quotes for the **same revision**.
6. Order only after the mechanical release review changes the files from quote geometry to a controlled first-article release.

## Research decision

No custom welding, bent aluminum, five-axis machining, or free-form metal bodywork is required for HR-V0 R0.1. If a future revision introduces bearing pockets, precision bores, or non-flat load paths, obtain a separate Xometry/Protolabs CNC quote or use Artisans Asylum only with a checked-out operator and an inspection plan. Do not silently convert a laser-cut part into a locally routed aluminum part.

**PRELIMINARY—NOT APPROVED FOR FABRICATION OR ENERGIZATION.**
