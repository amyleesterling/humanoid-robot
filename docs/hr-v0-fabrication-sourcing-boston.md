# HR-V0 Boston fabrication and custom-metal sourcing

**PRELIMINARY - SOURCING RESEARCH ONLY - NOT APPROVED FOR PROCUREMENT, QUOTATION, FABRICATION, ASSEMBLY, OR ENERGIZATION**

Research updated: 2026-08-07

Region: Boston, Massachusetts, USA

Identifier: `HR-V0-FAB-SRC-P0.2`

Current geometry input: `HR-V0-ARM-ARCH-P0.4` / R57

Controlled route register: `cad/hr-v0/manufacturing/hr-v0-r57-fabrication-route-register.csv`

## Configuration correction

The earlier version of this page named `MV0-001`, `MV0-002`, and `MV0-003` as current custom parts. R53 withdrew those parts because their coplanar-frame assumption was wrong. They remain historical only and must not be quoted, cut, or uploaded to a supplier.

The current R57 arm candidate uses:

- four identical `MV0-C01` adapter candidates, each `48 x 40 x 9.525 mm` nominal, from a single received heat lot of OnlineMetals `1249` 6061-T651 stock;
- one 100 mm and one 50 mm 80/20 `20-2040` extrusion candidate, each with the proposed `20-7047` two-hole M5 end-tap service; and
- catalog ROBOTIS frames and current exact fastener candidates recorded in `HR-V0-ARM-ARCH-P0.4`.

The distal H104 interface pattern, complete cable/guard envelope, hard stop, stopping-overtravel margin, bench anchor, received fit, supplier DFM, FAI, proof testing, and qualified mechanical acceptance remain open. The parent `HR-V0-MECH-P0.3` release hold remains in force.

## Recommended Boston-area route

Use catalog ROBOTIS/80/20 hardware wherever the current candidate permits it. For the four adapters, obtain written DFM from a one-stop 3-axis CNC supplier only after a qualified reviewer accepts the P0.4 drawing controls. Use Artisans Asylum as the leading nearby candidate for machine-capability confirmation, training, minor finishing, or independent dimensional inspection. Use SendCutSend only as a possible profile-blank source followed by qualified secondary CNC machining; no current profile-only upload artifact exists, so nothing may be uploaded or ordered on that route.

The Boston Public Library pages checked for this research document design, software, and PLA resources but no suitable structural-aluminum machining capability. FabVille describes education and prototyping rather than production. Neither is a current structural-metal supplier route.

## Current part-to-process plan

| Current item | Candidate quantity | Candidate process | Current action | Hold point |
|---|---:|---|---|---|
| `MV0-C01` adapter | 4 | One-stop 3-axis CNC from accepted drawing/STEP/DXF | Capability/DFM inquiry only after qualified drawing review | Material specification and MTR acceptance, final H104 pattern, supplier DFM, one-first-article authorization, FAI and proof |
| `MV0-C01` profile blank | 4 | Profile cutting without holes/countersinks, then qualified secondary CNC | Research only; no controlled upload artifact exists | Generate a separate hole-free artifact and prove material traceability, datum/fixture plan, finished-feature capability and FAI |
| 80/20 `20-2040`, 100 mm | 1 | Catalog cut plus `20-7047` two-hole M5 end-tap service | Written supplier configuration/DFM confirmation only | Received length, squareness, end-tap location/depth, thread-gauge result and joint proof |
| 80/20 `20-2040`, 50 mm | 1 | Catalog cut plus `20-7047` two-hole M5 end-tap service | Written supplier configuration/DFM confirmation only | Same as 100 mm member |
| Bench anchor | 2 candidate | Selection required after actual bench survey | Site survey only | Substrate, edge distance, access, anchor system, pull-out basis, slots, DFM, FAI and proof |
| Fit/guard/cable aids | as needed | PLA, plywood, foam, or other approved nonstructural material | Prototype only | Must not enter a primary load path or be mistaken for released guarding |

## Capability screen

All pages were checked 2026-08-07; no formal revision was exposed unless the page itself stated one.

| Candidate | Published evidence | Controlled use |
|---|---|---|
| [Artisans Asylum, Allston](https://www.artisansasylum.com/home) | Current page lists Machine Shop, Metal Shop, and CNC Plasma Cutter resources at 96 Holton Street. | Local capability confirmation, training, finishing, or inspection candidate. Exact machine, operator, tolerance, material policy, access, and accepted job remain unverified. |
| [Xometry CNC](https://www.xometry.com/capabilities/cnc-machining-service/) | Advertises 6061 CNC machining, DFM feedback, and inspection options. | One-stop CNC/DFM candidate after drawing review; no quote, supplier selection, or work authorization exists. |
| [Protolabs aluminum CNC](https://www.protolabs.com/services/cnc-machining/aluminum/) | Advertises 6061-T651 CNC machining and published machining tolerances. | Independent one-stop quotation candidate after drawing review; exact material, inspection, and quote terms govern. |
| [SendCutSend 6061](https://sendcutsend.com/blog/6061-t6-aluminum-laser-cutting-service/) | Advertises 6061-T6 profile cutting. | Research-only profile-blank candidate. Current 2.70 mm holes and countersinks require secondary CNC; no active profile-only artifact exists. |
| [80/20 20-2040](https://8020.net/20-2040.html) | Current profile page offers the proposed two-hole M5 x 0.8 end-tap service. | Catalog member/service candidate subject to written configuration confirmation and received inspection. |
| [Boston Public Library KBLIC](https://www.bpl.org/kblic/) | Checked pages document maker/design resources, not suitable structural-metal machining. | Design and nonstructural prototype aids only on current evidence. |
| [FabVille, Somerville](https://fabville.org/) | Current page describes education, prototyping, and open-shop support. | Training/prototyping candidate only; not a released structural-part route. |

## Evidence required before any first article

1. Qualified mechanical acceptance of the P0.4 drawing, tolerances, material specification, provisional MTR threshold, load cases, and analytical method.
2. Closure of the H104 distal pattern and complete adapter quantity/configuration.
3. Supplier written DFM against the exact repository commit, file names, SHA-256 values, quantity, material, process, tolerances, finish, certificate, and FAI requirements.
4. A separately signed authorization for one first article only. A quote or portal upload is not authorization.
5. Completed `tests/forms/hr-v0-arm-adapter-fai-template.csv` and received-fit evidence using calibrated instruments.
6. Released installation torque, anti-galling, locking, reuse, witness-mark, proof, and nonconformance rules.
7. Physical joint proof, slip/backlash, cycle/impact, cable/guard, hard-stop, and stopping-overtravel evidence.
8. Signed qualified mechanical disposition and every applicable electrical/functional-safety gate before powered use.

The robot's light 100 g foam-object payload reduces the design load case; it does not remove these controls or make an untested moving arm safe around children.

**PRELIMINARY - SOURCING RESEARCH ONLY - NOT APPROVED FOR PROCUREMENT, QUOTATION, FABRICATION, ASSEMBLY, OR ENERGIZATION**
