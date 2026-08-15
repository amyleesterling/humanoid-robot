# HR-V0 DXL carrier mounting interface P0.2

> **PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, DRILLING, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION**

R264 replaces the stale P0.6 mounting centers with exact coordinate transforms for the R263 rotated P0.7 planning candidates. The P0.3 PCB local datums map to twelve panel hole centers and six JIN1/JOUT1 connector anchors. The transform is `x_panel = x0 + (60 - y_board); y_panel = y0 + x_board` in the controlled y-down coordinate frames.

These are datums, not fabrication instructions. Panel-hole diameter, tolerance, coating/deburr process, received dimensions, connector and wire sweep, duct entry, cut length, component height, cover/rear clearance, torque, load, creep, vibration, thermal behavior and qualified acceptance remain open. The board-to-WD2 gap is 14.2 mm and the LIM3-to-WD4 gap is only 5.0 mm nominal; neither proves usable three-dimensional service space.

Essentra's current official page identifies `NSE-1580-M3-6` as the replacement for legacy `0120070000VR`. R264 records that relationship as a held candidate only. Current order route, received identity, dimensional equivalence and application evidence are required.

Interactive guide: [release package](../release/hr-v0/dxl-carrier-mount-p0.2/index.html).
