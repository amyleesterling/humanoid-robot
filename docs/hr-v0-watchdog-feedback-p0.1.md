# HR-V0 Watchdog Feedback Receiver P0.1

> **PRELIMINARY - NOT APPROVED FOR FABRICATION OR ENERGIZATION**

Electrical dependency: `Project Button Electrical V3-P1.0`

Firmware configuration: `HR-V0-WD-P0.4`

Date: 2026-08-06

## Scope and decision

This record replaces the opaque `IFB1` and `IFB2` placeholders from Electrical V3-P0.3 with one proposed dual-channel `ISO1212DBQ` receiver and explicit supporting components. R30 / Electrical V3-P0.9 froze exact passive order codes. R31 / Electrical V3-P1.0 adds the explicit PCB connector boundary and an unrouted PCB-P0.1 placement source, but routed layout, stack-up, enclosure, passive derating, EMC/surge testing, received-part inspection, hardware-in-the-loop testing, fault injection and qualified review remain open.

No PL, SIL, galvanic-isolation or functional-safety credit is assigned. `GND1`, `FGND1`, and `FGND2` all return to `SAFETY_0V` in this ordinary watchdog architecture. The component contains an isolation barrier, but this implementation does not preserve separate field and logic reference domains.

## Controlled circuit

The circuit is modeled on KiCad sheet `08_watchdog_feedback_interface.kicad_sch`.

| Function | Channel 1 | Channel 2 | Controlled connection |
|---|---|---|---|
| relay NC diagnostic input | `WD1_NC_24V` | `WD2_NC_24V` | KWD terminal `22` to `RTHR` input and wetting load |
| threshold/surge resistor | `RTH1`, Vishay `MMA02040C1001FB300` | `RTH2`, same | 1.00 kOhm 1%, 0.4 W MELF; module input to `SENSEx` |
| current-set resistor | `RSN1`, Panasonic `ERJ6ENF5620V` | `RSN2`, same | 562 Ohm 1%, 0805; between `SENSEx` and `INx`, exactly as TI specifies |
| input filter | `CFI1`, TDK `CGA3E2X7R1H103K080AA` | `CFI2`, same | 10 nF 50 V X7R 0603; `SENSEx` to `FGNDx`; locate at `UFB1`; DC-bias evidence open |
| contact-wetting load | `RW1`, Vishay `CRCW12102K70FKEA` | `RW2`, same | 2.70 kOhm 1%, 0.5 W 1210; module input to `SAFETY_0V` |
| receiver output | `OUT1` through `RSO1`, Panasonic `ERJ6ENF1001V` | `OUT2` through `RSO2`, same | 1.00 kOhm 1%, 0805; to Pico `GP6` / `GP7` candidate inputs |
| default-low bias | `RPD1`, Panasonic `ERJ6ENF1002V` | `RPD2`, same | 10.0 kOhm 1%, 0805; Pico input to `SAFETY_0V` |

`UFB1` is the exact active-orderable candidate `ISO1212DBQ`, 16-pin SSOP. Pins 1 and 8 are `GND1`; pin 2 is `VCC1`; pin 3 `EN` is tied to `WD_3V3`; pins 4 and 5 are `OUT1` and `OUT2`; pins 6 and 7 are NC; pins 9/10/11 are `FGND2`/`IN2`/`SENSE2`; pins 14/15/16 are `FGND1`/`IN1`/`SENSE1`. `SUB1` pin 13 and `SUB2` pin 12 remain electrically floating. TI recommends a separate floating 2 mm by 2 mm copper plane for each SUB pin; that requirement remains a PCB-layout gate.

`CDEC1` is the proposed Murata `GRM21BR71H104KA01L`, 100 nF, 50 V, X7R, 0805, from `WD_3V3` to `SAFETY_0V`. It must be located within 2 mm of the `VCC1`/`GND1` pins. PCB placement, land pattern and received-board measurement remain open.

## Input threshold and wetting-current screen

The proposed GlobTek `WR9QI1660YL4NKITR6B` output is 24 V with output regulation of plus/minus 5% measured at the output connector in specification Rev B. The screened operating endpoints are therefore:

```text
Vrail_min = 24.0 V * 0.95 = 22.8 V
Vrail_max = 24.0 V * 1.05 = 25.2 V
```

For `RSENSE = 562 Ohm` and `RTHR = 1 kOhm`, TI specifies a module-input low threshold of 8.7 V to 9.2 V, a high threshold of 10.4 V to 10.95 V, and 1.0 V to 1.2 V hysteresis. Both screened rail endpoints are therefore above the specified high threshold. This is a component-level margin check, not an EMC or wiring-drop validation.

Phoenix Contact specifies a 5 V / 10 mA minimum switching load for the proposed `PLC-RSC-24DC/21-21` contact. A 2.70 kOhm, 1%, 0.5 W shunt is therefore placed across each input. Using worst-case rail and resistor tolerance:

```text
Rwet_max = 2700 Ohm * 1.01 = 2727 Ohm
Iwet_min = 22.8 V / 2727 Ohm = 8.36 mA

Iiso_min = 2.05 mA
Icontact_min = 8.36 mA + 2.05 mA = 10.41 mA

Rwet_min = 2700 Ohm * 0.99 = 2673 Ohm
Iwet_max = 25.2 V / 2673 Ohm = 9.43 mA
Iiso_max = 2.75 mA
Icontact_max = 9.43 mA + 2.75 mA = 12.18 mA
```

The `Iiso` bounds use TI's specified 2.05 mA to 2.75 mA input-current range for a 562 Ohm current-set resistor above the low threshold and below 30 V. Applying that table to the module input with the 1 kOhm threshold resistor is an engineering inference: the resistor drops only a few volts at the current limit, leaving `SENSE` within the cited range. Received-board current measurements across temperature remain required.

Worst-case steady dissipation in the wetting resistor is:

```text
Pwet_max = 25.2 V^2 / 2673 Ohm = 0.238 W
0.238 W / 0.5 W = 47.6% of candidate rating
```

The exact proposed wetting resistor is Vishay `CRCW12102K70FKEA`, rated 0.5 W at 70 degrees C under the cited manufacturer conditions. The 0.5 W rating has preliminary steady-state margin, but pulse, temperature-rise, mounting, ambient and enclosure derating still require review. The exact proposed threshold resistor is Vishay `MMA02040C1001FB300`, a MELF with a 0.4 W power-operation rating at 70 degrees C. At the screened 2.75 mA input current its simple steady loss is 7.56 mW; pulse/surge qualification remains open.

## Logic-side screen

At a 3.3 V supply, TI specifies `VOH >= VCC1 - 0.4 V` and `VOL <= 0.4 V` at the documented output currents. The RP2040 input thresholds used for this screen are `VIH >= 2.0 V` and `VIL <= 0.8 V`. The component-level static margins are therefore positive:

```text
high margin >= (3.3 V - 0.4 V) - 2.0 V = 0.9 V
low margin  >= 0.8 V - 0.4 V = 0.4 V
```

The 10 kOhm pulldowns bias each Pico input low when the receiver output is high impedance. TI documents output behavior as undetermined while `VCC1` is between the 1.7 V falling and 2.25 V rising UVLO thresholds, so brownout behavior cannot be closed by resistor analysis. It remains a target-board fault-injection and HIL test.

Raw high means the KWD NC feedback contact is closed, which corresponds to the ordinary watchdog relay being de-energized. Firmware configuration `feedback_gpio_active_high: true` records that polarity. Low is not treated as proof that a relay is safely energized; channel agreement, commanded state, timeout and restart sequencing must all be validated.

## Evidence still required

- received-part identity and measurements for the frozen passive order codes, plus approved footprints, land patterns, placement and derating evidence;
- PCB schematic/board files, creepage/clearance and SUB-plane implementation;
- exact field and logic connectors, terminal protection, test points and enclosure interface;
- source-tolerance, wiring-drop, temperature, surge, EFT, ESD, EMC and thermal validation;
- open/short fault analysis for every passive and every `UFB1` pin;
- received-part inspection and resistance/capacitance measurement;
- powered threshold, wetting-current, brownout, power-sequence and propagation tests;
- fault injection for open contact, welded contact, short to 24 V, short to 0 V, missing 3.3 V, missing 24 V, stuck output and stuck GPIO;
- compiled target firmware, disconnected-load HIL traces and qualified electrical/functional-safety review.

## Primary manufacturer evidence

- Texas Instruments, *ISO121x Isolated 24V to 60V Digital Input Receivers*, `SLLSEY7G`, revised February 2025: https://www.ti.com/lit/ds/symlink/iso1211.pdf
- Texas Instruments, `ISO1212DBQ` active orderable part page, accessed 2026-08-06: https://www.ti.com/product/ISO1212/part-details/ISO1212DBQ
- Phoenix Contact, `PLC-RSC-24DC/21-21`, item `2967060`, product PDF generated 2026-08-04, product-data maintenance date 2026-04-01: https://www.phoenixcontact.com/en-pc/products/relay-module-plc-rsc-24dc-21-21-2967060?type=pdf
- GlobTek, `WR9QI1660YL4NKITR6B` specification Rev B, rechecked 2026-08-08: https://spec.globtek.info/spec/?id=01t0c000008jfZg
- Raspberry Pi, current RP2040 and Pico datasheets, accessed 2026-08-06: https://datasheets.raspberrypi.com/rp2040/rp2040-datasheet.pdf and https://datasheets.raspberrypi.com/pico/pico-datasheet.pdf
- Vishay Beyschlag, MELF resistor document `28963`, revision 2026-06-02: https://www.vishay.com/docs/28963/mmu0102_mma0204_mmb0207.pdf
- Vishay, D/CRCW resistor document `20035`, revision 2026-04-14: https://www.vishay.com/docs/20035/dcrcwe3.pdf
- Panasonic Industry, `ERJ6ENF5620V`, `ERJ6ENF1001V`, and `ERJ6ENF1002V` current product pages, accessed 2026-08-06.
- TDK, `CGA3E2X7R1H103K080AA` current production product page, accessed 2026-08-06: https://product.tdk.com/en/search/capacitor/ceramic/mlcc/info?part_no=CGA3E2X7R1H103K080AA
- Murata, `GRM21BR71H104KA01L` official specification asset, updated 2025 and accessed 2026-08-06.

This calculated and part-number-controlled candidate is ready for independent circuit review. It is not a released PCB, wiring instruction, fabrication package or permission to energize. See `docs/hr-v0-watchdog-feedback-passive-closure-r30.md` and execute `INSPECT-ELEC-006` before powered feedback-board testing.
