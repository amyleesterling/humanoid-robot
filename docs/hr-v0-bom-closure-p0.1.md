# HR-V0 BOM closure and evaluation boundary P0.1

Status: **PRELIMINARY—NOT A PROCUREMENT, FABRICATION, OR ENERGIZATION RELEASE**

Control date: 2026-08-07

## Result

The system BOM now contains 82 configuration groups: 17 evaluation candidates, 33 exact candidates on hold, three grouped-component holds, 24 selection-required groups, four exclusions and one integrated item. R46 exposed previously invisible assembly assumptions; later controlled passes add exact source, enclosure, compute-carrier and retention candidates. R122 advances only the Pi-to-U2D2 catalog cable to held StarTech.com `USB2AC50CM`. None of these changes is a complete procurement or application release.

R61 advances `BOM-041` from `selection_required` to `exact_candidate_hold` for IDEC `HW1P-1FQD-A-24V`. This removes the obsolete `SAFE ELIGIBLE` value and synchronizes the system BOM with Electrical V3-P1.5 and `HR-V0-CP-P0.1`. It is not added to Evaluation Batch A and is not procurement- or wiring-released; `HR-V0-H1-RCV-P0.1` remains unexecuted.

R62 advances `BOM-019` to an exact-candidate hold for two Phoenix `PT 4-HESI (5X20)` item `3211861` holders and adds `BOM-072` for the two still-unresolved fuse links. R63 adds exact-candidate-hold `BOM-073` for one Phoenix `D-ST 4` item `3030420` end cover. R64 advances `BOM-042` to exact-candidate hold for Littelfuse `75920-01`; conductor/lug, source-fault, load-break, touch-protection, cutout, zero-energy/padlock, human-factors, Boston application and physical tests remain open. Those historical counts have since been superseded by the current 82-group closure totals above. Both FSR fuse links, received accessory compatibility/grouping, all protection calculations and all physical evidence remain open; manufacturer maximum ratings are not project fuse or conductor ratings.

R66 reconciles custom mechanical group `BOM-027` to the P0.5 geometry: three `MV0-C01`, one `MV0-C04`, and one `MV0-C05` candidate. The group remains `selection_required` in the closure register because supplier/process/quote, received material, separate first article per geometry, fit, T-slot proof, physical proof, and qualified release are not selected or executed. This quantity correction does not change the closure-class totals or authorize fabrication.

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

## Current manufacturer-page contradictions

The 2026-08-07 primary-source recheck found two reasons the receiving boundary cannot be skipped:

- R122 advances `BOM-070` to an exact held StarTech.com `USB2AC50CM` candidate using the current official product page and generated datasheet. The catalog record closes connector/length/shield/OD selection only. Received U2D2 Type-C revision, Pi/case fit, bend/retention, enumeration, waveform/error, common-mode, no-backfeed, EMC, thermal, HIL and qualified application evidence remain open.
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
