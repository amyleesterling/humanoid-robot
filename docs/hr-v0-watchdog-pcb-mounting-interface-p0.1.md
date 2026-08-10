# HR-V0 Watchdog PCB Current-Source Reconciliation and Mounting Interface P0.1

Status: **PRELIMINARY - NOT APPROVED FOR FABRICATION OR ENERGIZATION**

Identifier: `HR-V0-WD-MOUNT-IF-P0.1`

Date: 2026-08-09

Compatible board: `PCB-P0.6 / Electrical V3-P1.13`

## Outcome

The reported ISO1 land defect is real in the immutable historical `PCB-P0.5` CAM source, but it is not present in the current native `PCB-P0.6` source.

- Historical P0.5 used X centers `+/-4.400 mm` and `2.00 mm` copper width, producing a `6.800 mm` inner gap and `10.800 mm` overall span.
- Current P0.6 uses X centers `+/-4.765 mm` and `1.52 mm` copper width, producing an `8.010 mm` inner gap and `11.050 mm` overall span.
- The current native footprint includes the Vishay datasheet URL and records document `83432`, Rev. 2.1, dated 2025-01-22.
- KiCad 10.0.5 native DRC on the current board reports zero violations, zero unconnected pads and zero footprint errors.

No second ISO1 geometry change is warranted. The earlier P0.5 package remains superseded and prohibited from upload or fabrication. This reconciliation prevents a historical-source finding from being incorrectly applied to the current board.

DRC and arithmetic confirm only the encoded source. They do not prove solderability, cleanliness, insulation-system suitability, EMC, thermal behavior, physical mounting or safety performance.

## Mounting definition advanced

The current board is `160 x 100 x 1.6 mm` in source and has four `3.20 mm` NPTH holes:

| Reference | Board-relative center, mm | Candidate panel center, mm |
|---|---:|---:|
| MH1 | 5, 5 | 59, 235 |
| MH2 | 155, 5 | 209, 235 |
| MH3 | 5, 95 | 59, 325 |
| MH4 | 155, 95 | 209, 325 |

The panel coordinates derive from the P0.6 planning envelope at X `54..214 mm`, Y `230..330 mm`. They are not drilling instructions. Received Hammond `18P2721` geometry, flatness, coating, inserts, keepouts and enclosure fit must precede a released panel drawing.

Three exact Harwin catalog candidates are now controlled without selecting one:

- `R30-1611000`: M3 female-female, 10 mm body, 5.5 mm A/F, Polyamide 66, UL94V-2, 0.226 g.
- `R30-1611300`: M3 female-female, 13 mm body, 5.5 mm A/F, Polyamide 66, UL94V-2, 0.294 g.
- `R30-1611500`: M3 female-female, 15 mm body, 5.5 mm A/F, Polyamide 66, UL94V-2, 0.339 g; Harwin states 6 mm minimum threaded at both ends.

The board-edge arithmetic is favorable but incomplete. A 5.5 mm A/F regular hex has a nominal corner radius of `3.175426 mm`; with each hole center 5 mm from its adjacent edges, the nominal body-envelope margin is `1.824574 mm`. Screw heads, washers, tolerances and installed loads remain unresolved.

## Selection boundary

Standoff height remains **SELECTION REQUIRED** until the populated board's underside THT lead and solder-fillet envelope is measured. Top screws, panel-side fasteners, washers, locking method, thread engagement and torque also remain **SELECTION REQUIRED**. No fastener order code is inferred.

The complete stack cannot be released until all of the following are controlled:

1. received board thickness, hole diameters, center positions and warp;
2. received `18P2721` thickness, flatness, coating and enclosure fit;
3. installed DC1/JWP1/JWF1/JWH1 lead protrusion, lead-trim and solder-fillet limits;
4. exact standoff height and complete upper/lower fastener stack;
5. drill diameter, tolerances, datums, deburring and coating-repair process;
6. connector insertion, conductor-tightening, static, vibration and service-cycle loads;
7. plastic-hardware flammability and qualified insulation/bonding disposition;
8. assembler-approved mask, stencil, paste, reflow/manual-THT, cleaning, AOI and rework process;
9. physical first-article inspection and independent PCB/assembly review.

## Controlled artifacts

- `electrical/panel/hr-v0-watchdog-pcb-mounting-p0.1/current-board-reconciliation.csv`
- `electrical/panel/hr-v0-watchdog-pcb-mounting-p0.1/mount-coordinate-register.csv`
- `electrical/panel/hr-v0-watchdog-pcb-mounting-p0.1/standoff-candidate-register.csv`
- `electrical/panel/hr-v0-watchdog-pcb-mounting-p0.1/interface-screen.csv`
- `electrical/panel/hr-v0-watchdog-pcb-mounting-p0.1/closure-holds.csv`
- `electrical/panel/hr-v0-watchdog-pcb-mounting-p0.1/receiving-template.csv`
- `electrical/panel/hr-v0-watchdog-pcb-mounting-p0.1/source-register.csv`
- `release/hr-v0/watchdog-pcb-mounting-p0.1/index.html`
- `electrical/kicad/project-button-v3/validation/project-button-v3-r131-audit-drc.rpt`

## Primary manufacturer records

- Vishay, VO618A datasheet `83432`, Rev. 2.1, 2025-01-22; rechecked 2026-08-09: https://www.vishay.com/docs/83432/vo618a.pdf
- Harwin `R30-1611000`, current product record rechecked 2026-08-09: https://www.harwin.com/products/R30-1611000
- Harwin `R30-1611300`, current product record rechecked 2026-08-09: https://www.harwin.com/products/R30-1611300
- Harwin `R30-1611500`, current product record rechecked 2026-08-09: https://www.harwin.com/products/R30-1611500
- Hammond Manufacturing `18P2721`, current product record rechecked 2026-08-09: https://www.hammfg.com/part/18P2721

This package does not release a board, CAM package, panel hole, standoff, screw, washer, torque, assembly process, fabrication, wiring, connection or energization.
