# HR-V0 watchdog PCB routed-copper candidate P0.3

> **PRELIMINARY - NOT APPROVED FOR FABRICATION OR ENERGIZATION**

Electrical dependency: `Project Button Electrical V3-P1.0`

PCB identifier: `PCB-P0.3`

Date: 2026-08-06

## Decision

R33 advances the corrected PCB-P0.2 placement into a reviewable two-layer routed-copper candidate. It does not release a board for manufacture. No Gerber, drill, stencil, pick-and-place, stack-up or assembly package exists.

The source generator creates 160 copper segments, 45 vias and one filled `SAFETY_0V` B.Cu zone. Native KiCad 10.0.5 DRC reports zero violations, zero routed unconnected pads and zero footprint errors. The independent checker rebuilds KiCad connectivity and confirms that every multi-pad modeled net is one connected pad set, all 18 deliberate singleton nets remain isolated, and all 89 footprint pads without assigned nets remain untouched.

These results prove only the rules encoded in the current ECAD model. They do not prove manufacturability, component orientation, current capacity, EMC, thermal behavior, insulation, safety performance or correct operation on hardware.

## Controlled evidence

- Native PCB: `electrical/kicad/project-button-v3/project-button-v3.kicad_pcb`
- Generator: `tools/generate_hr_v0_watchdog_pcb.py`
- Independent checker: `tools/check_hr_v0_watchdog_pcb.py`
- Complete DRC: `electrical/kicad/project-button-v3/validation/project-button-v3-pcb-routing-drc.rpt`
- Machine evidence: `electrical/kicad/project-button-v3/validation/project-button-v3-pcb-routing-evidence.json`
- CLI record: `electrical/kicad/project-button-v3/validation/project-button-v3-pcb-routing-cli.log`
- Top and bottom review renders: `electrical/kicad/project-button-v3/output/project-button-v3-pcb-routing-top.png` and `project-button-v3-pcb-routing-bottom.png`

The checker reproduces these routed-path measurements:

| Explicit path | P0.3 path length |
|---|---:|
| `CDEC1.VCC` to `UFB1.VCC2` | 3.3757 mm |
| `CDEC1.VCC` to `UFB1.VCC3` | 3.6537 mm |
| `CDRV1` to `UDRV1.COM` | 7.8250 mm |
| `CDRV1.GND` to `UDRV1.GND8` | 6.8335 mm |
| `CDRV2` to `UDRV2.COM` | 7.8250 mm |
| `CDRV2.GND` to `UDRV2.GND8` | 6.8335 mm |

The corrected placement screens remain within their controlled preliminary limits: `CDEC1` VCC and GND copper-edge gaps are 1.8250 mm and 1.8997 mm, both `CFI` centre distances remain below 3.5 mm, both `RTH` high-voltage pads remain 16.0811 mm from protected receiver/filter copper, and both driver-capacitor COM centre distances remain 3.2797 mm.

## Copper rules and limitations

- Default candidate clearance is 0.15 mm and ordinary candidate track width is 0.25 mm.
- `SAFETY_24V`, `WD1_COIL_N` and `WD2_COIL_N` use the provisional `POWER24` class with 0.75 mm nominal width. Final current capacity and protection coordination are not released.
- Fine-pitch package breakouts use 0.10 mm tracks. A PCB fabricator, stack-up, copper thickness, mask limits, annular-ring rules and documented capability must be selected before those features can be accepted.
- The B.Cu `SAFETY_0V` plane stops above the `ISO1` corridor. This is a geometric candidate only; no creepage, clearance, pollution-degree, overvoltage-category or insulation-system claim is made.
- `UFB1` field and logic returns intentionally share `SAFETY_0V`. The ISO1212 barrier is bypassed by the system net and receives no galvanic-isolation or functional-safety credit.
- The board has no released test-point set. `WD_SWDIO` and `WD_SWCLK` remain isolated singleton pads, not a completed programming connector.
- `UFB1.SUB1` and `SUB2` remain isolated singleton pads. The TI-recommended floating copper-area implementation has not been added or reviewed.

## Fabrication gate remains open

Before fabrication outputs may be generated, the project still needs:

1. independent schematic-to-PCB parity and layout review;
2. official-land-pattern comparison and received-part orientation checks for `UFB1`, `ISO1` and every terminal block;
3. exact board fabricator, controlled stack-up and confirmed 0.10 mm feature capability;
4. final test-point and debug/programming access design;
5. reviewed `SUB1`/`SUB2` floating-copper implementation;
6. prospective-fault-current, source-foldback, fuse, conductor, connector and trace coordination;
7. thermal, COM-slew, brownout, EMC/surge and fault-injection analysis;
8. enclosure, mounting, harness, strain-relief and service-access definition;
9. generated fabrication outputs subjected to a separate controlled review; and
10. qualified electrical and functional-safety review.

After any later fabrication release, received boards still require dimensional inspection, microscope/AOI inspection, resistance and continuity checks, current-limited disconnected-load bring-up, waveform measurements and controlled fault testing before external relays, contactors, actuators or robot loads are connected.

## Primary manufacturer documentation

- Texas Instruments, *ISO121x Isolated 24-V to 60-V Digital Input Receivers*, `SLLSEY7G`, revised February 2025, accessed 2026-08-06: https://www.ti.com/lit/ds/symlink/iso1211.pdf
- Texas Instruments, *TPL7407L 40-V 7-Channel Low-Side Driver*, `SLRS066D`, revised March 2016, accessed 2026-08-06: https://www.ti.com/lit/ds/symlink/tpl7407l.pdf
- Vishay, *VO618A*, document `83432`, revision 2.1 dated 2025-01-22, accessed 2026-08-06: https://www.vishay.com/docs/83432/vo618a.pdf

PCB-P0.3 is suitable for independent routed-layout review. It is not suitable for procurement, fabrication, assembly or energization.
