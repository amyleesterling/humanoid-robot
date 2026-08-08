# Independent review request - HR-V0 watchdog CCF P0.1

Review `HR-V0-WD-CCF-P0.1` for accuracy, completeness and functional-safety boundary discipline. This is a criticism request, not an authorization.

## Required review

1. Reproduce all 18 exact paths from Electrical V3-P1.12 net, connector and wire schedules.
2. Confirm KWD1/KWD2 terminal mapping from the current Phoenix Contact item 2967060 primary document.
3. Independently analyze shorts from each KWD A1/21 terminal to 11/14/12/22/24 and state the consequence for `SR1:S12` or `SR1:S22` without accepting an undocumented fault exclusion.
4. Determine whether the current placement of ordinary relay contacts inside the candidate `SF-01` input paths can meet the selected architecture after negative contribution, diagnostic coverage and CCF are included.
5. Challenge all 32 FMEA rows and identify omitted opens, shorts, cross-channel, supply, contamination, service, feedback, debug and configuration failures.
6. Challenge all 12 common-cause groups and 16 separation controls against the actual PCB-P0.5 and nominal HR-V0-CP-P0.4 allocation.
7. Confirm that feedback and debug paths have no RESET, ARM, coil or motion authority in firmware, ECAD and as-built plans.
8. Review all 28 cases for safe fixture design, instrumentation, test order, numerical acceptance limits, stop conditions and cases that should remain analysis-only.
9. Decide whether redesign is required before physical fault injection, and provide an exact native-ECAD correction proposal if so.
10. Preserve zero safety credit for DF-01 and do not assign a PLr, category, PL or SIL without the complete qualified allocation record.

## Files

- `docs/hr-v0-watchdog-common-cause-p0.1.md`
- `safety/hr-v0-watchdog-ccf-p0.1/`
- `safety/hr-v0-watchdog-boundary-fmea.csv`
- `safety/hr-v0-safety-function-allocation.csv`
- `tests/forms/hr-v0-watchdog-fault-injection-template.csv`
- `tests/forms/hr-v0-watchdog-separation-inspection-template.csv`
- `electrical/kicad/project-button-v3/`
- `electrical/panel/hr-v0-control-panel-p0.4/`
- `tools/generate_hr_v0_watchdog_ccf.py`
- `tools/check_hr_v0_watchdog_ccf.py`

Return `BLOCKER / MAJOR / MINOR` findings with exact sheet, reference, terminal, net, PCB/panel boundary and source revision. Separate nominal-connectivity evidence from physical validation and functional-safety approval. Do not mark the design approved for fabrication, wiring, connection, fault injection or energization.
