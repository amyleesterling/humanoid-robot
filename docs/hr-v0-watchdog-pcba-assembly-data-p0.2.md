# HR-V0 watchdog PCBA assembly data P0.2

> **PRELIMINARY - NOT APPROVED FOR FABRICATION, ASSEMBLY, CONNECTION, OR ENERGIZATION.**

Identifier: `HR-V0-WD-PCBA-DATA-P0.2`

Board: `PCB-P1.0 / Electrical V3-P1.15` (R195 direct-binding correction)

Date: 2026-08-10

## Current configuration result

PCB-P1.0 carries exact hidden manufacturer, manufacturer part number, assembly description, process class, no-alternate policy, assembly-process state, and preliminary fabrication state on all 42 populated footprints. The native-field register contains 294 exact hidden matches. The four R138 critical references retain their deeper primary-document, revision/date, package-drawing, and land-basis fields.

The current assembly package contains:

- 42 populated top-side references;
- 16 exact-MPN BOM lines totaling 42 components;
- 38 `SMD_REFLOW` planning-class placements and four `MANUAL_THT_POST_REFLOW` planning-class placements;
- four separate unpopulated 3.20 mm NPTH mounting features;
- explicit board-relative coordinates, native rotations, orientation controls, no-alternate rules, twelve open holds, and a machine-import prohibition.

## Parity result

The PCB-P0.8 and PCB-P1.0 field-independent structural snapshots share SHA-256 `dc1f86c067e9617aed7e82b177bc7e1b0fb61b25cc3ab878e6c4440889c4c5ea`. Footprint identity and placement, pad geometry/nets/layers, tracks, vias, Edge.Cuts, and zones are unchanged.

All 46 P0.7-to-P1.0 assembly comparison rows pass: 42 populated identities/positions/rotations and four NPTH identities/positions. PCB-P1.0 directly binds the existing native assembly definition to Electrical V3-P1.15; no geometry, topology, placement, net or land change is claimed. Native KiCad DRC remains zero violations, zero unconnected pads, and zero footprint errors.

## Manufacturing boundary

The `SMD_REFLOW` and `MANUAL_THT_POST_REFLOW` values are planning classes, not accepted manufacturing instructions. Every footprint retains `AssemblyProcessState = SELECTION REQUIRED`. Supplier origin/axes/rotation/centroid conventions, machine-ready XYRS, paste/alloy/flux, stencil/apertures, mask, reflow profile, THT method, cleaning, cleanliness, inspection, stackup, finish, panelization, CAM, electrical test, traceability, first article, and qualified review remain open.

No provider has been selected or contacted. Quarantined current CAM review outputs exist but are not supplier-released. No fabricated board, assembled board, physical test, functional-safety credit, fabrication authorization, or energization authorization exists.

Evidence:

- `electrical/manufacturing/hr-v0-watchdog-pcba-assembly-data-p0.2/board-assembly-bom.csv`
- `electrical/manufacturing/hr-v0-watchdog-pcba-assembly-data-p0.2/assembly-placement-reference.csv`
- `electrical/manufacturing/hr-v0-watchdog-pcba-assembly-data-p0.2/native-identity-field-register.csv`
- `electrical/manufacturing/hr-v0-watchdog-pcba-assembly-data-p0.2/assembly-parity-p0.7-to-p1.0.csv`
- `electrical/manufacturing/hr-v0-watchdog-pcba-assembly-data-p0.2/p0.8-p1.0-geometry-topology-parity.json`
- `electrical/e2/hr-v0-e2-hardware-p0.4/`
- `release/hr-v0/watchdog-pcba-assembly-data-p0.2/index.html`

This package advances configuration consistency only. It is not a supplier payload or work authorization.
