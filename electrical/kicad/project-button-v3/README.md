# Project Button HR-V0 Electrical V3

**PRELIMINARY - NOT APPROVED FOR FABRICATION OR ENERGIZATION**

This is a generated, connected native KiCad candidate derived from `tools/generate_hr_v0_electrical_v3.py`. It does not supersede the reviewed Electrical V2.1 package until exact selections, application reviews, calculations, physical tests and qualified review close.

## Pages

1. `01_external_sources.kicad_sch` — External listed sources and DC boundaries
2. `02_estop_eligibility.kicad_sch` — Dual-channel E-stop and RESET eligibility
3. `03_arm_watchdog_eligibility.kicad_sch` — Distinct ARM and watchdog eligibility
4. `04_contactor_edm.kicad_sch` — Contactor coils, mirror contacts and EDM
5. `05_actuator_interruption.kicad_sch` — Redundant actuator-power interruption
6. `06_branches_and_injection.kicad_sch` — Protected actuator branches and VDD-isolating injection
7. `07_watchdog_control.kicad_sch` — Independent watchdog power, controller and drivers
8. `08_compute_and_control_terminals.kicad_sch` — Compute, debug and control terminals
9. `09_actuator_interfaces.kicad_sch` — U2D2, actuator ports and bonding boundary

## Material corrections relative to V2.1

- Separate SR1 RESET eligibility and SRA1 ARM/EDM stages.
- Two separately driven watchdog relay contacts interrupt the two SRA1 input channels.
- Heartbeat restoration cannot restore contactors; SRA1 requires a new monitored ARM action.
- External Mean Well adapters replace project-built mains wiring.
- The GST280A12-C6P source bond is explicit; project star point SP1 is DNP/prohibited.
- Three poles per candidate contactor are represented in series, pending Schneider application confirmation.
- U2D2 VDD is omitted and protected power is injected by three custom modules; those modules remain a design gate.

## Validate

Run `python tools/generate_hr_v0_electrical_v3.py --validate` with KiCad 10 installed. Generated ERC proves only modeled connectivity/annotation. Every `TBD-*`, `SELECTION REQUIRED`, `DESIGN REQUIRED`, and application-confirmation item remains a release blocker.

No drawing in this directory authorizes ordering, wiring, fabrication or energization.
