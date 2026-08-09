# R151 independent review request - DXL-STAR-P0.1 manufacturing evidence

**PRELIMINARY - NOT APPROVED FOR SUPPLIER UPLOAD, QUOTATION, FABRICATION, ASSEMBLY, CONNECTION, MOTION, OR ENERGIZATION**

Please independently regenerate `HR-V0-DXL-STAR-MFG-P0.1` from native `DXL-STAR-P0.1` with KiCad 10.0.5.

Verify:

1. Every recorded source hash matches the live native board/project, BOM and connector schedule.
2. Native DRC is zero within modeled scope and the output set contains exactly ten Gerber/job plus five drill/map/report files, IPC-D-356, raw positions and statistics.
3. All seven connector positions and rotations reconcile exactly to native centers; do not treat the raw file or derived transform as supplier XYRS.
4. All eighteen schedule terminals match native pads, especially JC1.2 as deliberate no-net/no-copper and JP1-JP3/JA1-JA3 as isolated VDD branches.
5. Connector footprints, pin-1 orientation, polarity, land patterns and mounting-hole records are correct for the intended application.
6. The 3 A JST EH limit versus XM540 4.4 A stall-current conflict remains explicit and unresolved.
7. All eighteen holds and eleven manufacturing selections remain open; no archive, supplier action or work authority exists.
8. `BOM-051` is an exact candidate hold, not a fabrication or energization release.

Review every CAM layer, aperture, mask, silk, outline, PTH/NPTH split, connector reference, pad, net and hold. Report findings by exact file/reference/pad/net/hold ID. Do not approve supplier upload, fabrication, assembly, connection, motion or energization.
