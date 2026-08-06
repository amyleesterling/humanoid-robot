# Disposition — Fable Independent Engineering Review R11

Review received: 2026-08-06  
Reviewed configuration: GitHub `main` at `ee276af…` plus published Electrical V2.1 artifacts  
Evidence file: `2026-08-06-fable-independent-engineering-review.txt`  
Evidence SHA-256: `b1e75a1e6d74537994b5cc918545a6d3fdd159b58567d4c57bc5677237ae2f54`  
Disposition status: provisional engineering triage; calculations and primary-source checks remain required  
Package status: **PRELIMINARY—NOT APPROVED FOR ENERGIZATION**

Fable reported 7 BLOCKER, 11 MAJOR, and 12 MINOR findings. This disposition records the findings without treating reviewer calculations as released design values. No mass allocation, actuator selection, transmission ratio, battery chemistry, safety topology, or operating envelope changes merely because the review proposed one.

## Blocker disposition

| ID | Disposition | Controlled response |
|---|---|---|
| B-1 authoritative repository lacked ECAD | Accepted; correction in progress | PR #3 adds the native V2.1 KiCad project, 15 sheets, schedules, validation records, and source manifest. Closure requires merge to authoritative `main`, a controlled revision/tag, and a post-merge clone/parse/ERC/hash check. |
| B-2 no buildable HR-V0 mechanical definition | Accepted; open | Remains a fabrication blocker. Close only with released dimensioned CAD/drawings, load paths, shafts, bearings, fasteners, stops, gripper, guards, tolerances, harness routing, and proof calculations/tests. |
| B-3 electrical protection and conductors unselected | Accepted; open | Preserve `SELECTION REQUIRED`. Close only after fault-current, foldback, length, ambient, bundling, connector, inrush, regeneration, duty-cycle, voltage-drop, jurisdiction, and selected-device evidence exists. |
| B-4 mass budget cannot close as allocated | Accepted for independent recalculation; open | Immediately create the supplier-mass ledger required by G-20. Reconcile the 1.30 kg two-arm target against proposed actuator mass and perform a controlled leg/whole-body buildup before actuator procurement or walking-feasibility claims. |
| B-5 4S chemistry / 14.8 V limit / torque basis conflict | Accepted; open | Select chemistry and conversion topology first, then repeat every leg torque/speed screen at loaded end-of-discharge voltage. Include regulator mass, heat, efficiency, transient behavior, and actuator absolute limits. |
| B-6 safe drive-energy-loss behavior unresolved | Accepted; existing blocker | G-18/G-23 remain closed. No untethered or human-facing walking until a selected mitigation passes pose-by-pose restrained fault testing. |
| B-7 incomplete leg-axis load analysis | Accepted; open | Extend the controlled load model to all six joint types at the 10 kg ceiling, worst poses, dynamic/impact/kneel/stand cases, and end-of-discharge voltage. Hip-roll direct drive is not a released baseline until measured evidence closes the screen. |

## Major disposition

| ID | Disposition | Controlled response |
|---|---|---|
| M-1 watchdog permit may restore power without monitored reset | Accepted and elevated as a safety-architecture blocker | Re-review exact V2.1 nets and hardware behavior. Require heartbeat-restoration testing proving contactors cannot re-energize without the intended physical reset/arm sequence. Do not credit a non-safety-rated firmware latch without accepted fault analysis. |
| M-2 no PLr/SIL integrity target | Accepted | Create a safety-requirements specification defining each safety function, PLr or justified alternative integrity target, architecture/category, diagnostics, CCF, fault exclusions, validation, and operating boundary. No compliance claim is authorized. |
| M-3 knee speed deficit at upper gait band | Accepted for recalculation | Add joint torque-speed trajectory screening at worst voltage and load before G-14. The 0.20 m/s target is not released performance. |
| M-4 XM540 stall citation mismatch | Accepted pending official-source recheck | Verify exact XM540-W270 variant, voltage, current, document revision/date, then correct `docs/mechanical.md`, BOM, and claim register together. |
| M-5 TCP and 30 deg/s limits conflict | Accepted | Make the TCP limit governing, define pose-dependent joint-rate enforcement, and test worst-case combined motion at maximum reach. |
| M-6 actuator radial-load and connector-current constraints absent | Accepted with qualification | Add the exact actuator radial-load value after primary-source verification. Do not adopt an approximate connector rating until the exact connector/contact MPN and derating evidence are selected. |
| M-7 verification IDs unresolved | Accepted | Define all referenced verification IDs, correct `INSPECT-ELEC-030` versus `TEST-ELEC-030`, add procedure stubs with method/instrument/acceptance fields, and make the checker reject undefined requirement and release-evidence IDs. |
| M-8 non-objective MUST requirements | Accepted | Add numeric timing, detection, thermal, lighting, stopping, and rubric thresholds or explicit controlled references. |
| M-9 environmental/endurance test categories missing | Accepted | Add an applicability table for EMC, ingress, transport, maintenance, abuse/foreseeable misuse, fatigue/endurance, thermal cycling, and connector retention, with test IDs or documented exclusions. |
| M-10 website distributes unreleased STLs | Accepted | Quarantine, watermark, or remove fabrication downloads until controlled `BUILD-RELEASE-*` status exists. Reference meshes must be unmistakably non-fabrication artifacts. |
| M-11 regeneration and DC switching remain open | Confirmed | Preserve as selection/test blockers; include supply OVP latch and controlled-stop integrity in regeneration testing. |

## Minor disposition

- `m-1`: already corrected; the controlled website displays 62 draft requirements.
- `m-2`: accepted; document the 15-page convention as root/index plus 14 checked child sheets.
- `m-3`: current controlled register contains 106 data rows. Add a counting rule and reject alternate representations as release counts unless mapped.
- `m-4` through `m-8`: accepted for clarification or calculation—moving-mass/payload scope, foot interference, U2D2 latency boundary, head torque, and tether voltage-drop/drag all need controlled treatment.
- `m-9`: benchmark confirmation recorded; no design closure follows from benchmark similarity.
- `m-10`: accepted; add the YM070 24 V domain mismatch to its rejection record.
- `m-11`: accepted; add voltage-domain and bus-architecture mixing to the AK70 hybrid-baseline trade.
- `m-12`: accepted; list all four ignored ERC check classes wherever ERC 0/0 is summarized.

## Readiness after R11

| Question | Disposition |
|---|---|
| HR-V0 build | Not ready |
| HR-V0 energization | Not ready |
| HR-30A design | Not ready |
| HR-30W walking | Unproven; current Baseline A assumptions require revision or evidence |
| Qualified mechanical review | Ready for concept review only |
| Qualified electrical review | Ready for architecture review after authoritative ECAD merge; not design review |
| Functional-safety review | Not ready |

## Correction order

1. Merge and post-merge validate the authoritative KiCad source correction.
2. Independently reproduce the new mass, voltage, torque, speed, TCP, and tether calculations in controlled calculation records.
3. Resolve the watchdog restart topology before crediting reset-to-motion prevention.
4. Create the safety-requirements specification and objective verification-procedure registry.
5. Correct only those numerical claims supported by current primary documents and recorded assumptions.
6. Obtain R12 independently before reconciling reviewer disagreements.

No finding is closed by this disposition alone.
