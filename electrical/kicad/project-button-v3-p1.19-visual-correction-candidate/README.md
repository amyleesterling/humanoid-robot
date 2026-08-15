# Project Button HR-V0 Electrical V3-P1.19-VISUAL-CORRECTION-CANDIDATE

**PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION**

This is a generated, connected native KiCad candidate derived from `tools/generate_hr_v0_electrical_v3.py`. It does not supersede the reviewed Electrical V2.1 package until exact selections, application reviews, calculations, physical tests and qualified review close.

## Pages

1. `01_external_sources.kicad_sch` — External listed sources and DC boundaries
2. `02_estop_eligibility.kicad_sch` — Dual-channel E-stop and RESET eligibility
3. `03_arm_watchdog_eligibility.kicad_sch` — Distinct ARM and watchdog-gated SR1 supply
4. `04_contactor_edm.kicad_sch` — Contactor coils, mirror contacts and EDM
5. `05_actuator_interruption.kicad_sch` — Redundant actuator-power interruption
6. `06_branches_and_limiters.kicad_sch` — Protected actuator branches and current-limiter carriers
7. `07_watchdog_control.kicad_sch` — Independent watchdog power, controller and drivers
8. `08_watchdog_feedback_interface.kicad_sch` — Calculated dual-channel 24 V watchdog feedback
9. `09_compute_and_control_terminals.kicad_sch` — Compute and control terminals
10. `10_actuator_interfaces.kicad_sch` — U2D2, DXL star, actuator ports and bonding boundary
11. `11_watchdog_pcb_connectors.kicad_sch` — Watchdog PCB external connectors
12. `12_watchdog_pcb_test_access.kicad_sch` — Watchdog PCB test access

## Material corrections relative to V2.1

- Separate SR1 RESET eligibility and SRA1 ARM/EDM stages.
- Two separately driven ordinary watchdog relay contacts are in series with the SR1 A1 supply. Heartbeat loss power-cycles SR1 and forces the physical RESET stage to drop, while S0 remains direct in both SR1 input loops. Internal KWD A1/21-to-14 shorts can defeat the diagnostic gate but cannot inject downstream of S0. Supply switching, protected routing, common-cause analysis and physical proof remain open; the watchdog receives zero safety credit.
- Phoenix relay terminals are frozen from the official circuit diagram. Both 24 V NC diagnostics pass through the calculated ISO1212DBQ input network before the Pico GPIO. Exact proposed passive order codes are frozen; PCB, received measurements, derating and physical validation remain open.
- Compute heartbeat crosses an exact VO618A-4X017T optical interface with exact 910 Ohm input and 10 kOhm pullup candidates. Two separate TPL7407LPWR packages drive the two relay coils, with unused inputs tied low, unused outputs open, and local 100 nF COM bypass candidates. These ordinary circuits receive no safety credit and still require PCB, timing, hot-plug, fault-injection, EMC and qualified review.
- The ISO1212 feedback network uses exact proposed Vishay, Panasonic, TDK and Murata passive order codes. Receiving, PCB land-pattern/placement, DC-bias, pulse, thermal, EMC, fault and HIL evidence remain mandatory.
- Three exact Phoenix Contact PCB terminal-block candidates freeze the project pin allocation for 24 V/control return, two coil sinks, two NC feedback channels and the isolated heartbeat pair. Harness, conductor, ferrule, protection, enclosure, received-orientation and thermal evidence remain open.
- `PCB-P0.9 baseline watchdog board (separate unchanged native source)` is the native PCB-P0.9 routed/test-access candidate. It is geometry/topology-identical to PCB-P0.8 and adds exact hidden manufacturer, MPN, assembly-description, process-class, no-alternate and process-state fields for all 42 populated references. It retains the deeper R138 document/land fields for UDRV1/UDRV2/UFB1/ISO1, the R89 manufacturer-traced lands and exact rectangular 3.45 x 1.85 mm Harwin issue-10 test-point copper. It encodes a 0.1524 mm minimum trace/clearance. Supplier-normalized XYRS and assembly process remain SELECTION REQUIRED. It is not a Gerber or fabrication release; supplier acceptance, installed probe access, protection coordination, schematic parity review, creepage/clearance, thermal, EMC and HIL evidence remain gates.
- Heartbeat restoration cannot restore contactors; SRA1 requires a new monitored ARM action.
- Factory-sealed external adapters replace project-built mains wiring; the 24 V candidate is GlobTek `WR9QI1660YL4NKITR6B` with its factory YL4/C40337 locking cord.
- The GST280A12-C6P source bond is explicit; project star point SP1 is DNP/prohibited.
- Three poles per candidate contactor are represented in series, pending Schneider application confirmation.
- U2D2 VDD is omitted and protected power is injected by one central DXL-STAR-P0.2-CARRIER-CANDIDATE board with three isolated VDD branches; harness, thermal, waveform and no-backfeed evidence remain design gates.
- RESET `S1` and ARM `S2` retain exact complete IDEC order codes, but their physical terminals remain `TBD-*`. IDEC's 2026 production transition permits prior or redesigned internals under the same complete codes, and the live product BOM exposes no component identity. Only received-lot markings, orientation, continuity and independent comparison may release the terminal map.
- H1 is exact amber IDEC `HW1P-1FQD-A-24V`, labeled `RESET STAGE READY - DIAGNOSTIC ONLY / NO MOTION AUTHORITY`. The prior `SAFE ELIGIBLE` name and `+/-` pin implication are removed. `TBD-HA/TBD-HB` are project placeholders pending received terminal, internal-circuit, polarity/current, brightness and human-factors evidence; H1 receives no safety credit.

## Validate

Run the R230 visual-correction candidate generator with `--validate` with KiCad 10 installed. Generated ERC proves only modeled connectivity/annotation. Every `TBD-*`, `SELECTION REQUIRED`, `DESIGN REQUIRED`, and application-confirmation item remains a release blocker.

No drawing in this directory authorizes ordering, wiring, fabrication or energization.
