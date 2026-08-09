# R156 validation record

> **PRELIMINARY - NOT APPROVED FOR SUPPLIER UPLOAD, QUOTATION, PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, MOTION, OR ENERGIZATION**

- Configuration: `HR-V0-DXL-PROT-CARRIER-P0.1`
- Date: 2026-08-09

## Verified source evidence

- Texas Instruments TPS25946 datasheet `SLVSGA8B`, revision B, April 2022: exact pinout, forward-only current limiting, ILM ranges, layout, transient and thermal-example boundaries.
- Texas Instruments TPS25946EVM guide `SLVUC35A`, revision A, August 2021: exact EVM passive and Keystone test-point identities.
- Current JST VH catalog: exact B2P-VH PCB-header identity and family dimensions; harness application remains held.
- Current TDK product records: exact 1 uF, 0.1 uF and 2.2 nF candidates.
- Diodes Incorporated B330A datasheet revision 19-2, April 2026: exact B330A-13-F candidate.
- Exact Yageo candidate order codes are recorded for all five resistors.

## Executed repository checks

- KiCad 10.0.5 parsed the root and four child sheets.
- Native ERC: 0 errors / 0 warnings.
- Native DRC: 0 violations / 0 unconnected pads / 0 footprint errors.
- Routed PCB: four copper layers, 20 populated references, four board-only M3 holes and a drawing-derived 14-land/10-terminal RPW footprint.
- Controlled release source is byte-identical to the native source.
- Schematic PDF and five SVGs generated; top and bottom board renders generated.
- All four copper Gerbers, drill, position and board-statistics review outputs generated.
- Package checker: PASS for five native sheets, 20 physical placements, three assembly variants, seven primary sources, ten blank tests, sixteen open holds and exact file-manifest parity.
- Complete non-`pcbnew` repository sweep: 102 / 102 checkers passed after deterministic build-traveler regeneration.
- Native KiCad/PCB checker sweep: 8 / 8 passed under the KiCad 10 Python runtime.
- Staged release manifest: PASS for 2,295 package files.
- Visual QA: the initial crowded sheet was rejected; the final source is split into core, threshold, transient and measurement sheets. Board top/bottom renders and all four child sheets were inspected.
- Robot baseline change: no.
- System BOM change: no.
- Tests executed: 0.
- Qualified approvals: 0.
- Work authorizations: 0.

ERC/DRC and CAM generation establish encoded connectivity and geometry only. They do not establish footprint acceptance, assembly yield, current capacity, thermal behavior, transient containment, reverse-energy handling, harness suitability, EMC, functional safety or permission to perform physical work.
