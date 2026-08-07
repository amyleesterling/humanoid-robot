# Sol R12 findings rechecked against R35

> **PRELIMINARY - NOT APPROVED FOR FABRICATION OR ENERGIZATION**

Date: 2026-08-06

This is a project-owned reconciliation, not a new independent Sol review. Sol's R12 totals remain **18 BLOCKER, 30 MAJOR and 8 MINOR** against the historical configuration.

## R35 correction

R35 issues PCB-P0.5 while retaining Electrical V3-P1.1. It reroutes every former 0.10 mm feature at a minimum 0.1524 mm (6 mil), records a proposed OSH Park U.S. two-layer fabrication envelope, and machine-checks minimum trace width, via drill and annular ring against the supplier's current published rules. The board now has 201 segments, 56 vias and three filled zones. Native KiCad DRC remains zero violations with zero routed unconnected pads. No Gerber, drill or placement output was generated.

## What R35 narrows

- Sol B-004 is narrowed because the watchdog PCB no longer depends on an undocumented fine-feature exception; a current supplier process and exact board minima are now recorded.
- Sol B-016 and M-022 remain narrowed by the existing exact DBQ footprint, test access, separate SUB copper, route-connectivity checks and now a documented 6 mil manufacturing envelope.
- The open `0.10 mm capability` item is removed. Supplier acceptance of the final archive and all fabrication-release reviews remain open.

## What remains open

- OSH Park is proposed, not selected for ordering, and has not accepted a final controlled archive.
- Paste/mask review, final CAM review, assembly process, physical test-point access and received-board inspection remain unexecuted.
- Protection, conductor/connector limits, source current sharing, contactor duty, thermal behavior, COM slew, brownout, EMC/surge, fault injection and HIL remain unresolved.
- Native ERC/DRC and source checks do not establish functional-safety performance, stopping time, PLr/SIL suitability or permission to energize.
- HR-V0 still lacks a released mechanical assembly, closed mass/COM/inertia evidence, validated stops/guards/restraint, received-part evidence and qualified review.
- All applicable energization gates remain unresolved.

## Disposition

Sol's central verdict remains correct: HR-V0 is not yet a buildable machine and energization remains prohibited. PCB-P0.5 is suitable only for independent layout and fabrication-envelope review. It is not a fabrication or energization release.
