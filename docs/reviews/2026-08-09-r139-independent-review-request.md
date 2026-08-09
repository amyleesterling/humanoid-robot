# R139 independent PCB-P0.9 assembly-data review request

> **PRELIMINARY - NOT APPROVED FOR FABRICATION, ASSEMBLY, CONNECTION, TESTING, OR ENERGIZATION.**

Review `PCB-P0.9 / HR-V0-WD-PCBA-DATA-P0.2 / HR-V0-E2-HW-P0.3` against PCB-P0.8, historical R133 P0.7 assembly data, R132 process/DFM evidence, and current controlled manufacturer sources.

## Reproduce

```powershell
& 'C:\Program Files\KiCad\10.0\bin\python.exe' tools/generate_hr_v0_watchdog_pcb.py
& 'C:\Program Files\KiCad\10.0\bin\python.exe' tools/generate_hr_v0_watchdog_pcba_assembly_data_p02.py
& 'C:\Program Files\KiCad\10.0\bin\python.exe' tools/check_hr_v0_watchdog_pcba_assembly_data_p02.py
python tools/generate_hr_v0_e2_hardware_slice.py
python tools/check_hr_v0_e2_hardware_slice.py
```

## Required questions

1. Verify all 294 native identity fields across all 42 populated references against the exact BOM and controlled primary-source register.
2. Independently reproduce P0.8/P0.9 structural parity for footprint placement, pads, nets, copper, vias, outline, and zones.
3. Independently reconcile all 46 P0.7/P0.9 assembly-parity rows, including every identity, X/Y position, native rotation, footprint, process class, orientation note, and NPTH feature.
4. Confirm the 16 BOM lines total exactly 42 parts with no blank MPN, implicit alternate, or silent substitution.
5. Verify the 38 SMD / four post-reflow THT classification, while confirming it is not an accepted paste/stencil/reflow/THT process.
6. Confirm machine import remains prohibited and no assembler-normalized centroid/origin/rotation/side transform exists.
7. Confirm the current E2 P0.3 slice points to PCB-P0.9/P0.2 while keeping the actuator source and branches physically absent or disconnected.
8. Re-run KiCad DRC/ERC and report complete results and tool version.
9. State separately whether this package is ready for qualified electrical review, assembler DFM inquiry, CAM generation, fabrication, assembly, unpowered test, functional-safety review, or energization.

Return `BLOCKER / MAJOR / MINOR` findings with exact reference, field, BOM line, placement row, pad, net, file, or source-document clause. Passing parity and repository checks do not authorize work.
