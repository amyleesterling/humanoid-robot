# HR-V0 watchdog PCBA assembly-data review package P0.1

Status: **PRELIMINARY - NOT APPROVED FOR FABRICATION OR ENERGIZATION**

Identifier: `HR-V0-WD-PCBA-DATA-P0.1`

Round: R133

Board binding: `PCB-P0.7`

## Purpose

R133 closes a documentation gap identified after the R132 capability inquiry. The current native board had exact footprints and placements but no controlled board-only assembly BOM, coordinate convention, per-reference orientation register or inspectable assembly map.

The package now supplies:

- 42 populated references reconciled to the current R132 placement/process register;
- sixteen exact-manufacturer-part-number BOM lines totaling 42 parts;
- 38 SMD and four proposed post-reflow THT placements, all on the top side;
- four separate 3.20 mm NPTH mechanical features with no hardware selection;
- board-relative X/Y coordinates derived from the `160.000 x 100.000 mm` Edge.Cuts rectangle;
- native KiCad rotation copied without an assembler-specific transform;
- explicit orientation controls for the TI devices, ISO1, DC1, three not-keyed terminal blocks and the Pico module;
- ten assembly notes, ten file-state records and twelve open closure holds; and
- a responsive interactive placement/reference guide.

## Coordinate boundary

The internal review origin is the minimum-X/minimum-Y Edge.Cuts corner. `+X` runs right and `+Y` runs down when viewing the board from the top. Coordinates are millimetres. Native KiCad rotation is copied verbatim.

This is not machine-ready XYRS. The selected assembler must state its origin, axes, rotation zero and direction, side-mirroring rule, centroid rule and feeder convention. It must return its transformed placement file for written disposition before machine import.

## BOM boundary

Every populated reference maps to one explicit manufacturer and part number. No distributor, provider, lot, date code, attrition quantity or authorized sourcing route is released. No alternate is permitted without written Project Button disposition.

The four mounting holes are not BOM components. Screw, washer, standoff, panel drilling, torque, locking, insulation and load proof remain open under R131 and R132.

## Manufacturing boundary

R133 does not create:

- Gerber or drill files;
- IPC-356 or another released fabrication netlist;
- assembler-normalized XYRS;
- a selected laminate, stackup, copper weight, finish, solder mask, legend or panelization;
- a released stencil, solder, flux, reflow, THT, cleaning, inspection or rework process;
- a supplier packet, quotation, purchase order or work authorization; or
- a physical article, inspection result, connection or energization permission.

R132 supplier capability/DFM responses, independent review and qualified electrical/insulation/mechanical disposition remain required before a later immutable manufacturing-data release can be considered.

## Controlled artifacts

- `electrical/manufacturing/hr-v0-watchdog-pcba-assembly-data-p0.1/board-assembly-bom.csv`
- `electrical/manufacturing/hr-v0-watchdog-pcba-assembly-data-p0.1/assembly-placement-reference.csv`
- `electrical/manufacturing/hr-v0-watchdog-pcba-assembly-data-p0.1/mechanical-feature-register.csv`
- `electrical/manufacturing/hr-v0-watchdog-pcba-assembly-data-p0.1/coordinate-orientation-control.csv`
- `electrical/manufacturing/hr-v0-watchdog-pcba-assembly-data-p0.1/assembly-note-register.csv`
- `electrical/manufacturing/hr-v0-watchdog-pcba-assembly-data-p0.1/assembly-data-file-state.csv`
- `electrical/manufacturing/hr-v0-watchdog-pcba-assembly-data-p0.1/assembly-data-holds.csv`
- `electrical/manufacturing/hr-v0-watchdog-pcba-assembly-data-p0.1/assembly-top-reference.svg`
- `electrical/manufacturing/hr-v0-watchdog-pcba-assembly-data-p0.1/source-register.csv`
- `electrical/manufacturing/hr-v0-watchdog-pcba-assembly-data-p0.1/package-status.json`
- `release/hr-v0/watchdog-pcba-assembly-data-p0.1/index.html`

Run the generator with KiCad 10 Python and the checker with the controlled project Python. A passing checker proves synchronization and fail-closed state only.

**PRELIMINARY - NOT APPROVED FOR FABRICATION OR ENERGIZATION**
