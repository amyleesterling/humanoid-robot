# Sol R12 Findings Rechecked against R41

> **PRELIMINARY—NOT APPROVED FOR FABRICATION OR ENERGIZATION**

Date: 2026-08-07

System baseline: `HR-30-SYS-R0.2`

Correction baseline: Electrical `V3-P1.3`

This is a project-owned status reconciliation, not a new independent review. Sol R12 remains the independent assessment of the pre-correction `ee276af...` baseline: 18 BLOCKER, 30 MAJOR and 8 MINOR findings; 62 of 62 then-audited requirements draft; 106 unresolved Electrical V2.1 selections; and no executed, approved verification evidence. The newly supplied summary is the same R12 review and is not double-counted.

## R41 correction

R41 narrows the `EG-013` K1/K2 evidence defect without closing it:

- rechecked Schneider `LC1D25BD` product data dated 2017-09-13, Schneider FAQ `FA126437` modified 2026-05-12, and Schneider TeSys Catalog 2026 `MKTED210011EN`;
- recorded the current catalog's 32 A / 24 V LC1D25 row for one, two or three poles in series;
- retained the exact K1/K2 three-poles-in-series topology and integrated `21-22` mirror-contact EDM mapping;
- corrected the BOM so the product-name 25 A value is not presented as an HR-V0 DC rating;
- exposed the catalog's lower-current/critical-current warning as material because the HR-V0 summed-stall screen is 11.1 A, below the published 32 A row;
- added an exact manufacturer-query and measured-test closure route; and
- issued synchronized Electrical `V3-P1.3` native source, schedules, BOM, netlist, ERC, PDF and SVG artifacts.

## What remains open

- The actual 12 V electronic/regenerative load has no measured break-current, bus-transient, capacitance or equivalent time-constant envelope.
- Schneider has not issued an identifiable written disposition for this application or its lower-current critical-current condition.
- Prospective fault current, source limiting, fuses, conductors, terminals and interrupting/clearing coordination remain unresolved.
- No K1/K2 devices have been received, inspected, wired or tested.
- No loaded interruption, welded-contact injection, rail-decay, residual-motion or total stopping-time test exists.
- No PLr/SIL allocation or qualified electrical/functional-safety approval exists.
- Sol's mechanical, CAD, mass/inertia, power-loss, continuous-torque, protection, grounding, battery, bus, real-time, restraint, fabrication and walking blockers remain open.
- Through E2 the gate result remains 0 closed, 15 partial and 6 open. `EG-013` remains partial.

## Disposition

Sol's central verdict is unchanged: HR-V0 is not ready for fabrication or energization, and HR-30W walking is not demonstrated. R41 replaces a vague DC-duty caveat with current primary-source evidence and a precise closure route. It does not select or approve K1/K2 and grants no permission to procure, fabricate, wire or energize.
