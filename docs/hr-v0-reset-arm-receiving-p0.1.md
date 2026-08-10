# HR-V0 RESET/ARM Received-Lot Closure P0.1

> **PRELIMINARY - NOT APPROVED FOR FABRICATION OR ENERGIZATION**

Date: 2026-08-07

Electrical candidate: `V3-P1.5` (retains the P1.4 RESET/ARM terminal-control correction)

Gate: `EG-011` remains **partial**

## Controlled result

The complete assemblies remain proposed and frozen as:

| Reference | Function | Complete order code | Visible control |
|---|---|---|---|
| `S1` | monitored RESET for `SR1` only | IDEC `HW1B-M1F10-B` | black, flush, momentary, 1NO, screw terminal; explicit `RESET` legend required |
| `S2` | later monitored ARM for `SRA1` only | IDEC `HW1B-M1F10-G` | green, flush, momentary, 1NO, screw terminal; explicit `ARM` legend required |

The physical terminal identifiers are **not frozen**. They remain `S1:TBD-R1/TBD-R2` and `S2:TBD-A1/TBD-A2` in the connected KiCad candidate.

## Why terminal numbers cannot be copied from an older drawing

IDEC's product-change notice dated 2026-07-14 states that HW shipments have been transitioning since 2026-06-15, either the prior or updated design may be received under the unchanged complete-switch order code, and some internal BOM component codes changed. The live US page for `HW1B-M1F10-G` still identifies the complete assembly as green, flush, momentary, 1NO and screw-terminal, and lists `HW Series Catalog_Screw` dated 2026-07-23. On 2026-08-07, its `View BOM` control returned **No BOM products found**.

This evidence supports the complete order code and function. It does not establish which internal design will arrive, a lot-specific contact-block identity, terminal numbering, or physical orientation. The project will not transfer terminal numbers from a legacy catalog, a push-in model, or visual convention.

## Required closure evidence

Execute `tests/forms/hr-v0-reset-arm-receiving-template.csv` for each received switch before the ECAD terminal labels change. The record must include:

1. purchase order, supplier, lot/date code and complete received marking;
2. packaging label plus front, side and underside photographs with a declared orientation datum;
3. prior/redesigned/unknown design classification, using written IDEC evidence if the appearance is ambiguous;
4. every molded contact-block and terminal marking exactly as received;
5. released-state and pressed-state resistance for the same physical pair, using a recorded meter and lead-compensated open/short checks;
6. mechanical return, retaining mechanism and panel-adapter inspection;
7. independent second-person comparison of photograph, continuity record, harness marker and KiCad mapping; and
8. qualified electrical/safety-reviewer disposition.

An IDEC response may close the design-identification question only if it is attributable to the exact complete code and received lot/design. It does not replace continuity testing.

## Wiring allocation after evidence closes

- `S1` shall connect only `SR1_S12` to `SR1_START_RETURN`; it cannot bypass `SRA1` or command motion.
- `S2` shall connect only `SRA1_S12` to `ARM_AFTER_S2`; it remains distinct from RESET and requires a new press/release after every safety dropout.
- A terminal-map correction must update the generator, checker, native KiCad sheets, BOM, connector schedule, net schedule, wire table, exports and source hashes together.

## Primary manufacturer evidence

- IDEC `HW1B-M1F10-B` product page, rechecked 2026-08-07: https://www.idec.com/en-us/switches-indicator-lights/switches-pushbuttons/pushbuttons-pilot-lights/hw-22mm-heavy-duty/hw1b-m1f10-b
- IDEC `HW1B-M1F10-G` product page, rechecked 2026-08-07: https://www.idec.com/en-us/switches-indicator-lights/switches-pushbuttons/pushbuttons-pilot-lights/hw-22mm-heavy-duty/hw1b-m1f10-g
- IDEC HW specification-change notice dated 2026-07-14: https://www.idec.com/en-us/news/usa-idec-hw-series-product-specification-change

No device has been received or tested. No terminal number, fabrication release, wiring release or energization permission is issued by this record.
