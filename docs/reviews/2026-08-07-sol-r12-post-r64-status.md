# Sol R12 Post-R64 Status Reconciliation

> **PRELIMINARY - NOT APPROVED FOR FABRICATION OR ENERGIZATION**

Date: 2026-08-07

Independent review being reconciled: Sol R12, 18 BLOCKER / 30 MAJOR / 8 MINOR

Project response: R64 / Electrical `V3-P1.8` / `HR-V0-CP-P0.4` / `HR-V0-SD-P0.2`

## Review-count disposition

The supplied Sol summary is the same independent R12 review commissioned in parallel with Fable R11. It is not counted as a new independent review or a new set of 56 findings. R64 is a project-owned correction and status pass against that existing review.

## Statements now stale or narrowed

- Native KiCad source, source manifests, clean ERC/DRC evidence, source code, deterministic builds, controlled CAD and evidence templates now exist in the authoritative repository. Their existence does not make the machine buildable or energizable.
- The current V3 watchdog path uses two ordinary contacts in the two SR1 input returns, followed by monitored RESET and a distinct ARM stage. It receives zero functional-safety credit and still requires physical fault/CCF validation.
- `SD1` is no longer an unnamed selection. Active Littelfuse order code `75920-01` is the exact SPST high-side catalog candidate. That closes only catalog identity and topology; it does not close the installed application.
- The control-panel package now contains 25 BOM rows, 20 backplate allocations, five door rows, one fail-closed sidewall option, 66 synchronized V3 wire endpoints, six unreleased cable-entry zones and unexecuted evidence forms.

## Statements that remain correct

- HR-V0 is not ready to fabricate or energize.
- HR-30W walking feasibility is not demonstrated; mass/inertia, continuous leg torque, thermal, dynamic restraint, sensing, battery and power-loss closure remain open.
- No PLr/SIL claim or functional-safety approval exists. Qualified allocation, common-cause analysis, stopping-time/distance validation and physical fault testing remain required.
- Fuse values, conductor sizing, prospective fault current, DC contactor application, grounding/bonding, enclosure integration, harness construction, battery/charger architecture and physical test evidence remain unresolved.
- No requirement has approved executed verification evidence sufficient to release fabrication or energization.

## R64 correction

- Rejected ABB `OTDCP25SA11M` for the present positive-only/shared-return topology because the official `OTDCP_11_` diagram switches negative and positive with both poles. Project Button did not infer use of one pole.
- Retained Blue Sea Systems `6004200` as historical screening only because its published rating depends on 4/0 AWG and its instructions require loads off before switching; a locking key did not close the project energy-control route.
- Froze active Littelfuse `75920-01` as the exact `SD1` catalog candidate. Current primary sources establish SPST circuitry, high-side use, 3/8-24 studs, through-panel mounting, On/Off markings, a yellow knob and an OFF-position padlock feature.
- Retained `TBD-IN` and `TBD-OUT`. The identical studs were not assigned source/load without manufacturer evidence.
- Issued Electrical `V3-P1.8` with synchronized native source, schedules, BOM, netlist and exports. Counts remain 13 pages, 76 component blocks, 295 terminals, 64 named connected plus 36 unconnected nets, 259 wire labels, 63 unresolved rows and 24 `TBD-*` terminals. ERC remains 0 errors / 0 warnings.
- Issued `HR-V0-CP-P0.4` with 25 panel-BOM rows and a right-side-wall option only. No coordinate, cutout, conductor route, rear guard or padlock procedure is released.
- Issued `HR-V0-SD-P0.2` and protection P0.4. The current Littelfuse datasheet's high current-cycle values depend on 4/0 cable and are not Project Button conductor, fault-duty or load-break proof.
- The system BOM remains 73 groups: 16 evaluation candidates, 21 exact candidates on hold, three grouped-component holds, 28 selection-required groups, four exclusions and one integrated item.

## Remaining blockers most relevant to first energization

- execute all 15 `SD1` records: received geometry/identity, source-load disposition, conductor/lug stack, calibrated torque, touch protection, fault/load-break duty, temperature rise, padlock/zero-energy method, legend/human factors and qualified Boston application review;
- exact `JC1`, all six fuse links, conductors, terminations, cable entries and bonding hardware;
- measured source current-limit/fault envelope and released protection/clearing analysis;
- received panel depth, bend/service space, duct fill, heat, PE/bonding and enclosure-system proof;
- K1/K2 written DC application disposition and loaded interruption/regeneration tests;
- received S0/S1/S2/H1 and all remaining terminal maps;
- fabricated/inspected PCB and harness test articles, no-backfeed tests, watchdog HIL and controlled fault injection;
- qualified electrical, mechanical, enclosure, human-factors and functional-safety review;
- separate written fabrication and energization authorization after every applicable gate has executed evidence.

R64 closes no energization gate. The package remains **PRELIMINARY - NOT APPROVED FOR FABRICATION OR ENERGIZATION**.
