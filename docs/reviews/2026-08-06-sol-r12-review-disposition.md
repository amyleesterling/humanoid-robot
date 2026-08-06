# Disposition - Sol Independent Engineering Review R12

Review received: 2026-08-06

Reviewed configuration: GitHub `main` at `ee276af6f1a17c3a168f55efc91df2dd4a9eba38` plus the hosted Electrical V2.1 artifacts

Original evidence: `2026-08-06-sol-r12-independent-engineering-review.docx`

Searchable extraction: `2026-08-06-sol-r12-independent-engineering-review.txt`

Original evidence SHA-256: `37f390d07d76c4c82411c543af299ddaab193213bd060319e1e4ab8171fd6631`

Reviewer finding count: 18 BLOCKER, 30 MAJOR, 8 MINOR

Package status: **PRELIMINARY - NOT APPROVED FOR FABRICATION OR ENERGIZATION**

## Independence and timing

R11 Fable and R12 Sol were commissioned in parallel against the same pre-correction baseline. Sol's review is therefore independent evidence, not a follow-up review of R14. A Sol finding that was independently corrected during R13 or R14 is recorded as addressed by that later project-owned pass; it is not deleted, backdated, or counted as a defect newly introduced after R14.

The DOCX is preserved without edits. The TXT file is a searchable structural extraction of the DOCX and is subordinate to the original if formatting or character encoding differs. The canonical document renderer could not complete because the supplied DOCX has no explicit OOXML page-size element and LibreOffice is not installed in the review environment. Structural parsing succeeded: 560 paragraphs, 275 tables, one section, no tracked changes, and no active comments. This archival limitation does not affect the finding text or its disposition, but the package does not claim a visual-layout validation of the original DOCX.

## Disposition vocabulary

- **Addressed on branch**: the specific documentation, arithmetic, or configuration defect has a controlled correction in this pull-request branch. This is not physical validation and is not effective on authoritative `main` until merge and post-merge checks.
- **Partially addressed; open**: R13/R14 added requirements, calculations, or controls, but the evidence Sol requires still does not exist.
- **Accepted; open**: the finding remains a release blocker or unresolved engineering task.
- **Staged; merge validation required**: source exists on the review branch, but authoritative-main closure requires merge, clean-clone verification, parse/ERC regeneration, and hash comparison.

## BLOCKER disposition

| ID | Current disposition | Controlled response and remaining evidence |
|---|---|---|
| B-001 authoritative repository lacks native implementation | **Staged; merge validation required** | R13 adds the complete 15-sheet native KiCad V2.1 tree, project/symbol files, schedules, ERC records, netlist, exports, and source manifest. CAD and firmware remain placeholders. ECAD provenance closes only after PR merge and clean-clone parse/ERC/hash validation. |
| B-002 electrical revision and metrics inconsistent | **Addressed on branch** | R10-R14 establish `HR-30-SYS-R0.2`, preserve Electrical V2.1 as a separate identifier, and reconcile 142 components, 181 total/168 named nets, 106 unresolved rows, 62 requirements, and 40 risks. Deployment and main-branch verification remain configuration gates. |
| B-003 no buildable HR-V0 mechanical definition | **Accepted; open** | Requires released dimensioned CAD/drawings, datums/tolerances, materials, shafts, bearings, fasteners, hard stops, guard, receiver, cable paths, mass properties, calculations, and proof evidence. |
| B-004 electrical package is not wireable | **Accepted; open** | All safety/power-critical part numbers, terminals, pin maps, conductor/protection selections, panel layout, and harness drawings remain `SELECTION REQUIRED`. ERC 0/0 is connectivity evidence only. |
| B-005 watchdog contact can defeat heartbeat energy removal | **Accepted; open safety-architecture blocker** | R14 explicitly removes safety credit from the current non-safety permit and firmware latch. Select and validate a hardware restart interlock that cannot restore either contactor before physical reset and a later distinct ARM action. |
| B-006 no SRS or PLr/SIL allocation | **Partially addressed; open** | `docs/safety-functions.md` now defines six preliminary functions, boundaries, safe responses, restart behavior, and evidence fields. Qualified PLr/SIL determination, category/architecture calculations, DCavg, MTTFd/B10d, CCF, fault exclusions, and validation remain open. |
| B-007 total response time/stopping distance undefined | **Partially addressed; open** | R14 requires complete sensor-to-energy-removal-to-motion-stop measurement and makes the 0.15 m/s TCP limit governing. No released time budget, pose-dependent stopping distance, or guard-clearance evidence exists. |
| B-008 K1/K2 DC interruption suitability unestablished | **Accepted; open** | Exact DC making/breaking duty, regenerative interruption, suppression, SCCR, life, and manufacturer-approved application data are required before contactor selection. |
| B-009 PE, DC bonding, shielding, and enclosure unresolved | **Accepted; open** | The single proposed DC 0 V/PE star point remains a proposal. Enclosure, PE continuity, creepage/clearance, shield treatment, fault return paths, and jurisdiction-specific evidence are required. |
| B-010 mass, COM, and inertia are unclosed allocations | **Accepted; open** | R14 demonstrates that the arm allocation fails and the leg target is not closed. A part-level BOM/CAD/measured ledger, COMs, inertia tensors, cable/battery mass, and reserve are required. |
| B-011 XH540 plus 1.5:1 continuous/impact margin unproved | **Accepted; open** | R14 corrects endpoint data and reduces the test speed band, but continuous/cyclic torque-speed-temperature, efficiency, backlash, compliance, shock, and life require W0 hardware evidence. |
| B-012 leg drivetrain/load paths undesigned | **Accepted; open** | Requires released joint CAD, belt/pulley/shaft/bearing/fastener calculations, tolerance stack, fatigue/impact cases, and proof/endurance tests. |
| B-013 safe power-loss behavior unresolved | **Accepted; open** | Remains a blocker for untethered walking. Select brakes, counterbalance, retained-energy ride-down, passive geometry, or an accepted-fall strategy and validate every released pose. |
| B-014 fall restraint not dynamically specified | **Accepted; open** | Static proof alone is insufficient. Define drop distance, arrest stroke, peak load, allowable acceleration, tether elasticity, attachment/rail loads, swing clearance, dynamic test, inspection, and retirement criteria. |
| B-015 battery/precharge/isolation/charging/regeneration are blocks only | **Accepted; open** | Chemistry, cells/pack, BMS, fuse, contactors, precharge, disconnect, charger interlock, telemetry, enclosure, fault current, and regeneration remain `SELECTION REQUIRED`. |
| B-016 foot-force and IMU electronics not implementable | **Accepted; open** | Sensor sheets remain functional interfaces. Exact sensors, analog front end, anti-aliasing, excitation/reference, calibration, PCB, protection, connector, EMC, and fault behavior require release. |
| B-017 real-time controller/firmware/bus timing absent | **Accepted; open** | No implemented controller, firmware, timing measurement, HIL, source, or fault-test evidence exists. R15 removes a document-level ownership contradiction only. |
| B-018 requirements draft and governance schema deficient | **Partially addressed; open** | R14 resolves all 62 requirement and release-document procedure references into 61 controlled procedure definitions and adds applicability controls. Owners, approvers, change history, passed evidence, and atomic requirement cleanup remain open. |

## MAJOR disposition

| ID | Current disposition | Controlled response and remaining evidence |
|---|---|---|
| M-001 XM540/XH540 data cross-contaminated | **Addressed on branch** | R14 corrects XM540-W270 to 10.6 N m at 12 V/4.4 A and keeps XH540 data separate. Continuous-duty evidence remains open. |
| M-002 static multipliers substitute for dynamics/fatigue | **Accepted; open** | Require configuration-specific inverse dynamics, impact/fall cases, fatigue spectra, and test correlation. |
| M-003 actuator side-load limits not reconciled | **Partially addressed; open** | R14 records XH540 radial/axial limits and mandates dual-supported output load paths; final geometry, life calculation, and proof remain open. |
| M-004 mechanical component calculations absent | **Accepted; open** | Fastener, shaft, bearing, belt, pulley, housing, and structural calculations await released CAD and load cases. |
| M-005 polymer material/process assumptions unspecified | **Accepted; open** | Select material, process, orientation, conditioning, inserts, allowables, fire/temperature behavior, and lot verification. |
| M-006 cable routing lacks geometric verification | **Accepted; open** | Requires CAD routes, bend/twist limits, strain relief, abrasion/pinch protection, flex-life tests, and service access. |
| M-007 guard thickness/mounting/clearance undefined | **Accepted; open** | Requires hazard geometry, stopping/drop envelopes, material/fastener design, access probes, and impact/retention tests. |
| M-008 50 A source ceiling not demonstrated | **Accepted; open** | Requires measured simultaneous-motion load profile, rail transient model, source foldback, voltage-drop, thermal, and protection coordination. |
| M-009 80 A-class tether is not a protection design | **Accepted; open** | R14 exposes voltage-drop/heating scale but does not select a tether. Fault current, conductor/connector limits, drag, strain relief, protection, and regeneration remain open. |
| M-010 no closed thermal model | **Accepted; open** | Requires loss maps, duty cycle, ambient/enclosure airflow, transient/steady-state model, instrumented correlation, and derating. |
| M-011 no regenerative sink/clamp | **Accepted; open** | R14 enumerates clamp/dump/storage/bidirectional options and test cases; hardware and thresholds remain `SELECTION REQUIRED`. |
| M-012 fuse discrimination/conductor sizing lacks inputs | **Accepted; open** | Fault current, cable length, ambient, bundling, insulation, installation, connector limits, inrush, duty, interrupt rating, and jurisdiction are still missing. |
| M-013 custom U2D2 data-only harness unreleased | **Partially addressed; open** | `docs/actuator-interface.md` prohibits ordinary full-pin branch joining, VDD-sense assumptions, and U2D2 Power Hub overloading. Exact harness drawings, pin views, parts, and continuity/no-backfeed tests remain open. |
| M-014 physical bus topology unspecified | **Accepted; open** | Release trunk/branch geometry, segment lengths, termination/biasing, shielding, grounding, separation, baud/return delay, and oscilloscope margin tests. |
| M-015 direct-drive outputs lack independent verification | **Accepted; open** | Reduced joints require output sensing; direct-drive error detection and safety role still need quantitative requirements and validation. |
| M-016 support-polygon margins unquantified | **Accepted; open** | Require CAD/measured foot geometry, COM/CoP/capture envelopes, friction, saturation, latency, and disturbance margins. |
| M-017 capture/recovery authority unbounded | **Accepted; open** | Define recoverable impulse/state set, step authority, joint/torque saturation, latency, and abort thresholds, then validate restrained. |
| M-018 friction and step-width definitions insufficient | **Accepted; open** | Define measurement conditions, floor/sole friction limits, nominal versus commanded step width, and wear/contamination effects. |
| M-019 controller ownership inconsistent | **Addressed on branch in R15** | `docs/control.md` now assigns HR-V0 bench execution to the Pi and HR-30 balance-critical estimation, stabilization, and actuator writes to the deterministic real-time controller, with a canonical authority table. Implementation remains absent. |
| M-020 fault responses conditional/unbounded | **Partially addressed; open** | R14 adds a canonical state machine and safety-function responses, but deterministic pose/fault timers, thresholds, energy states, and tested fallbacks remain open. |
| M-021 command-source security incomplete | **Accepted; open** | Requires threat model, authenticated command/update path, key management, secure boot/rollback, debug policy, segmentation, least privilege, and failure/fuzz tests. |
| M-022 logging/timing/calibration infrastructure absent | **Accepted; open** | Requirements exist, but clock/synchronization design, timestamp uncertainty, schema, calibration equipment/intervals, checksums, and retention do not. |
| M-023 critical qualification tests missing | **Partially addressed; open** | R14 adds the applicability register for EMC, ingress, transport, maintenance, misuse, endurance, thermal cycling, harness retention, and battery abuse. Standards, severities, fixtures, procedures, and evidence remain open. |
| M-024 equivalent-evidence bypass undefined | **Accepted; open** | Define mandatory inheritance, equivalence criteria, change-impact analysis, waiver authority, and non-waivable safety revalidation before release inheritance is used. |
| M-025 product classification/jurisdiction open | **Accepted; open** | Adult experimental machinery is a boundary, not a legal classification. Build/use jurisdiction, intended users, and qualified standards/legal applicability review are required. |
| M-026 3D rig cannot support packaging | **Accepted; open** | The rig remains a visual/fit reference only. Packaging requires parametric CAD, vendor envelopes, swept volumes, cooling, harness/service space, assembly study, and mass properties. |
| M-027 AK70 fallback carries system penalty | **Partially addressed; open** | The current BOM limits AK70 to a two-unit comparison article and explicitly records 24/48 V and CAN-domain impacts. A system trade remains required before any alternate baseline. |
| M-028 battery mass/runtime lacks measured power | **Accepted; open** | Measure gait peaks, average, regeneration, reserve, end-of-life, and temperature behavior before pack selection and mass/COM closure. |
| M-029 accuracy/saturation requirements missing | **Accepted; open** | Derive quantitative joint/output/estimator error budgets, saturation duration, tracking thresholds, and recovery limits from gait stability requirements. |
| M-030 unbraked arm gravity fall unbounded | **Accepted; open** | Require power-off tests by pose/payload and a selected catch, counterbalance, park geometry, guard, or receiver envelope. |

## MINOR disposition

| ID | Current disposition | Controlled response and remaining evidence |
|---|---|---|
| N-001 website metrics stale | **Addressed on branch/deployment** | Current presentation reports 62 requirements, 40 risks, 142 components, 181 total/168 named nets, and 106 unresolved rows. Source-generated metric automation remains desirable. |
| N-002 duplicate HR-30A evidence ID | **Addressed on branch in R15** | The redundant `INSPECT-PROD-002` occurrence is removed; exact IDs remain listed. |
| N-003 qualitative BMI088 label | **Addressed on branch in R15** | The BOM now labels BMI088 as a candidate and makes numeric range, bandwidth, noise, bias, shock/saturation, temperature, board integration, and test evidence selection gates. |
| N-004 compound requirements | **Accepted; open** | Split the named rows into atomic requirements with parent trace links without losing existing release evidence. |
| N-005 inconsistent unit notation | **Accepted; open** | Adopt a repository SI/style rule and lint; do not change manufacturer notation inside archived evidence. |
| N-006 manufacturer evidence not frozen | **Accepted; open** | Record immutable document identifiers/revisions and hashes, and archive vendor documents only where redistribution is permitted. |
| N-007 incomplete coordinate/sign conventions | **Accepted; open** | Release robot/world/link frames, positive rotations, zero poses, left/right mirroring, and polarity diagrams. |
| N-008 endurance statistics undefined | **Accepted; open** | Define independent trials, failure taxonomy, rerun/rework rules, confidence reporting, sample size, and acceptance rationale. |

## Reconciliation with Fable R11

The two independent reviews agree on the central blockers: absent buildable CAD; unselected protection/conductors; failed mass closure; incompatible fixed battery assumptions; unproven leg torque/speed/thermal performance; unsafe or undefined drive-energy-loss behavior; watchdog restart weakness; absent PLr/SIL work; incomplete verification; and no physical evidence. Sol adds useful breadth in dynamic restraint, response time/stopping distance, DC interruption, sensing circuits, real-time implementation, cybersecurity, logging/calibration, product classification, packaging, statistical evidence, and arm power-off behavior.

No conflict between reviewers currently justifies releasing a blocked subsystem. Where wording or calculation assumptions differ, the more conservative unresolved state controls until a configuration-specific calculation or physical test settles the issue.

## Current readiness after reconciliation

| Decision | Status |
|---|---|
| HR-V0 fabrication | Not ready |
| HR-V0 energization | Prohibited / not ready |
| HR-30A detailed design | System concept only |
| HR-30W walking feasibility | Physically plausible in principle; not established by the current design |
| Qualified mechanical review | Ready for concept/PDR and hazard review only |
| Qualified electrical review | Ready for architecture review after ECAD merge validation; not a wireable design review |
| Functional-safety review | Ready to begin SRS/PLr work; not ready for validation |

This disposition does not approve fabrication, procurement, energization, functional-safety performance, untethered operation, or operation around children.
