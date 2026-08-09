# HR-V0 watchdog PCBA capability inquiry P0.1

Status: **PRELIMINARY - NOT APPROVED FOR FABRICATION OR ENERGIZATION**

Identifier: `HR-V0-WD-PCBA-RFI-P0.1`

Date: 2026-08-09

Review round: R132

## Decision

Current PCB-P0.7 is the only board considered by this inquiry. R132 retains all R89 manufacturer-traced component lands and makes one exact current-source correction: TP1-TP16 change from rounded rectangles to Harwin's dimensioned rectangular 3.45 x 1.85 mm copper land without changing size, centroid, placement or net. It binds all 46 current footprints and extracts the actual process split: 38 SMD placements, four post-reflow THT placements and four board-only NPTH holes.

The earlier passive/IC audit findings against PCB-P0.5 are not current-board defects. R89 corrected those source lands, R131 reconciled the historical ISO1 defect, and R132 closes the remaining exact Harwin copper-shape mismatch. The remaining fabrication blocker is configuration-specific acceptance of the complete bare-board, mask, stencil, solder, mixed-process, cleanliness, inspection, traceability, test and first-article system.

## Capability routes

Four official provider routes were screened. None is selected or contacted:

- [MacroFab capabilities](https://www.macrofab.com/capabilities): public North American SMD/THT/hybrid/module, solder/flux, IPC-A-610 Class 2/3, J-STD-001 and consignment capability gives the most explicit published process screen.
- [NEOTech Westborough](https://www.neotech.com/about-neo-tech/locations/westborough-massachusetts/): local quick-turn/NPI, low-to-medium-volume high-mix PCBA capability approximately 30 minutes from Boston.
- [Screaming Circuits services overview](https://www.screamingcircuits.com/assets/pdfs/SC-ServicesOverview.pdf): minimum-one prototype, turnkey/partial/customer-supplied route and explicit requirement to discuss work outside standard capability.
- [Cirtronics New Hampshire](https://www.cirtronics.com/pcb-assembly-manufacturer-new-hampshire/): regional robotics/industrial, DFM, inspection and testing capability.

These are capability claims only. The exact factory, process, standard, inspection, documentation, price and schedule require written application responses.

## Controlled inquiry content

The machine-readable package at `electrical/manufacturing/hr-v0-watchdog-pcba-rfi-p0.1/` contains:

- every source placement, exact part, footprint, process class, side, board-relative coordinate, rotation, pad count and local mask/paste setting;
- a nine-group current-geometry reconciliation covering all 21 retained R89 corrections plus sixteen R132 rectangular Harwin lands, with every process-dependent decision still explicit;
- twenty mandatory assembly requirements, including no silent substitutions;
- twenty-four blank capability questions marked `NOT SENT`;
- a ten-item file-release register showing that current CAM does not exist and all supplier artifacts remain withheld;
- fourteen closure holds: eleven `OPEN`, three `PARTIAL`;
- twenty-four blank first-article/receiving records marked `NOT EXECUTED - NO ARTICLE`;
- four unselected provider routes and sixteen dated source records; and
- a package-status record with every contact, upload, quote, CAM, fabrication, assembly, physical-article and energization flag false.

## Release sequence

1. Independent PCB/assembly review must challenge the current source, extracted register and manufacturer evidence.
2. The program owner must separately authorize sending only the bounded capability questions.
3. Candidate providers must return reference-level DFM redlines and exact process/quality answers without starting work.
4. Qualified electrical, insulation and mechanical reviewers must accept the selected response and close the relevant holds.
5. Only then may a separately identified, hash-bound PCB-P0.7-or-later fabrication/assembly data candidate be generated for independent CAM review.
6. Upload, quotation, purchase, fabrication and assembly each require a separate written authorization against one immutable configuration.
7. A held first article must pass receiving, bare-board, assembly and unpowered electrical evidence before any later powered-work decision.

Passing `tools/check_hr_v0_watchdog_pcba_inquiry.py` proves only internal configuration consistency. No provider has answered the questions. No current CAM exists. No fabrication, assembly, connection, test, motion or energization is authorized.
