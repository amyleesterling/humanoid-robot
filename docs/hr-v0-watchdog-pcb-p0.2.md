# HR-V0 watchdog PCB constrained-placement candidate P0.2

> **PRELIMINARY - NOT APPROVED FOR FABRICATION OR ENERGIZATION**

Electrical dependency: `Project Button Electrical V3-P1.0`

PCB identifier: `PCB-P0.2`

Date: 2026-08-06

## Decision

R32 supersedes the PCB-P0.1 staging placement with a manufacturer-constrained placement candidate. It corrects the physical ISO1212 package, moves the complete field-input network to the field side of `UFB1`, moves the logic network to the logic side, places the side-1 decoupler and both driver COM capacitors locally, and adds reproducible numerical placement checks.

The board remains deliberately unrouted. It contains zero tracks, zero vias and zero zones, and KiCad reports 68 unconnected pads. No Gerber, drill, stencil, position, stack-up or assembly output is released.

## Defects corrected from P0.1

1. `UFB1` previously used KiCad footprint `SSOP-16_5.3x6.2mm_P0.65mm`. That does not match Texas Instruments' `DBQ0016A` package identification for `ISO1212DBQ`, whose documented nominal body is 3.9 mm by 4.9 mm at 0.635 mm pitch. P0.2 uses the candidate KiCad `SSOP-16_3.9x4.9mm_P0.635mm` land pattern. The official TI drawing and a received part still require independent land-pattern and orientation verification before fabrication release.
2. P0.1 placed `RTH1/RTH2`, `RSN1/RSN2`, and `CFI1/CFI2` on the logic side of `UFB1`. P0.2 places the field-input components and `JWF1` to the field side and the output/decoupling network to the logic side.
3. P0.1 did not prove the ISO1212 bypass placement, the high-voltage RTH spacing, or the TPL7407L COM-capacitor loops. P0.2 adds executable geometry screens and a generated JSON evidence record.

## Reproduced placement evidence

`tools/check_hr_v0_watchdog_pcb.py` measures the native board rather than trusting drawing labels. The current result is:

| Placement screen | P0.2 measured result | Control basis |
|---|---:|---|
| `CDEC1` VCC copper edge to nearest `UFB1` VCC copper | 1.025 mm | project maximum 2.0 mm derived from TI layout example |
| `CDEC1` GND copper edge to nearest `UFB1` GND copper | 1.025 mm | project maximum 2.0 mm derived from TI layout example |
| `CFI1` to `UFB1.SENSE1` pad centres | 3.2230 mm | compact field-side cluster screen; routing path remains to be measured |
| `CFI2` to `UFB1.SENSE2` pad centres | 3.4691 mm | compact field-side cluster screen; routing path remains to be measured |
| `RTH1` external-high-voltage copper to protected `UFB1/CFI1/RSN1` copper | 16.0811 mm | TI minimum 4.0 mm placement rule |
| `RTH2` external-high-voltage copper to protected `UFB1/CFI2/RSN2` copper | 16.0811 mm | TI minimum 4.0 mm placement rule |
| `CDRV1` to `UDRV1.COM` pad centres | 3.2797 mm | local COM transient loop screen |
| `CDRV2` to `UDRV2.COM` pad centres | 3.2797 mm | local COM transient loop screen |

The authoritative machine record is `electrical/kicad/project-button-v3/validation/project-button-v3-pcb-placement-constraints.json`. KiCad DRC reports zero placement, clearance, courtyard, solder-mask, or silkscreen violations apart from the separately reported open connections.

## Important electrical boundary

`UFB1` is used as an ordinary 24 V input receiver. Its field-side and logic-side returns are both assigned to `SAFETY_0V` in the controlled schematic. The isolation barrier is therefore bypassed by the system net and receives **no galvanic-isolation or functional-safety credit**. Routing must not relabel this circuit as isolated, and an independent reviewer must decide whether this use of ISO1212 should remain or be replaced by a non-isolated industrial receiver before the PCB is frozen.

`ISO1` remains a separate optical boundary between `PI_HEARTBEAT/COMPUTE_0V` and the watchdog domain. Its component insulation ratings do not by themselves establish system insulation, safety credit, creepage, clearance, pollution degree, overvoltage category, or compliance.

## Routing gate

The next PCB revision may add copper only after its source generator and checker enforce all of the following:

1. two-layer routing with explicit provisional net classes and no released fabricator stack-up;
2. wide `SAFETY_24V`, `SAFETY_0V`, `WD1_COIL_N`, and `WD2_COIL_N` paths, with final widths still dependent on protection and measured fault-current coordination;
3. measured routed path length from `CDEC1` to `UFB1` and from each `CDRV` to `UDRV` COM/GND;
4. 2 mm by 2 mm floating copper features on `SUB1` and `SUB2` without connection to each other or any plane;
5. a copper-free isolation corridor beneath and around `ISO1` consistent with its option-7 land pattern and the final insulation assessment;
6. accessible labeled test points for both supplies, heartbeat, both drive outputs, both coil sinks, both NC inputs, both feedback outputs and watchdog programming/debug;
7. zero DRC violations and zero open connections on every required multi-pad net, while retaining explicit no-connect treatment for unused and substrate/debug-only pads;
8. independent schematic/PCB parity review, layout review, received-board inspection, continuity/short testing and disconnected-load bring-up before any external relay, contactor, actuator or robot load is connected.

## Evidence still required

- official-land-pattern comparison and received-part measurement for `UFB1`, `ISO1`, and all three terminal blocks;
- exact PCB fabricator capability, copper weight, solder-mask limits, finished thickness, material system, temperature rating, controlled stack-up and coupon requirements;
- protection coordination from prospective fault current, source foldback, conductor/connector limits, branch fuse, trace fusing behavior and interrupt rating;
- routed DRC, schematic parity, independent layout review and controlled fabrication-output review;
- assembled-board AOI/microscope inspection, resistance/continuity, current-limited bring-up, COM-slew measurement, brownout, thermal, EMC and injected-fault evidence;
- qualified electrical and functional-safety review.

## Primary manufacturer documentation

- Texas Instruments, *ISO121x Isolated 24-V to 60-V Digital Input Receivers*, `SLLSEY7G`, revised February 2025, accessed 2026-08-06: https://www.ti.com/lit/ds/symlink/iso1211.pdf
- Texas Instruments, *TPL7407L 40-V 7-Channel Low-Side Driver*, `SLRS066D`, revised March 2016, accessed 2026-08-06: https://www.ti.com/lit/ds/symlink/tpl7407l.pdf
- Vishay, *VO618A*, document `83432`, revision 2.1 dated 2025-01-22, accessed 2026-08-06: https://www.vishay.com/docs/83432/vo618a.pdf

PCB-P0.2 is suitable for independent constrained-placement and routing-plan review. It is not suitable for fabrication, assembly or energization.
