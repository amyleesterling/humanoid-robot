# HR-V0 E2 control-only commissioning package P0.1

**PRELIMINARY - PROCEDURE CANDIDATE ONLY - NOT AN AUTHORIZATION TO CONNECT OR ENERGIZE ANY SOURCE**

Date: 2026-08-07

Identifier: `HR-V0-E2-SEQ-P0.1`

Applies to: HR-V0 only, exact accepted configuration to be recorded

## Purpose and hard boundary

E2 is the first possible powered stage, but it is not actuator energization. Only the accepted 24 V safety/control source and 5.1 V compute source may be connected. The 12 V actuator source must be physically absent from the test boundary, disconnected at both AC and DC, and every actuator branch and actuator plug must be disconnected, covered, labeled and verified at zero volts.

This package defines what qualified humans must review, inspect, test and sign. It does not provide those signatures and it does not close a gate. Repository checks cannot establish electrical safety, functional-safety performance, reviewer competence, site suitability or permission to energize.

The controlled sequence is `tests/e2/hr-v0-e2-control-only-sequence.csv`. It is fail-closed: each step names its prerequisites, required source states, required E-stop state, observation, abort condition, evidence file and responsible role. Any mismatch, unexpected voltage, unauthorized state, expired calibration, open deviation, role conflict, configuration change or exclusion-zone breach revokes the run and requires `E2-140` controlled shutdown.

## Stage correction

The historical `TEST-SAFE-001` description combines two evidence scopes:

1. disconnected-load logic and restart behavior, which can be tested at E2; and
2. loaded interruption, stopping time and residual travel, which cannot be tested until an actuator is connected at a later authorized stage.

`TEST-E2-002` is now the controlled E2 subset of `TEST-SAFE-001` through `TEST-SAFE-003`. It may prove relay/contactor-coil logic, channel response, monitored RESET, distinct ARM, diagnostic dropout and no automatic restart while no actuator energy exists. It cannot prove stopping distance, guard clearance, loaded contactor interruption, achieved PL/SIL, or motion safety. Those later claims still require the full procedures and physical evidence.

## Entry conditions

No connection may begin unless all of the following are true for the exact article and commit:

- Every gate applicable before or at E2 is closed by accepted executed evidence, not merely marked partial by project documents. EG-009 is an E4 gate and is not silently pulled into E2 by its numeric identifier.
- The release manifest reproduces from a clean clone and the accepted commit is recorded on every form.
- `INSPECT-E2-001`, `INSPECT-E2-002` and `TEST-E2-001` have passed with signed dispositions.
- Exact received source, control-device, terminal, conductor, protection, enclosure, guard, stop and firmware identities agree with the accepted baseline.
- The test director, qualified electrical reviewer, functional-safety reviewer and independent witness sign `hr-v0-e2-authorization-template.csv` for this run. Competence and independence evidence is attached where required.
- The exact site, receptacle, branch/GFCI basis, external factory adapters, cords, disconnect/LOTO method, test instruments and numerical limits are accepted.
- Children and all uninvolved people are excluded. The fixed guard remains installed even though no actuator source is present.

## Permitted source architecture

The candidate control source is GlobTek `WR9QI1660YL4NKITR6B`, 24 V / 1.66 A, with its factory `YL4/C40337` locking cord; the candidate compute source is the official Raspberry Pi 27 W USB-C supply. Both remain proposed until receiving/application evidence closes. The control source is Class II/floating and uses an interchangeable Q-NA blade from its factory kit; no project 0 V/PE bond is inferred. Factory AC inputs must remain unmodified; project-built mains wiring is outside this candidate.

The Pilz `PNOZ s4` 750104 records support 24 V DC operation, two inputs, three safety N/O outputs, manual/automatic start modes and current operating-manual revision 21396-23 dated 2026-06-22. The current product record and manual do not validate this project application. Received identity, selector position, protected reset/EDM routing, output protection, device timing, fault tests and qualified functional-safety review remain mandatory.

The Raspberry Pi supply product record gives 100-240 VAC, 50-60 Hz input and 5.1 V / 5 A output. Its compliance documentation does not certify the complete robot or site installation.

Primary records verified 2026-08-07:

- Mean Well `GST40A` specification, file `GST40A-SPEC 2026-04-03`: https://www.meanwell.com/Upload/PDF/GST40A/GST40A-SPEC.PDF
- Pilz `PNOZ s4` 750104 product/download record, including operating manual 21396-23 dated 2026-06-22: https://www.pilz.com/en-US/eshop/product/750104
- Raspberry Pi 27 W USB-C Power Supply product record: https://www.raspberrypi.com/products/27w-power-supply/
- Schneider `LC1D25BD` product record. Its AC-3 headline is not evidence of the required project DC interruption behavior: https://www.se.com/in/en/product/LC1D25BD/

## Required evidence files

| Gate | Candidate evidence input | Current state |
|---|---|---|
| EG-018 | `tests/forms/hr-v0-e2-unpowered-configuration-template.csv` | template only; not executed |
| EG-019 | `tests/forms/hr-v0-e2-mains-pe-insulation-template.csv` | template only; limits/site/measurements open |
| EG-020 | `tests/forms/hr-v0-e2-elv-point-to-point-template.csv` | template only; harness and readings open |
| EG-021 | `tests/forms/hr-v0-e2-safety-logic-template.csv` | 20 planned disconnected-load cases; not executed |
| EG-022 | `tests/forms/hr-v0-e2-authorization-template.csv` | explicitly `NOT AUTHORIZED` |

Raw files are append-only evidence. A rerun gets a new authorization ID and record IDs; a failed result is never overwritten. Every record must identify commit, article, site, instruments, calibration, operator, witness, raw-data references, nonconformances and signed disposition.

## Measurement and fault-injection rules

- Use isolated or properly rated measurement channels. Probe grounds must not create a second `SAFETY_0V`, PE or source return path.
- Test equipment ratings, CAT category where applicable, bandwidth, isolation and calibration must be accepted for the exact measurement.
- Do not apply a megohmmeter or dielectric withstand voltage through connected electronics unless the exact manufacturers and qualified reviewer explicitly permit the method and voltage. Disconnect sensitive electronics or use an accepted alternative.
- No loose jumper, hand-held short or improvised bridge is an acceptable safety fault injector. The approved fixture must have guarded contacts, current/energy limits, labeled states and an independently verified schematic.
- A zero-volt observation uses a separately approved threshold and live-dead-live meter check. This document does not invent that threshold.
- `S1` RESET and `S2` ARM terminals remain `TBD-*` until the received-lot mapping procedure closes. No test may infer those terminals from color or earlier drawings.

## Required state sequence

The essential state order is:

`all sources absent -> unpowered configuration/PE/ELV proof -> E-stop pressed -> 24 V control on -> compute on -> E-stop release does nothing -> valid monitored RESET may make SR1 ready but coils stay off -> later distinct ARM may energize K1/K2 coils -> no actuator voltage exists -> any safety/diagnostic dropout removes the appropriate permit -> restoration alone does nothing -> RESET alone still leaves coils off -> later ARM required -> controlled shutdown`

Neither RESET nor ARM may generate torque, motion or a trajectory. A valid ARM at E2 may energize only the K1/K2 24 V coils and change their auxiliary/mirror contacts; it must not energize an actuator conductor because the actuator source and branches are absent.

## Stop-work conditions

Stop immediately, press E-stop if safe to do so, disconnect compute then 24 V control, verify dead and quarantine the article if any of these occurs:

- any nonzero/unexpected voltage on `ACT_12V_RAW`, a contactor load side, `J1_VDD`, `J2_VDD` or `J3_VDD`;
- K1/K2 coil action before the accepted distinct-ARM state or automatic re-energization after restoration/reset;
- mismatch between relay, mirror, auxiliary, indicator and logged states;
- smoke, odor, heating, chatter, arcing, damaged insulation, loose conductor or unexpected source behavior;
- failed E-stop channel, failed safe dropout, unsafe fault-injection state or measuring-instrument saturation;
- changed commit, hardware, firmware, wiring, site, instrument, role or procedure after authorization;
- lost communication, expired authorization/calibration, open nonconformance or person entering the exclusion zone.

## Exit and disposition

After planned completion or any abort, execute `E2-140`: E-stop pressed, compute removed, 24 V removed, stored-energy wait completed, all relevant rails checked live-dead-live, disconnects/LOTO restored, data secured and abnormal conditions quarantined. The qualified reviewers decide whether the run is accepted, repeated or rejected.

Passing E2 would permit only the separately written next-stage review. It would not authorize actuator connection, motion, fabrication, human exposure, child-adjacent use or HR-30 work.

**CURRENT VERDICT: NOT EXECUTED; NOT AUTHORIZED; NOT APPROVED FOR ENERGIZATION.**
