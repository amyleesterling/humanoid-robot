# HR-V0 BOM closure and evaluation boundary P0.1

Status: **PRELIMINARY—NOT A PROCUREMENT, FABRICATION, OR ENERGIZATION RELEASE**

Control date: 2026-08-07

## Result

The system BOM now contains 85 configuration groups: 17 evaluation candidates, 39 exact candidates on hold, three grouped-component holds, 21 selection-required groups, four exclusions and one integrated item. R46 exposed previously invisible assembly assumptions; later controlled passes add exact source, enclosure, compute-carrier and retention candidates. R122 holds the Pi-to-U2D2 cable; R123 separates exact rail, duct and DR1-DR3 end-bracket candidates into `BOM-083` through `BOM-085` while leaving residual `BOM-059` unresolved; R147 advances `BOM-063` to one exact held Eaton `P006-006` actuator-source AC cord candidate; R148 reconciles `BOM-027` to the exact held P0.7 C01/C04/C05/C06/C07 custom set; R149 binds `BOM-048` to current PCB-P0.9 / Electrical V3-P1.14 and `HR-V0-WD-PCBA-DATA-P0.2`. None is a complete procurement, fabrication or application release.

R61 advances `BOM-041` from `selection_required` to `exact_candidate_hold` for IDEC `HW1P-1FQD-A-24V`. This removes the obsolete `SAFE ELIGIBLE` value and synchronizes the system BOM with Electrical V3-P1.5 and `HR-V0-CP-P0.1`. It is not added to Evaluation Batch A and is not procurement- or wiring-released; `HR-V0-H1-RCV-P0.1` remains unexecuted.

R62 advances `BOM-019` to an exact-candidate hold for two Phoenix `PT 4-HESI (5X20)` item `3211861` holders and adds `BOM-072` for the two still-unresolved fuse links. R63 adds exact-candidate-hold `BOM-073` for one Phoenix `D-ST 4` item `3030420` end cover. R64 advances `BOM-042` to exact-candidate hold for Littelfuse `75920-01`; conductor/lug, source-fault, load-break, touch-protection, cutout, zero-energy/padlock, human-factors, Boston application and physical tests remain open. Those historical counts have since been superseded by the current 85-group closure totals above. Both FSR fuse links, received accessory compatibility/grouping, all protection calculations and all physical evidence remain open; manufacturer maximum ratings are not project fuse or conductor ratings.

R148 supersedes the stale R66 quantity statement for current configuration use. `BOM-027` now binds the controlled P0.7 custom set: one each `MV0-C01`, `MV0-C04`, `MV0-C05`, `MV0-C06`, and `MV0-C07`, totaling five candidate parts. Fifteen exact STEP/DXF/SVG identities already exist in `HR-V0-MECH-DFM-DATA-P0.1`, so the item advances to `exact_candidate_hold`. All fifteen DFM holds remain open, including provider/process selection, qualified drawing review, material/MTR, received fit, T-slot/fastener/stop/cable/guard/load proof, first articles, physical evidence and qualified release. No provider contact, upload, quotation, purchase, fabrication, assembly, motion or energization is authorized.

R149 supersedes the stale live PCB-P0.5 description for current configuration use. `BOM-048` now binds the controlled PCB-P0.9 native SHA-256 identity to P0.2 assembly data: sixteen exact-MPN lines totaling 42 populated references, 42 internal placements and four NPTH features. The item advances to `exact_candidate_hold`; all twelve assembly-data holds, current CAM, supplier-normalized XYRS, provider/process acceptance, physical evidence and qualified review remain open. Historical PCB-P0.5 CAM is prohibited from current use. No upload, quotation, fabrication, assembly, connection, motion or energization is authorized.

R73 reconciles the physical-evidence batch to the current P0.7 architecture. `BOM-023` moves from exact-candidate hold to evaluation candidate and `EVA-013` restores two exact ROBOTIS FR13-S102K sets, SKU `903-0269-300`. The resulting 17-line batch covers every actuator and actuator-frame article required for unpowered P0.7 receiving and fit work. `HR-V0-MECH-EVAL-P0.1` extracts the seven-line, nine-article mechanical subset. Every line still requires separate program-owner approval before purchase and remains unpowered evaluation only.

The machine-readable closure register is `bom/hr-v0-bom-closure.csv`. Every `bom/bom.csv` item has exactly one classification:

- `evaluation_candidate`: exact candidate order code and evaluation quantity are frozen, but program-owner approval is required before purchase and application suitability remains open;
- `exact_candidate_hold`: an exact candidate exists but is not included in the receiving batch;
- `grouped_components_hold`: the system row contains several parts and must be expanded before an orderable release;
- `selection_required`: order code, construction, quantity detail, or application evidence remains unresolved;
- `excluded_from_hr_v0_candidate`: historical, DNP, or superseded material; or
- `integrated_no_separate_purchase`: evidence is controlled through its parent item.

No row is classified as production-selected or procurement-released.

## Evaluation Batch A

`bom/hr-v0-evaluation-batch-a.csv` identifies seventeen exact candidate lines whose receipt is needed to execute identity, terminal, current, thermal, source, restart and fault tests. R53 removed the actuator body-frame purchase while the architecture was unresolved; R73 restores it after R69 froze the current P0.7 arrangement around two exact S102 sets. The batch includes the three actuators, U2D2, safety relays, contactors, E-stop, watchdog controller/relays, output/body/gripper frames, RESET/ARM operators and both external DC sources.

`bom/hr-v0-unpowered-mechanical-evaluation.csv` is a narrower seven-line subset covering nine actuator/frame/gripper articles. It is an evidence-planning view of the same Batch A rows, not a second procurement list. It permits no powered work and does not include custom metal, a guard, a receiver, or an installed fastener release.

The batch is not a shopping instruction. Every line states:

- `PROGRAM OWNER APPROVAL REQUIRED`;
- `EVALUATION ONLY`;
- current primary manufacturer source and document/access date; and
- required receiving and test routes.

After separately approving any purchase, quarantine each received unit and execute `INSPECT-BOM-001` using `tests/forms/hr-v0-evaluation-batch-a-receiving-template.csv`. Item-specific procedures remain mandatory. Receipt does not release a component for machine use.

R146 replaces the anonymous “duplicate this row” execution ambiguity with `HR-V0-EVAL-BATCH-A-RCV-P0.1`: 21 deterministic unit IDs, twelve receiving steps per unit, seven evidence placeholders per unit and one quarantine label per unit. The original form remains historical/generic; the current execution scaffold is `tests/forms/hr-v0-evaluation-batch-a-unit-receiving-template-p0.1.csv`. Every record remains `NOT AUTHORIZED`, `NOT ORDERED`, `NOT RECEIVED` and `NOT EXECUTED`.

R147 advances `BOM-063` from `selection_required` to `exact_candidate_hold` for Eaton `P006-006`. Current MEAN WELL evidence identifies the GST280A12-C6P Class-I C14 inlet, 3 A typical input and 95 A cold-start inrush at 115 VAC; current Eaton evidence identifies the held NEMA 5-15P-to-C13 10 A / 125 VAC / 18 AWG / 6 ft UL/cUL cord candidate. Site, branch, code, received identity, PE/isolation, fit, routing, inrush, thermal and qualified-review evidence remain open; no purchase or connection is released.

## Current manufacturer-page contradictions

The 2026-08-07 primary-source recheck found two reasons the receiving boundary cannot be skipped:

- R122 advances `BOM-070` to an exact held StarTech.com `USB2AC50CM` candidate using the current official product page and generated datasheet. The catalog record closes connector/length/shield/OD selection only. Received U2D2 Type-C revision, Pi/case fit, bend/retention, enumeration, waveform/error, common-mode, no-backfeed, EMC, thermal, HIL and qualified application evidence remain open.
- R123 corrects the insufficient single-perforated-rail branch by holding two `1207648` unperforated rails, one `3240189` duct and six `3022218` DR1-DR3 brackets. `BOM-059`, DR4 end retention, final lengths/kerf, tools, holes, fasteners, bonding and physical proof remain `SELECTION REQUIRED` or open.
- The current `XM540-W270-T` and `XM430-W350-T` pages identify SKUs `902-0137-000` and `902-0124-000`, but their package-content tables name `-R` actuators. The purchase record must state the required TTL `-T` model, prohibit unreviewed substitution, and quarantine any unit whose label/model readback does not match.

These conflicts do not invalidate evaluation of the candidate SKU. They prohibit treating a store title or packing list as received configuration evidence.

## What remains before EG-003 can close

1. Expand grouped assemblies into individual orderable lines, especially the watchdog input/feedback circuits and Molex harness.
2. Execute received/application evidence for the held Pi 5, US supply, enclosure, carrier, retention and USB-cable candidates; select remaining panel hardware, conductors, DYNAMIXEL-side harness, labels, cord sets, storage, anchoring, fasteners, guard, receiver and termination hardware; execute the held H1 received-evidence route before wiring.
3. Resolve the XM540 4.4 A stall screen versus the JST EH 3 A series basis before releasing the actuator harness.
4. Select protection only after measured source fault/current/regeneration, cable, connector, inrush, ambient, bundling and clearing evidence closes.
5. Complete supplier DFM and first articles before ordering custom plates or either PCB.
6. Record received markings, lot/revision, package contents, measured mass and item-specific acceptance evidence.
7. Issue a signed hierarchical release BOM tied to an accepted Git commit and the released CAD/ECAD/harness configuration.
8. Execute `INSPECT-MECH-010` and obtain qualified disposition of the six exact frame-joint candidates before accepting the T-slot frame assembly.

`EG-003` therefore advances from **open** to **partial**. The package still does not contain a complete orderable machine BOM.
