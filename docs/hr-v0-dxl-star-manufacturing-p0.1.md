# HR-V0 DYNAMIXEL star manufacturing review package P0.1

**PRELIMINARY - NOT APPROVED FOR SUPPLIER UPLOAD, QUOTATION, FABRICATION, ASSEMBLY, CONNECTION, MOTION, OR ENERGIZATION**

Identifier: `HR-V0-DXL-STAR-MFG-P0.1`

Round: R151

Controlled source: `DXL-STAR-P0.1`

## Result

R151 generates a source-bound CAM and assembly review set from the native DYNAMIXEL star-injection board using KiCad 10.0.5. It advances `BOM-051` from `design_required` to `exact_candidate_hold` without releasing the board or any harness:

- native DRC at zero violations, zero unconnected pads and zero footprint errors within the modeled board scope;
- nine Gerber layers plus one Gerber job file;
- separate PTH/NPTH drill files, two SVG drill maps and one drill report;
- IPC-D-356, raw KiCad position and board-statistics outputs;
- exact SHA-256 identities for the native board/project, source BOM and connector schedule;
- exact native-coordinate parity for all seven populated connector references;
- eighteen terminal-to-native-pad parity rows, including JC1 pin 2 as deliberate `NO_NET_NO_COPPER`;
- seven held connector BOM rows and four NPTH mounting-hole records; and
- a manifest covering every package file.

The board encodes three isolated actuator VDD rails, common DXL TTL data and common actuator return. Those are connectivity facts only. They do not establish harness suitability, current capacity, thermal performance, signal margin, grounding, safety, or permission to fabricate.

## Manufacturing and application boundary

Eleven of eighteen manufacturing inputs remain explicitly `SELECTION REQUIRED`: base material/Tg, copper, finish, mask, legend, hole/plating tolerance, profile tolerance, panelization/tooling, electrical test/coupon, impedance disposition, and provider.

Eighteen release holds remain open. They include connector pattern/polarity review; exact mating housings and contacts; conductor and crimp definition; fuse/protection coordination; the published 3 A JST EH connector limit versus the XM540 4.4 A stall-current condition; DXL waveform/error evidence; U2D2 no-backfeed; return/PE/shield implementation; thermal/load testing; first article; HIL/fault/EMC validation; and qualified release.

No archive or upload packet exists. Supplier selection/contact, upload, quotation, fabrication, assembly, physical article, connection, motion, energization and safety credit remain false.

## Controlled evidence

- [Interactive manufacturing review guide](../release/hr-v0/dxl-star-manufacturing-p0.1/index.html)
- `release/hr-v0/dxl-star-manufacturing-p0.1/cam-output-register.csv`
- `release/hr-v0/dxl-star-manufacturing-p0.1/placement-parity-register.csv`
- `release/hr-v0/dxl-star-manufacturing-p0.1/terminal-parity-register.csv`
- `release/hr-v0/dxl-star-manufacturing-p0.1/manufacturing-input-register.csv`
- `release/hr-v0/dxl-star-manufacturing-p0.1/manufacturing-release-holds.csv`
- `tools/generate_hr_v0_dxl_star_manufacturing_p01.py`
- `tools/check_hr_v0_dxl_star_manufacturing_p01.py`

`EG-004` and `EG-015` remain **partial**. The package adds configuration evidence; it does not close any physical or authorization gate.
