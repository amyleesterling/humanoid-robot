# Sol R12 findings rechecked against R34

> **PRELIMINARY - NOT APPROVED FOR FABRICATION OR ENERGIZATION**

Date: 2026-08-06

This is a project-owned reconciliation, not a new independent Sol review. Sol's R12 totals remain **18 BLOCKER, 30 MAJOR and 8 MINOR** against the historical configuration. The review summary resupplied on 2026-08-06 is the same R12 analysis and is not counted again.

## R34 correction

R34 issues Electrical V3-P1.1 and PCB-P0.4. It adds 16 exact schematic test-point records, a proposed Harwin `S1751-46R` footprint based on drawing issue 10, top-side access to the controlled diagnostic nets, and separate 2 mm x 2 mm floating B.Cu areas for `UFB1.SUB1` and `SUB2` per TI `SLLSEY7G`. The board now has 42 schematic references, 200 segments, 56 vias and three filled zones. Native KiCad DRC remains zero violations with zero routed unconnected pads. The independent checker verifies test-point identity, net assignment, land dimensions, SUB isolation, route connectivity and absence of fabrication outputs.

## What R34 narrows

- Sol B-004 is narrowed for the watchdog-board subset by explicit probe points on the power, heartbeat, dual shutdown, feedback and programming nets.
- Sol B-016 is narrowed by implementing the two separate manufacturer-recommended SUB thermal areas without connecting them to ground or each other.
- Sol M-022 is narrowed by exact machine checks for test-point land dimensions, net identity, SUB copper dimensions and saved zone fill.

## What remains open

- No exact fabricator, stack-up, copper thickness or confirmed 0.10 mm manufacturing capability is released.
- Test-point fit and access have not been checked on an assembled board or inside an enclosure.
- Protection, conductor/connector limits, source current sharing, contactor duty, thermal behavior, COM slew, brownout, EMC/surge, fault injection and HIL remain unresolved.
- Native ERC/DRC and source checks do not establish functional-safety performance, stopping time, PLr/SIL suitability or permission to energize.
- HR-V0 still lacks a released mechanical assembly, closed mass/COM/inertia evidence, validated stops/guards/restraint, received-part evidence and qualified review.
- All applicable energization gates remain unresolved.

## Disposition

Sol's central verdict remains correct: HR-V0 is not yet a buildable machine and energization remains prohibited. PCB-P0.4 is suitable only for independent layout/test-access review. It is not a fabrication or energization release.
