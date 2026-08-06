# Sol R12 Findings Rechecked Against R18

Date: 2026-08-06

Current configuration: `HR-30-SYS-R0.2`, Electrical `V3-P0.3`, firmware `HR-V0-FW-P0.1`

Status: **PRELIMINARY—NOT APPROVED FOR FABRICATION OR ENERGIZATION**

## Scope and counting rule

This is a project-owned disposition update, not a new independent review round. It reconciles Sol's R12 review—18 BLOCKER, 30 MAJOR, and 8 MINOR findings against GitHub `main` at `ee276af6f1a17c3a168f55efc91df2dd4a9eba38` and the hosted Electrical V2.1 package—with controlled project work through R18. Sol has not independently reviewed R13-R18.

The original R12 evidence, searchable extraction, all 56 finding dispositions, and hashes remain controlled in this directory. Historical finding totals are not silently reduced when a later project-owned pass adds evidence.

## Material changes after Sol's reviewed baseline

| R12 finding area | Current controlled evidence | Current disposition |
|---|---|---|
| Authoritative repository lacked native KiCad source. | The repository contains the archived 15-sheet Electrical V2.1 project and the separate ten-page Electrical V3-P0.3 connected candidate, including native source, manifests, schedules, ERC, netlist, PDF, and SVG exports. | Source-absence claim corrected. Neither package is a fabrication or energization release. |
| Watchdog permit and restart behavior could restore motion authority without an enforced new reset/arm sequence. | V3-P0.3 places one ordinary watchdog-relay NO contact in each SR1 input return. Nominal heartbeat loss drops SR1; recovery requires physical RESET and then a distinct physical ARM through SRA1 and K1/K2 EDM. | Nominal sequence corrected. Welded-contact, common-cause, diagnostic-coverage, PLr/SIL, stopping-time, and application-suitability findings remain open. |
| No implemented firmware existed. | `HR-V0-FW-P0.1` contains portable watchdog C source, executable watchdog and supervisor models, a controlled manifest, and 17 source-level tests. | Source-model gap partially corrected. No selected platform binding, compiled target binary, HIL, bus timing, physical fault injection, or safety credit exists. |
| Watchdog feedback path was not electrically defined. | R18 found and removed a modeled 24 V-to-Pico GPIO path. V3-P0.3 separates the Phoenix relay safety-return contact from its diagnostic changeover and inserts explicit `IFB1`/`IFB2` 24 V-to-3.3 V interface blocks. | Unsafe modeled boundary corrected. The two interface circuits remain `DESIGN REQUIRED`; resistor, CTR, threshold, protection, PCB, terminal, and fault-analysis evidence remains open. |
| Requirements and verification evidence were incomplete. | Traceability resolves 62 draft requirements, 40 risks, 61 procedures, and 45 release/walking-document references. A 30-row energization-gate register now separates documentation evidence from physical evidence. | Governance structure improved. No applicable E0-E2 gate is closed and no requirement has approved executed verification evidence. |

## Findings that still control the program

Sol's central verdict remains correct: HR-V0 is not yet a buildable or energizable machine, and HR-30W walking is plausible only as a program objective. The following evidence is still absent:

- a released, inspected mechanical manufacturing definition with closed fasteners, hard stops, cable paths, guard, bench anchor, mass, center of mass, inertia, and proof loads;
- an exact orderable electrical BOM with released terminals, connectors, harness views, conductor and protection coordination, DC interruption and regeneration evidence, grounding/bonding, enclosure, and received-part verification;
- a qualified safety-requirements specification and PLr/SIL allocation with MTTFd/B10d, diagnostic coverage, common-cause analysis, fault exclusions, stopping-time and stopping-distance validation;
- validated continuous/cyclic/thermal joint capability rather than stall-torque multiplication, plus a closed HR-30 mass and inertia model;
- a validated safe-power-loss and dynamic fall-restraint strategy for every walking pose;
- released battery/BMS/precharge/disconnect/charger-interlock/telemetry, sensing, RS-485 physical layer, and deterministic real-time control designs;
- compiled target firmware, disconnected-load HIL, inspected assembly, calibrated test records, fault injection, accountable signatures, and qualified reviewer authorization.

## Reproduced current checks

- Electrical V3-P0.3: 10 native pages, 43 component blocks, 209 modeled terminals, 56 named connected nets, 21 deliberate unconnected nets, 188 wire labels, 31 unresolved component/interface rows, and KiCad 10.0.5 ERC 0 errors / 0 warnings.
- Firmware P0.1: 17 source-level tests pass; target compile, binary, deployment, and HIL were not performed.
- Traceability: 62 requirements, 40 risks, 61 procedures, and 45 release/walking-document procedure references resolve.
- CAD source check: 4 custom parts and 8 vendor references pass repository-level validation; this is not a manufacturing release.
- Energization gates through E2: 21 applicable, 0 closed, 13 partial, and 8 open.

## Readiness statement

| Decision | Status after R18 |
|---|---|
| HR-V0 fabrication | **NOT READY** |
| HR-V0 control-only energization | **NOT READY—0/21 applicable E0-E2 gates closed** |
| HR-V0 actuator energization | **NOT READY** |
| HR-30W walking feasibility | Physically plausible in principle; not established by this design |
| Qualified mechanical review | Suitable for concept/preliminary review only |
| Qualified electrical review | Suitable for detailed candidate review, not wireable-design approval |
| Functional-safety review | Suitable to begin SRS/PLr/SIL determination, not validation |

This reconciliation does not approve procurement, fabrication, energization, functional-safety performance, walking, or operation around children.
