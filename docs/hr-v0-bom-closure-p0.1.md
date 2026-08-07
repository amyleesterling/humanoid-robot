# HR-V0 BOM closure and evaluation boundary P0.1

Status: **PRELIMINARY—NOT A PROCUREMENT, FABRICATION, OR ENERGIZATION RELEASE**

Control date: 2026-08-07

## Result

The system BOM now contains 71 configuration groups. R46 added thirteen groups that were previously invisible assembly assumptions: the control enclosure, panel hardware, stationary wire, actuator signal harness, labels, AC cords, boot media, bench anchors, project-added structural fasteners, cable-entry/strain-relief hardware, guard access hardware, wire terminations, and the Raspberry Pi-to-U2D2 USB cable. R49 corrects `BOM-071` to twelve exact `75-3422` frame-joint bolt assemblies and binds `BOM-024`/`BOM-025` to the non-overlapping `40-4040` cut schedule and six `40-4332` brackets under `HR-V0-FRAME-P0.2`; none is application-released.

R61 advances `BOM-041` from `selection_required` to `exact_candidate_hold` for IDEC `HW1P-1FQD-A-24V`. This removes the obsolete `SAFE ELIGIBLE` value and synchronizes the system BOM with Electrical V3-P1.5 and `HR-V0-CP-P0.1`. It is not added to Evaluation Batch A and is not procurement- or wiring-released; `HR-V0-H1-RCV-P0.1` remains unexecuted.

The machine-readable closure register is `bom/hr-v0-bom-closure.csv`. Every `bom/bom.csv` item has exactly one classification:

- `evaluation_candidate`: exact candidate order code and evaluation quantity are frozen, but program-owner approval is required before purchase and application suitability remains open;
- `exact_candidate_hold`: an exact candidate exists but is not included in the receiving batch;
- `grouped_components_hold`: the system row contains several parts and must be expanded before an orderable release;
- `selection_required`: order code, construction, quantity detail, or application evidence remains unresolved;
- `excluded_from_hr_v0_candidate`: historical, DNP, or superseded material; or
- `integrated_no_separate_purchase`: evidence is controlled through its parent item.

No row is classified as production-selected or procurement-released.

## Evaluation Batch A

`bom/hr-v0-evaluation-batch-a.csv` identifies sixteen exact candidate lines whose receipt is needed to execute identity, terminal, current, thermal, source, restart and fault tests. R53 removes the actuator body-frame purchase from this batch because S101, S102, or a custom-frame route remains an architecture selection. The remaining batch includes the three actuators, U2D2, safety relays, contactors, E-stop, watchdog controller/relays, output/gripper frames, RESET/ARM operators and both external DC sources.

The batch is not a shopping instruction. Every line states:

- `PROGRAM OWNER APPROVAL REQUIRED`;
- `EVALUATION ONLY`;
- current primary manufacturer source and document/access date; and
- required receiving and test routes.

After separately approving any purchase, quarantine each received unit and execute `INSPECT-BOM-001` using `tests/forms/hr-v0-evaluation-batch-a-receiving-template.csv`. Item-specific procedures remain mandatory. Receipt does not release a component for machine use.

## Current manufacturer-page contradictions

The 2026-08-07 primary-source recheck found two reasons the receiving boundary cannot be skipped:

- ROBOTIS' current U2D2 page identifies SKU `902-0132-000` and says the product was upgraded to USB-C, while the same page still lists a Micro-USB cable and Micro-USB connector in its package/table text. Record the actual received connector revision and retained cable; `BOM-070` remains `SELECTION REQUIRED`.
- The current `XM540-W270-T` and `XM430-W350-T` pages identify SKUs `902-0137-000` and `902-0124-000`, but their package-content tables name `-R` actuators. The purchase record must state the required TTL `-T` model, prohibit unreviewed substitution, and quarantine any unit whose label/model readback does not match.

These conflicts do not invalidate evaluation of the candidate SKU. They prohibit treating a store title or packing list as received configuration evidence.

## What remains before EG-003 can close

1. Expand grouped assemblies into individual orderable lines, especially the watchdog input/feedback circuits and Molex harness.
2. Select exact Pi 5/US supply SKUs, remaining enclosure/panel application hardware, conductors, cables, labels, cord sets, storage, anchoring, fasteners, guard, receiver and termination hardware; execute the held H1 received-evidence route before wiring.
3. Resolve the XM540 4.4 A stall screen versus the JST EH 3 A series basis before releasing the actuator harness.
4. Select protection only after measured source fault/current/regeneration, cable, connector, inrush, ambient, bundling and clearing evidence closes.
5. Complete supplier DFM and first articles before ordering custom plates or either PCB.
6. Record received markings, lot/revision, package contents, measured mass and item-specific acceptance evidence.
7. Issue a signed hierarchical release BOM tied to an accepted Git commit and the released CAD/ECAD/harness configuration.
8. Execute `INSPECT-MECH-010` and obtain qualified disposition of the six exact frame-joint candidates before accepting the T-slot frame assembly.

`EG-003` therefore advances from **open** to **partial**. The package still does not contain a complete orderable machine BOM.
