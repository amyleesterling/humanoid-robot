# R200 validation record

> **PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION**

Artifact: `HR-V0-RUNTIME-OBS-P0.1`

Date: 2026-08-10

## Correction

- Superseded R199's incorrect “nine physical observations” statement.
- Traced four positive panel status candidates to exact sheets, references, terminals, nets and XT1 positions.
- Kept control power, E-stop health, watchdog health, EDM health and compute undervoltage as five distinct unavailable providers.
- Kept bus health software-derived from exact transport operations.
- Rejected inversion of unused 41-42 NC auxiliary contacts into positive ready claims because an open conductor could resemble the changed state.
- Added explicit unknown observation semantics to the supervisor. Unknown values inhibit heartbeat and motion.
- Reduced the GPIO schema to `SR1_STATUS`, `SRA1_STATUS`, `K1_STATUS` and `K2_STATUS` while leaving every line and polarity unselected.
- Recorded twelve open closure holds and created an interactive observation guide.

## Executed source checks

- `tools/check_hr_v0_runtime_observation_p01.py`: passed; 4 positive panel states, 5 unavailable health providers, 1 software bus result and 12 open holds.
- Firmware supervisor/runtime suite: 67/67 tests passed; three tests directly cover unknown observation behavior.
- Watchdog suite: 11/11 tests passed; total firmware count 78/78.
- Host suite: 16/16 tests passed.
- Host preflight: expected exit 78 with 45 holds before backend import.
- Host deployment and runtime execution checkers passed.
- Complete standard-runtime sweep: 143/143 checkers passed.
- Native KiCad `pcbnew` sweep: 13/13 checkers passed.
- Deterministic release manifest: 3,400 package files before this validation-record update; regenerated after it.
- `check_energization_gates.py --through E2 --require-ready` returned its documented non-ready exit 2: 0/21 gates closed and all 21 partial.

## Electrical boundary

No receiver schematic is released. `SR1_STATUS` remains specifically blocked because SR1:Y32 already drives H1 and the sum of exact received lamp current plus worst-case receiver current has not been proven within Pilz's 20 mA limit. K1/K2 receiver current must meet Schneider's 5 mA and 17 V minima. ISO1212 remains only an evaluation architecture; passives, protection, connectors, layout, GPIOs, grounding, isolation and physical evidence are open.

No native KiCad source was changed in R200. The current P1.15 electrical package remains the trace authority; the future observation interface must be added as connected native source only after the load and provider architecture is resolved.

## Boundary

No target image, GPIO, receiver, health provider, wire, connector, HIL, waveform, fault injection, powered test or motion result exists. Zero functional-safety credit is claimed. No Sol finding, requirement, energization gate or work authorization closes.
