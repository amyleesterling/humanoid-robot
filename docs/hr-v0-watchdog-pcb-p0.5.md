# HR-V0 watchdog PCB fabrication-envelope candidate P0.5

> **PRELIMINARY - NOT APPROVED FOR FABRICATION OR ENERGIZATION**

Electrical compatibility: `Project Button Electrical V3-P1.13`

PCB identifier: `PCB-P0.5`

Date: 2026-08-08

## Decision

R35 removes PCB-P0.4's dependence on 0.10 mm fine routing and records a proposed, source-backed U.S. two-layer prototype process. It does not authorize an order, fabrication, assembly or energization.

PCB-P0.5 encodes a minimum routed trace width and net-class clearance of **0.1524 mm (6 mil)**. The narrow ISO1212 and driver fan-outs were rerouted at that width. The smallest encoded via drill is 0.30 mm and the smallest encoded via annular ring is 0.15 mm. These exceed the published minimums for the proposed OSH Park Two Layer Prototype Service:

- two copper layers and 1 oz copper;
- 1.6 mm nominal finished board thickness;
- 175 Tg FR-4, ENIG finish and solder mask over bare copper;
- 0.1524 mm minimum trace width and spacing;
- 0.254 mm minimum drill;
- 0.127 mm minimum annular ring; and
- 406.4 mm x 558.8 mm maximum board size, compared with this board's 160 mm x 100 mm outline.

The service is a **proposed fabrication envelope**, not a released supplier or purchase. The supplier must still accept the final controlled archive, and an independent reviewer must check the complete stack-up, solder-mask behavior, footprint lands, drill table, board-edge clearance and manufacturing notes before fabrication outputs can be authorized.

## Controlled evidence

- Native PCB: `electrical/kicad/project-button-v3/project-button-v3.kicad_pcb`
- Generator: `tools/generate_hr_v0_watchdog_pcb.py`
- Independent checker: `tools/check_hr_v0_watchdog_pcb.py`
- Complete DRC: `electrical/kicad/project-button-v3/validation/project-button-v3-pcb-test-access-drc.rpt`
- Machine evidence: `electrical/kicad/project-button-v3/validation/project-button-v3-pcb-test-access-evidence.json`
- CLI record: `electrical/kicad/project-button-v3/validation/project-button-v3-pcb-test-access-cli.log`
- Review renders: `electrical/kicad/project-button-v3/output/project-button-v3-pcb-test-access-top.png` and `project-button-v3-pcb-test-access-bottom.png`

The generated board has 42 schematic references, four board-only M3 holes, 201 copper segments, 56 vias and three filled B.Cu zones. Native KiCad 10.0.5 DRC reports zero violations, zero routed unconnected pads and zero footprint errors. The checker proves the 6 mil minimum trace width, 0.30 mm minimum via drill, 0.15 mm minimum via annular ring, all multi-pad modeled nets connected, 14 unused singleton pads isolated, both SUB thermal nets limited to their own pad/trace/via/plane copper, all 89 no-net pads untouched, all 16 test points assigned to the intended net, and no Gerber or drill outputs present.

These are source and geometry checks, not fabricator acceptance or physical validation.

## Fabrication gate remains open

R88 generated a deterministic CAM **review candidate** at
`release/hr-v0/watchdog-pcb-fabrication-candidate-p0.1/`. The candidate has
Gerber, PTH/NPTH drill, placement, IPC-D-356, statistics, fresh DRC, BOM,
source and checksum records. It is not a fabrication release and cannot be
uploaded, ordered, assembled or energized.

PCB-P0.5 still needs all of the following before a fabrication order may be authorized:

1. independent schematic-to-PCB parity and layout review;
2. official-land-pattern, paste, mask and orientation review for every footprint;
3. written or portal-recorded acceptance of the final controlled design by the selected fabricator;
4. prospective-fault-current, source-foldback, fuse, conductor, connector and trace coordination;
5. physical test-point access and programming-tool compatibility review;
6. thermal, COM-slew, brownout, EMC/surge and fault-injection evidence;
7. enclosure, mounting, harness, strain relief and service-access definition;
8. independent review of the controlled fabrication-output candidate and supplier portal preview; and
9. qualified electrical and functional-safety review.

No physical board, received-part, AOI, continuity, current-limited bring-up, waveform, thermal, EMC, fault-injection or HIL evidence exists yet. CAM files exist only inside the explicitly non-released review candidate; no Gerber, drill or placement manufacturing release exists.

## Primary documentation

- OSH Park, *2 Layer Prototype Service*, web page with no revision stated, accessed 2026-08-06: https://docs.oshpark.com/services/two-layer/
- Texas Instruments, *ISO121x Isolated 24-V to 60-V Digital Input Receivers*, `SLLSEY7G`, revised February 2025, accessed 2026-08-06: https://www.ti.com/lit/ds/symlink/iso1212.pdf
- Harwin, *S1751-XXR Technical Drawing*, drawing `DRG 02202`, issue 10 dated 2023-02-15, accessed 2026-08-06: https://content.harwin.com/asset/e4e6a5e1-de35-4a2b-8b49-ff06562cba9d/DRG-02202-Technical-Drawing-Datasheet-S1751R-pdf.pdf

PCB-P0.5 is suitable for independent schematic/layout and fabrication-envelope review only. It is not suitable for fabrication, assembly or energization.
