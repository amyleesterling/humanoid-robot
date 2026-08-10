# R202 validation record

**PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION**

## Native source

- KiCad 10.0.5 parsed the root plus all four child sheets.
- Netlist/export generation succeeded; schematic ERC is 0 errors / 0 warnings.
- The 120 x 90 mm four-layer board contains 29 mounted component footprints plus four board-only M3 holes, 143 routed segments, 56 vias and three internal zones.
- Native PCB DRC is 0 violations, 0 unconnected pads and 0 footprint errors.
- `tools/check_hr_v0_runtime_observation_carrier_p02.py` independently checked schematic/PCB pad-net parity, board membership and datums, exact six-position Phoenix pitch/drill identity, saved plane fills, field/compute corridor, source/hold counts, absence of production outputs and web legibility minima.
- The package contains no Gerber, drill, supplier placement, supplier archive or reviewed PDF output. The browser guide uses SVG and responsive HTML.
- Browser QA at 1280 x 720 and 390 x 844 confirmed a 16 px minimum rendered text size, no page-level horizontal overflow, contained horizontal scrolling for the 900 px technical figure/tables, visible warning text and a loaded board SVG. The first visual pass exposed KiCad's low-contrast pale silkscreen color; the generator now replaces browser-export colors with dark blue copper/outline and deep gold legend while leaving native KiCad copper unchanged.

## Regression

- The first standard-runtime sweep passed 141/144 checks and exposed exactly the expected two stale release-candidate hashes plus the unstaged deterministic manifest. Configuration reconciliation and the build traveler were regenerated; no failure was suppressed.
- After staging the deliberate R202 package, the next sweep passed every non-manifest checker; only deterministic manifest regeneration remained.
- Supervisor tests: 67/67 passed. Watchdog tests: 11/11 passed. Total firmware source tests: 78/78.
- Host tests: 16/16 passed. The host preflight remains deliberately non-ready with 45 explicit holds and motion authority `NONE`.
- Native KiCad `pcbnew` checker sweep under KiCad 10.0.5 Python: 14/14 passed, including R202.
- The energization-gate checker returned documented non-ready exit 2: 0/21 gates closed and 21/21 partial through E2.
- The deterministic release manifest contains 3,476 staged package files and passes its dedicated checker. It freezes source/configuration content only and does not imply acceptance.
- After manifest regeneration, the complete standard-runtime sweep passed 144/144 checkers at the exact staged candidate.

## Remaining evidence

All fourteen carrier holds remain open: H1/Y32 behavior, contact application, EMC/protection, fabricator DFM, assembly process, grounding/insulation, Pi GPIO/header selection, harness, mounting/enclosure, first article, fault injection, thermal behavior and qualified confirmation of the diagnostic-only boundary. R202 closes no Sol R12 finding, requirement, gate, functional-safety credit or work authority.
