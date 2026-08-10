# HR-V0-WD-CAM-P0.1

> **PRELIMINARY - NOT APPROVED FOR SUPPLIER UPLOAD, QUOTATION, FABRICATION, ASSEMBLY, CONNECTION, MOTION, OR ENERGIZATION**

This is a source-bound CAM **review** package for `PCB-P0.9 / Electrical V3-P1.14`. It contains no supplier release and no machine-ready assembler XYRS.

## What exists

- current native KiCad board/project copies and their hashes;
- fresh KiCad 10.0.5 DRC, Gerber/job, separate PTH/NPTH drill, IPC-D-356, raw position and statistics outputs;
- exact source hashes for the P0.2 assembly BOM, internal placement reference, mechanical-feature register and twelve open assembly holds;
- a 42-reference exact internal-coordinate parity proof between the raw KiCad position export and P0.2 placement reference;
- eighteen manufacturing inputs and eighteen open release holds; and
- a checksum manifest for every package file.

## Boundary

The raw KiCad position export is not supplier-normalized XYRS and is prohibited from machine import. Material, stackup, copper, finish, mask, legend, hole/profile tolerances, panelization, electrical test, provider/process, DFM, first article, physical tests and qualified release remain unresolved. No archive or upload bundle is produced.

Passing the checker proves only source/output membership, hashes, native DRC and internal coordinate parity. It does not prove manufacturability, physical correctness, electrical performance, functional safety or permission to perform work.
