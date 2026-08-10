# HR-V0-DXL-STAR-MFG-P0.1

> **PRELIMINARY - NOT APPROVED FOR SUPPLIER UPLOAD, QUOTATION, FABRICATION, ASSEMBLY, CONNECTION, MOTION, OR ENERGIZATION**

This is a source-bound CAM and assembly **review** package for native board `DXL-STAR-P0.1`. It is not a supplier packet and contains no machine-ready assembler XYRS.

## What exists

- fresh KiCad 10.0.5 DRC, Gerber/job, separate PTH/NPTH drill, IPC-D-356, raw position and statistics outputs;
- exact SHA-256 identities for the native board/project, source BOM and connector schedule;
- seven connector placement parity rows and eighteen terminal-to-native-pad parity rows;
- seven proposed connector BOM rows and four mounting-hole records; and
- eighteen manufacturing inputs, eighteen open release holds and a checksum manifest.

## Boundary

The connector families remain application holds. Harness lengths, conductor gauges, fuses/protection, current/thermal limits, crimp process, signal integrity, no-backfeed, grounding/shielding, physical validation, supplier/process, DFM, first article and qualified release remain unresolved. The raw position export is not supplier-normalized XYRS. No archive or upload bundle is produced.

Passing the checker proves only source/output membership, hashes, native DRC and encoded parity. It does not prove manufacturability, electrical performance, safety, or permission to perform work.
