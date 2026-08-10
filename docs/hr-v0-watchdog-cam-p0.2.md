# HR-V0 watchdog CAM review P0.2

Status: **PRELIMINARY - NOT APPROVED FOR SUPPLIER UPLOAD, QUOTATION, FABRICATION, ASSEMBLY, CONNECTION, MOTION, OR ENERGIZATION**

Identifier: `HR-V0-WD-CAM-P0.2`

## What R166 closes

P0.2 removes the internal configuration mismatch between the active `Project Button Electrical V3-P1.15-CARRIER-CANDIDATE` baseline and the historical P1.14-bound watchdog CAM review. It hash-binds:

- native watchdog board `PCB-P0.9`, whose title block intentionally retains `Electrical V3-P1.14`;
- the complete P1.15 native source manifest;
- `HR-V0-E2-P115-PARITY-P0.1`, which proves the watchdog/E2 subset is unchanged at 69 references and 263 terminals;
- `HR-V0-WD-PCBA-DATA-P0.2`; and
- fresh KiCad 10.0.5 CAM outputs generated from the controlled board source.

Native DRC reports zero violations, zero unconnected pads, and zero footprint errors. The review set contains ten Gerber/job files, five drill/map/report files, IPC-D-356, board statistics, and a raw 42-reference position export. All 42 references reproduce the internal placement register with zero position and rotation error after the controlled coordinate transform.

## What remains open

The position export is not supplier-normalized XYRS and is prohibited from machine import. The fabricator, assembler, stackup, laminate/Tg, copper, finish, mask, legend, tolerances, panelization, electrical-test process, stencil, paste, THT process, sourcing/traceability, DFM disposition, first article, inspection, cleanliness, physical tests, and qualified release remain unresolved.

All eighteen manufacturing/release holds remain open. No supplier was contacted; no archive was created; no file was uploaded; and no quotation or work was authorized.

## Controlled artifacts

- [Interactive CAM guide](../release/hr-v0/watchdog-pcb-cam-p0.2/index.html)
- `release/hr-v0/watchdog-pcb-cam-p0.2/cam-output-register.csv`
- `release/hr-v0/watchdog-pcb-cam-p0.2/cam-assembly-parity.csv`
- `release/hr-v0/watchdog-pcb-cam-p0.2/manufacturing-input-register.csv`
- `release/hr-v0/watchdog-pcb-cam-p0.2/cam-release-holds.csv`
- `tools/generate_hr_v0_watchdog_cam_p02.py`
- `tools/check_hr_v0_watchdog_cam_p02.py`

Passing the checker establishes file membership, hashes, native DRC, source binding, and internal coordinate parity only. It is not evidence of manufacturability, physical correctness, functional safety, or permission to fabricate or energize.
