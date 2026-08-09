# R138 independent watchdog IC-metadata review request

> **PRELIMINARY - NOT APPROVED FOR FABRICATION, ASSEMBLY, CONNECTION, TESTING, OR ENERGIZATION.**

Review `HR-V0-WD-IC-META-P0.1` and `PCB-P0.8 / Electrical V3-P1.14` against PCB-P0.7, the current official manufacturer documents, and the R132/R133 historical records. This is a source-definition/configuration review, not manufacturing or safety approval.

## Reproduce

```powershell
& 'C:\Program Files\KiCad\10.0\bin\python.exe' tools/generate_hr_v0_watchdog_pcb.py
& 'C:\Program Files\KiCad\10.0\bin\python.exe' tools/generate_hr_v0_watchdog_footprint_metadata.py
& 'C:\Program Files\KiCad\10.0\bin\python.exe' tools/check_hr_v0_watchdog_footprint_metadata.py
& 'C:\Program Files\KiCad\10.0\bin\python.exe' tools/check_hr_v0_watchdog_pcb.py
```

Do not run `--capture-baseline`; the checked-in P0.7 baseline is immutable review evidence.

## Required questions

1. Verify all 36 native fields on `UDRV1`, `UDRV2`, `UFB1`, and `ISO1` against the cited primary manufacturer revisions/dates.
2. Independently compare the P0.7 baseline and current PCB-P0.8 structural snapshots. Confirm that footprint identity/placement/orientation, pad geometry/net/layers, tracks, vias, Edge.Cuts, and zones are identical.
3. Re-run native KiCad DRC and report complete results and KiCad version.
4. Confirm TPL7407L PW and ISO1212 DBQ pad dimensions/orientation against the manufacturer example layouts, and VO618A option-7 geometry against its dimensioned land drawing.
5. Confirm UFB1 `R0.05` is identified as project-controlled rather than a TI-dimensioned requirement.
6. Confirm every `AssemblyProcess` remains `SELECTION REQUIRED` and no paste, mask, stencil, reflow, cleaning, inspection, fabrication, or safety selection is implied.
7. Confirm R132/R133 remain historical P0.7 records whose hashes were not silently rebound to P0.8.
8. State separately whether the package is ready for qualified electrical review, assembler DFM inquiry, CAM generation, fabrication, assembly, physical test, functional-safety review, and energization.

Return `BLOCKER / MAJOR / MINOR` findings with exact reference, field, pad, net, file, or source-document clause. Do not infer physical correctness or work authority from field completeness, DRC, or digest parity.
