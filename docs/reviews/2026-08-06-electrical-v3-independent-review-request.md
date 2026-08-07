# Project Button HR-V0 Electrical V3-P1.3 / PCB-P0.5 / DXL-STAR-P0.1 Independent Review Request

Review date: 2026-08-07
Controlled candidate: **Electrical V3-P1.3 / PCB-P0.5 / DXL-STAR-P0.1**
Systems baseline: **HR-30-SYS-R0.2**  
Status: **PRELIMINARY - NOT APPROVED FOR FABRICATION OR ENERGIZATION**

## Review objective

Independently audit the accuracy, completeness, and physical implementability of the connected HR-V0 Electrical V3 candidate. Do not treat clean ERC, generated schedules, or this request as functional-safety validation or permission to procure, fabricate, wire, or energize.

The authoritative source is this repository. The workshop website is presentation context only. Electrical V2.1 is the previously reviewed baseline; V3-P1.3 is a separate correction candidate and does not supersede it until its selections, calculations, tests, and qualified reviews close. Electrical P0.1 through P1.2 remain historical. P1.2 retained the watchdog PCB boundary and test points while replacing three undefined inline DYNAMIXEL injection modules with one exact central `DXL-STAR-P0.1` board boundary. P1.3 adds current Schneider K1/K2 catalog evidence and explicitly retains the lower-current critical-current/application blocker. PCB-P0.5 is a two-layer routed/test-access candidate with 201 segments, 56 vias, one filled return zone, two separate floating 2 mm x 2 mm SUB thermal zones, native DRC 0/0 and independent pad/copper-connectivity evidence. DXL-STAR-P0.1 is a separate 100 mm x 60 mm, two-layer routed candidate with seven connectors, 18 terminals, 17 segments, one common-return zone, mutually isolated J1/J2/J3 VDD nets and an unrouted U2D2 pin 2. Neither project has fabrication outputs. Supplier archive acceptance, physical test access, source current-sharing, harness/protection, connector-current, contactor critical-current/application disposition, thermal/waveform/no-backfeed, COM-slew, brownout/EMC, received proof, physical terminals, panel/SKU/retention, HIL and functional-safety blockers remain open.

## Controlled inputs

- Architecture and open design basis: `docs/hr-v0-electrical-v3-candidate.md`
- R27 terminal evidence and limits: `docs/hr-v0-electrical-terminal-closure-r27.md`
- R28 source-interface evidence and limits: `docs/hr-v0-source-interface-closure-r28.md`
- R29 heartbeat/driver evidence and limits: `docs/hr-v0-heartbeat-driver-closure-r29.md`
- R30 feedback-passive evidence and limits: `docs/hr-v0-watchdog-feedback-passive-closure-r30.md`
- R32 PCB package and constrained-placement evidence: `docs/hr-v0-watchdog-pcb-p0.2.md`
- R33 PCB routed-copper and connectivity evidence: `docs/hr-v0-watchdog-pcb-p0.3.md`
- R34 PCB test-access and ISO1212 SUB-copper evidence: `docs/hr-v0-watchdog-pcb-p0.4.md`
- R35 PCB fabrication-envelope evidence: `docs/hr-v0-watchdog-pcb-p0.5.md`
- R36 protection-coordination evidence: `docs/hr-v0-protection-coordination-p0.1.md`; `electrical/hr-v0-protection-coordination-inputs.csv`; `tests/forms/hr-v0-protection-coordination-template.csv`
- R37 DYNAMIXEL star-injection evidence: `docs/hr-v0-dxl-star-injection-p0.1.md`; `electrical/kicad/hr-v0-dxl-star/`; `tests/forms/hr-v0-dxl-star-inspection-template.csv`
- R38 actuator current/configuration evidence: `docs/hr-v0-actuator-current-envelope-p0.1.md`; `firmware/supervisor/actuator-config.json`; `tests/forms/hr-v0-actuator-current-characterization-template.csv`
- R39 watchdog target/build evidence: `docs/hr-v0-watchdog-build-p0.1.md`; `firmware/watchdog/platform/pico/main.c`; `firmware/watchdog/toolchain-lock.json`; `firmware/watchdog/output/P0.1/`
- native PCB and custom candidate footprints: `electrical/kicad/project-button-v3/project-button-v3.kicad_pcb` and `electrical/kicad/project-button-v3/PBV3_Footprints.pretty/`
- Received control-device record: `tests/forms/hr-v0-control-device-receiving-template.csv`
- Source-interface receiving/test record: `tests/forms/hr-v0-source-interface-receiving-template.csv`
- Heartbeat/driver physical test record: `tests/forms/hr-v0-watchdog-drive-test-template.csv`
- Feedback-passive receiving/derating record: `tests/forms/hr-v0-watchdog-feedback-passive-receiving-template.csv`
- Native KiCad project: `electrical/kicad/project-button-v3/project-button-v3.kicad_pro`
- Root schematic plus eleven child sheets: `electrical/kicad/project-button-v3/*.kicad_sch`
- Watchdog feedback calculation and circuit basis: `docs/hr-v0-watchdog-feedback-p0.1.md`
- Generator: `tools/generate_hr_v0_electrical_v3.py`
- Independent consistency checker: `tools/check_hr_v0_electrical_v3.py`
- Generated BOM, connector/terminal, wire-number, net and unresolved schedules: `electrical/kicad/project-button-v3/*.csv`
- KiCad ERC, native netlist and command log: `electrical/kicad/project-button-v3/validation/`
- PDF/SVG review exports: `electrical/kicad/project-button-v3/output/`
- Program BOM: `bom/bom.csv`
- Energization gates: `requirements/hr-v0-energization-gates.csv`
- Safety-function basis: `docs/safety-functions.md`
- Control-state basis: `docs/control.md`
- Primary-source register: `references/primary-sources.md`

## Reproduction commands

With KiCad 10.0.5 and Python available, run:

```text
python tools/generate_hr_v0_electrical_v3.py --validate
python tools/check_hr_v0_electrical_v3.py
"C:\Program Files\KiCad\10.0\bin\python.exe" tools/generate_hr_v0_watchdog_pcb.py
"C:\Program Files\KiCad\10.0\bin\python.exe" tools/check_hr_v0_watchdog_pcb.py
"C:\Program Files\KiCad\10.0\bin\python.exe" tools/generate_hr_v0_dxl_star.py
"C:\Program Files\KiCad\10.0\bin\python.exe" tools/check_hr_v0_dxl_star.py
python tools/check_traceability.py
python tools/check_energization_gates.py --through-stage E2 --require-ready
```

The final command is expected to remain nonzero while applicable release gates are open. A zero result would require evidence and authorized closure for every applicable gate; it must not be manufactured by weakening the gate criteria.

## Baseline claims to reproduce, not assume

- thirteen native pages: one root/index and twelve child sheets;
- 76 component blocks and 295 modeled terminals;
- 100 native nets: 64 named connected nets plus 36 deliberate auto-generated unconnected nets;
- 259 unique wire labels synchronized to `wire-number-table.csv`;
- 63 unresolved component/interface schedule rows;
- 24 deliberately unresolved `TBD-*` terminal designations;
- KiCad 10.0.5 ERC: 0 errors and 0 warnings;
- successful native netlist, thirteen-page A3 PDF, and thirteen-page SVG export;
- native PCB-P0.5 source with 42 schematic references, four board-only holes, 201 segments, 56 vias, one filled `SAFETY_0V` zone, two isolated 2 mm x 2 mm SUB zones, native DRC zero violations/zero routed unconnected pads, 14 isolated unused singleton nets, 89 untouched no-net pads, 16 exact test-point records, 0.1524 mm minimum trace/clearance, top/bottom renders and a passing generated fabrication-envelope/test-access evidence record; and
- exact agreement between every modeled `(reference, terminal, net)` tuple and the KiCad-exported native netlist.
- separate DXL-STAR-P0.1 source with seven connectors, 18 terminals, 17 routed segments, one common-return zone, three isolated positive rails, an unrouted/no-net `JC1:2`, ERC/DRC 0/0, readable top/bottom renders, and no fabrication outputs.

## Required technical review

1. Open every KiCad sheet and confirm parsing, hierarchy, cross-sheet connectivity, sheet order, warnings, readable text, and absence of misleading whitespace or line-art-only circuitry.
2. Rerun ERC and native netlist export. Record every compatibility warning, ignored ERC class, command version, and failure. Explain the limited meaning of ERC 0/0.
3. Compare every terminal and net against the component, connector, terminal, wire, net, BOM and unresolved schedules. Verify the 36 deliberate native unconnected terminals and 24 `TBD-*` terminal designations are intentional and are neither silently shorted nor omitted from the release record. Independently verify `S0:R-1/R-2` and `S0:L-1/L-2` against the manufacturer TOP-up bottom view, and confirm that the project prefixes cannot be mistaken for manufacturer markings. Confirm S1/S2 remain unresolved during IDEC's documented old/new assembly transition.
4. Verify the dual-channel E-stop, one watchdog NO contact in each SR1 input return, monitored RESET eligibility, direct SR1-to-SRA1 safety-output paths, distinct manual ARM, SRA1 monitored start, K1/K2 coils, mirror-contact EDM, and redundant series actuator-power interruption.
5. Prove from the schematic and control requirements that E-stop release, RESET, compute boot, watchdog recovery, software restart, brownout, or communication recovery cannot by themselves command actuator power or motion. Specifically confirm that watchdog recovery cannot restore SR1 without physical RESET and cannot restore SRA1/K1/K2 without the later physical ARM. Identify every single fault or common-cause path that could violate that rule.
6. Review the exact Pilz PNOZ s4 750104 candidate application, selector mode, terminal use, contact protection, reset/ARM timing, diagnostic contacts, and any need for force-guided or otherwise safety-suitable external devices. Do not assign PL/SIL credit without a complete safety calculation and evidence.
7. Review the two Phoenix Contact watchdog-relay candidate coil circuits, official `A1/A2`, `11-12-14`, and `21-22-24` terminal mapping, low-side drivers, suppression/polarity, supply/common reference, pickup/dropout timing, contact routing, welded-contact behavior, common-cause controller/supply failures, and diagnostic limitations. Confirm that `WD1_NC_24V` and `WD2_NC_24V` terminate only at the `UFB1` field-input networks and never directly at a Pico GPIO. Independently reproduce the ISO1212DBQ pinout and both channels: 1 kOhm `RTHR` from module input to SENSE, 562 Ohm `RSENSE` between SENSE and IN, 10 nF CIN from SENSE to FGND, 2.70 kOhm 1% 0.5 W contact-wetting load, 100 nF VCC bypass, 1 kOhm GPIO series resistor and 10 kOhm pulldown. Recalculate the 23.4-24.6 V rail, 10.63 mA minimum screened contact current, 0.226 W maximum wetting-resistor dissipation, input thresholds and RP2040 logic margins. Review the tied GND1/FGND architecture, SUB pins, PCB/layout, brownout, EMC/surge, single faults and exact passive selections. These ordinary relays, receiver circuit and firmware currently receive no safety credit.
8. Verify K1/K2 coil polarity, mirror-contact designations, auxiliary contacts, all three main poles in series, DC utilization category, loaded DC interruption capability, regenerative-current behavior, coordination, suppression, and welded-pole detection. Mark every unsupported application assumption as unresolved.
9. Verify the Mean Well GST280A12-C6P internal `-V`/PE bond from current manufacturer evidence. Confirm that SP1 is DNP/prohibited for that source, identify all other conductive chassis/frame/shield bonds, and assess touch-current, protective-earth continuity, site cord/GFCI/code, enclosure and fault-current assumptions.
10. Verify the GST40A24-P1J and Raspberry Pi supply boundaries, locking/retention needs, source segregation, control-only energization boundary, grounding, and all project-built DC protection interfaces. Independently verify `JA1` Molex `39012066`/`444783112`, HCS compatibility with the 5559 housing, 16 AWG range, `63819-0900` tool scope, strip/pull criteria, pins 1-3 positive and 4-6 return, and the 7 A/contact idealized screen. Do not assume equal parallel-contact sharing or unpublished adapter-side contact capacity; require received current-division, crimp, retention and stabilized thermal evidence.
11. Review every fuse/protection placeholder and independently audit the R36 six-reference register without inventing values. Verify Littelfuse `FHAC0002SXJ` against document `062923-B`, Blue Sea Systems `5025`, and Littelfuse ATOF against Rev. 02/04/2025; treat all product maxima as limits rather than released ratings. Reproduce the XM540 4.4 A stall versus JST EH 3 A series conflict and independently audit `HR-V0-ACT-P0.1`: raw 800 × approximately 2.69 mA = nominal 2.152 A internal current and an ideal 5.18 N·m XM540 stall-line screen. Confirm that internal motor current is not treated as guaranteed branch supply current, that raw 800/300 remain test candidates, and that ROBOTIS's stated 21 AWG cable versus JST's AWG 22 EH maximum remains unresolved. Assess whether written application evidence plus external branch-current/thermal/clearing proof is sufficient. List every still-missing prospective fault current, cable length, conductor/terminal/splice order code, ambient, bundling, insulation, connector limit, inrush, duty cycle, regeneration, coordination, source foldback, temperature rise and jurisdiction input. Confirm that no ampere-specific fuse order code has been released.
12. Verify the U2D2 has no actuator VDD connection and does not carry summed actuator current. Independently audit the native DXL-STAR-P0.1 project: `JC1:1` common return, `JC1:2` no net/no copper, `JC1:3` TTL data; `JP1`-`JP3` separate VDD plus common return; `JA1`-`JA3` common return/data plus only their respective VDD. Review the proposed JST exact headers/housings/contacts, the controller cable's empty pin-2 cavities, three-rail isolation, no-backfeed behavior under every power sequence, the XM540 4.4 A versus EH 3 A conflict, copper/return paths, TTL star signal integrity, cable length, baud rate, connector orientation, strain relief, crimping, thermal evidence and test requirements. Confirm DRC 0/0 does not resolve any of those physical questions.
13. Verify ROBOTIS model/SKU/interface claims and distinguish stall or estimated torque data from continuous validated joint capacity. Check received-unit revision, model readback and USB-connector evidence requirements.
14. Review the watchdog controller, heartbeat input, Raspberry Pi/control-terminal boundary, firmware ownership, diagnostics, startup defaults, stuck-high/stuck-low faults, loss of common supply, reset behavior, and fault-injection testability. Independently reproduce the VO618A-4X017T pins and CTR-bin facts, 910 ohm input-current screen, 10 kilohm pullup current, inversion and edge timing. Reproduce both separate TPL7407LPWR pin maps, tied-low unused inputs, no-connect unused outputs, COM clamp/bypass, 18 mA typical Phoenix coil load comparison, and TI's less-than-0.5 V/us COM-slew requirement. Confirm that the proposed 100 nF parts do not by themselves prove slew compliance. Independently verify TRACO POWER `TSR 1-2450` pin 1 `+VIN`, pin 2 `GND`, pin 3 `+VOUT`, non-isolated topology, 6.5-36 V input and 5 V/1 A output, then identify the exact branch-protection, load, startup, slow-ramp brownout, fast-dropout, recovery, output-fault, EMC and enclosed-thermal evidence needed for release. Audit the DYNAMIXEL pre-torque readback contract, Operating Mode 5 reset side effects, startup-torque and torque-on-goal-update bits, torque-off EEPROM rule, received identity/firmware requirements, software position-limit dependency and mismatch fault behavior.
15. Inspect the native PCB, all four project footprints, board subset/net mapping, outline, mounting holes, terminal orientation, candidate net classes, every routed segment/via/zone, top/bottom renders and complete DRC output. Independently confirm that `UFB1` uses the 3.9 mm by 4.9 mm, 0.635 mm-pitch DBQ candidate and that every `TP1`-`TP16` pad matches Harwin drawing issue 10. Reproduce every result in `project-button-v3-pcb-test-access-evidence.json`: 201 segments, 56 vias, three filled B.Cu zones, all multi-pad modeled nets connected, 14 unused singleton nets isolated, both SUB nets confined to their own pad/route/via/2 mm x 2 mm plane, 89 no-net pads untouched, zero native DRC violations, zero routed unconnected pads, placement screens, explicit path lengths and net route totals. Independently reproduce the 0.1524 mm minimum trace width/clearance, 0.30 mm minimum via drill and 0.15 mm minimum annular ring, then compare the complete design—not just those three minima—with the current official OSH Park Two Layer Service stack-up, mask, copper, drill, outline and board-edge rules. Audit the `SAFETY_0V` zone boundary around `ISO1`, current-return paths, power widths, connector approaches, physical probe clearance and absence of unintended copper at unused pads. Confirm that the two SUB planes remain separate from each other and every ground/signal net. Identify the supplier-acceptance, physical test-access, protection, thermal, EMC and parity evidence still needed. Confirm that no Gerber/drill output exists and that DRC 0/0 is not a fabrication or safety approval. Review `docs/hr-v0-watchdog-pcb-p0.5.md`, including the explicit absence of isolation credit for `UFB1` and the proposed-only supplier status.
16. Inspect the PDF and every SVG at normal viewing size for clipping, overlap, tiny text, ambiguous crossings, misleading contact state, incomplete titles, or absent preliminary warnings. Treat web rendering as a separate presentation check.

## Required findings format

Provide a prioritized **BLOCKER / MAJOR / MINOR** list. Every finding must include:

- exact sheet, reference, terminal and net, or exact controlled document/table row;
- the failed requirement or engineering principle;
- proposed correction;
- current primary-source link and document revision/date where a component claim is involved;
- evidence needed to close the finding; and
- whether the finding blocks design review, procurement, fabrication, control-only energization, actuator energization, or all of them.

Also provide:

- complete ERC output and compatibility problems;
- an independently derived list of every unresolved selection;
- a comparison of KiCad source, native netlist, schedules, BOM, exports and documentation;
- a statement of what was verified versus not verified;
- readiness for qualified electrical review;
- readiness for functional-safety review; and
- explicit verdicts for procurement, fabrication, control-only energization and actuator energization.

Do not mark the design approved. If corrections are made, return them as a reviewable patch or branch, regenerate every synchronized artifact, rerun all checks, and preserve the preliminary warning on every output.
