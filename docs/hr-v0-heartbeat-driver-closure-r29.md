# HR-V0 heartbeat and watchdog-relay driver closure — R29

Status: **PRELIMINARY — NOT APPROVED FOR FABRICATION OR ENERGIZATION**

Configuration: Electrical `V3-P0.8`

Date: 2026-08-06

## What this correction closes

Electrical P0.7 left `ISO1`, `Q1`, and `Q2` as anonymous interfaces. P0.8 replaces them with exact proposed order codes, all physical package pins, explicit passives, and checked native nets:

- `ISO1`: Vishay `VO618A-4X017T`, SMD-4 option 7, CTR bin 4;
- `RHB1`: Panasonic `ERJ6ENF9100V`, 910 ohm, 1%, 0805, 0.125 W;
- `RHP1`: Panasonic `ERJ6ENF1002V`, 10.0 kilohm, 1%, 0805, 0.125 W;
- `UDRV1` and `UDRV2`: two physically separate Texas Instruments `TPL7407LPWR` packages;
- `CDRV1` and `CDRV2`: Murata `GRM21BR71H104KA01L`, 100 nF, 50 V, X7R, 0805.

The two separate driver packages avoid making one seven-channel IC a shared point controlling both relay coils. The RP2040, power rails, clock, firmware, board environment, and upstream safety architecture remain common causes. None of these ordinary components receives functional-safety credit.

## Heartbeat circuit

The exact proposed path is:

`PI_HEARTBEAT -> RHB1 -> ISO1 pin 1 anode; ISO1 pin 2 cathode -> COMPUTE_0V; ISO1 pin 4 collector -> WD_HEARTBEAT; ISO1 pin 3 emitter -> SAFETY_0V; RHP1 pulls WD_HEARTBEAT to WD_3V3.`

The optical interface means the compute and watchdog signal returns are not directly connected through this path. This is a signal-boundary statement only, not an approved insulation coordination or safety-isolation claim. PCB material, pollution degree, creepage, clearance, connectors, protective circuits, contamination, enclosure, transient environment, and production test remain unreleased.

### Resistor screen

Using a deliberately conservative **project screening floor** of 2.6 V for GPIO high and Vishay's 1.65 V maximum LED forward voltage:

`IF(min screen) = (2.6 V - 1.65 V) / 910 ohm = 1.044 mA`

Using 3.3 V and the 1.0 V minimum forward-voltage entry:

`IF(max screen) = (3.3 V - 1.0 V) / 910 ohm = 2.527 mA`

The 2.6 V value is a project input screen, **not** a claimed Raspberry Pi 5 guaranteed output specification. The real Pi output level and LED current must be measured over the released supply, load, temperature, cable, connector, and startup conditions.

At the watchdog side, the 10 kilohm pullup draws:

`IPULLUP = 3.3 V / 10,000 ohm = 0.330 mA`

Vishay specifies CTR bin 4 as 160% to 320% at 1 mA and 5 V, and a 0.4 V maximum saturation voltage at 1 mA LED current and 0.25 mA collector current. Those datasheet points support a design candidate, but do not replace threshold, leakage, temperature, aging, propagation, power-sequence, and fault tests in the actual 3.3 V circuit. The watchdog responds to edges, so inversion is acceptable only after compiled firmware and HIL prove every state and timing requirement.

## Relay-driver circuits

Each relay has its own `TPL7407LPWR` package:

- pin 1 `IN1` receives only `WD1_DRIVE` or `WD2_DRIVE`;
- pins 2 through 7, the unused inputs, are explicitly tied to `SAFETY_0V`;
- pin 8 `GND` returns to `SAFETY_0V`;
- pin 9 `COM` connects to `SAFETY_24V` for the internal flyback clamp and has its own 100 nF candidate bypass;
- pins 10 through 15, unused outputs 7 through 2, are deliberate no-connects;
- pin 16 `OUT1` sinks only `WD1_COIL_N` or `WD2_COIL_N`.

Phoenix Contact publishes 18 mA typical input current at nominal voltage for the proposed `PLC-RSC-24DC/21-21`, versus the driver's much larger single-channel capability. That current comparison is necessary but insufficient: received coil current, pickup/dropout timing, output low voltage, driver temperature, integrated relay diode polarity, clamp interaction, startup, brownout, and open/short faults must be measured.

TI requires the COM pin slew rate to remain below 0.5 V/us and calls for bypass capacitance where hot-plug or repetitive transients could exceed it. The 100 nF parts reserve local bypass positions; they do **not** prove the slew requirement. Oscilloscope evidence in the released PCB/harness/source arrangement remains mandatory.

## Fail-closed expectations to test

- compute output static high, static low, disconnected, or reset must not produce a valid continuing edge stream;
- watchdog startup, reset, brownout, clock fault, stale heartbeat, too-fast heartbeat, and contradictory relay feedback must leave both driver outputs off;
- one driver input, output, COM, or ground open/short must not silently create permission to energize;
- a welded watchdog contact remains a known limitation and must be covered by the system FMEA and qualified safety allocation;
- heartbeat restoration cannot reset SR1, arm SRA1, or energize K1/K2; the physical RESET and later distinct physical ARM sequence remains mandatory.

## Evidence still required

Execute `TEST-ELEC-005` using the controlled template in `tests/forms/hr-v0-watchdog-drive-test-template.csv`. Required evidence includes received-part photographs, PCB artwork and stackup, creepage/clearance inspection, calibrated voltage/current/waveform traces, temperature data, COM slew, relay pickup/dropout, reset/brownout behavior, every listed open/short fault, cross-channel testing, and a qualified electrical plus functional-safety disposition.

P0.8 has 11 native pages, 59 component blocks, 274 modeled terminals, 63 named connected nets, 37 deliberate unconnected nets, 237 wire labels, 47 unresolved component/interface rows, and 46 `TBD-*` terminal designators. KiCad 10.0.5 ERC reports 0 errors and 0 warnings, and the independent exact-net checker passes. ERC proves modeled connectivity and annotation only.

## Primary manufacturer evidence

- Vishay, *VO618A Optocoupler*, document 83432, Rev. 2.1, 2025-01-22, accessed 2026-08-06: https://www.vishay.com/docs/83432/vo618a.pdf
- Texas Instruments, *TPL7407L 40-V 7-Channel Low Side Driver*, `SLRS066D`, revised 2016-03; active `TPL7407LPWR` orderability checked 2026-08-06: https://www.ti.com/lit/ds/symlink/tpl7407l.pdf
- Phoenix Contact, `PLC-RSC-24DC/21-21`, order 2967060, product-data PDF generated 2026-05-19, accessed 2026-08-06: https://www.phoenixcontact.com/en-pc/products/relay-module-plc-rsc-24dc-21-21-2967060?type=pdf
- Panasonic Industry, `ERJ6ENF9100V`, current product page accessed 2026-08-06: https://industrial.panasonic.com/ww/products/pt/general-purpose-chip-resistors/models/ERJ6ENF9100V
- Panasonic Industry, `ERJ6ENF1002V`, current product page accessed 2026-08-06: https://industrial.panasonic.com/ww/products/pt/general-purpose-chip-resistors/models/ERJ6ENF1002V
- Murata, `GRM21BR71H104KA01L` official specification asset, updated 2025 and accessed 2026-08-06: https://pim.murata.com/asset/pim4/ceramicCapacitorSMD/GRM21BR71H104KA01-01-EN_PDF_CERAMICCAPACITORSMD?lastModifiedDatetime=20250707233810
- Raspberry Pi, *RP1 Peripherals*, current official PDF accessed 2026-08-06: https://datasheets.raspberrypi.com/rp1/rp1-peripherals.pdf

No part of this record authorizes ordering, PCB fabrication, wiring, energization, or safety validation.
