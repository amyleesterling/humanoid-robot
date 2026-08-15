# HR-V0 Panel Node Placement and Stock Allocation P0.1

**PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION**

Document ID: `HR-V0-PANEL-NODE-PLACEMENT-P0.1`

Configuration reconciliation: `HR-V0-CONFIG-REC-P0.4`

Round: R223

Date: 2026-08-11

## Outcome

R223 gives the five R222 topology nodes a controlled catalog-envelope position on the P0.6 backplate planning geometry. It allocates a candidate 160 mm `DR5` rail and a candidate 323.8 mm `WD4` duct in the prior lower reserve. It also adds the node parts and remaining accessory dependency to the covered system BOM.

This is a layout and stock-arithmetic candidate. It does not release terminal entry coordinates, rail or duct cuts, mounting holes, fasteners, conductor routes, cut lengths, end preparations, wiring, physical tests or energization.

## Candidate coordinates

All coordinates use the existing 533.4 x 685.8 mm P0.6 backplate planning frame.

| Reference | X mm | Y mm | Width mm | Height mm | Basis |
|---|---:|---:|---:|---:|---|
| `DR5` | 54.0 | 545.0 | 160.0 | 7.5 | planning segment of held Phoenix Contact item 1207648 |
| `XD24` | 64.0 | 555.0 | 28.6 | 58.1 | Phoenix Contact item 3273114 catalog envelope |
| `XD0` | 98.6 | 555.0 | 28.6 | 58.1 | Phoenix Contact item 3273112 family envelope |
| `XN1` | 133.2 | 555.0 | 5.2 | 60.4 | Phoenix Contact item 3209549 catalog envelope |
| `XN2` | 138.4 | 555.0 | 5.2 | 60.4 | Phoenix Contact item 3209549 catalog envelope |
| `XN3` | 143.6 | 555.0 | 5.2 | 60.4 | Phoenix Contact item 3209549 catalog envelope |
| `WD4` | 54.0 | 625.0 | 323.8 | 40.0 | planning segment of held Phoenix Contact item 3240189 |

The five node envelopes are mutually non-overlapping, remain inside the backplate boundary and retain at least 9.6 mm nominal planning separation above `WD4`. This is two-dimensional catalog arithmetic only. It does not prove received fit, depth, terminal access, conductor bend, marking, covering, separation, heat, rail retention or enclosure closure.

## Existing-stock arithmetic

- `RAIL-B`: 500 - 153.8 (`DR2`) - 100 (`DR4`) - 160 (`DR5`) = **86.2 mm before kerf**.
- `DUCT-A`: 2000 - 665.8 (`WD1`) - 665.8 (`WD2`) - 323.8 (`WD3`) - 323.8 (`WD4`) = **20.8 mm before kerf**.

The rail arithmetic supports retaining the existing two-stock candidate quantity. The duct result is deliberately held: 20.8 mm is not accepted kerf, tolerance or damage allowance and is not permission to cut.

## BOM correction

The covered system BOM now contains 95 groups: 17 evaluation candidates, 49 exact candidates on hold, three grouped-component holds, 19 selection-required groups, four exclusions and three integrated items.

- `BOM-083` retains two 500 mm rail stock candidates and adds `DR5` to the allocation.
- `BOM-084` retains one 2 m duct candidate and adds `WD4` to the allocation.
- `BOM-085` increases from six to eight held end-bracket candidates for `DR5`.
- `BOM-092` adds one 3273114 and one 3273112 distribution-block candidate.
- `BOM-093` adds three 3209549 junction-terminal candidates.
- `BOM-094` adds one 3030488 group-end-cover candidate.
- `BOM-095` exposes all remaining node markers, partitions, covers, adapters and restraint as `SELECTION REQUIRED`.

None of these rows is procurement-released.

## Route evidence boundary

The package carries one route-status row for each of the 55 R222 conductors. Thirty-seven have center-to-center Manhattan planning screens between same-frame catalog envelopes. Those numbers exclude terminal offsets, duct paths, bends, service loops, door motion, segregation and installation allowance. They are explicitly prohibited as cut lengths. All 55 cut lengths remain `SELECTION REQUIRED`.

## Primary sources

- Phoenix Contact item 3273114 online-catalog PDF generated 2026-08-10: 28.6 mm width, 58.1 mm height, 32.4 mm depth on NS 35/7.5 and 19 connections: <https://www.phoenixcontact.com/us/products/3273114>
- Phoenix Contact item 3273112 current product record, accessed 2026-08-11: blue PTFIX 6/18X2,5-NS35 family member: <https://www.phoenixcontact.com/us/products/3273112>
- Phoenix Contact item 3209549 online-catalog PDF generated 2026-08-10: 5.2 mm width, 60.4 mm height, 36.8 mm depth on NS 35/7.5, open side and listed 3030488 end cover: <https://www.phoenixcontact.com/us/products/3209549>

Catalog ratings and dimensions do not establish Project Button application suitability, protection coordination, safety integrity or physical acceptance.

## Remaining holds

Twelve holds cover P1.18 disposition; received enclosure/backplate geometry; rail/duct release; received node fit and access; PTFIX support/accessories; PT end-cover/segregation; holes/fasteners/bonding; actual routes/cut lengths; door loom; duct fill/separation; loading/protection/thermal evidence; and installed inspection plus qualified release.

The interactive guide is at `release/hr-v0/panel-node-placement-p0.1/index.html`. `HR-V0-CONFIG-REC-P0.4` reconciles the candidate into the controlled configuration while retaining P1.15 as current and P1.18 as unaccepted.
