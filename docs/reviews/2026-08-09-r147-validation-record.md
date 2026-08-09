# R147 validation record - actuator-source AC cord candidate

**PRELIMINARY - NOT APPROVED FOR FABRICATION, CONNECTION, MOTION, OR ENERGIZATION**

Date: 2026-08-09

Product: `HR-V0-ACT-AC-CORD-P0.1`

## Source and data validation

- Current official MEAN WELL and Eaton records were rechecked on 2026-08-09.
- Source identity, revision/access, connector families, catalog ratings/construction, typical input, cold-start inrush and PE/DC relationship are captured with explicit evidence boundaries.
- The generated package contains 18 controls, twelve open holds, sixteen unexecuted receiving records and fourteen unexecuted site-fit records.
- `BOM-063` advances to exact-candidate hold; system totals become 17 evaluation candidates, 37 exact-candidate holds, three grouped-component holds, 23 selection-required groups, four exclusions and one integrated item.
- `EG-001`, `EG-003`, `EG-016`, and `EG-019` remain partial.

## Visual QA

- The generated interactive guide was served locally and inspected in the in-app browser at the available wide desktop viewport.
- The warning is fully visible without clipping, the metric cards reflow within the page, and the long interface table is contained by its dedicated horizontal-scroll wrapper.
- The browser DOM snapshot contains all eighteen interface rows, all twelve open holds, the zero-executed-record statement and all four artifact links.
- The stylesheet uses 16-pixel-or-larger body text, `clamp()` sizing, an auto-fit card grid and a table wrapper. Narrow-screen behavior was source-inspected but was not claimed as a separate physical mobile-device test.

## Automated regression

- 96 standard engineering checkers passed in the controlled CadQuery environment.
- Five native KiCad checkers passed under KiCad 10.0.5 Python, including zero native watchdog-board DRC violations and the existing zero ERC/DRC star-injection result.
- The release manifest was regenerated over 2,041 package files and passed its dedicated checker. Total regression: 102 engineering checkers passed (96 standard, five native KiCad and one release-manifest checker).

## Disposition

Catalog selection is internally specified but application evidence remains absent. No purchase, received identity, site survey, physical fit, conductor mapping, PE/insulation result, branch/inrush/thermal result, code disposition, connection or energization authority exists.
