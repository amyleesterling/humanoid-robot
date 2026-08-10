# HR-V0 watchdog PCB placement/interface candidate P0.1

> **PRELIMINARY - NOT APPROVED FOR FABRICATION OR ENERGIZATION**

> **SUPERSEDED BY PCB-P0.2.** P0.1 used a non-matching `UFB1` package footprint and a staging placement that did not satisfy the field/control-side layout constraints. Do not route or fabricate P0.1.

Electrical dependency: `Project Button Electrical V3-P1.0`

PCB identifier: `PCB-P0.1`

Date: 2026-08-06

## Decision

R31 creates the first native KiCad PCB source for the ordinary HR-V0 watchdog circuit. It freezes the board membership, candidate footprints, a 160 mm by 100 mm staging outline, four board-only M3 mounting holes, and three external PCB connector candidates with project-controlled pin allocation. It does **not** route copper, define a fabrication stack-up, release Gerbers, close DRC connectivity, assign safety credit or authorize assembly or energization.

This responds to Sol R12's missing-native-hardware-source finding with a controlled placement/interface artifact. It does not close Sol's build-readiness or energization findings because routing, enclosure fit, protection, conductor/harness selection, received-part verification, HIL, fault injection, EMC, thermal, stopping-time and qualified review remain open.

## Native source and generated evidence

- board: `electrical/kicad/project-button-v3/project-button-v3.kicad_pcb`;
- project footprints: `electrical/kicad/project-button-v3/PBV3_Footprints.pretty/`;
- generator: `tools/generate_hr_v0_watchdog_pcb.py`;
- checker: `tools/check_hr_v0_watchdog_pcb.py`;
- DRC report: `electrical/kicad/project-button-v3/validation/project-button-v3-pcb-placement-drc.rpt`;
- top render: `electrical/kicad/project-button-v3/output/project-button-v3-pcb-placement-top.png`.

The checker controls 26 board-mounted schematic references plus four board-only mounting holes. The board contains zero tracks, zero vias and zero zones. KiCad reports zero placement/clearance/silkscreen DRC violations and **68 unconnected pads**. Those unconnected pads are the explicit routing gate, not a waived success condition.

## Frozen board interfaces

| Reference | Exact proposed device | Project pin allocation | What remains open |
|---|---|---|---|
| `JWP1` | Phoenix Contact `MKDS 1/4-3,5`, item `1751264` | 1 `SAFETY_24V`; 2 `SAFETY_0V`; 3 `WD1_COIL_N`; 4 `WD2_COIL_N` | branch protection, current profile, conductor/ferrule, cable length, bundling, marking, strain relief, received orientation and thermal proof |
| `JWF1` | Phoenix Contact `MKDS 1/2-3,5`, item `1751248` | 1 `WD1_NC_24V`; 2 `WD2_NC_24V` | relay harness, conductor/ferrule, terminal torque, marking, received orientation, EMC and fault proof |
| `JWH1` | Phoenix Contact `MKDS 1/2-3,5`, item `1751248` | 1 `PI_HEARTBEAT`; 2 `COMPUTE_0V` | Raspberry Pi GPIO identity, cable/shielding, retention, source levels/timing, received orientation and EMC |

Phoenix Contact's current official product data records 3.5 mm pitch, 1.1 mm PCB holes, nominal 17.5 A and 200 V, AWG 26-16, 5 mm stripping and 0.22-0.25 N m screw torque for this family. These are component data, not a released Project Button current or voltage rating. The project land patterns remain candidate patterns until the official drawing and received-part measurements are independently checked.

## Controlled placement boundaries

- `WDCTRL1` uses the KiCad `Module:RaspberryPi_Pico_SMD` footprint, including `D1` SWCLK, `D2` ground and `D3` SWDIO pads.
- `UDRV1` and `UDRV2` use separate `TSSOP-16` packages. Their supplies, controller, oscillator, software and PCB remain common causes; separate packages do not establish a safety category.
- `UFB1` uses the `SSOP-16_5.3x6.2mm_P0.65mm` footprint. The current project net class records a 0.15 mm candidate copper clearance because the chosen 0.65 mm-pitch land pattern cannot satisfy the former 0.20 mm default. Fabricator capability and qualified layout review remain required.
- `ISO1` uses a project-controlled Vishay option-7 candidate footprint. It is ordinary signal isolation only. The footprint and creepage/clearance implementation require datasheet and received-part verification.
- `RTH1/RTH2`, `RSN1/RSN2`, `CFI1/CFI2`, `RW1/RW2`, `CDEC1`, `RSO1/RSO2` and `RPD1/RPD2` retain the exact R30 order codes and package candidates.
- The four M3 holes are board-only geometry. Their exact board size, edge distance, fastener, washer, standoff, enclosure and torque remain `DESIGN REQUIRED`.

## Mandatory routing/layout gates

The staging placement is intentionally not treated as datasheet-compliant placement. The routed revision must, at minimum:

1. place `CDEC1` at the `UFB1` `VCC1/GND1` pair within TI's cited close-placement limit and verify the actual copper path;
2. place `CFI1/CFI2`, `RSN1/RSN2` and `RTH1/RTH2` to meet the ISO1212 layout guidance, including the cited separation between the high-voltage end of each threshold resistor and the receiver/filter network;
3. implement the required floating `SUB1` and `SUB2` copper features without tying either substrate pin to a net;
4. keep heartbeat input copper, compute return and the optocoupler boundary separate from 24 V field routing and relay-coil transient loops;
5. locate `CDRV1/CDRV2` at the `TPL7407L` COM/GND loops and prove TI's COM slew requirement by measurement, not capacitance alone;
6. define trace widths from measured normal and fault current, copper weight, temperature rise, ambient, enclosure, duty cycle and fabricator limits;
7. add accessible, labeled test points for both supplies, heartbeat, drive, coil-sink, NC-input, receiver-output and Pico diagnostic nets without creating unsafe shorts or bypass paths;
8. complete routing with zero unconnected pads, rerun KiCad DRC, perform controlled schematic-subset parity, independent layout review, fabricated-board inspection, continuity/short testing and disconnected-load bring-up.

No Gerber, drill, pick-and-place, stencil or assembly release is generated at P0.1.

## Disconnected-load test boundary

The first powered board test, after qualified release of a routed PCB and completion of receiving/assembly inspections, must leave `KWD1`, `KWD2`, both contactors and every actuator load disconnected. Programmable current-limited supplies and relay-load fixtures substitute for field loads. `TEST-ELEC-005` remains the controlling electrical test. R31 adds a PCB inspection record so footprint, orientation, shorts, continuity, current limit, waveform, brownout, COM-slew, thermal and injected-fault evidence cannot be confused with source-only validation.

## Primary manufacturer evidence

- Phoenix Contact, item `1751264`, official product PDF generated 2026-08-06: https://www.phoenixcontact.com/gb/products/1751264/pdf
- Phoenix Contact, item `1751248`, current official product page accessed 2026-08-06: https://www.phoenixcontact.com/en-us/products/printed-circuit-board-terminal-mkds-1-2-35-1751248
- Texas Instruments, *TPL7407L 40-V 7-Channel Low-Side Driver*, `SLRS066D`, revised March 2016: https://www.ti.com/lit/ds/symlink/tpl7407l.pdf
- Texas Instruments, *ISO121x Isolated 24-V to 60-V Digital Input Receivers*, `SLLSEY7G`, revised February 2025: https://www.ti.com/lit/ds/symlink/iso1211.pdf
- Vishay, *VO618A*, document `83432`, revision 2.1 dated 2025-01-22: https://www.vishay.com/docs/83432/vo618a.pdf
- Raspberry Pi, *Pico Datasheet*, current official PDF accessed 2026-08-06: https://datasheets.raspberrypi.com/pico/pico-datasheet.pdf

PCB-P0.1 is suitable for independent placement/interface review. It is not suitable for fabrication, assembly or energization.
