# HR-V0 watchdog PCB test-access candidate P0.4

> **PRELIMINARY - NOT APPROVED FOR FABRICATION OR ENERGIZATION**

Electrical dependency: `Project Button Electrical V3-P1.1`

PCB identifier: `PCB-P0.4`

Date: 2026-08-06

## Decision

R34 advances PCB-P0.3 only far enough to encode probe access and the ISO1212 exposed-pad treatment that were explicitly open in R33. It does not release fabrication, assembly or energization.

Electrical V3-P1.1 adds a thirteenth native schematic page and sixteen `TP1`-`TP16` test-point components. PCB-P0.4 uses the proposed Harwin `S1751-46R` top-side SMT test point and its manufacturer-recommended 3.45 mm x 1.85 mm land pattern for:

- `SAFETY_24V`, `SAFETY_0V`, `WD_5V` and `WD_3V3`;
- `PI_HEARTBEAT` and `WD_HEARTBEAT`;
- both driver commands, coil returns and NC feedback inputs;
- both ISO1212 logic outputs; and
- `WD_SWDIO` and `WD_SWCLK`.

The board also gives `UFB1.SUB1` and `UFB1.SUB2` separate, electrically floating 2 mm x 2 mm B.Cu areas. Neither SUB net connects to the other SUB net, `SAFETY_0V`, field ground, logic ground or any signal net. This follows the thermal-layout recommendation in TI `SLLSEY7G`; it does not create isolation or safety credit.

## Controlled evidence

- Native PCB: `electrical/kicad/project-button-v3/project-button-v3.kicad_pcb`
- Generator: `tools/generate_hr_v0_watchdog_pcb.py`
- Independent checker: `tools/check_hr_v0_watchdog_pcb.py`
- Complete DRC: `electrical/kicad/project-button-v3/validation/project-button-v3-pcb-test-access-drc.rpt`
- Machine evidence: `electrical/kicad/project-button-v3/validation/project-button-v3-pcb-test-access-evidence.json`
- CLI record: `electrical/kicad/project-button-v3/validation/project-button-v3-pcb-test-access-cli.log`
- Review renders: `electrical/kicad/project-button-v3/output/project-button-v3-pcb-test-access-top.png` and `project-button-v3-pcb-test-access-bottom.png`

The generated board has 42 schematic references, four board-only M3 holes, 200 copper segments, 56 vias and three filled B.Cu zones. Native KiCad 10.0.5 DRC reports zero violations, zero routed unconnected pads and zero footprint errors. The checker proves all multi-pad modeled nets connected, 14 unused singleton pads isolated, both SUB thermal nets limited to their own pad/trace/via/plane copper, all 89 no-net pads untouched, all 16 test points assigned to the intended net, and no Gerber or drill outputs present.

These are ECAD consistency results, not physical validation. The exact test-point order code and land pattern are proposed and frozen for review, but received identity, solderability, probe clearance, clip retention, access with the enclosure installed and safe probing procedure remain open.

## Fabrication gate remains open

PCB-P0.4 still needs all of the following before fabrication outputs may be generated:

1. independent schematic-to-PCB parity and layout review;
2. official-land-pattern and orientation review for every footprint;
3. exact fabricator, stack-up, copper thickness, mask rules and confirmed 0.10 mm capability;
4. prospective-fault-current, source-foldback, fuse, conductor, connector and trace coordination;
5. physical test-point access and programming-tool compatibility review;
6. thermal, COM-slew, brownout, EMC/surge and fault-injection evidence;
7. enclosure, mounting, harness, strain relief and service-access definition;
8. a controlled fabrication-output review; and
9. qualified electrical and functional-safety review.

No physical board, received-part, AOI, continuity, current-limited bring-up, waveform, thermal, EMC, fault-injection or HIL evidence exists yet.

## Primary manufacturer documentation

- Texas Instruments, *ISO121x Isolated 24-V to 60-V Digital Input Receivers*, `SLLSEY7G`, revised February 2025, accessed 2026-08-06: https://www.ti.com/lit/ds/symlink/iso1212.pdf
- Harwin, `S1751-46R` product page, accessed 2026-08-06: https://www.harwin.com/products/S1751-46R
- Harwin, *S1751-XXR Technical Drawing*, drawing `DRG 02202`, issue 10 dated 2023-02-15, accessed 2026-08-06: https://content.harwin.com/asset/e4e6a5e1-de35-4a2b-8b49-ff06562cba9d/DRG-02202-Technical-Drawing-Datasheet-S1751R-pdf.pdf

PCB-P0.4 is suitable for independent schematic/layout and test-access review only. It is not suitable for fabrication, assembly or energization.
