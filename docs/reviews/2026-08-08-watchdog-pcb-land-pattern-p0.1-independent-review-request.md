# Independent Review Request — HR-V0 Watchdog PCB Land Patterns P0.1

Status: **PRELIMINARY - NOT APPROVED FOR FABRICATION OR ENERGIZATION**
Candidate: `HR-V0-WD-LAND-P0.1` / `PCB-P0.6` / Electrical `V3-P1.13`
Date: 2026-08-08

Please independently review the exact candidate commit. Do not treat KiCad DRC, generated source, this disposition, or the former R88 CAM package as fabrication or energization approval.

## Review scope

1. Reproduce Electrical V3 and PCB-P0.6 generation and both checkers in KiCad 10.0.5.
2. Audit all 42 schematic references and four board-only holes against the exact primary manufacturer records in `land-pattern-audit.csv`.
3. Recalculate every corrected land dimension, pitch, row spacing, inner gap, overall span, pin numbering and orientation.
4. Challenge the proposed SMD-reflow then manual-THT sequence, including component temperature limits and ordering.
5. Review solder-mask expansion/webs, stencil thickness/apertures, paste volume/type, reflow profile, cleaning, AOI, rework and first-article criteria. No process is released merely because `0.05 mm` NSMD margins are encoded on candidate SMD footprints.
6. Recalculate system-level ISO1 creepage/clearance from working voltage, overvoltage category, pollution degree, material group, coating, altitude, environment and applicable requirements.
7. Review Pico solder-pool and overhang/access risks, Phoenix torque support and service access, DC1 THT drill/land/height evidence, Harwin probe access, and the unselected M3 stack.
8. Confirm the immutable R88 CAM source is PCB-P0.5 and is not interchangeable with PCB-P0.6. Confirm no current P0.6 Gerber/drill package exists.
9. Inspect the native board and renders for pin-1 visibility, silkscreen ambiguity, probe access, courtyard conflicts and misleading claims.
10. Report every missing manufacturer revision, tolerance, fabrication rule, assembly capability or physical test needed before a new CAM candidate could be issued.

## Reproduction

Run from the repository root:

```powershell
& 'C:\Users\amyle\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' tools/generate_hr_v0_electrical_v3.py --validate
& 'C:\Program Files\KiCad\10.0\bin\python.exe' tools/generate_hr_v0_watchdog_pcb.py
& 'C:\Program Files\KiCad\10.0\bin\python.exe' tools/check_hr_v0_watchdog_pcb.py
& 'C:\Users\amyle\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' tools/check_hr_v0_watchdog_pcb_land_pattern.py
```

## Required output

Provide `BLOCKER`, `MAJOR` and `MINOR` findings with exact reference, pad, footprint, dimension, source document and revision/date. Separate source correctness from assembler acceptance, fabricated-board evidence and system safety. State explicitly whether the package is ready for qualified PCB/assembly review and whether any fabrication or energization permission exists.

It is expected that fabrication and energization remain prohibited after this source-level review.
