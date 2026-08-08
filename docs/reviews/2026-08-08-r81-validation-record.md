# R81 validation record — 24 V factory-cord and load-budget correction

Status: **PRELIMINARY—NOT APPROVED FOR FABRICATION OR ENERGIZATION**

Date: 2026-08-08

## Controlled change

- Electrical V3-P1.11 replaces the unsupported Mean Well P1J conversion chain with exact GlobTek `WR9QI1660YL4NKITR6B` and its factory `YL4/C40337` cord.
- The manufacturer assignment is preserved without inference: cord pin 1 is `+V`, pin 3 is `-V`/shield, and pins 2/4 are N/C.
- `J24` remains the exact Kycon `KPJX-PM-4S` panel-jack candidate. The received factory plug is described as Kycon or equal, so received identity, fit, retention, jack-view reconciliation and continuity remain mandatory.
- The source is Class II/double-insulated with floating output. No project 0 V/PE bond is inferred or released.
- `HR-V0-24V-IF-P0.2` adds a five-load steady-state screen: 27.024 W / 1.126 A. This leaves 12.976 W nominal headroom through 40 °C and 4.976 W at the manufacturer's 80% load limit at 50 °C.
- The screen uses exact K1/K2 and safety-relay coil records where available, typical-only watchdog-relay coil data, a family-only H1 screen, and a conservative 10 W project reserve for the watchdog PCB/regulator. It is not a measured load budget.

## Validation result

- KiCad 10.0.5 parsed and regenerated all thirteen V3 pages.
- Native ERC: **0 errors / 0 warnings**.
- Current V3 counts: 77 component blocks; 298 modeled terminals; 103 native nets, comprising 64 named connected nets and 39 deliberate unconnected nets; 259 unique wire labels; 75 nonzero-quantity BOM rows; 65 unresolved rows; 14 deliberate `TBD-*` terminals.
- `HR-V0-24V-IF-P0.2`: five BOM rows, ten pin rows, eight holds, ten source records and five load rows.
- `HR-V0-E2-HW-P0.2`: 23 configuration rows, six XT1 rows, three source-domain rows and twelve holds.
- Repository validation: all 32 controlled checkers passed using the general, CadQuery and KiCad runtimes as applicable.
- Release manifest: 896 package files. Clean-clone reproduction and remote-branch verification are required after the R81 commit is created and pushed.
- The generated interactive guides retain 16 px body text, 14 px secondary text, responsive flow/table scrolling and the preliminary warning. Direct local-file browser rendering was not executed because the in-app browser rejected `file:` navigation; no visual-browser result is claimed for R81.

## Open evidence

Received plug identity and mating fit; exact H1 current; actual watchdog-board consumption; startup and simultaneous pickup; brownout; source foldback/recovery; F24 selection and coordination; conductor/termination sizing; connector temperature rise; enclosure temperature; abnormal and single-fault behavior; physical continuity/polarity; and qualified electrical and functional-safety review all remain open.

Clean ERC and passing checkers establish modeled consistency only. They do not establish physical suitability, functional-safety performance, fabrication readiness or permission to energize.
