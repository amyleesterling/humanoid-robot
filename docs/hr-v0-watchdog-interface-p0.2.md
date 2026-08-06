# HR-V0 Watchdog Hardware Interface P0.2

> **PRELIMINARY—NOT APPROVED FOR FABRICATION OR ENERGIZATION**

Electrical dependency: `Project Button Electrical V3-P0.3`

Firmware configuration: `HR-V0-WD-P0.2`

Date: 2026-08-06

Historical status: this R18 voltage-boundary correction is retained for traceability. Electrical V3-P0.6 and `docs/hr-v0-watchdog-feedback-p0.1.md` supersede the opaque `IFB1`/`IFB2` design placeholders with a calculated ISO1212DBQ candidate and retain the physical-validation gates. The PCB and physical-validation gates remain open.

## Correction being controlled

Electrical V3-P0.2 connected the `KWD1`/`KWD2` first-changeover NC diagnostic nodes directly to unresolved Pico feedback pins. Those NC nodes share their contact common with the 24 V SR1 input returns. Treating them as logic-level signals was incorrect and could expose a 3.3 V GPIO to 24 V.

V3-P0.3 removes that path. The first changeover is used only for the SR1 return. The second changeover switches a separate 24 V diagnostic feed, and its NC output terminates at an explicit `IFB1` or `IFB2` 24 V-to-3.3 V input-interface block. No `WD1_NC_24V` or `WD2_NC_24V` net reaches `WDCTRL1` directly.

## Frozen relay terminals

The Phoenix Contact `PLC-RSC-24DC/21-21`, item `2967060`, official product PDF generated 2026-08-04 contains the circuit diagram and identifies:

| Function | Terminal |
|---|---|
| polarized 24 VDC input | `A1`, `A2` |
| changeover 1 | common `11`, NC `12`, NO `14` |
| changeover 2 | common `21`, NC `22`, NO `24` |

V3-P0.3 assigns `11-14` to the SR1 safety-input return and `21-22` to the diagnostic feedback feed. Terminals `12` and `24` are explicitly unused. The official data also record 24 VDC nominal input, 20.2–33.6 VDC input range at 20 °C, 18 mA typical input current, 8 ms typical response, 10 ms typical release, a polarized input with protection/freewheel diode, screw connection, AWG 26–14 conductor range, 0.6–0.8 N·m terminal torque, and IP20 at the relay base.

These are manufacturer component facts, not an application release. Received-device polarity, contact-state continuity, terminal orientation, conductor/ferrule choice, enclosure, fault behavior, welded-contact detection and common-cause analysis remain required. The ordinary relay receives no PL/SIL credit.

Primary source: [Phoenix Contact product PDF](https://www.phoenixcontact.com/en-pc/products/relay-module-plc-rsc-24dc-21-21-2967060?type=pdf), product-data maintenance date 2026-04-01, generated 2026-08-04.

## Frozen Pico candidate pins

The following assignment is frozen for review so ECAD and firmware configuration cannot drift:

| Signal | RP2040 GPIO | Pico physical terminal |
|---|---:|---:|
| heartbeat input | GP2 | 4 |
| KWD1 default-off drive command | GP3 | 5 |
| KWD2 default-off drive command | GP4 | 6 |
| conditioned KWD1 NC feedback | GP6 | 9 |
| conditioned KWD2 NC feedback | GP7 | 10 |
| watchdog supply input | VSYS | 39 |
| watchdog ground | GND | 38 |
| logic pull-up source | 3V3(OUT) | 36 |

The official Pico documentation identifies VSYS pin 39, 3V3(OUT) pin 36, 3.3 V GPIO operation and the separate `SWDIO`/`GND`/`SWCLK` debug pads. Pin assignment alone does not release the platform. The final carrier or harness must provide external default-off bias on GP3/GP4, protected/conditioned inputs on GP2/GP6/GP7, defined states during reset and SWD programming, current limiting, connector retention and a documented power sequence.

Primary sources: [Raspberry Pi Pico datasheet](https://datasheets.raspberrypi.com/pico/pico-datasheet.pdf) and [current Pico pinout documentation](https://www.raspberrypi.com/documentation/microcontrollers/pico-series.html), rechecked 2026-08-06.

## Feedback input design gate

`IFB1` and `IFB2` are deliberately `DESIGN REQUIRED`. `VO615A-3X001` is recorded only as an optocoupler screening candidate because its exact input resistor, tolerance, power rating, CTR margin, output pull-up, threshold, propagation, leakage, temperature behavior, PCB creepage/clearance, terminal protection and failure response have not been calculated and released.

Before assigning interface terminals or ordering a PCB, the design must establish:

1. minimum and maximum 24 V rail at the installed interface, including source tolerance and transients;
2. relay minimum switching requirement and diagnostic wetting current;
3. optocoupler LED current across rail, resistor tolerance, temperature and forward-voltage limits;
4. worst-case CTR and Pico input-high/input-low margin across temperature and aging;
5. resistor pulse/steady-state dissipation and open/short failure behavior;
6. reverse-voltage/transient protection and input filtering without masking relay dropout;
7. external pull-up and default state for open wiring, unpowered interface and controller reset;
8. exact connector, PCB, enclosure, inspection and test points; and
9. fault-injection traces for open, short-to-24 V, short-to-0 V, welded NC/NO, missing supply and stuck GPIO.

Vishay source used for screening: `VO615A` datasheet document 81753, revision 2.3 dated 2017-02-08. A newer web publication date does not change the revision printed in the datasheet.

## Release effect

This correction closes neither `EG-012` nor `EG-017`. It removes a modeled overvoltage path, freezes reviewable relay/Pico terminals and makes the missing interface explicit. Exact interface circuitry, target compilation, hardware binding, HIL, functional-safety analysis and qualified review remain open.
