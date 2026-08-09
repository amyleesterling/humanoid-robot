# HR-V0 watchdog critical-IC native metadata P0.1

> **PRELIMINARY - NOT APPROVED FOR FABRICATION OR ENERGIZATION.**

Identifier: `HR-V0-WD-IC-META-P0.1`

Board candidate: `PCB-P0.8 / Electrical V3-P1.14`

Date: 2026-08-09

## Correction

PCB-P0.8 adds hidden native KiCad fields to `UDRV1`, `UDRV2`, `UFB1`, and `ISO1`. Each footprint now carries manufacturer, exact manufacturer part number, package code, primary document, document revision/date, package drawing, land basis, assembly-process state, and preliminary fabrication state.

The controlled values identify:

- `UDRV1` and `UDRV2`: Texas Instruments `TPL7407LPWR`, `PW / TSSOP-16`;
- `UFB1`: Texas Instruments `ISO1212DBQ`, `DBQ / SSOP-16`;
- `ISO1`: Vishay `VO618A-4X017T`, `SMD-4 option 7`.

The TI example-board land dimensions and Vishay option-7 dimensioned land basis are recorded in the native fields and evidence register. UFB1's `R0.05` rounded pad corner remains explicitly project-controlled because the TI drawing does not dimension that radius.

## Geometry and topology result

A field-independent snapshot was taken from PCB-P0.7 before regeneration. It covers footprint library identity, placement, orientation, every pad's position/size/drill/shape/layers/net, all tracks and vias, Edge.Cuts, and zone outlines/nets/layers. The regenerated PCB-P0.8 snapshot has the same SHA-256 digest: `dc1f86c067e9617aed7e82b177bc7e1b0fb61b25cc3ab878e6c4440889c4c5ea`.

Therefore R138 changes native identity/evidence fields and the title-block configuration revision only. It changes no pad, placement, net, routed copper, via, board outline, or zone geometry/topology. Native KiCad DRC remains zero violations, zero unconnected pads, and zero footprint errors.

## Explicitly unresolved

`AssemblyProcess` remains `SELECTION REQUIRED` for all four references. No solder alloy, paste, stencil thickness/aperture, mask treatment, reflow profile, THT sequence, cleaning, cleanliness limit, inspection class, acceptance criterion, assembler, CAM set, fabrication stackup, or physical article is selected or released. R132 and R133 remain historical P0.7 inquiry/assembly-data records; their source hashes are not silently rebound to PCB-P0.8.

Evidence:

- `electrical/manufacturing/hr-v0-watchdog-footprint-metadata-p0.1/footprint-metadata-register.csv`
- `electrical/manufacturing/hr-v0-watchdog-footprint-metadata-p0.1/geometry-topology-parity.json`
- `electrical/manufacturing/hr-v0-watchdog-footprint-metadata-p0.1/source-register.csv`
- `release/hr-v0/watchdog-footprint-metadata-p0.1/index.html`

This package closes a source-definition ambiguity only. It grants no functional-safety credit and no permission to quote, upload, fabricate, assemble, connect, test, or energize.
