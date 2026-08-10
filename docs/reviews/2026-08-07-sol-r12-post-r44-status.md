# Sol R12 status after R44 functional-safety allocation correction

Status: **PROJECT-OWNED RECONCILIATION—NOT AN INDEPENDENT REVIEW OR APPROVAL**

Date: 2026-08-07

Baseline reviewed by Sol: the R12 pre-correction configuration

Current correction: R44 / `HR-V0-FSA-P0.1`

## What R44 changes

R44 removes an unjustified functional-safety implication rather than claiming a higher integrity level:

- classifies the Raspberry Pi/RP2040/ordinary-relay heartbeat path as `DF-01`, an uncredited diagnostic whose failure is assumed;
- limits current HR-V0 credited candidates to `SF-01` E-stop and `SF-03` prevention of unexpected restart, both still without assigned PLr/category/achieved PL;
- classifies the fixed guard/receiver/catch as `PG-01`, a physical protective measure requiring release against worst-case motion with `DF-01` failed;
- requires a separately selected safety-rated `SF-02` for HR-30 or any HR-V0 configuration whose guard cannot contain assumed control-loss motion;
- corrects `SAFE-003`, `SAFE-008`, adds `CTRL-007`, and makes the historical `TEST-SAFE-002` identifier explicitly diagnostic-only;
- adds an eight-row function/allocation register, eleven open watchdog-boundary FMEA cases, a qualified-review template, two analysis procedures and a machine checker; and
- updates `EG-012`, which remains partial.

## Sol finding disposition

| Finding | R44 status | Remaining evidence |
|---|---|---|
| `B-005` non-safety watchdog contact can defeat heartbeat energy removal | **Claim corrected; physical non-interference still open** | `DF-01` now receives zero safety credit. Routed PCB/harness separation, contact faults, common-cause analysis, physical fault injection and proof that `DF-01` cannot impair `SF-01`/`SF-03` remain mandatory. |
| `B-006` no SRS or PLr/SIL allocation | **Framework materially advanced; allocation open** | Function boundaries and an execution form now exist, but severity/exposure/avoidance inputs, selected PLr/SIL, category, MTTFd/B10d, DC, CCF, systematic measures, validation and qualified signatures remain `SELECTION REQUIRED`. |
| `B-007` total response/stopping distance undefined | **Unchanged; open** | The 300 ms value is now explicitly a diagnostic detection candidate, not a safety stopping limit. Full detection-to-rail-decay-to-motion-stop measurement and guard clearance remain open. |
| `M-006/M-007` cable/guard physical definition | **Unchanged; open** | `PG-01` cannot be credited until exact guard, routing, stopping/drop envelope and physical tests close. |

## Current verdict

- **HR-V0 fabrication readiness:** not ready.
- **HR-V0 energization readiness:** prohibited; no gate closes in R44.
- **Functional-safety review readiness:** improved for allocation work; not ready for PL/validation approval.
- **HR-30 walking:** requires a separate `SF-02` architecture and all previously open walking evidence.

R44 assigns no PLr, SIL, category, achieved PL, functional-safety approval, fabrication release or permission to energize.

**PRELIMINARY—NOT APPROVED FOR FABRICATION OR ENERGIZATION.**
