# HR-V0 functional-safety allocation P0.1

Status: **PRELIMINARY—QUALIFIED ALLOCATION NOT EXECUTED—NOT APPROVED FOR ENERGIZATION**

Control date: 2026-08-07

## Decision

The ordinary Raspberry Pi heartbeat, RP2040 watchdog, firmware, relay drivers, Phoenix Contact relays, feedback circuit and bus watchdog are classified as `DF-01`, an **uncredited diagnostic control** for guarded HR-V0 testing. The risk assessment shall assume that `DF-01` can fail to demand a stop. Its nominal dropout and restart behavior still require physical testing because a diagnostic must not create a new hazard or impair a credited function.

The current candidate safety-related control functions for HR-V0 are:

- `SF-01`: emergency-stop actuator-energy removal; and
- `SF-03`: prevention of unexpected restart following a credited safety dropout.

Neither has an assigned PLr, category, achieved PL, or approval. Those values remain `SELECTION REQUIRED` until a qualified reviewer executes `ANALYSIS-SAFE-001` using the actual operating modes, exposure, guard, stopping, hardware, reliability and validation evidence.

`PG-01`, the tool-removable fixed guard/receiver/catch system, is a physical protective measure rather than an SRP/CS. It must be designed and validated against the worst-case swept, stopping and drop envelope **with DF-01 failure assumed**. It cannot be treated as released until `INSPECT-GUARD-001` and `TEST-DROP-001` pass with exact hardware.

For HR-30, or for any HR-V0 configuration where the fixed guard cannot contain the assumed control-loss case, `SF-02` remains a future required safety function. The project must then select a safety-rated control-loss architecture and allocate/validate its integrity; the ordinary watchdog cannot be promoted by documentation.

## Why this correction is necessary

Electrical V3 improves nominal restart order: heartbeat dropout opens both SR1 input returns, then recovery requires physical RESET followed by a distinct physical ARM. That is useful diagnostic and restart behavior. It does not make the shared ordinary controller, clock, firmware, supply, drivers or relays a safety-rated two-channel system. A stuck-valid heartbeat, stuck driver or welded contacts can defeat the heartbeat-driven stop demand.

The fixed E-stop NC contacts remain nominally in series with the SR1 input channels. A welded watchdog contact should not by itself bypass its corresponding E-stop contact, but R86 proves that this is not the complete fault boundary: KWD A1 and 21 carry `SAFETY_24V`, while KWD terminal 14 returns downstream of S0 to `SR1:S12` or `SR1:S22`. An internal or panel bridge to 14 could inject voltage after an E-stop contact. `WDF-008`, `WDF-011`, and `WDF-012..016` therefore remain safety-critical open cases. See `docs/hr-v0-watchdog-common-cause-p0.1.md`.

## Controlled allocation

The machine-readable allocation is `safety/hr-v0-safety-function-allocation.csv`. Its classification rules are:

| Classification | Meaning | Safety credit now |
|---|---|---|
| `credited_candidate` | Proposed SRP/CS boundary requiring qualified PLr/SIL allocation, calculation and validation | none until approved |
| `physical_protective_measure` | Guard or inherently physical risk-reduction measure | only after physical release; no PL label |
| `uncredited_diagnostic` | Ordinary control whose failure is assumed in the safety assessment | zero |
| `future_safety_function` | Required when the qualified hazard/exposure analysis establishes the need | none; architecture selection required |

No row may claim a PL or SIL while its risk inputs, architecture calculation or validation remain unresolved.

## Qualified allocation inputs

The reviewer shall complete `tests/forms/hr-v0-functional-safety-allocation-template.csv` and preserve:

1. every operating mode and lifecycle task, including setup, calibration, normal motion, fault recovery, maintenance and foreseeable misuse;
2. hazard severity, frequency/duration of exposure, possibility of avoidance, existing non-control measures, and the documented risk method;
3. each credited function's initiator, logic, final element, safe state, restart rule, response-time budget and demand assumptions;
4. selected PLr or SIL, architecture/category, MTTFd/B10d, DCavg, CCF measures, systematic measures and mission/proof-test assumptions;
5. every fault exclusion and dependent/common-cause failure, including shared 24 V, enclosure, routing, contamination, relay welding, feedback faults and contactor behavior;
6. a validation plan tied to ISO 13849-2:2012 or the selected IEC 62061 method; and
7. reviewer competence, independence, signatures and residual-risk disposition.

The project shall use the complete controlled standard obtained by the responsible organization; public abstracts establish scope and revision only.

## Current standards basis

- ISO 12100:2010, Edition 1, published 2010-11, remains current but is under revision; its official abstract defines the machinery risk-assessment and risk-reduction methodology. Rechecked 2026-08-07: https://www.iso.org/standard/51528.html
- ISO 13849-1:2023, Edition 4, published 2023-04, defines the methodology for SRP/CS that perform safety functions and explicitly does not prescribe the PLr for a particular application. Rechecked 2026-08-07: https://www.iso.org/standard/73481.html
- ISO 13849-2:2012, Edition 2, published 2012-10, remains the published validation standard while a replacement draft is under development. Its official abstract covers validation by analysis and testing of safety functions, category and achieved PL. Rechecked 2026-08-07: https://www.iso.org/standard/53640.html
- IEC 62061 current official lifecycle evidence includes IEC 62061:2021 plus Amendments 1:2024 and 2:2026; it covers design, integration and validation of safety-related machine control systems. Rechecked 2026-08-07: https://webstore.iec.ch/en/publication/92835
- ISO 13850:2015, Edition 3, published 2015-11, specifies emergency-stop functional requirements and design principles. Rechecked 2026-08-07: https://www.iso.org/standard/59970.html
- ISO 14120:2015, Edition 2, published 2015-11 and confirmed in 2021, specifies general requirements for fixed and movable guards. Rechecked 2026-08-07: https://www.iso.org/standard/59545.html
- Pilz PNOZ s4 operating manual `21396-EN-23`, colophon 2026-02 and current product file dated 2026-06-22, supports component-mode screening only. It does not assign the project PLr or validate the complete function: https://www.pilz.com/download/open/OM_PNOZ_s4_21396-EN-23.pdf

## Release consequences

- `SAFE-003` now requires a separately allocated safety-rated control-loss function when exposure demands one.
- `CTRL-007` controls the ordinary HR-V0 watchdog diagnostic and preserves the 300 ms candidate detection test without calling it a safety limit.
- `SAFE-008` now matches the hardware architecture: physical RESET, later distinct physical ARM, then a fresh validated trajectory.
- `TEST-SAFE-002` is retained as a historical identifier but explicitly verifies an uncredited diagnostic only.
- `EG-012` remains partial. R86 supplies 18 exact paths, 32 open failure modes, 12 common-cause groups, 28 unexecuted cases and 16 separation controls, but topology non-interference, qualified allocation, protected routing, physical fault injection and timing evidence remain open.

This correction removes an unjustified safety claim. It does not close Sol `B-005` or `B-006`, assign a PLr/SIL, approve a component, release a guard, or authorize fabrication or energization.
