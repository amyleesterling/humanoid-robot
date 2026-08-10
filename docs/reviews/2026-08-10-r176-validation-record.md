# R176 validation record

> **PRELIMINARY — BENCH R&D EQUIPMENT ONLY — NOT APPROVED FOR PROCUREMENT, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION.**

R176 issues `HR-V0-DYN-EVENT-IF-P0.1`, an exact but nonselected isolated dynamic-event evaluation candidate.

## Package checks

- two Texas Instruments `ISO1212EVM` evaluation units;
- seven held field-event taps plus one FIO0 trigger/witness bit;
- exact EVM J4 pins 9/8/7/6 and J2 pins 2/4/6/8;
- exact T7 DB37 FIO0–FIO7 pin mapping;
- one proposed `FIO_STATE` common-clock word;
- seven primary TI/LabJack source records;
- fifteen open selection/noninterference holds;
- four blank receiving rows; and
- zero procurement, connection, powered-run, physical-result, release or safety-function authority.

The controlled TI `SLLU254A` PDF is 648,488 bytes with SHA-256 `8F7F03908AFF49C2BA7C6BEC378D121A1EDD75AE52E5FEE0F4490F256BB60BC5`.

## Native KiCad validation

KiCad 10.0.5 parsed the root plus four child sheets. Native ERC reports **0 errors / 0 warnings**. Netlist, PDF and four child SVG exports completed. Visual inspection rejected the first crowded one-child layout; the accepted source separates EVM A field, EVM B field, EVM logic and DAQ/trigger boundaries. The final exports show no clipped connector labels, crossed blocks or unreadable warning text.

ERC validates only the encoded topology. It does not validate ISO1212 application, shared field ground, diagnostic-pulse noninterference, EDM behavior, coil dropout, propagation delay, grounding, harnesses or permission to connect.

## Browser validation

The interactive guide was checked in the in-app browser at a native 1280 px viewport and inside a same-origin 390 × 844 px mobile viewport harness.

- body text is 16 px;
- the smallest rendered text is 13.333 px;
- desktop document width is 1265/1265 px with no page overflow;
- mobile document width is 375/375 px with no page overflow;
- the mobile flow reflows to one 284 px column;
- the 980 px technical table owns a 335 px horizontal scroller at mobile width;
- warning, signal-path cards and links remain readable; and
- the guide, engineering record and native SVG links each return HTTP 200.

The desktop page produced no console entries. The iframe-based mobile harness produced one Browser-plugin `MutationObserver` error while instrumenting the iframe; the delivered static page contains no script and the measured iframe DOM/layout loaded correctly. This tool-level error is not treated as application evidence.

## Repository validation

- non-pcbnew checker sweep: **120/120 passed**, comprising 119 domain/configuration checks plus the staged deterministic release-manifest check;
- native KiCad/pcbnew checker sweep: **13/13 passed**;
- controlled total: **133/133 checks passed**; and
- final manifest is regenerated after this record and rechecked before commit.

Automated success proves source consistency, candidate identity, encoded pin/net parity and fail-closed authorization state only. No hardware is received, no field tap is authorized, no propagation/uncertainty result exists, no stopping/reset trace is executed and no qualified reviewer has accepted noninterference. `EG-025` remains open and `EG-026` partial.
