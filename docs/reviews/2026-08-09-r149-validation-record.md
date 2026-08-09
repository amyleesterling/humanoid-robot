# R149 validation record - watchdog PCB BOM binding

**PRELIMINARY - NOT APPROVED FOR FABRICATION, ASSEMBLY, CONNECTION, MOTION, OR ENERGIZATION**

Date: 2026-08-09

Product: `HR-V0-WD-BOM-BIND-P0.1`

## Configuration result

- `BOM-048` now names current PCB-P0.9 / Electrical V3-P1.14 and P0.2 assembly data.
- One native PCB SHA-256 identity, sixteen BOM lines, 42 populated references, 42 placements and four NPTH features are hash-bound.
- The system BOM closure becomes 39 exact-candidate holds and 21 selection-required groups.
- All twelve assembly-data holds remain open.
- Current CAM, supplier-normalized XYRS, supplier packet, provider/process acceptance, physical article and qualified review remain absent.
- `EG-003` and `EG-004` remain partial. All fabrication, assembly, connection, motion, energization and safety-credit flags remain false.

## Visual QA and automated regression

- The interactive guide was served locally and inspected in the in-app browser at the available desktop viewport. Its preliminary warning, 42/16/4/0 cards, controlled-file table, twelve-hold statement and artifact links were fully visible and legible. The table is contained in a horizontal-scroll wrapper. Source inspection confirms 16-pixel-or-larger body text, 14-pixel code text, responsive `clamp()` sizing and an auto-fit card grid; narrow behavior was source-inspected but is not claimed as a separate physical mobile-device test.
- Ninety-eight standard engineering checkers passed in the controlled project environment.
- Five native KiCad checkers passed under KiCad 10.0.5 Python, including native board DRC at zero violations within modeled scope.
- The release manifest was regenerated over 2,059 package files and passed its dedicated checker. Total regression: 104 engineering checkers passed (98 standard, five native KiCad and one release-manifest checker).

## Disposition

R149 corrects a current configuration mismatch only. It does not release manufacturing data, prove the watchdog function, establish functional-safety performance, or authorize any physical work or power.
