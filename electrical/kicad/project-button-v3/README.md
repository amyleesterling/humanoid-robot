# Project Button HR-V0 Electrical V3-P1.7

**PRELIMINARY - NOT APPROVED FOR FABRICATION OR ENERGIZATION**

This is a generated, connected native KiCad candidate derived from `tools/generate_hr_v0_electrical_v3.py`. It does not supersede the reviewed Electrical V2.1 package until exact selections, application reviews, calculations, physical tests and qualified review close.

## Pages

1. `01_external_sources.kicad_sch` — External listed sources and DC boundaries
2. `02_estop_eligibility.kicad_sch` — Dual-channel E-stop and RESET eligibility
3. `03_arm_watchdog_eligibility.kicad_sch` — Distinct ARM and watchdog eligibility
4. `04_contactor_edm.kicad_sch` — Contactor coils, mirror contacts and EDM
5. `05_actuator_interruption.kicad_sch` — Redundant actuator-power interruption
6. `06_branches_and_injection.kicad_sch` — Protected actuator branches and central DYNAMIXEL star injection
7. `07_watchdog_control.kicad_sch` — Independent watchdog power, controller and drivers
8. `08_watchdog_feedback_interface.kicad_sch` — Calculated dual-channel 24 V watchdog feedback
9. `09_compute_and_control_terminals.kicad_sch` — Compute, debug and control terminals
10. `10_actuator_interfaces.kicad_sch` — U2D2, actuator ports and bonding boundary
11. `11_watchdog_pcb_connectors.kicad_sch` — Watchdog PCB external connectors
12. `12_watchdog_pcb_test_access.kicad_sch` — Watchdog PCB test access

## Material corrections relative to V2.1

- Separate SR1 RESET eligibility and SRA1 ARM/EDM stages.
- Two separately driven watchdog relay contacts interrupt the two SR1 input returns so heartbeat loss forces the physical RESET stage to drop.
- Phoenix relay terminals are frozen from the official circuit diagram. Both 24 V NC diagnostics pass through the calculated ISO1212DBQ input network before the Pico GPIO. Exact proposed passive order codes are frozen; PCB, received measurements, derating and physical validation remain open.
- Compute heartbeat crosses an exact VO618A-4X017T optical interface with exact 910 Ohm input and 10 kOhm pullup candidates. Two separate TPL7407LPWR packages drive the two relay coils, with unused inputs tied low, unused outputs open, and local 100 nF COM bypass candidates. These ordinary circuits receive no safety credit and still require PCB, timing, hot-plug, fault-injection, EMC and qualified review.
- The ISO1212 feedback network uses exact proposed Vishay, Panasonic, TDK and Murata passive order codes. Receiving, PCB land-pattern/placement, DC-bias, pulse, thermal, EMC, fault and HIL evidence remain mandatory.
- Three exact Phoenix Contact PCB terminal-block candidates freeze the project pin allocation for 24 V/control return, two coil sinks, two NC feedback channels and the isolated heartbeat pair. Harness, conductor, ferrule, protection, enclosure, received-orientation and thermal evidence remain open.
- `project-button-v3.kicad_pcb` is the native PCB-P0.5 routed/test-access candidate. It retains the corrected ISO1212 DBQ footprint, field/control zoning, sixteen exact Harwin S1751-46R test terminals and separate TI-recommended 2 mm x 2 mm SUB1/SUB2 floating copper planes. It encodes a 0.1524 mm minimum trace/clearance and passes the proposed OSH Park U.S. two-layer width, spacing, drill and annular-ring envelope. It is not a Gerber or fabrication release; supplier acceptance, installed probe access, protection coordination, schematic parity review, creepage/clearance, thermal, EMC and HIL evidence remain gates.
- Heartbeat restoration cannot restore contactors; SRA1 requires a new monitored ARM action.
- External Mean Well adapters replace project-built mains wiring.
- The GST280A12-C6P source bond is explicit; project star point SP1 is DNP/prohibited.
- Three poles per candidate contactor are represented in series, pending Schneider application confirmation.
- U2D2 VDD is omitted and protected power is injected by one central DXL-STAR-P0.1 board with three isolated VDD branches; harness, thermal, waveform and no-backfeed evidence remain design gates.
- RESET `S1` and ARM `S2` retain exact complete IDEC order codes, but their physical terminals remain `TBD-*`. IDEC's 2026 production transition permits prior or redesigned internals under the same complete codes, and the live product BOM exposes no component identity. Only received-lot markings, orientation, continuity and independent comparison may release the terminal map.
- H1 is exact amber IDEC `HW1P-1FQD-A-24V`, labeled `RESET STAGE READY - DIAGNOSTIC ONLY / NO MOTION AUTHORITY`. The prior `SAFE ELIGIBLE` name and `+/-` pin implication are removed. `TBD-HA/TBD-HB` are project placeholders pending received terminal, internal-circuit, polarity/current, brightness and human-factors evidence; H1 receives no safety credit.

## Validate

Run `python tools/generate_hr_v0_electrical_v3.py --validate` with KiCad 10 installed. Generated ERC proves only modeled connectivity/annotation. Every `TBD-*`, `SELECTION REQUIRED`, `DESIGN REQUIRED`, and application-confirmation item remains a release blocker.

No drawing in this directory authorizes ordering, wiring, fabrication or energization.
