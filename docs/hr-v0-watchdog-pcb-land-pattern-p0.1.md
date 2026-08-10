# HR-V0 Watchdog PCB Land-Pattern and Assembly-Process Correction P0.1

Status: **PRELIMINARY - NOT APPROVED FOR FABRICATION OR ENERGIZATION**
Board: `PCB-P0.6`
Compatible electrical source: `Project Button Electrical V3-P1.13`
Package identifier: `HR-V0-WD-LAND-P0.1`
Date: 2026-08-08

## Outcome

R89 audited every one of the 42 schematic references and four board-only mounting holes against current primary manufacturer records. The audit found one blocking isolation-land error, two undocumented TI alternate IC lands and seventeen support-passive lands that did not match the cited manufacturers' published patterns.

`PCB-P0.6` corrects the following source geometry:

- `ISO1` now encodes Vishay VO618A option-7 lands at `1.52 x 1.78 mm`, `2.54 mm` pin pitch, at least `8.0 mm` inner copper gap and `11.05 mm` overall copper span.
- `UDRV1` and `UDRV2` now encode TI `PW0016A` example lands at `1.50 x 0.45 mm`, `0.65 mm` pitch and `5.80 mm` row-centre spacing.
- `UFB1` now encodes TI `DBQ0016A` example lands at `1.60 x 0.41 mm`, `0.635 mm` pitch and `5.40 mm` row-centre spacing.
- `CDEC1`, `CDRV1` and `CDRV2` now use a controlled nominal reflow land inside Murata's GRM21 guidance.
- `CFI1` and `CFI2` now use a controlled nominal reflow land inside TDK's CGA3 guidance.
- `RHB1`, `RHP1`, `RSN1`, `RSN2`, `RSO1`, `RSO2`, `RPD1` and `RPD2` now use a controlled nominal reflow land inside Panasonic's ERJ6 guidance.
- `RTH1` and `RTH2` now use Vishay's published MMA0204 IPC reflow pattern instead of the prior wave-only match.
- `RW1` and `RW2` now use Vishay's published CRCW1210 reflow pattern.

The native board regenerated with 42 schematic references, four board-only M3 holes, 201 routed segments, 56 vias, three filled zones, 40 modeled nets and zero KiCad DRC violations or routed-unconnected pads. These results prove only the encoded source and rules; they are not physical solderability, isolation, EMC, thermal or safety evidence.

## Proposed assembly sequence

The candidate process is now explicitly mixed:

1. Reflow the SMD population, including the Pico module, ICs, optocoupler, passives and Harwin test points.
2. Inspect the SMD first article before adding through-hole parts.
3. Manually solder `DC1`, `JWP1`, `JWF1` and `JWH1` only after their drill/land, support, torque-reaction and service-clearance evidence is accepted.
4. Clean and inspect according to an assembler-approved contamination process before any isolation-spacing claim.

This is a proposed process architecture, not an assembler release. Stencil thickness, aperture reduction, paste alloy/type, reflow profile, mask expansion/webs, hand-solder thermal limits, cleaning, AOI criteria, rework limits and first-article acceptance remain **SELECTION REQUIRED**.

## Configuration decision

The R88 directory `release/hr-v0/watchdog-pcb-fabrication-candidate-p0.1/` remains an immutable record of `PCB-P0.5`. It is **superseded for current fabrication review** because its IC/isolation/passive land geometry predates R89. It must not be uploaded, ordered, fabricated or described as current.

No CAM package is issued from `PCB-P0.6` in R89. A new candidate may be generated only after the open application/process evidence below is accepted; it must receive a new identifier and hashes rather than replacing R88 bytes.

## Remaining release blockers

1. An assembler must accept the controlled copper lands and supply the stencil, mask, paste, reflow, hand-solder, cleaning, AOI and rework process.
2. System-level ISO1 creepage/clearance must be calculated from working voltage, overvoltage category, pollution degree, material group, coating, altitude, environment and applicable Boston/US requirements. The component headline value is not a system safety claim.
3. The Phoenix terminal blocks require housing support against conductor-tightening torque, screwdriver access, wire-entry/bend clearance, strain relief and assembly-view pin numbering. The manufacturer does not document the current `2.10 mm` copper-land diameter as a recommended land.
4. `DC1` needs approved drill/land tolerances, annular-ring rationale, installed-height, lead-trim and airflow/service clearance. TRACO publishes the pins and outline but no recommended PCB land.
5. `WDCTRL1` matches Raspberry Pi's official SMD geometry, including enlarged paste apertures, but needs Pico reflow capability, solder-pool/AOI acceptance, overhang/access and received-lot control.
6. `TP1` through `TP16` match Harwin's exact land, but fixture approach, vertical clearance, collision and centroid/reel convention remain unproved.
7. `MH1` through `MH4` remain generic `3.20 mm` NPTH holes. Exact screws, washers, standoffs, enclosure stack, tolerances, torque, loads and edge-distance acceptance are unselected.
8. Manufacturer PDFs must be frozen by URL, document identifier, revision/date, retrieval date and SHA-256 in the eventual fabrication release.
9. The populated board must pass polarity, lead-wetting, fillet, bridge, void/contamination, isolation-gap and dimensional first-article inspection.
10. Independent PCB/assembly review, physical board evidence and every applicable energization gate remain open.

## Controlled evidence

- Reference-by-reference register: `release/hr-v0/watchdog-pcb-land-pattern-audit-p0.1/land-pattern-audit.csv`
- Human-readable guide: `release/hr-v0/watchdog-pcb-land-pattern-audit-p0.1/index.html`
- Native board: `electrical/kicad/project-button-v3/project-button-v3.kicad_pcb`
- Board checker: `tools/check_hr_v0_watchdog_pcb.py`
- Independent review request: `docs/reviews/2026-08-08-watchdog-pcb-land-pattern-p0.1-independent-review-request.md`

## Primary records

- TI, *TPL7407L*, `SLRS066D`, revised March 2016; embedded `PW0016A` drawing `4220204/B`, December 2023: https://www.ti.com/lit/ds/symlink/tpl7407l.pdf
- TI, *ISO121x*, `SLLSEY7G`, revised February 2025; embedded `DBQ0016A` drawing `4214846/A`, March 2014: https://www.ti.com/lit/ds/symlink/iso1212.pdf
- Vishay, *VO618A*, document `83432`, Rev. 2.1, 2025-01-22: https://www.vishay.com/docs/83432/vo618a.pdf
- Murata, `GRM21BR71H104KA01-01`, exact-part reference sheet; asset updated 2025-07-07: https://pim.murata.com/asset/pim4/ceramicCapacitorSMD/GRM21BR71H104KA01-01-EN_PDF_CERAMICCAPACITORSMD?lastModifiedDatetime=20250707233810
- TDK, automotive MLCC delivery specification `AC11010023`, June 2026: https://product.tdk.com/system/files/dam/doc/product/capacitor/ceramic/mlcc/specification/mlccspec_automotive_general_en.pdf
- Panasonic, chip-resistor land-pattern guide, dated 2025-12-24: https://industrial.panasonic.com/cdbs/www-data/pdf/RDM0000/DMM0000COL17.pdf
- Vishay, MMA0204 land-pattern document `28950`, Rev. 2022-07-12: https://www.vishay.com/doc/?28950=
- Vishay, CRCW e3 document `20035`, Rev. 2026-04-14: https://www.vishay.com/docs/20035/dcrcwe3.pdf
- Raspberry Pi, *Pico datasheet*, release 2026-07-03: https://datasheets.raspberrypi.com/pico/pico-datasheet.pdf
- Phoenix Contact, items `1751264` and `1751248`, live catalog records accessed 2026-08-08: https://www.phoenixcontact.com/us/products/1751264 and https://www.phoenixcontact.com/en-us/products/printed-circuit-board-terminal-mkds-1-2-35-1751248
- TRACO Power, *TSR 1 series*, Rev. 2024-02-07: https://www.tracopower.com/products/tsr1.pdf
- Harwin, `DRG 02202`, issue 10, 2023-02-15: https://content.harwin.com/asset/e4e6a5e1-de35-4a2b-8b49-ff06562cba9d/DRG-02202-Technical-Drawing-Datasheet-S1751R-pdf.pdf

**PRELIMINARY - NOT APPROVED FOR FABRICATION OR ENERGIZATION.**
