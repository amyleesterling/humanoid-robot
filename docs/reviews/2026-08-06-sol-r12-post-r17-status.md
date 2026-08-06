# Sol R12 Findings Rechecked Against R17

Date: 2026-08-06  
Current configuration: `HR-30-SYS-R0.2`, Electrical `V3-P0.2`, firmware `HR-V0-FW-P0.1`  
Status: **PRELIMINARY—NOT APPROVED FOR FABRICATION OR ENERGIZATION**

## Purpose

This is a project-owned status reconciliation, not a new independent review round. Sol's R12 review examined GitHub `main` at `ee276af6f1a17c3a168f55efc91df2dd4a9eba38` and the hosted Electrical V2.1 artifacts. R13 through R17 were created afterward and were not independently reviewed by Sol.

## Claims that are now stale

| R12 baseline claim | Current controlled evidence | Disposition |
|---|---|---|
| The authoritative repository contains no native KiCad project or sheets. | `electrical/kicad/project-button-v2/` contains the archived reviewed V2.1 source; `electrical/kicad/project-button-v3/` contains the separate connected V3-P0.2 candidate, source manifest, schedules, native netlist, ERC and exports. | Corrected by R13 and R16/R17. This does not make either package buildable or energizable. |
| Firmware contains only a future directory split. | `firmware/watchdog/` contains portable C source plus an executable reference model; `firmware/supervisor/` contains the fail-closed authority model; `firmware/SOURCE-MANIFEST.csv` controls hashes; `tools/check_hr_v0_firmware.py` runs 17 source-level tests. | Corrected at source-model level by R17. No selected GPIO binding, toolchain binary, target deployment, bus driver or HIL evidence exists. |
| The modeled watchdog restart arrangement is the Electrical V2.1 arrangement. | Electrical V3-P0.2 places one KWD NO contact in each SR1 input return, so nominal watchdog loss drops SR1 and requires physical RESET, followed by distinct physical ARM at SRA1. | Nominal restart chain corrected in R17. Welded contacts, common cause, application suitability and safety integrity remain unresolved. |

## Findings that remain valid

Sol's headline verdict remains correct: Project Button is a preliminary architecture, not a buildable or energizable machine. The following R12 blockers remain open unless a newer controlled record explicitly closes them with evidence:

- no released manufacturing definition, completed assembly, inspected wiring, or executed physical test evidence;
- no safety-requirements specification with qualified PLr/SIL allocation, calculation, common-cause analysis, fault exclusions, achieved stopping-time proof and validation;
- no demonstrated DC contactor interruption/coordination, regeneration behavior, protection sizing, conductor sizing, connector derating, grounding/bonding or enclosure implementation;
- no closed HR-V0 or HR-30 mass, center-of-mass and inertia model tied to released CAD and measured components;
- no continuous/cyclic/thermal leg-joint capability evidence and no approved direct-drive hip-roll solution;
- no validated safe-power-loss and dynamic restraint strategy for the walking configuration;
- battery, BMS, precharge, service disconnect, charger interlock, telemetry, sensing circuits, RS-485 physical layer and real-time control remain architecture or selection work;
- 62 requirements remain draft and no requirement has an executed, approved verification record; and
- no qualified reviewer has approved procurement, fabrication, control-only energization, actuator energization, walking or child-adjacent operation.

## Count interpretation

The R12 totals—18 BLOCKER, 30 MAJOR and 8 MINOR findings—belong to the `ee276af...` review configuration. They are preserved as review history and must not be represented as a fresh count for R17.

The 106 unresolved records are the independently reviewed Electrical V2.1 register. Electrical V3-P0.2 has a separate generated register containing 29 unresolved component/interface rows and 85 deliberately unresolved `TBD-*` terminal designations. Those V3 counts do not prove that the broader 106 V2.1 issues have been reduced to 29 or closed.

## Independent re-review required

Sol or another independent reviewer should rerun the controlled Electrical V3-P0.2 and HR-V0-FW-P0.1 review requests against the exact candidate commit. A new review must reproduce the generators and checks, inspect all KiCad sheets and source paths, examine the corrected restart sequence under single faults and common causes, and distinguish source-level evidence from compiled, target, HIL and physical evidence.

This reconciliation changes neither the gate state nor the release status. **Fabrication and energization remain unauthorized.**
