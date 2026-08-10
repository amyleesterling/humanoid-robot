# HR-V0 watchdog PCB BOM binding P0.1

**PRELIMINARY - NOT APPROVED FOR FABRICATION, ASSEMBLY, CONNECTION, MOTION, OR ENERGIZATION**

Identifier: `HR-V0-WD-BOM-BIND-P0.1`

Round: R149

Controlled board: `PCB-P1.0 / Project Button Electrical V3-P1.15`

Controlled assembly data: `HR-V0-WD-PCBA-DATA-P0.2`

## Correction

The live system BOM still described `BOM-048` as historical `PCB-P0.5`. That conflicted with the current native KiCad board and current assembly-data package.

`BOM-048` now binds the current native board SHA-256 identity to the P0.2 assembly package:

- native PCB SHA-256 `4e893c7d0d8e18ad933487bd51e390ef4497f9d021df8e67b7821797db296720`;
- 42 populated references;
- sixteen exact-MPN assembly-BOM lines totaling 42 components;
- 42 internal placement-reference rows;
- four NPTH mechanical features; and
- twelve inherited assembly holds, all open.

The binding and its hashes are machine-readable in `bom/hr-v0-watchdog-pcb-binding.csv` and `release/hr-v0/watchdog-pcb-bom-binding-p0.1/package-status.json`.

## What this establishes

The current BOM no longer points at a superseded board. The `exact_candidate_hold` classification means that the configuration identity and candidate quantity are exact enough for controlled review. It does not make a build package.

At R149 issuance, current Gerber/drill CAM did not exist. R150 supplied historical `HR-V0-WD-CAM-P0.1`; R195 synchronizes `HR-V0-WD-CAM-P0.2` to direct-bound PCB-P1.0 as a quarantined internal review set. Neither package is supplier-released, and P0.1 is prohibited for current supplier use. Supplier-normalized XYRS and an accepted supplier packet still do not exist. Provider, board process, stackup, finish, stencil, paste, reflow, THT, cleanliness, inspection, electrical test, first article, physical, HIL, EMC, thermal and qualified-review evidence remain unresolved.

Historical PCB-P0.5 and PCB-P0.9 artifacts are prohibited from upload or order against PCB-P1.0. No provider has been selected or contacted; no files have been uploaded; and no quotation, fabrication, assembly, connection, motion, energization or safety credit is authorized.

## Controlled evidence

- [Interactive watchdog PCB binding guide](../release/hr-v0/watchdog-pcb-bom-binding-p0.1/index.html)
- `bom/hr-v0-watchdog-pcb-binding.csv`
- `electrical/kicad/project-button-v3/project-button-v3.kicad_pcb`
- `electrical/manufacturing/hr-v0-watchdog-pcba-assembly-data-p0.2/`
- `tools/generate_hr_v0_watchdog_pcb_bom_binding.py`
- `tools/check_hr_v0_watchdog_pcb_bom_binding_p01.py`

`EG-003` and `EG-004` remain **partial**. This correction closes only the live BOM-to-native-board identity contradiction.
