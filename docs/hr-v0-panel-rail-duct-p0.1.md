# HR-V0 panel rail and duct candidate P0.1

**Identifier:** `HR-V0-PANEL-RD-P0.1`

**Status:** **PRELIMINARY - NOT APPROVED FOR FABRICATION OR ENERGIZATION**

**Configuration:** R123 correction against `HR-V0-CP-P0.6`

## Defect corrected

P0.6 previously carried one 500 mm Phoenix Contact perforated rail candidate against four planning segments totaling 642.6 mm. That stock quantity was insufficient. The same candidate's current manufacturer record states a minimum perforated rail length greater than 100 mm, while P0.6 contains 65 mm and 100 mm segments. The earlier panel definition therefore could not produce all four rails as written.

No material was ordered or cut. R123 corrects the candidate before physical work.

## Exact held candidates

- `BOM-083`: two Phoenix Contact `NS 35/7,5 UNPERF 500MM`, item `1207648`.
- `BOM-084`: one Phoenix Contact `CD 40X40`, item `3240189`, 40 x 40 x 2000 mm cable duct comprising upper part and mounting base.
- `BOM-085`: six Phoenix Contact `CLIPFIX 35`, item `3022218`, allocated as two each for DR1, DR2 and DR3.

These are application quantities, not manufacturer pack quantities and not purchase authorization. Direct manufacturer order minimums may exceed the application quantities; an authorized distributor/quote route and overbuy disposition remain required before any purchase.

`BOM-059` remains `SELECTION REQUIRED` for the residual backplate fasteners, rail/duct fasteners, hole patterns, DR4 end retention and protective-bonding hardware.

## Analytical stock screen

The current planning allocation is:

| Stock | Segments | Nominal used before kerf | Nominal reserve before kerf |
|---|---|---:|---:|
| RAIL-A, 500 mm | DR1 323.8 mm + DR3 65 mm | 388.8 mm | 111.2 mm |
| RAIL-B, 500 mm | DR2 153.8 mm + DR4 100 mm | 253.8 mm | 246.2 mm |
| DUCT-A, 2000 mm | WD1 665.8 mm + WD2 665.8 mm + WD3 323.8 mm | 1655.4 mm | 344.6 mm |

All four unperforated rail segments exceed Phoenix Contact's published greater-than-20-mm minimum for unperforated rail. This proves only that sufficient nominal stock exists. It does not release a length, tolerance, kerf, cut method, hole pattern or finished part.

## DR4 end-retention boundary

The PI5-CASE-D planning envelope is 90.5 mm wide and DR4 is 100 mm long. Two `CLIPFIX 35` brackets are 19 mm wide in total before any clearance. R123 therefore does not allocate those brackets to DR4. Exact DR4 end retention must be selected from the received case bracket, usable rail span, clamp behavior, service access and pull/vibration evidence, or the layout must change.

This avoids turning a catalog-compatible end bracket into an unsupported physical-fit claim.

## Work still prohibited

Before any rail or duct is cut, drilled or installed:

1. Receive and inspect the exact stock, cover and brackets.
2. Fit the received device groups and freeze final lengths, tolerances and service clearances.
3. Select the maker-space tool, workholding, blade/cutter, kerf, burr/chip control and operator/PPE process.
4. Release exact rail/duct/backplate hole patterns from the received backplate and device loads.
5. Select exact fasteners, torque, locking, coating-damage/corrosion treatment and witness marks.
6. Select DR4 end retention from received evidence.
7. Obtain a qualified fault/EMC decision for rail/backplate bonding or isolation; no project DC 0 V/PE bond may be inferred.
8. Issue separate fabrication and assembly authorizations, then execute the controlled forms.

Installed acceptance still requires pull, slip, vibration, service-cycle, fill, segregation, cover, depth, thermal, bonding and qualified enclosure-system evidence. No powered work is included.

## Controlled artifacts

- `electrical/vendor/phoenix-contact/panel-rail-duct-r123/source-manifest-p0.1.csv`
- `electrical/panel/hr-v0-control-panel-p0.6/rail-duct-cut-plan-p0.1.csv`
- `electrical/panel/hr-v0-control-panel-p0.6/rail-duct-holds-p0.1.csv`
- `tests/forms/hr-v0-panel-rail-duct-receiving-template-p0.1.csv`
- `tests/forms/hr-v0-panel-rail-duct-installation-template-p0.1.csv`
- `release/hr-v0/panel-rail-duct-p0.1/index.html`
- `tools/check_hr_v0_panel_rail_duct_p01.py`

## Primary sources

- Phoenix Contact, [NS 35/7,5 UNPERF 500MM item 1207648](https://www.phoenixcontact.com/en-us/products/din-rail-ns-35-75-unperf-500mm-1207648), current official product page, no formal revision stated, rechecked 2026-08-08.
- Phoenix Contact, [CD 40X40 item 3240189](https://www.phoenixcontact.com/en-us/products/wiring-duct-cd-40x40-3240189), current official product page, no formal revision stated, rechecked 2026-08-08.
- Phoenix Contact, [CLIPFIX 35 item 3022218](https://www.phoenixcontact.com/en-us/products/end-block-clipfix-35-3022218), current official product page, no formal revision stated, rechecked 2026-08-08.

**PRELIMINARY - NOT APPROVED FOR FABRICATION OR ENERGIZATION**
