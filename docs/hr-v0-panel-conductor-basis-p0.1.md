# HR-V0 panel conductor engineering basis P0.1

**PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION**

Identifier: `HR-V0-PANEL-COND-P0.1`

Date: 2026-08-11

Round: R221
Configuration: Project Button Electrical `V3-P1.15-CARRIER-CANDIDATE` under `HR-V0-CP-CONFIG-P0.1`

## Outcome

This pass replaces the false idea that every current panel row can simply use the existing 22 AWG observation wire. Schneider's exact `LC1D25BD` product sheet requires at least 1 mm2 for one flexible control-circuit conductor. Belden 3051 is 22 AWG and approximately 0.33 mm2, so it is rejected for those terminals.

Belden 3057 is now a **source-controlled family candidate** for the 56 fixed internal panel endpoint records. It is 16 AWG, approximately 1.31 mm2, 26x30 tinned copper, 2.3 mm nominal OD, 300 V AWM and intended by Belden for control-panel/internal-wiring applications. The current official page lists active color/put-up variants.

That does not make it an orderable or released wire schedule:

- no color/order-code suffix is selected;
- no cut length or physical route is frozen;
- no opposite endpoint or splice policy is frozen;
- no ferrule, lug or direct-wire method is selected;
- no controlled DCR is available from the reviewed live product record, so voltage drop is not calculated;
- ambient, bundling, duct fill, installed ampacity and protection coordination are unresolved; and
- `F24` remains `SELECTION REQUIRED`.

## Door-loom exclusion

The ten endpoints on `S0`, `S1`, `S2` and `H1` are on the enclosure door. Belden publishes only a 23 mm **stationary** minimum bend radius for 3057. The project has no dynamic-flex rating, door-cycle target, torsion model, abrasion control or installed strain-relief proof. No 3057 door-loom candidate is released; those ten records remain `SELECTION REQUIRED`.

## Terminal compatibility result

The 16 AWG family is only a gauge-fit candidate at Pilz `750104`, Phoenix `2967060`, Schneider `LC1D25BD` control terminals and Phoenix `PT 2,5`. Exact end preparation is still open.

The watchdog PCB's Phoenix `1751248` terminal accepts 16 AWG flexible conductor without a ferrule but publishes only 0.25 to 0.5 mm2 for ferruled flexible conductor. A 16 AWG ferrule at that terminal is therefore explicitly rejected. The watchdog PCB terminal is an interface caution and is not one of the 66 device endpoint rows.

## Why the 66-row table is not a buildable wire list

The current ECAD-derived table is an endpoint register: one device terminal per row. It does not freeze the opposite endpoint for each conductor, implicit or explicit splices, service loops, route, cut length or two-ended termination process. R221 preserves that distinction in every row. A point-to-point from/to schedule must be generated only after received panel and door geometry are measured and the qualified electrical reviewer accepts the topology and process.

## Controlled package

Interactive guide: `release/hr-v0/panel-conductor-basis-p0.1/index.html`

Machine-readable registers:

- `source-register.csv`
- `conductor-family-candidates.csv`
- `terminal-compatibility.csv`
- `endpoint-conductor-candidate-schedule.csv`
- `load-envelope.csv`
- `engineering-screens.csv`
- `unresolved-selection-register.csv`
- `authority-boundary.csv`
- `package-status.json`

Generate with `tools/generate_hr_v0_panel_conductor_basis_p01.py` and validate with `tools/check_hr_v0_panel_conductor_basis_p01.py`.

## Primary sources

- Belden 3057 live record, revision 0.120 dated 2026-06-30, accessed 2026-08-11: https://www.belden.com/products/cable/electronic-wire-cable/lead-wire-hook-up-wire/3057
- Pilz PNOZ s4 operating manual `21396-EN-23`, 2026-02 document, accessed 2026-08-11: https://www.pilz.com/download/open/OM_PNOZ_s4_21396-EN-23.pdf
- Phoenix Contact item 2967060, data maintenance 2026-04-01, accessed 2026-08-11: https://www.phoenixcontact.com/en-us/products/relay-module-plc-rsc-24dc21-21-2967060
- Schneider Electric `SQD-LC1D25BD.PDF`, dated 2017-09-13, live identity rechecked 2026-08-11: https://iportal.se.com/Contents/docs/SQD-LC1D25BD.PDF
- Phoenix Contact item 3209510, accessed 2026-08-11: https://www.phoenixcontact.com/en-us/products/feed-through-terminal-block-pt-25-3209510
- IDEC HW and XW exact product records/catalogs, accessed 2026-08-11.

No result in this document authorizes procurement, fabrication, wiring, connection, powered testing, motion or energization.
