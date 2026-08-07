# Sol R12 Post-R63 Status Reconciliation

> **PRELIMINARY - NOT APPROVED FOR FABRICATION OR ENERGIZATION**

Date: 2026-08-07

Independent review being reconciled: Sol R12, 18 BLOCKER / 30 MAJOR / 8 MINOR

Project response: R63 / Electrical `V3-P1.7` / `HR-V0-CP-P0.3` / `HR-V0-SD-P0.1`

## Review-count disposition

The supplied Sol summary is the same independent R12 review commissioned in parallel with Fable R11. It is not counted as a new independent review or a new set of 56 findings. R63 is a project-owned correction and status pass against that existing review.

## Statements now stale

- Native KiCad source is no longer absent from the authoritative repository. The repository contains the reviewed V2.1 source and the separate current V3-P1.7 correction candidate.
- Firmware is no longer only a folder plan. Source, fail-closed models, reproducible builds, compiled-C differential evidence and source manifests exist. Target flash, HIL and physical validation remain open.
- A mechanical source package now exists, including controlled ROBOTIS vendor interfaces and an exact-coordinate HR-V0 arm candidate. It is still not a released build because received fit, material/FAI, hard stop, cable/guard, proof and qualified review are open.
- The current V3 watchdog permit is not a single downstream contact. One ordinary watchdog contact is in each SR1 input return, followed by monitored RESET and a distinct ARM stage. The watchdog path still receives zero functional-safety credit.
- The control-panel package is no longer blank architecture. P0.3 has 24 panel-BOM rows, 20 bounded backplate allocations, five door rows, 66 synchronized wire endpoints, six unreleased cable-entry zones and unexecuted receiving records. No hole, conductor or assembly is released.

## Statements that remain correct

- HR-V0 is not ready to fabricate or energize.
- HR-30W walking feasibility is not demonstrated; mass/inertia, continuous leg torque, thermal, dynamic restraint, sensing, battery and power-loss closure remain open.
- No PLr/SIL claim or functional-safety approval exists. Qualified allocation, common-cause analysis, stopping-time/distance validation and physical fault testing remain required.
- Fuse values, conductor sizing, prospective fault current, DC contactor application, grounding/bonding, enclosure integration, harness construction, battery/charger architecture and physical test evidence remain unresolved.
- No requirement has approved executed verification evidence sufficient to release fabrication or energization.

## R63 correction

- Froze Phoenix Contact `D-ST 4`, item `3030420`, only as the candidate open-side end cover for the two proposed `PT 4-HESI (5X20)` item `3211861` holders.
- Issued Electrical V3-P1.7 and synchronized native KiCad source, schedules, BOM, netlist and exports. Counts remain 13 pages, 76 component blocks, 295 terminals, 64 named connected plus 36 unconnected nets, 259 wire labels, 63 unresolved rows and 24 `TBD-*` terminals. ERC remains 0 errors / 0 warnings.
- Issued `HR-V0-CP-P0.3` with 24 panel-BOM rows. The nominal holder/end-cover body width is 14.6 mm inside a 25 mm planning envelope, but received compatibility, access, grouping and thermal evidence remain open.
- Expanded the system BOM to 73 groups: 16 evaluation candidates, 20 exact candidates on hold, three grouped-component holds, 29 selection-required groups, four exclusions and one integrated item.
- Issued `HR-V0-SD-P0.1` and 15 unexecuted application/receiving records. Blue Sea `6004200` is screening-only: its published rating assumes 4/0 AWG, its instructions require loads off before switching, and no project lockout, fault/load-break, conductor/lug, placement or jurisdiction acceptance exists.

## Remaining blockers most relevant to first energization

- exact `SD1`, `JC1`, all six fuse links, conductors, terminations, cable entries and bonding hardware;
- measured source current-limit/fault envelope and released protection/clearing analysis;
- received panel depth, bend/service space, duct fill, heat, PE/bonding and enclosure-system proof;
- K1/K2 written DC application disposition and loaded interruption/regeneration tests;
- received S0/S1/S2/H1 and all remaining terminal maps;
- fabricated/inspected PCB and harness test articles, no-backfeed tests, watchdog HIL and controlled fault injection;
- qualified electrical, mechanical, enclosure, human-factors and functional-safety review;
- separate written fabrication and energization authorization after every applicable gate has executed evidence.

R63 closes no energization gate. The package remains **PRELIMINARY - NOT APPROVED FOR FABRICATION OR ENERGIZATION**.
