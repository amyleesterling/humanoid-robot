# HR-V0 non-contact event observation P0.1

> **PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION.**

Document ID: **HR-V0-NONCONTACT-EVENT-OBS-P0.1**

Round: **R179**

Date: **2026-08-10**

Electrical configuration: **Project Button Electrical V3-P1.15-CARRIER-CANDIDATE**

## Decision

The permanent passive-divider/AMC3330 field-adapter route is rejected for the current baseline. R178 established that Pilz does not publish an allowable parallel observer load for the five monitored input/start/EDM paths and that the two contactor-coil transient envelopes are unmeasured. A mathematically plausible divider therefore remains insufficient evidence for a physical connection.

R179 retains a non-contact AC/DC current-observation route for evaluation. A Tektronix `TCP0030A` jaw would surround one insulated conductor at a time. It would not make a galvanic field connection or add a resistor/capacitor return path to the monitored node. This removes the specific passive-tap loading mechanism; it does **not** establish noninterference, measurement validity, stopping performance, functional-safety performance, or work authority.

No new electrical adapter or connected KiCad circuit is issued. The R178 native KiCad one-sided no-connect boundaries remain the controlling electrical disposition.

## Exact conductor candidates

| Net | P1.15 wire number | Exact terminal | Candidate observation |
|---|---:|---|---|
| `SR1_S12` | `W2008` | `SR1:S12` | probe jaw around this conductor only |
| `SR1_START_RETURN` | `W2011` | `SR1:S34` | probe jaw around this conductor only |
| `ARM_AFTER_S2` | `W3021` | `S2:TBD-A2` | held until the received S2 terminal is exact |
| `K1_A1` | `W4001` | `K1:A1` | coil-feed current; return remains `K1:A2/SAFETY_0V` |
| `K2_A1` | `W4007` | `K2:A1` | coil-feed current; return remains `K2:A2/SAFETY_0V` |
| `EDM_K1_OUT` | `W4005` | `K1:22` | probe jaw around the conductor toward `K2:21` |
| `SRA1_START_RETURN` | `W3007` | `SRA1:S34` | probe jaw around this conductor only |

These are exact logical P1.15 locations, not released as-built conductors. Wire part number, gauge, insulation diameter, length, routing, segregation, terminal hardware and service-loop geometry remain `SELECTION REQUIRED`.

## Exact instrument evidence

Tektronix's current `TCP0030A` datasheet, document `51W-19042-12`, released 2025-04-10, identifies:

- DC to at least 120 MHz bandwidth;
- selectable 5 A and 30 A ranges;
- sensitivity down to 1 mA with a compatible host setting;
- 14.5 ns signal delay;
- 5 mm maximum conductor size; and
- direct operation with a compatible TekVPI oscilloscope.

The exact probe is an **evaluation candidate**, not a procurement selection. The host oscilloscope model/options, quantity of simultaneous probes, sample rate, record length, trigger, trace export, calibration and uncertainty remain `SELECTION REQUIRED`. The manufacturer's stated capability does not prove that the 50 mA Pilz steady current, the published 0.2 A pulses or the contactor-coil waveform can be classified with the Project Button thresholds and uncertainty budget.

## Disconnected-load E2 boundary

Any future comparison is restricted to the existing disconnected-load E2 concept:

1. the actuator source is physically absent;
2. K1/K2 load poles are unsourced and unwired;
3. no actuator, gripper or moving mechanism can receive power;
4. all seven conductors are reconciled unpowered before a jaw is fitted;
5. jaw-open and jaw-closed sequences are compared with the rest of the setup unchanged;
6. an independent motion witness and an accepted isolated 24 V rail witness share the accepted timebase for any stopping/no-motion claim; and
7. powered execution requires separate qualified authorization after every prerequisite is closed.

`electrical/analysis/hr-v0-noncontact-event-observation-p0.1/e2-comparison-sequence.csv` is an unexecuted procedure architecture. It is not permission to apply the 24 V source.

## Remaining blockers

The twelve controlled holds include as-built conductor identity, jaw fit, host selection, calibration, polarity/thresholds, jaw-open/jaw-closed noninterference, simultaneity, independent motion and source witnesses, the E2 boundary, a complete uncertainty budget, and qualified electrical/functional-safety disposition.

A current probe can observe conductor current without an electrical tap, but current alone does not prove:

- contact position;
- actuator-power removal at the unsourced load poles;
- motion stop;
- reset or ARM behavior without motion;
- source-rail integrity;
- a safety integrity level or performance level; or
- suitability for the later walking robot.

## Gate effect

- `EG-025` remains **open**.
- `EG-026` remains **partial**.
- zero electrical field taps are released;
- zero physical tests have executed;
- the probe, host and acquisition chain receive **zero safety credit**; and
- no procurement, fabrication, connection, powered test, motion or energization is authorized.

The Sol analysis supplied again on 2026-08-10 matches the controlled independent R12 verdict and is not counted as a new review round. R179 is a project-owned correction responding to that review's instrumentation, stopping-time and physical-evidence blockers.
