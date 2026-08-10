# HR-V0 watchdog PCB CAM review package P0.1

**PRELIMINARY - NOT APPROVED FOR SUPPLIER UPLOAD, QUOTATION, FABRICATION, ASSEMBLY, CONNECTION, MOTION, OR ENERGIZATION**

Identifier: `HR-V0-WD-CAM-P0.1`

Round: R150

Controlled source: `PCB-P0.9 / Project Button Electrical V3-P1.14`

Assembly-data basis: `HR-V0-WD-PCBA-DATA-P0.2`

## Result

R150 generates a current, source-bound CAM review set from PCB-P0.9 with KiCad 10.0.5. It replaces the complete absence of current-board outputs with quarantined internal evidence:

- native DRC with zero violations, zero unconnected pads and zero footprint errors within the modeled board scope;
- nine Gerber layers plus one Gerber job file;
- separate PTH and NPTH Excellon drill files, two SVG drill maps and one drill report;
- one IPC-D-356 review netlist;
- one raw KiCad position export covering exactly 42 populated references;
- one board-statistics record;
- exact source hashes for the native board/project and four P0.2 assembly-data inputs; and
- a package manifest covering every controlled file.

The raw KiCad position export and the P0.2 internal placement register reconcile exactly after one derived coordinate transform: `board_x = PosX - 20 mm` and `board_y = -PosY - 20 mm`, with zero position and rotation error across all 42 references. This is internal parity evidence only. It is not a supplier coordinate convention and it is prohibited from machine import.

## Manufacturing boundary

The package records eighteen manufacturing inputs. Eleven remain explicitly `SELECTION REQUIRED`, including material/Tg, copper, finish, mask, legend, finished-hole/plating tolerance, profile tolerance, panelization/tooling, bare-board electrical test/coupon, impedance disposition and provider.

The twelve P0.2 assembly holds remain open and six CAM-specific holds are added, for eighteen open holds total. They require independent layer/drill preview, provider capability/process acceptance, returned DFM/CAM disposition, supplier-normalized XYRS, bare-board and first-article acceptance, and qualified written manufacturing release.

No upload archive is generated. Provider selection/contact, file upload, quotation request, fabrication, assembly, physical article, connection, motion, energization and safety credit remain false.

## Controlled evidence

- [Interactive CAM review guide](../release/hr-v0/watchdog-pcb-cam-p0.1/index.html)
- `release/hr-v0/watchdog-pcb-cam-p0.1/cam-output-register.csv`
- `release/hr-v0/watchdog-pcb-cam-p0.1/cam-assembly-parity.csv`
- `release/hr-v0/watchdog-pcb-cam-p0.1/manufacturing-input-register.csv`
- `release/hr-v0/watchdog-pcb-cam-p0.1/cam-release-holds.csv`
- `tools/generate_hr_v0_watchdog_cam_p01.py`
- `tools/check_hr_v0_watchdog_cam_p01.py`

`EG-004` remains **partial**. Current outputs now exist, but manufacturing definition, supplier normalization, physical evidence, qualified review and every work authorization remain unresolved.
