# Sol R12 Post-R62 Status Reconciliation

Date: 2026-08-07

System baseline: `HR-30-SYS-R0.2`

Project response: R62 / Electrical `V3-P1.6` / `HR-V0-CP-P0.2`
Status: **PRELIMINARY—NOT APPROVED FOR FABRICATION OR ENERGIZATION**

## Review identity

The newly supplied Sol summary is the same independent R12 review commissioned in parallel with Fable R11. It is not counted as another independent review. R62 is a project-owned correction and validation pass against Sol's buildability and protection findings.

## Defect reproduced

The R60 `HR-V0-CP-P0.1` drawing reserved only 270 x 43 mm for `JC1`, `FSR1`, `FSR2`, `F0`, `F1`, `F2`, `F3`, and `SD1`. Current primary manufacturer dimensions prove that reserve cannot contain the proposed hardware:

- Blue Sea Systems `5025` body: 84.20 x 124.31 mm;
- Phoenix Contact `PT 4-HESI (5X20)` item `3211861`: 55.9 mm high and 6.2 mm wide per holder;
- Littelfuse `FHAC0002SXJ`: separate main-holder body and lead-service envelope.

P0.1 therefore remains historical and is not a fabrication basis.

## R62 correction

- Issued `HR-V0-CP-P0.2` around Hammond `PJ242010RT` and steel inner panel `18P2117` (533.4 x 431.8 mm nominal panel face).
- Allocated separate bounded service envelopes for the Blue Sea `5025`, two Phoenix `3211861` holders, Littelfuse `FHAC0002SXJ`, and a remaining unresolved-device zone.
- Issued Electrical `V3-P1.6`; `FSR1` and `FSR2` now identify the same exact Phoenix holder candidate.
- Updated the protection register without selecting any fuse rating.
- Expanded the system BOM to 72 groups: 16 evaluation candidates, 19 exact candidates on hold, 3 grouped-component holds, 29 selection-required groups, 4 exclusions, and 1 integrated item.
- Expanded the panel receiving/assembly route to 22 unexecuted records.

Native KiCad validation remains 13 pages, 76 component blocks, 295 modeled terminals, 63 unresolved rows, and ERC 0 errors / 0 warnings. This proves modeled connectivity and annotation only.

## Still open

R62 closes no energization gate. At minimum, the following remain unresolved:

- all six fuse links and their current/time-current/interrupting selections;
- the Phoenix compatible end cover and final grouping arrangement;
- prospective fault current and protection coordination;
- cable length, conductor size, termination, ambient, bundling, inrush and duty cycle;
- received enclosure/backplate/device dimensions and depth/service-clearance proof;
- heat-loss, temperature-rise, duct-fill and human-factors evidence;
- PE bonding, entry hardware, inlet, service disconnect and jurisdictional review;
- released hole/cut coordinates, assembly records and qualified electrical/functional-safety review.

The Sol R12 verdict therefore remains materially valid: HR-V0 is technically achievable but is not yet a buildable or energizable machine.

## Primary records

- Hammond `PJ242010RT`: https://www.hammfg.com/part/PJ242010RT
- Hammond `18P2117`: https://www.hammfg.com/part/18P2117
- Phoenix Contact item `3211861`: https://www.phoenixcontact.com/en-us/products/fuse-terminal-block-pt-4-hesi-5x20-3211861
- Blue Sea Systems `5025`: https://www.bluesea.com/products/5025
- Littelfuse `FHAC0002SXJ`: https://www.littelfuse.com/assetdocs/littelfuse-fuse-holder-ato-fhac-datasheet.pdf

No source maximum is treated as a project selection or application approval.
