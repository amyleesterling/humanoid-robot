# Sol R12 findings rechecked against R26

> **PRELIMINARY - NOT APPROVED FOR FABRICATION OR ENERGIZATION**

This is a project-owned reconciliation, not a new Sol review. Sol's R12 totals remain 18 BLOCKER, 30 MAJOR and 8 MINOR against the historical 62-requirement baseline. Sol has not independently reviewed R13-R26. The current package has 67 draft requirements and 74 registered verification procedures.

## What R26 changes

R26 addresses a bounded part of Sol's unresolved electrical-interface and human-factors findings:

- Electrical V3 advances from P0.4 to P0.5 without changing the restart/contact topology.
- `S1` RESET is frozen as IDEC `HW1B-M1F10-B`, black, flush, momentary, 1NO, screw terminal.
- `S2` ARM is frozen as IDEC `HW1B-M1F10-G`, green, flush, momentary, 1NO, screw terminal.
- Explicit `RESET` and `ARM` legends remain mandatory. Panel spacing/guarding, received bottom-view terminal numbering, continuity and qualified human-factors acceptance remain open.
- `PSU3` is narrowed to the official `Raspberry Pi 27W USB-C Power Supply US` regional model. Exact SKU/color remains `SELECTION REQUIRED` because the primary portal lists twelve family SKUs without mapping them to region/color; cable retention and received/site evidence remain open.
- `INSPECT-ELEC-003` and `tests/forms/hr-v0-control-device-receiving-template.csv` define the physical evidence route without inferred terminal numbers.

The generator rebuilt eleven native pages, 55 component blocks, 241 terminals, 87 native nets, 216 wire labels, synchronized schedules, PDF/SVG exports and the source manifest. KiCad 10.0.5 ERC is 0 errors / 0 warnings and exact-net validation passes. Visual QA of the changed A3 pages found no clipping; the smallest technical annotations remain zoomable in the vector exports.

## What remains open

- all 43 unresolved component/interface records and all 64 `TBD-*` terminal designations;
- exact E-stop physical contacts, panel construction and human-factors acceptance;
- fuses/holders, conductors, connectors, service disconnect, locking 24 V interface, watchdog supply/drivers/interface, terminals, enclosure and frame/shield treatment;
- PLr/SIL allocation, common-cause analysis, loaded contactor application evidence, compiled firmware, HIL, physical fault injection, stopping and protective-measure validation;
- all controlled build and energization approvals.

The gate checker still reports 21 applicable gates through E2: 0 closed, 14 partial and 7 open. R26 closes no gate.

## Verdict

Sol's headline conclusions remain correct. HR-V0 is not yet buildable or energizable, and HR-30W walking remains physically plausible but unproved. R26 removes one avoidable RESET/ARM same-color ambiguity and narrows a compute-source identity; it is not physical verification or functional-safety validation.

R26 does not approve procurement, fabrication, actuator connection, energization or operation around people.
