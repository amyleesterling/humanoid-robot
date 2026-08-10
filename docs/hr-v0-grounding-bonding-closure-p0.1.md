# HR-V0 grounding, bonding, and shield closure P0.1

Status: **PRELIMINARY - NOT APPROVED FOR WIRING, FABRICATION, TESTING, OR ENERGIZATION**

Identifier: `HR-V0-GND-BOND-P0.1`

## Corrected design boundary

The V3 source does not have one generic ground. It has three DC returns, two unresolved metal/shield placeholders, conductive mechanical assemblies that are absent from ECAD, and one manufacturer-internal relationship:

- the proposed Mean Well GST280A source connects `-V` to AC protective earth internally;
- `ACT_0V_PE_BONDED` therefore has a source-defined PE relationship, subject to received-source verification;
- `SP1` is DNP and prohibited because adding it would create a second intentional actuator-return/PE bond;
- the proposed GlobTek 24 V source is Class II and floating, while its factory cord shield is explicitly the pin-3 output return;
- `SAFETY_0V` is not assigned to PE or frame;
- the current Raspberry Pi product brief does not establish the received SKU or USB-shell relationship, so `COMPUTE_0V` remains separate;
- `ROBOT_FRAME` and `CABLE_SHIELD_TERM` are isolated one-terminal V3 placeholders; and
- steel backplate, DIN rails, actuator cases, USB shells and guard frame are not represented as released electrical nodes.

This corrects the earlier shorthand “single proposed DC 0 V/PE star point.” A DC system-reference bond and an equipment protective-bonding network are different design questions. Protective bonding must provide the required permanent, continuous, effective fault path; it is not released by drawing a star symbol. Conversely, joining every return and shield to metal can create unintended current and EMC paths.

## Current fail-closed rules

1. Keep all three external AC adapters unmodified and outside the project enclosure.
2. Retain the Mean Well manufacturer-internal `-V`/FG relationship; do not add `SP1`.
3. Do not label the GlobTek pin-3 output-return shield as PE.
4. Do not bond or isolate robot frame, guard frame, backplate, DIN rail, cable shield, USB shell, `SAFETY_0V`, or `COMPUTE_0V` by assumption.
5. Do not use a DC return conductor as an equipment-grounding conductor unless a qualified application design establishes its fault capacity and compliance.
6. Do not use mechanical fastener contact, anodized extrusion contact, DIN mounting, cable braid, USB shell, actuator case, or guard contact as an unverified fault path.
7. Do not perform insulation-resistance testing through installed electronics. The stimulus, disconnection boundary, instrument and numeric limits require qualified approval.
8. Update native KiCad, harness views, BOM, labels and inspection records only after one configuration-specific topology is selected.

## Controlled evidence

- `electrical/vendor/grounding-r118/source-manifest-p0.1.csv` records eight current primary-source identities and their limits.
- `electrical/grounding/hr-v0-grounding-node-register-p0.1.csv` records fifteen exact modeled or physical relationships.
- `electrical/grounding/hr-v0-grounding-selection-matrix-p0.1.csv` records twelve closure holds.
- `tests/forms/hr-v0-grounding-bonding-survey-template-p0.1.csv` defines eighteen unexecuted and unauthorized survey rows.

The current V3 net schedule contains 18 `ACT_0V_PE_BONDED` terminals, 41 `SAFETY_0V` terminals, five `COMPUTE_0V` terminals, one `ROBOT_FRAME` placeholder and one `CABLE_SHIELD_TERM` placeholder. Those counts prove only the logical model state.

## Boston code and site boundary

The Massachusetts Department of Fire Services current page identifies 527 CMR 12.00 as based on the 2026 edition of NFPA 70, effective 2026-04-24. Boston's current permit page describes the licensed-contractor application and inspection route for covered electrical installation work. OSHA 29 CFR 1910.304 requires a permanent, continuous, effective grounding path and defines circumstances for grounding exposed metal equipment, while preserving an exception for listed double-insulated equipment.

No project document determines that every provision applies to a not-yet-selected home, library, makerspace, or workplace site. The exact site, occupancy, ownership, installation scope, permit status and workplace status must be reviewed by the site representative and a qualified local electrical professional.

## Closure sequence

1. Freeze the exact site and written site permission.
2. Obtain the local code/permit/workplace applicability disposition.
3. Receive and inspect the exact external adapters, Pi supply, actuators, U2D2, enclosure, backplate, DIN rails, guard/frame members and cables.
4. Approve a non-damaging unpowered measurement method and calibrated instruments.
5. Complete all eighteen survey rows with raw evidence.
6. Perform configuration-specific shock, touch-voltage, fault-current, clearing, leakage, first-fault, parallel-path and EMC analysis.
7. Select exact bonding/shield topology and hardware, including conductor, terminals, fasteners, finish preparation, torque, routing, labels and inspection limits.
8. Update native ECAD and every synchronized schedule/harness artifact.
9. Execute qualified continuity, insulation, polarity, no-backfeed and fault-injection validation at the authorized stage.
10. Obtain signed electrical, EMC and functional-safety dispositions.

`EG-001`, `EG-014`, `EG-015`, `EG-016`, `EG-019`, `EG-020`, `EG-021` and `EG-022` remain unresolved. This packet closes no gate and authorizes no physical work.

**PRELIMINARY - NOT APPROVED FOR WIRING, FABRICATION, TESTING, OR ENERGIZATION.**
