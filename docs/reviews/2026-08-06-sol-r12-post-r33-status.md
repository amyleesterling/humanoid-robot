# Sol R12 findings rechecked against R33

> **PRELIMINARY - NOT APPROVED FOR FABRICATION OR ENERGIZATION**

Date: 2026-08-06

This is a project-owned reconciliation, not a new independent Sol review. Sol's R12 totals remain **18 BLOCKER, 30 MAJOR and 8 MINOR** against the historical configuration. The resupplied summary is the same R12 review and is not counted again.

## R33 correction

R33 advances the watchdog board from the corrected PCB-P0.2 placement into PCB-P0.3, a controlled routed-copper candidate. Native KiCad 10.0.5 DRC now reports zero violations and zero routed unconnected pads. An independent checker rebuilds connectivity and proves 160 segments, 45 vias, one filled `SAFETY_0V` zone, complete connectivity for every multi-pad modeled net, isolation of 18 intentional singleton nets and no copper contact at 89 no-net footprint pads. Top and bottom renders were inspected. No Gerber or drill output exists.

## What R33 narrows

- Sol B-001's missing-native-source concern remains stale for this branch: native schematic and PCB source are present and manifest-controlled.
- Sol B-004's unwireable-electrical concern is narrowed for the watchdog PCB subset by an exact board boundary, exact pad/net mapping and DRC-clean routed candidate.
- Sol B-016's architecture-only sensing concern is narrowed by an exact ISO1212 receiver circuit, frozen candidate passives, corrected DBQ land pattern and routed implementation candidate.
- Sol M-022's evidence-infrastructure concern is narrowed by native DRC, independent connectivity reconstruction, route-length evidence, source hashes and reproducible top/bottom renders.

## What remains open

- PCB-P0.3 lacks an exact fabricator and stack-up, confirmed 0.10 mm capability, test points, reviewed SUB copper, fabrication outputs, enclosure/harness definition and independent layout review.
- Zero DRC violations do not validate current capacity, protection coordination, temperature, COM slew, EMC/surge, brownout behavior, land-pattern orientation or physical assembly.
- `UFB1` field and logic returns share `SAFETY_0V`; no isolation or safety credit is claimed.
- The electrical system still has unresolved source-current sharing, branch protection, conductor/connector limits, contactor application, terminals and physical device evidence.
- No assembled-board, continuity, current-limited bring-up, waveform, thermal, EMC, fault-injection or HIL evidence exists.
- HR-V0 mechanics, moving mass/COM, stops, guarding, restraint, functional-safety allocation and qualified review remain unclosed.
- All energization gates remain unresolved.

## Disposition

Sol's central verdict remains correct: HR-V0 is not yet a buildable machine and energization remains prohibited. PCB-P0.3 is suitable only for independent routed-layout review. It is not a fabrication or energization release.
