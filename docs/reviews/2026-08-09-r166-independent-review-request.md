# R166 independent review request

Status: **PRELIMINARY - NOT APPROVED FOR SUPPLIER UPLOAD, QUOTATION, FABRICATION, ASSEMBLY, CONNECTION, MOTION, OR ENERGIZATION**

Independently regenerate `HR-V0-WD-CAM-P0.2` with KiCad 10.0.5 from the controlled PCB-P0.9 source. Verify DRC, Gerber/job and drill membership, IPC-D-356, board statistics, all source hashes, and exact 42-reference placement/rotation parity.

Challenge the P1.15 binding. Confirm the complete P1.15 source manifest and `HR-V0-E2-P115-PARITY-P0.1` are hash-controlled, that the native board title remains explicitly P1.14 rather than being silently relabeled, and that P0.1 is quarantined as historical.

Confirm the raw position file is not machine-ready XYRS, all eighteen holds remain open, all supplier/work authorization fields remain false, and no package language implies fabrication or energization approval.
