# Project Button HR-V0 Electrical V3-P1.0 / PCB-P0.2 Independent Review Request

Review date: 2026-08-06  
Controlled candidate: **Electrical V3-P1.0 / PCB-P0.2**
Systems baseline: **HR-30-SYS-R0.2**  
Status: **PRELIMINARY - NOT APPROVED FOR FABRICATION OR ENERGIZATION**

## Review objective

Independently audit the accuracy, completeness, and physical implementability of the connected HR-V0 Electrical V3 candidate. Do not treat clean ERC, generated schedules, or this request as functional-safety validation or permission to procure, fabricate, wire, or energize.

The authoritative source is this repository. The workshop website is presentation context only. Electrical V2.1 is the previously reviewed baseline; V3-P1.0 is a separate correction candidate and does not supersede it until its selections, calculations, tests, and qualified reviews close. Electrical P0.1 through P0.9 remain historical. P1.0 retains the exact feedback passives and adds exact watchdog-PCB terminal-block candidates plus project pin allocation. PCB-P0.2 corrects P0.1's non-matching ISO1212 land pattern and incorrect field/control-side staging placement. The PCB is intentionally unrouted: it has zero tracks/zones and 68 unconnected pads. Routing, stack-up, source current-sharing, harness/protection, COM-slew, brownout/EMC, received proof, physical terminals, panel/SKU/retention, HIL and functional-safety blockers remain open.

## Controlled inputs

- Architecture and open design basis: `docs/hr-v0-electrical-v3-candidate.md`
- R27 terminal evidence and limits: `docs/hr-v0-electrical-terminal-closure-r27.md`
- R28 source-interface evidence and limits: `docs/hr-v0-source-interface-closure-r28.md`
- R29 heartbeat/driver evidence and limits: `docs/hr-v0-heartbeat-driver-closure-r29.md`
- R30 feedback-passive evidence and limits: `docs/hr-v0-watchdog-feedback-passive-closure-r30.md`
- R32 PCB package and constrained-placement evidence: `docs/hr-v0-watchdog-pcb-p0.2.md`
- native PCB and custom candidate footprints: `electrical/kicad/project-button-v3/project-button-v3.kicad_pcb` and `electrical/kicad/project-button-v3/PBV3_Footprints.pretty/`
- Received control-device record: `tests/forms/hr-v0-control-device-receiving-template.csv`
- Source-interface receiving/test record: `tests/forms/hr-v0-source-interface-receiving-template.csv`
- Heartbeat/driver physical test record: `tests/forms/hr-v0-watchdog-drive-test-template.csv`
- Feedback-passive receiving/derating record: `tests/forms/hr-v0-watchdog-feedback-passive-receiving-template.csv`
- Native KiCad project: `electrical/kicad/project-button-v3/project-button-v3.kicad_pro`
- Root schematic plus ten child sheets: `electrical/kicad/project-button-v3/*.kicad_sch`
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
python tools/check_traceability.py
python tools/check_energization_gates.py --through-stage E2 --require-ready
```

The final command is expected to remain nonzero while applicable release gates are open. A zero result would require evidence and authorized closure for every applicable gate; it must not be manufactured by weakening the gate criteria.

## Baseline claims to reproduce, not assume

- twelve native pages: one root/index and eleven child sheets;
- 62 component blocks and 283 modeled terminals;
- 100 native nets: 63 named connected nets plus 37 deliberate auto-generated unconnected nets;
- 246 unique wire labels synchronized to `wire-number-table.csv`;
- 50 unresolved component/interface schedule rows;
- 46 deliberately unresolved `TBD-*` terminal designations;
- KiCad 10.0.5 ERC: 0 errors and 0 warnings;
- successful native netlist, twelve-page A3 PDF, and twelve-page SVG export;
- native PCB-P0.2 source with 26 schematic references, four board-only holes, zero tracks/zones, zero non-routing DRC violations, 68 controlled unconnected pads, and a passing generated placement-constraint record; and
- exact agreement between every modeled `(reference, terminal, net)` tuple and the KiCad-exported native netlist.

## Required technical review

1. Open every KiCad sheet and confirm parsing, hierarchy, cross-sheet connectivity, sheet order, warnings, readable text, and absence of misleading whitespace or line-art-only circuitry.
2. Rerun ERC and native netlist export. Record every compatibility warning, ignored ERC class, command version, and failure. Explain the limited meaning of ERC 0/0.
3. Compare every terminal and net against the component, connector, terminal, wire, net, BOM and unresolved schedules. Verify the 37 deliberate native unconnected terminals and 46 `TBD-*` terminal designations are intentional and are neither silently shorted nor omitted from the release record. Independently verify `S0:R-1/R-2` and `S0:L-1/L-2` against the manufacturer TOP-up bottom view, and confirm that the project prefixes cannot be mistaken for manufacturer markings. Confirm S1/S2 remain unresolved during IDEC's documented old/new assembly transition.
4. Verify the dual-channel E-stop, one watchdog NO contact in each SR1 input return, monitored RESET eligibility, direct SR1-to-SRA1 safety-output paths, distinct manual ARM, SRA1 monitored start, K1/K2 coils, mirror-contact EDM, and redundant series actuator-power interruption.
5. Prove from the schematic and control requirements that E-stop release, RESET, compute boot, watchdog recovery, software restart, brownout, or communication recovery cannot by themselves command actuator power or motion. Specifically confirm that watchdog recovery cannot restore SR1 without physical RESET and cannot restore SRA1/K1/K2 without the later physical ARM. Identify every single fault or common-cause path that could violate that rule.
6. Review the exact Pilz PNOZ s4 750104 candidate application, selector mode, terminal use, contact protection, reset/ARM timing, diagnostic contacts, and any need for force-guided or otherwise safety-suitable external devices. Do not assign PL/SIL credit without a complete safety calculation and evidence.
7. Review the two Phoenix Contact watchdog-relay candidate coil circuits, official `A1/A2`, `11-12-14`, and `21-22-24` terminal mapping, low-side drivers, suppression/polarity, supply/common reference, pickup/dropout timing, contact routing, welded-contact behavior, common-cause controller/supply failures, and diagnostic limitations. Confirm that `WD1_NC_24V` and `WD2_NC_24V` terminate only at the `UFB1` field-input networks and never directly at a Pico GPIO. Independently reproduce the ISO1212DBQ pinout and both channels: 1 kOhm `RTHR` from module input to SENSE, 562 Ohm `RSENSE` between SENSE and IN, 10 nF CIN from SENSE to FGND, 2.70 kOhm 1% 0.5 W contact-wetting load, 100 nF VCC bypass, 1 kOhm GPIO series resistor and 10 kOhm pulldown. Recalculate the 23.4-24.6 V rail, 10.63 mA minimum screened contact current, 0.226 W maximum wetting-resistor dissipation, input thresholds and RP2040 logic margins. Review the tied GND1/FGND architecture, SUB pins, PCB/layout, brownout, EMC/surge, single faults and exact passive selections. These ordinary relays, receiver circuit and firmware currently receive no safety credit.
8. Verify K1/K2 coil polarity, mirror-contact designations, auxiliary contacts, all three main poles in series, DC utilization category, loaded DC interruption capability, regenerative-current behavior, coordination, suppression, and welded-pole detection. Mark every unsupported application assumption as unresolved.
9. Verify the Mean Well GST280A12-C6P internal `-V`/PE bond from current manufacturer evidence. Confirm that SP1 is DNP/prohibited for that source, identify all other conductive chassis/frame/shield bonds, and assess touch-current, protective-earth continuity, site cord/GFCI/code, enclosure and fault-current assumptions.
10. Verify the GST40A24-P1J and Raspberry Pi supply boundaries, locking/retention needs, source segregation, control-only energization boundary, grounding, and all project-built DC protection interfaces. Independently verify `JA1` Molex `39012066`/`444783112`, HCS compatibility with the 5559 housing, 16 AWG range, `63819-0900` tool scope, strip/pull criteria, pins 1-3 positive and 4-6 return, and the 7 A/contact idealized screen. Do not assume equal parallel-contact sharing or unpublished adapter-side contact capacity; require received current-division, crimp, retention and stabilized thermal evidence.
11. Review every fuse/protection placeholder and recalculate conductor/protective-device requirements without inventing values. List missing prospective fault current, cable length, ambient, bundling, insulation, connector limits, inrush, duty cycle, coordination, source foldback, temperature rise and jurisdiction inputs.
12. Verify the U2D2 has no actuator VDD connection and does not carry summed actuator current. Review the three VDD-isolating injection modules, pin-2 isolation, common TTL ground/data reference, no-backfeed behavior under every power sequence, connector orientation, strain relief, crimping and test requirements.
13. Verify ROBOTIS model/SKU/interface claims and distinguish stall or estimated torque data from continuous validated joint capacity. Check received-unit revision, model readback and USB-connector evidence requirements.
14. Review the watchdog controller, heartbeat input, Raspberry Pi/control-terminal boundary, firmware ownership, diagnostics, startup defaults, stuck-high/stuck-low faults, loss of common supply, reset behavior, and fault-injection testability. Independently reproduce the VO618A-4X017T pins and CTR-bin facts, 910 ohm input-current screen, 10 kilohm pullup current, inversion and edge timing. Reproduce both separate TPL7407LPWR pin maps, tied-low unused inputs, no-connect unused outputs, COM clamp/bypass, 18 mA typical Phoenix coil load comparison, and TI's less-than-0.5 V/us COM-slew requirement. Confirm that the proposed 100 nF parts do not by themselves prove slew compliance. Independently verify TRACO POWER `TSR 1-2450` pin 1 `+VIN`, pin 2 `GND`, pin 3 `+VOUT`, non-isolated topology, 6.5-36 V input and 5 V/1 A output, then identify the exact branch-protection, load, startup, slow-ramp brownout, fast-dropout, recovery, output-fault, EMC and enclosed-thermal evidence needed for release.
15. Inspect the native PCB, all three project footprints, board subset/net mapping, staging outline, mounting holes, terminal orientation, 0.15 mm candidate clearance, placement render and complete DRC output. Independently confirm that `UFB1` now uses the 3.9 mm by 4.9 mm, 0.635 mm-pitch DBQ candidate rather than P0.1's non-matching footprint. Reproduce every result in `project-button-v3-pcb-placement-constraints.json`, including CDEC spacing, RTH high-voltage spacing, field/control zoning and driver-capacitor placement. Confirm that zero routed tracks/zones and 68 unconnected pads block fabrication. Review every routing gate in `docs/hr-v0-watchdog-pcb-p0.2.md`, including the explicit absence of isolation credit for `UFB1`; do not treat the constrained positions as a compliant routed layout.
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
