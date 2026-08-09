# HR-V0 integrated unpowered build traveler P0.1

**PRELIMINARY - NOT APPROVED FOR FABRICATION, CONNECTION, MOTION, OR ENERGIZATION**

Identifier: `HR-V0-BUILD-TRAVELER-P0.1`

Round: R144

Date: 2026-08-09

## Purpose

R144 supplies the missing integrated assembly order for the current HR-V0 candidate. It links configuration control, receiving, Boston site/bench survey, control-panel mechanical work, frame dry assembly, joint metrology, custom first articles, final arm assembly, guard/receiver installation, harness fabrication, unpowered electrical assembly, compute/firmware staging and integrated inspection.

The traveler contains 14 phases, 85 steps, 14 phase hold points and a mapping for all 21 gates applicable through E2. Each step identifies required controlled inputs, required evidence, candidate owner role, stop-work behavior and energy boundary.

## Fail-closed state

- 0 steps authorized.
- 0 steps executed.
- 0 hold points closed.
- Every named executor, reviewer and releaser remains `SELECTION REQUIRED`.
- BT-P13, connection and powered work, is `PROHIBITED` under this traveler.
- No generated row is physical evidence or a work permit.

The traveler cannot be executed sequentially merely because it exists. Each phase requires exact accepted inputs, named competent people, phase-specific written authority and signed results. Fabrication, harness construction, assembly, connection and powered testing retain their separate gates.

## Controlled outputs

- `assembly/hr-v0-build-traveler-p0.1/build-phases.csv`
- `assembly/hr-v0-build-traveler-p0.1/build-steps.csv`
- `assembly/hr-v0-build-traveler-p0.1/gate-phase-matrix.csv`
- `assembly/hr-v0-build-traveler-p0.1/hold-points.csv`
- `assembly/hr-v0-build-traveler-p0.1/source-register.csv`
- `assembly/hr-v0-build-traveler-p0.1/build-traveler-summary.json`
- `release/hr-v0/build-traveler-p0.1/index.html`
