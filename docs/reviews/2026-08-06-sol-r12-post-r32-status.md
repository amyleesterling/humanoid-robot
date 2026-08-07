# Sol R12 findings rechecked against R32

> **PRELIMINARY - NOT APPROVED FOR FABRICATION OR ENERGIZATION**

Date: 2026-08-06

This is a project-owned status reconciliation, not a new independent Sol review. Sol's R12 totals remain 18 BLOCKER, 30 MAJOR and 8 MINOR against the historical configuration. The resupplied analysis is not counted again.

## R32 correction

R32 found two implementation defects that were not visible in the R31 source-presence summary:

- `UFB1` used a 5.3 x 6.2 mm, 0.65 mm-pitch KiCad footprint even though TI identifies `ISO1212DBQ` as the 3.9 x 4.9 mm, 0.635 mm-pitch DBQ package;
- the P0.1 staging arrangement put the ISO1212 field-input passives on the logic side of the receiver.

PCB-P0.2 corrects both defects and adds machine-checked placement evidence. KiCad now reports zero non-routing DRC violations. The native board remains explicitly unrouted with zero tracks, zero zones and 68 unconnected pads.

## What R32 narrows

- Sol B-001's missing-native-source concern remains stale for the current branch: native schematics and PCB source are present.
- Sol B-004's unwireable-electrical finding is narrowed only for the watchdog board membership, exact board connectors, corrected UFB1 package candidate and controlled placement constraints.
- Sol B-016's input-electronics concern is narrowed by a pin-level receiver circuit, exact passives and a physically credible package/placement candidate.
- Sol M-022's evidence-infrastructure concern is narrowed by the reproducible JSON placement record and source-manifest coverage.

## What remains open

- the PCB has no routed copper, test points, SUB copper features, stack-up, fabrication outputs or independent layout review;
- `UFB1` field and logic returns share `SAFETY_0V`, so the isolation barrier is bypassed and receives no galvanic-isolation or safety credit;
- branch protection, prospective fault current, conductor and trace coordination remain unresolved;
- no assembled-board, COM-slew, brownout, thermal, EMC, fault-injection or HIL evidence exists;
- no released HR-V0 mechanics, mass/COM closure, functional-safety allocation, stopping-time evidence or qualified review exists;
- all energization gates remain unresolved.

## Disposition

Sol's central verdict remains correct: HR-V0 is not yet buildable and energization is prohibited. PCB-P0.2 is suitable for independent constrained-placement and routing-plan review only. It is not a fabrication release.
