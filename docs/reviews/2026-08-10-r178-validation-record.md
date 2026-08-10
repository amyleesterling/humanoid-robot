# R178 validation record

> **PRELIMINARY — NOT APPROVED FOR PROCUREMENT, FABRICATION, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION.**

R178 issues `HR-V0-EVENT-TAP-DISP-P0.1`, a fail-closed source/application disposition for the seven blank field adapters introduced by R177. It releases no adapter or connection.

## Source and terminal verification

- all seven net names were rechecked against Electrical V3-P1.15;
- all fifteen exact P1.15 endpoint rows for those nets were rechecked in `wire-number-table.csv`;
- the five Pilz-path nodes and two Schneider coil nodes are distinguished rather than treated as one generic 24 V signal type;
- Pilz `21396-EN-23`, controlled SHA-256 `4B6E4768CEFAEDAF54F006347D32A8A04964B59A16F3616D8AC43698D3626BB4`, was checked at pages 9–23 for monitored-start behavior, wiring limitations and electrical data;
- the live Pilz 750104 record was accessed on 2026-08-10;
- the current controlled Schneider source record for `SQD-LC1D25BD.PDF`, SHA-256 `333EFD8170CDFADAAFBBA19CF07518E0C379380BC4BDA85D2A9355A4DB360D63`, and the live US product record were rechecked on 2026-08-10; and
- TI `SBASA34B`, controlled SHA-256 `1AC6B81FFB52DFDBDE49C86CA31F3A0BEAA7D52BFF60547834F34EC75A58B288`, was checked for input ranges, absolute limits, impedance/capacitance and divider-design guidance.

The verification corrects one prior ambiguity: Schneider identifies a built-in bidirectional peak-limiting diode suppressor in `LC1D25BD`. The installed clamp-voltage envelope and application suitability remain unresolved. No current Pilz source checked by R178 specifies an allowable parallel observer load for the Project Button monitored paths.

## Native KiCad validation

KiCad 10.0.5 parsed the root plus three child sheets. Native ERC reports **0 errors / 0 warnings**. Netlist, PDF and three child SVG exports completed.

The first visual export exposed long-label collisions, a lowest-row/title-block collision, dangling held-tap stubs and an overlong sheet note. The generator was corrected to:

- use short internal disposition-net names while retaining exact project net names in component titles/pins;
- move the three-row layout within the usable sheet region;
- represent each observation boundary as a one-sided component with no output pin; and
- remove the redundant sheet note.

The final three child pages were rendered at 120 dpi and visually inspected. Titles, warnings, exact net/terminal labels, held dispositions and title blocks are readable and unclipped. The drawings show no AMC3330EVM input, divider, protection part or released conductor.

ERC validates only this disposition topology. It does not validate field loading, transient protection, diagnostic behavior, reset/EDM noninterference, physical routing, timing, safety integrity or permission to connect.

## Interactive-guide validation

The interactive guide was rendered in the in-app browser at the available 1280 × 720 viewport:

- document width was 1265/1265 px with no page-level overflow;
- body/functional text was 16 px and the smallest visible text was 14 px;
- all seven cards, warning and three diagram links were present;
- the native `All 7` and `Pilz paths` buttons were exercised; the latter showed exactly five nodes; and
- the page-only console contained zero warnings or errors.

The first rendered pass caught an invalid font shorthand that left the buttons at 13.3333 px. The generator now uses explicit 16 px button/link typography and the second rendered pass contained only 14 px-or-larger functional/secondary text.

A 390 × 844 viewport override was requested, but the connected browser continued reporting 1280 × 720; no rendered mobile result is claimed. Static responsive review confirms that the `max-width:520px` rule retains 16 px body/functional text, 14 px technical labels, 18 px page padding and a one-column grid. A rendered narrow-mobile regression check remains advisable before public-site integration.

## Repository validation

- non-pcbnew checker sweep under the controlled CadQuery interpreter: **122/122 passed**;
- native KiCad/pcbnew checker sweep under KiCad 10.0.5 Python: **13/13 passed**;
- total domain checks: **135/135 passed**; and
- deterministic release manifest after R178 synchronization: **3,017 files**.

The first sweep correctly rejected stale configuration, build-traveler and governance source hashes; those generated controls were refreshed before the passing sweep. Temporary PDF-render and browser-server files were removed and are absent from the controlled package.

Automated success proves source synchronization, exact node/terminal trace, fail-closed dispositions and artifact integrity only. It supplies no permissible tap load, divider/protection design, received hardware, physical connection, calibration, waveform, stopping/reset result, safety credit or work authorization. `EG-025` remains open and `EG-026` partial.
