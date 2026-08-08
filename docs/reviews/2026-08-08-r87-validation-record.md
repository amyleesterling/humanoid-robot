# R87 validation record

**PRELIMINARY - NOT APPROVED FOR FABRICATION OR ENERGIZATION**

Round: R87
Configuration: Electrical V3-P1.13 / PCB-P0.5 / HR-V0-CP-P0.5 / HR-V0-WD-SUPPLY-P0.1
Change: remove KWD contacts from SR1 E-stop returns and place them in a series gate on `SR1:A1`.

## Current results

- native Electrical V3 generation and KiCad CLI export/ERC: pass, 13 pages;
- exact electrical-source checker: pass, 64 connected named nets, 39 deliberate unconnected nets, 257 wire labels, 64 unresolved selections/interfaces;
- watchdog PCB checker: pass, 42 references, 201 segments, 56 vias, three zones, native DRC 0 violations, no fabrication outputs;
- control-panel P0.5 checker: pass, 26 BOM rows, 20 backplate allocations, 66 synchronized endpoints and 12 unreleased route controls;
- watchdog supply-gate checker: pass, 14 paths, 32 open FMEA cases and 28 unexecuted fault cases;
- safety-allocation checker: pass with DF-01 at zero safety credit and PLr/category still `SELECTION REQUIRED`.
- complete non-manifest repository sweep: 37/37 pass, including traceability at 81 requirements, 40 risks and 106 controlled procedures;
- energization register through E2: 30 applicable gates, 0 closed, 22 partial and 8 open;
- rendered A3 review of the external-source, direct E-stop/RESET and watchdog-gated supply sheets: borders and warnings visible, terminals/nets readable, no wire/text collision or content clipping observed;
- interactive-guide structural/readability check: responsive layout, filtering script, table overflow, exact warnings and 16 px minimum table/body text pass. Local-file browser navigation was unavailable, so the HTML did not receive a live-browser interaction claim; the SVG and KiCad PDF views received direct rendered inspection.

The deterministic manifest, clean-clone reproduction, commit binding and remote-head comparison will be recorded before this round is published. No physical inspection, measurement, switching, fault injection, HIL, qualified review, fabrication, wiring, energization or motion occurred.

## Engineering disposition

The old source-encoded KWD-to-E-stop-return injection path is absent from P1.13. This is not a claim that physical noninterference is proved. Contact application/endurance, branch protection, routing, internal faults, brownout/recovery, manual reset, fresh-trajectory behavior, total stopping time and qualified functional-safety validation remain open.

**PRELIMINARY - NOT APPROVED FOR FABRICATION OR ENERGIZATION**
