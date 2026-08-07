# HR-V0 Watchdog Feedback Receiver P0.1

> **PRELIMINARY - NOT APPROVED FOR FABRICATION OR ENERGIZATION**

Electrical dependency: `Project Button Electrical V3-P0.8`

Firmware configuration: `HR-V0-WD-P0.3`

Date: 2026-08-06

## Scope and decision

This record replaces the opaque `IFB1` and `IFB2` placeholders from Electrical V3-P0.3 with one proposed dual-channel `ISO1212DBQ` receiver and explicit supporting components. It closes a schematic-definition gap only. Exact passive order codes, PCB layout, terminals, enclosure, EMC/surge testing, received-part inspection, hardware-in-the-loop testing, fault injection and qualified review remain open.

No PL, SIL, galvanic-isolation or functional-safety credit is assigned. `GND1`, `FGND1`, and `FGND2` all return to `SAFETY_0V` in this ordinary watchdog architecture. The component contains an isolation barrier, but this implementation does not preserve separate field and logic reference domains.

## Controlled circuit

The circuit is modeled on KiCad sheet `08_watchdog_feedback_interface.kicad_sch`.

| Function | Channel 1 | Channel 2 | Controlled connection |
|---|---|---|---|
| relay NC diagnostic input | `WD1_NC_24V` | `WD2_NC_24V` | KWD terminal `22` to `RTHR` input and wetting load |
| threshold/surge resistor | `RTH1`, 1.00 kOhm 1%, at least 0.25 W MELF | `RTH2`, same | module input to `SENSEx`; exact order code `SELECTION REQUIRED` |
| current-set resistor | `RSN1`, 562 Ohm 1% | `RSN2`, same | between `SENSEx` and `INx`, exactly as TI specifies |
| input filter | `CFI1`, 10 nF 50 V | `CFI2`, same | `SENSEx` to `FGNDx`; locate at `UFB1` |
| contact-wetting load | `RW1`, 2.70 kOhm 1%, 0.5 W | `RW2`, same | module input to `SAFETY_0V`, in parallel with the ISO1212 input path |
| receiver output | `OUT1` through `RSO1`, 1.00 kOhm | `OUT2` through `RSO2`, 1.00 kOhm | to Pico `GP6` / `GP7` candidate inputs |
| default-low bias | `RPD1`, 10.0 kOhm | `RPD2`, 10.0 kOhm | Pico input to `SAFETY_0V` |

`UFB1` is the exact active-orderable candidate `ISO1212DBQ`, 16-pin SSOP. Pins 1 and 8 are `GND1`; pin 2 is `VCC1`; pin 3 `EN` is tied to `WD_3V3`; pins 4 and 5 are `OUT1` and `OUT2`; pins 6 and 7 are NC; pins 9/10/11 are `FGND2`/`IN2`/`SENSE2`; pins 14/15/16 are `FGND1`/`IN1`/`SENSE1`. `SUB1` pin 13 and `SUB2` pin 12 remain electrically floating. TI recommends a separate floating 2 mm by 2 mm copper plane for each SUB pin; that requirement remains a PCB-layout gate.

`CDEC1` is 100 nF from `WD_3V3` to `SAFETY_0V`. It must be located at the `VCC1`/`GND1` pins. The exact dielectric, voltage rating, footprint and order code remain `SELECTION REQUIRED`.

## Input threshold and wetting-current screen

The proposed Mean Well `GST40A24-P1J` output is 24 V with a documented plus/minus 2.5% tolerance. The screened operating endpoints are therefore:

```text
Vrail_min = 24.0 V * 0.975 = 23.4 V
Vrail_max = 24.0 V * 1.025 = 24.6 V
```

For `RSENSE = 562 Ohm` and `RTHR = 1 kOhm`, TI specifies a module-input low threshold of 8.7 V to 9.2 V, a high threshold of 10.4 V to 10.95 V, and 1.0 V to 1.2 V hysteresis. Both screened rail endpoints are therefore above the specified high threshold. This is a component-level margin check, not an EMC or wiring-drop validation.

Phoenix Contact specifies a 5 V / 10 mA minimum switching load for the proposed `PLC-RSC-24DC/21-21` contact. A 2.70 kOhm, 1%, 0.5 W shunt is therefore placed across each input. Using worst-case rail and resistor tolerance:

```text
Rwet_max = 2700 Ohm * 1.01 = 2727 Ohm
Iwet_min = 23.4 V / 2727 Ohm = 8.58 mA

Iiso_min = 2.05 mA
Icontact_min = 8.58 mA + 2.05 mA = 10.63 mA

Rwet_min = 2700 Ohm * 0.99 = 2673 Ohm
Iwet_max = 24.6 V / 2673 Ohm = 9.20 mA
Iiso_max = 2.75 mA
Icontact_max = 9.20 mA + 2.75 mA = 11.95 mA
```

The `Iiso` bounds use TI's specified 2.05 mA to 2.75 mA input-current range for a 562 Ohm current-set resistor above the low threshold and below 30 V. Applying that table to the module input with the 1 kOhm threshold resistor is an engineering inference: the resistor drops only a few volts at the current limit, leaving `SENSE` within the cited range. Received-board current measurements across temperature remain required.

Worst-case steady dissipation in the wetting resistor is:

```text
Pwet_max = 24.6 V^2 / 2673 Ohm = 0.226 W
0.226 W / 0.5 W = 45.2% of candidate rating
```

The 0.5 W rating has preliminary steady-state margin, but exact pulse, temperature-rise, mounting, ambient and enclosure derating still require review. TI separately requires a 0.25 W MELF implementation for `RTHR` surge limiting; the exact part and surge qualification remain open.

## Logic-side screen

At a 3.3 V supply, TI specifies `VOH >= VCC1 - 0.4 V` and `VOL <= 0.4 V` at the documented output currents. The RP2040 input thresholds used for this screen are `VIH >= 2.0 V` and `VIL <= 0.8 V`. The component-level static margins are therefore positive:

```text
high margin >= (3.3 V - 0.4 V) - 2.0 V = 0.9 V
low margin  >= 0.8 V - 0.4 V = 0.4 V
```

The 10 kOhm pulldowns bias each Pico input low when the receiver output is high impedance. TI documents output behavior as undetermined while `VCC1` is between the 1.7 V falling and 2.25 V rising UVLO thresholds, so brownout behavior cannot be closed by resistor analysis. It remains a target-board fault-injection and HIL test.

Raw high means the KWD NC feedback contact is closed, which corresponds to the ordinary watchdog relay being de-energized. Firmware configuration `feedback_gpio_active_high: true` records that polarity. Low is not treated as proof that a relay is safely energized; channel agreement, commanded state, timeout and restart sequencing must all be validated.

## Evidence still required

- exact order codes and footprints for `RTH1/2`, `RSN1/2`, `CFI1/2`, `RW1/2`, `CDEC1`, `RSO1/2`, and `RPD1/2`;
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
- Mean Well, `GST40A` specification `GST40A-SPEC`, dated 2026-04-03: https://www.meanwell.com/Upload/PDF/gst40a/gst40a-spec.pdf
- Raspberry Pi, current RP2040 and Pico datasheets, accessed 2026-08-06: https://datasheets.raspberrypi.com/rp2040/rp2040-datasheet.pdf and https://datasheets.raspberrypi.com/pico/pico-datasheet.pdf

This calculated candidate is ready for independent circuit review. It is not a released PCB, wiring instruction, fabrication package or permission to energize.
