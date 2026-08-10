# R133 independent review request

Status: **PRELIMINARY - NOT APPROVED FOR FABRICATION OR ENERGIZATION**

Review `HR-V0-WD-PCBA-DATA-P0.1` against current `PCB-P0.7` and the R132 placement/process register.

Please independently:

1. Reproduce the exact 42 populated-reference and four-NPTH membership from native KiCad source.
2. Reconcile all sixteen grouped BOM lines, exact MPNs, quantities and references to the schematic, R89 audit and R132 register.
3. Reproduce the 160.000 x 100.000 mm Edge.Cuts rectangle and every board-relative coordinate from source geometry.
4. Audit native KiCad rotations and every explicit polarized, not-keyed and module-orientation note.
5. Confirm the internal origin/axis convention is unambiguous but cannot be mistaken for assembler-normalized XYRS.
6. Identify missing assembly drawing, fiducial, tooling, panelization, feeder, packaging, moisture, polarity, inspection, rework or traceability controls.
7. Confirm all ten file states and twelve holds prevent direct supplier upload, machine import, fabrication or assembly authorization.
8. Report BLOCKER / MAJOR / MINOR findings with exact file, row, reference and proposed correction.

Run:

```powershell
& 'C:\Program Files\KiCad\10.0\bin\python.exe' tools/generate_hr_v0_watchdog_pcba_assembly_data.py
& 'C:\Users\amyle\Documents\New project\.venvs\hr-v0-cad\Scripts\python.exe' tools/check_hr_v0_watchdog_pcba_assembly_data.py
```

Do not approve fabrication, assembly, connection or energization. A correct BOM or placement map is not supplier acceptance, a process release, physical evidence or functional-safety validation.
