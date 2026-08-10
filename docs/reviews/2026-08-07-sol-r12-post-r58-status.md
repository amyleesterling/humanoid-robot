# Sol R12 status after R58 E2 commissioning-boundary pass

**PRELIMINARY - NOT APPROVED FOR FABRICATION OR ENERGIZATION**

Date: 2026-08-07

Independent review: Sol R12, resupplied 2026-08-07

Project response: R58 / `HR-V0-E2-SEQ-P0.1`

The supplied Sol analysis remains the already controlled R12 independent review, not a new independent-review round. R58 is a project-owned correction and is not an approval.

## Correction made

The previous E2 gate required `TEST-SAFE-001` through `TEST-SAFE-003`, while `TEST-SAFE-001` also required maximum-speed moving-arm stopping evidence. That combined a disconnected-load control-only stage with a later motion/stopping stage and could not be executed as written.

R58 separates the evidence scopes without weakening the final test:

- `TEST-E2-002` is the disconnected-load E2 subset. The 12 V actuator source must be physically absent and all actuator branches disconnected, covered and verified at zero volts.
- Full loaded interruption, stopping time, residual travel, guard-clearance reconciliation and PL/SIL validation remain later physical evidence and receive no credit from E2.
- A 15-step controlled sequence now defines authorization, isolation, unpowered inspection, site/PE/insulation review, ELV point-to-point proof, initial 24 V and compute application, RESET/ARM order, E-stop/watchdog/recovery fault matrices and controlled shutdown.
- Twenty logic cases explicitly test that heartbeat restoration and RESET alone keep both K1/K2 coils off.
- Four human roles must sign a configuration-specific authorization; the form is currently `NOT AUTHORIZED`.

## Sol finding disposition

| Sol concern | R58 state | Still required |
|---|---|---|
| No controlled first-energization evidence chain | Sequence, forms, roles, abort conditions and machine checker now exist. | Accepted site/article/configuration, completed physical inspections and tests, raw data and qualified signatures. |
| Reset/restoration could command motion | Planned cases explicitly require coils off after restoration and RESET-only; no actuator source exists at E2. | Execute against received hardware and validate later with motion/stopping evidence. |
| PE, grounding and enclosure assumptions unresolved | Dedicated qualified site/mains/PE/insulation form now records exact method, values and disposition without inventing limits. | Select the as-built policy, site, test limits and perform accepted measurements. |
| Point-to-point and no-backfeed evidence missing | Dedicated ELV form and procedure now require reference/terminal/net, polarity, isolation and no-backfeed evidence. | Release and build the harness, then execute with calibrated instruments. |
| Functional-safety approval absent | R58 expressly grants none. | Qualified risk assessment, allocation, validation and signed review remain open. |

EG-018 through EG-022 advance only from empty/open to template/partial. Through E2 the register reports 21 applicable gates, zero closed and 21 partial. No source connection is authorized.

Sol's central verdict remains correct: HR-V0 is not build-ready, energization remains prohibited, and walking feasibility is not demonstrated.
