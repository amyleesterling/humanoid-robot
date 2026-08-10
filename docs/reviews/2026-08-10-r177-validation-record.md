# R177 validation record

> **PRELIMINARY — BENCH R&D EQUIPMENT ONLY — NOT APPROVED FOR PROCUREMENT, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION.**

R177 issues `HR-V0-DYN-EVENT-AIN-P0.1`, a preferred but nonselected low-loading isolated event-acquisition evaluation branch. R176 remains controlled historical evidence and is explicitly not preferred for field connection.

## Primary-source and package checks

- seven Texas Instruments `AMC3330EVM` evaluation candidates;
- seven held field divider/protection adapters with no parts or values released;
- exact EVM J2.1/J2.2/J2.3, J3.1/J3.2/J3.3 and J1.1/J1.2 mappings;
- exact LabJack T7 AIN0-AIN13 adjacent differential pairs and DB37 pins;
- one eight-address sequential scan model: seven AIN results plus `FIO_STATE`;
- seven current primary TI/LabJack source records;
- fifteen open selection, noninterference, timing and review holds;
- four blank receiving rows; and
- zero procurement, connection, powered-run, physical-result, release or safety-function authority.

The controlled TI `SBASA34B` PDF is 1,580,557 bytes with SHA-256 `1AC6B81FFB52DFDBDE49C86CA31F3A0BEAA7D52BFF60547834F34EC75A58B288`. The controlled TI `SBAU330C` PDF is 683,693 bytes with SHA-256 `75F5FC38B39B2C60C2D5D363812AFEBFA66EE78C523358F63221A48DAF8552D1`.

TI verifies a ±1 V linear differential input, 0.1 Gohm minimum input resistance, gain 2, 1.39 V to 1.49 V output common mode and a 300 kHz minimum output bandwidth. TI also says the EVM is not certified for high-voltage operation. These facts support only the evaluation-route decision; they do not define a 24 V-class field adapter.

## Native KiCad validation

KiCad 10.0.5 parsed the root plus five child sheets. Native ERC reports **0 errors / 0 warnings**. Netlist, PDF and five child SVG exports completed.

Visual review rejected the first four-channel field layout because it overlapped notes and the title block. The revised source splits field channels across three sheets. A second visual pass caught an incorrect `AIN0-5` capture-block label for EVM5-EVM7; the source now correctly encodes `AIN8-9`, `AIN10-11` and `AIN12-13`, and the checker asserts those labels. The final five sheets have separated blocks, readable warnings and no note/title collisions.

ERC validates encoded connectivity only. It does not validate a divider, protection, EVM high-voltage use, field loading, Pilz diagnostic behavior, monitored reset/start, EDM, coil dropout, common-mode behavior, grounding, harnesses, timing or permission to connect.

## Browser validation

The interactive guide was checked in the in-app browser at 1280 × 720 px and 390 × 844 px.

- body text is 16 px and the smallest rendered text is 14 px;
- desktop document width is 1265/1265 px with no page overflow;
- mobile document width is 375/375 px with no page overflow;
- the mobile signal flow reflows to one 299 px column;
- the 920 px technical table owns a 335 px horizontal scroller at mobile width;
- the initial mobile flow had a 14 px transformed-arrow vertical overflow and nested scrollbar; the generator was corrected to make the flow overflow visible;
- warning, signal-path cards, table and links remain readable; and
- a fresh page-only browser tab produced zero console warnings or errors.

Browser instrumentation emitted errors while repeatedly navigating raw SVG exports in an earlier shared tab. The delivered guide contains no script; the isolated page-only console was empty. Those tool errors are not application evidence.

## Repository validation

- non-pcbnew checker sweep: **120/120 passed** (106 standard-runtime checks plus 14 CadQuery geometry checks);
- native KiCad/pcbnew checker sweep: **13/13 passed**;
- staged deterministic release-manifest check passes for **2,986 files**; and
- controlled total after the manifest check is **134/134**.

Automated success proves source consistency, candidate identity, encoded pin/net parity and fail-closed authorization state only. No field adapter is selected, no hardware is received, no tap is authorized, no propagation/uncertainty result exists, no stopping/reset trace is executed and no qualified reviewer has accepted the application. `EG-025` remains open and `EG-026` partial.
