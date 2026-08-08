# HR-V0-WD-FAB-P0.1

> **PRELIMINARY - NOT APPROVED FOR FABRICATION OR ENERGIZATION**

This is a deterministic **CAM review candidate** for watchdog PCB `PCB-P0.5`, compatible with Electrical V3-P1.13. It is not a manufacturing release. Do not upload it to a supplier portal, order it, assemble it, connect it to a safety circuit, or energize it.

## What is present

- an immutable copy of the KiCad 10.0.5 board/project source;
- fresh DRC, Gerber, PTH/NPTH drill, position, IPC-D-356 and board-statistics outputs;
- a 42-reference candidate assembly BOM;
- the proposed fabrication envelope, primary-source register and 14 open holds; and
- checksums for every controlled file.

The native source includes four additional mechanical mounting-hole footprints. Native KiCad DRC must remain zero. Generated CAM is evidence for independent review only.

## Compatibility decision

OSH Park's current KiCad page documents direct processing using KiCad 9.x, while this source is KiCad 10.0.5. Therefore direct native-file submission is not assumed compatible. A qualified reviewer must inspect the generated Gerbers and supplier preview before any later, separately authorized fabrication release.

## Release state

All authorization flags in `package-status.json` are false. Every row in `fabrication-holds.csv` is open. Passing the package checker proves deterministic source/output consistency, not physical correctness or safety.
