# Independent review request: HR-V0 watchdog supply-gate correction

**PRELIMINARY - NOT APPROVED FOR FABRICATION OR ENERGIZATION**

Review target: `HR-V0-WD-SUPPLY-P0.1` / Electrical V3-P1.13 / HR-V0-CP-P0.5. This is an accuracy and completeness review, not a request for approval to build, wire, test, or energize.

## Why this review exists

R86 found a credible KWD A1/21-to-14 injection path because ordinary watchdog contacts were inside the two SR1 E-stop returns. R87 moves S0 directly onto both SR1 input channels and series-gates only `SR1:A1` with KWD1/KWD2. The review must decide whether the proposed correction is electrically sound, whether its recovery behavior is acceptable, and what additional faults or evidence are missing.

## Controlled sources

- `electrical/kicad/project-button-v3/` including all 13 native sheets, schedules, ERC and exports;
- `electrical/panel/hr-v0-control-panel-p0.5/` including the 66 endpoint schedule and 12 route controls;
- `safety/hr-v0-watchdog-supply-gate-p0.1/` including the interactive guide, 32-case FMEA and 28 unexecuted cases;
- `docs/hr-v0-watchdog-supply-gate-p0.1.md`;
- `safety/hr-v0-safety-function-allocation.csv` and `docs/hr-v0-functional-safety-allocation-p0.1.md`;
- `tests/procedures/procedure-registry.csv`, especially `ANALYSIS-SAFE-002`.

## Reproduce

```powershell
python tools/check_hr_v0_electrical_v3.py
python tools/check_hr_v0_control_panel.py
python tools/check_hr_v0_watchdog_supply_gate.py
python tools/check_hr_v0_safety_allocation.py
```

Also open every native KiCad sheet and run KiCad 10 ERC independently. Do not rely on the SVG/PDF alone.

## Questions requiring explicit findings

1. Does P1.13 actually eliminate every source-encoded path from KWD A1/21/coil/feedback faults to `SR1:S12` or `SR1:S22`?
2. Can any single or relevant common-cause fault in the gated A1 supply, shared rails, reset chain, ARM/EDM chain, PCB, terminals, routing, contamination, firmware, or recovery sequence impair `SF-01` or `SF-03`?
3. Is series interruption of PNOZ s4 A1 by two Phoenix 2967060 ordinary-relay contacts suitable for the exact electronic load, inrush, switching frequency, brownout and required endurance? What manufacturer evidence is required?
4. Does heartbeat loss and restoration reliably force physical RESET, then separate ARM, then fresh trajectory for every relevant state?
5. What protected-wiring, branch-protection, fault-current, terminal, ferrule, barrier, duct, creepage/clearance, EMC and environment controls are required?
6. Are all 32 FMEA cases and 28 fault cases complete, feasible and safely testable with loads disconnected?
7. What SRS, PLr/SIL, category, CCF, stopping-time and validation inputs remain necessary under the applicable U.S./Boston requirements and controlled standards?

Report BLOCKER / MAJOR / MINOR findings with exact file, sheet, reference, terminal and net. Cite current primary manufacturer documentation by revision/date. Distinguish source topology, proposed physical controls, executed physical evidence, and qualified acceptance. Do not infer a fault exclusion, safety credit, fabrication release, or permission to energize.

**PRELIMINARY - NOT APPROVED FOR FABRICATION OR ENERGIZATION**
