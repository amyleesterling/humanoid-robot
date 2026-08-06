# Project Button HR-V0 Electrical V3-P0.1 Independent Review Request

Review date: 2026-08-06  
Controlled candidate: **Electrical V3-P0.1**  
Systems baseline: **HR-30-SYS-R0.2**  
Status: **PRELIMINARY—NOT APPROVED FOR FABRICATION OR ENERGIZATION**

## Review objective

Independently audit the accuracy, completeness, and physical implementability of the connected HR-V0 Electrical V3 candidate. Do not treat clean ERC, generated schedules, or this request as functional-safety validation or permission to procure, fabricate, wire, or energize.

The authoritative source is this repository. The workshop website is presentation context only. Electrical V2.1 is the previously reviewed baseline; V3-P0.1 is a separate correction candidate and does not supersede it until its selections, calculations, tests, and qualified reviews close.

## Controlled inputs

- Architecture and open design basis: `docs/hr-v0-electrical-v3-candidate.md`
- Native KiCad project: `electrical/kicad/project-button-v3/project-button-v3.kicad_pro`
- Root schematic plus nine child sheets: `electrical/kicad/project-button-v3/*.kicad_sch`
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
python tools/check_traceability.py
python tools/check_energization_gates.py --through-stage E2 --require-ready
```

The final command is expected to remain nonzero while applicable release gates are open. A zero result would require evidence and authorized closure for every applicable gate; it must not be manufactured by weakening the gate criteria.

## Baseline claims to reproduce, not assume

- ten native pages: one root/index and nine child sheets;
- 41 component blocks and 198 modeled terminals;
- 76 native nets: 53 named connected nets plus 23 deliberate auto-generated unconnected nets;
- 175 unique wire labels synchronized to `wire-number-table.csv`;
- 29 unresolved component/interface schedule rows;
- 85 deliberately unresolved `TBD-*` terminal designations;
- KiCad 10.0.5 ERC: 0 errors and 0 warnings;
- successful native netlist, ten-page A3 PDF, and ten-page SVG export; and
- exact agreement between every modeled `(reference, terminal, net)` tuple and the KiCad-exported native netlist.

## Required technical review

1. Open every KiCad sheet and confirm parsing, hierarchy, cross-sheet connectivity, sheet order, warnings, readable text, and absence of misleading whitespace or line-art-only circuitry.
2. Rerun ERC and native netlist export. Record every compatibility warning, ignored ERC class, command version, and failure. Explain the limited meaning of ERC 0/0.
3. Compare every terminal and net against the component, connector, terminal, wire, net, BOM and unresolved schedules. Verify the 23 open terminals are intentional and are neither silently shorted nor omitted from the release record.
4. Verify the dual-channel E-stop, monitored RESET eligibility, distinct manual ARM, watchdog relay contacts, SRA1 monitored start, K1/K2 coils, mirror-contact EDM, and redundant series actuator-power interruption.
5. Prove from the schematic and control requirements that E-stop release, RESET, compute boot, watchdog recovery, software restart, brownout, or communication recovery cannot by themselves command actuator power or motion. Identify every single fault or common-cause path that could violate that rule.
6. Review the exact Pilz PNOZ s4 750104 candidate application, selector mode, terminal use, contact protection, reset/ARM timing, diagnostic contacts, and any need for force-guided or otherwise safety-suitable external devices. Do not assign PL/SIL credit without a complete safety calculation and evidence.
7. Review the two Phoenix Contact watchdog-relay candidate coil circuits, low-side drivers, suppression/polarity, supply/common reference, pickup/dropout timing, contact routing, welded-contact behavior, common-cause controller/supply failures, and diagnostic limitations. These ordinary relays currently receive no safety credit.
8. Verify K1/K2 coil polarity, mirror-contact designations, auxiliary contacts, all three main poles in series, DC utilization category, loaded DC interruption capability, regenerative-current behavior, coordination, suppression, and welded-pole detection. Mark every unsupported application assumption as unresolved.
9. Verify the Mean Well GST280A12-C6P internal `-V`/PE bond from current manufacturer evidence. Confirm that SP1 is DNP/prohibited for that source, identify all other conductive chassis/frame/shield bonds, and assess touch-current, protective-earth continuity, site cord/GFCI/code, enclosure and fault-current assumptions.
10. Verify the GST40A24-P1J and Raspberry Pi supply boundaries, locking/retention needs, source segregation, control-only energization boundary, grounding, and all project-built DC protection interfaces.
11. Review every fuse/protection placeholder and recalculate conductor/protective-device requirements without inventing values. List missing prospective fault current, cable length, ambient, bundling, insulation, connector limits, inrush, duty cycle, coordination, source foldback, temperature rise and jurisdiction inputs.
12. Verify the U2D2 has no actuator VDD connection and does not carry summed actuator current. Review the three VDD-isolating injection modules, pin-2 isolation, common TTL ground/data reference, no-backfeed behavior under every power sequence, connector orientation, strain relief, crimping and test requirements.
13. Verify ROBOTIS model/SKU/interface claims and distinguish stall or estimated torque data from continuous validated joint capacity. Check received-unit revision, model readback and USB-connector evidence requirements.
14. Review the watchdog controller, two channel drivers, heartbeat input, Raspberry Pi/control-terminal boundary, firmware ownership, diagnostics, startup defaults, stuck-high/stuck-low faults, loss of common supply, reset behavior, and fault-injection testability.
15. Inspect the PDF and every SVG at normal viewing size for clipping, overlap, tiny text, ambiguous crossings, misleading contact state, incomplete titles, or absent preliminary warnings. Treat web rendering as a separate presentation check.

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
