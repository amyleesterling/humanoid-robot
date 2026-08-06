# HR-V0 Source Interface Closure R28

> **PRELIMINARY - NOT APPROVED FOR FABRICATION OR ENERGIZATION**

Configuration: Electrical `V3-P0.7`

Date: 2026-08-06

## Scope

This pass freezes two previously anonymous interfaces:

- `JA1`, the six-position mating connector on the proposed 12 V actuator adapter; and
- `DC1`, the non-isolated 24 V-to-5 V supply for the ordinary watchdog controller.

It does not release the actuator harness, protection, enclosure or watchdog PCB. The exact wire order code and length, splices/distribution, protection, source fault behavior, loaded current profile, converter brownout behavior, EMC, thermal performance and physical evidence remain open.

## JA1 controlled candidate

The Mean Well `GST280A12-C6P` specification `GST280A-SPEC 2026-04-03` identifies its output as a Molex `39-01-2060`-equivalent six-position receptacle, pins 1-3 `+Vo` and pins 4-6 `-Vo`. The controlled project-side candidate is:

| Item | Exact candidate | Controlled facts | Remaining evidence |
|---|---|---|---|
| housing | Molex `39012066` / `39-01-2066` | Mini-Fit Jr. 5559 plug housing; six circuits; positive latch; panel ears; UL 94V-0; -40 to +105 deg C | received mating and keying check; panel/strain-relief drawing |
| contacts | six Molex `444783112` | Mini-Fit HCS male loose contacts; 16 AWG; 1.80-3.10 mm insulation OD; tin; published 11 A contact maximum | exact wire construction; crimp section; pull samples; contact retention; milliohm and thermal evidence |
| hand tool | Molex `63819-0900` | official scope includes `44478-3112`; full-cycle ratchet; 16 AWG profile | calibrated tool identity and lot-specific destructive samples |

Use one stranded-copper 16 AWG conductor per contact. Pins 1-3 remain three separate positive conductors until the released distribution point. Pins 4-6 remain three separate return conductors until the released distribution point. No double-wire crimp is permitted at JA1. The connector shall never be mated or unmated while energized.

### Current screen

The adapter nameplate maximum is 21 A. If the three positive and three return contacts divide current equally:

```text
I_contact_ideal = 21 A / 3 = 7.00 A
project-side HCS guideline = 11 A/contact for 4-6 circuits and 16 AWG
screened utilization = 7 / 11 = 63.6%
screened rating ratio = 11 / 7 = 1.57
```

This is not a released ampacity. The adapter manufacturer does not publish its internal contact construction or contact-by-contact current division, and parallel contacts are not assumed to share equally. `INSPECT-ELEC-004` must measure all three positive-leg currents and all three return-leg currents at the released maximum continuous current and duty cycle, after thermal stabilization in the released enclosure/strain-relief arrangement. The release test shall reject an unmapped pin, reversed polarity, incomplete latch, damaged housing, terminal back-out, contact/wire temperature outside the released limit, or current imbalance outside a limit established by qualified electrical review.

Molex `PS-44476-001` gives an 88.0 N minimum axial wire pullout for 16 AWG HCS contacts. `ATS-638190900` gives a 3.00-3.30 mm strip length and the applicable 16 AWG crimp profile. Destructive pull samples are required from each wire/contact/tool setup lot; the installed harness itself is not pull-tested to destruction.

## DC1 controlled candidate

`DC1` is proposed as TRACO POWER `TSR 1-2450`, a non-isolated 1 A point-of-load regulator:

| Terminal | Function | Project net |
|---|---|---|
| 1 | `+Vin` | `SAFETY_24V` |
| 2 | `GND` | `SAFETY_0V` |
| 3 | `+Vout` 5 V | `WD_5V` |

The current datasheet dated 2024-02-07 specifies 6.5-36 VDC input, 5 V nominal output, 1 A maximum output, short-circuit protection, -40 to +85 deg C operation, and no required external capacitor below 32 V input. This supports the nominal 23.4-24.6 V Mean Well range and removes four anonymous `TBD-*` terminals from the ECAD model.

The selection is still provisional. Manufacturer short-circuit protection is not branch-protection coordination, and the datasheet does not establish the project's startup, brownout, Pico reset, stuck-output, overvoltage-failure, conducted/radiated EMC or enclosed thermal behavior. `INSPECT-ELEC-004` must capture input, 5 V output, Pico 3.3 V, reset and both relay-drive outputs through controlled startup, slow input ramp, fast dropout and recovery with relay coils disconnected first. A qualified reviewer must release the load profile and pass/fail limits before execution.

## Configuration result

- Electrical revision advances from `V3-P0.6` to `V3-P0.7`.
- `DC1` changes from four anonymous interface terminals to exact pins 1-3.
- Modeled terminals decrease from 241 to 240.
- `TBD-*` terminal designations decrease from 60 to 56.
- Unresolved component/interface rows remain 43 because both candidates still require application and physical verification.
- No energization gate closes.

## Primary manufacturer evidence

- Mean Well, `GST280A-SPEC`, dated 2026-04-03: https://www.meanwell.com/Upload/PDF/GST280A/GST280A-SPEC.PDF
- Molex, 5559 series chart and part `39012066`, accessed 2026-08-06: https://www.molex.com/en-us/products/series-chart/5559
- Molex, 44478 series chart and part `444783112`, accessed 2026-08-06: https://www.molex.com/en-us/products/series-chart/44478
- Molex, `PS-44476-001`, revision D, dated 2003-06-12: https://www.molex.com/content/dam/molex/molex-dot-com/products/automated/en-us/productspecificationpdf/444/44476/PS-44476-001-001.pdf
- Molex, `ATS-638190900`, revision H, dated 2015-08-28: https://www.molex.com/content/dam/molex/molex-dot-com/products/automated/en-us/applicationtoolingspecificationpdf/638/63819/ATS-638190900-001.pdf
- TRACO POWER, `TSR 1 Series`, dated 2024-02-07: https://www.tracopower.com/tsr1-datasheet

No part of this record authorizes procurement of unreleased wire/protection/distribution parts, harness fabrication, installation or energization.
