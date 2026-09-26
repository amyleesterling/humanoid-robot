# Project Button — build convergence

**Selected engineering candidate: HR30-TETHER-LIGHT4-P0.1. Not a build release.**

Button remains a complete 762 mm humanoid with 25 active axes, two functional hands, a face, audio/vision, conversational intelligence, and a local deterministic motion boundary. Whole-body walking remains the goal. An instrumented joint is development equipment, not a replacement deliverable. Tether-first testing does not silently remove the eventual onboard-power and untethered requirements.

## Start here

[Active whole-body visual guide](hr30/whole-body-p0.1/active-light4-p0.1/index.html) · [Complete engineering showcase](hr30/whole-body-p0.1/index.html) · [Critical-joint test package](hr30/build-release/critical-joint-test.md) · [Open release decisions](hr30/build-release/blockers.csv)

The machine-readable [baseline lock](hr30/build-release/baseline.lock.json) selects exact existing artifacts at commit `174691255409336a7e25ba1505217859c98c3f80`; it does not regenerate or copy the robot. This is the entry point for the build-release sprint. Older generated package pages retain historical values and must not override these explicit roles.

| Role | Selected source / boundary |
| --- | --- |
| Whole-body geometry | `lightweight-hip-successor-p0.1/HR-30_light4_whole_body_candidate.step` and matching GLB under `hr30/whole-body-p0.1/` |
| Dynamics model | `active-light4-p0.1/hr30_tether_light4_active.urdf` and `.xml` |
| Existing control evidence | `active-light4-p0.1/hr30_tether_light4_ideal_fixture.xml`; the base is supported by a six-degree-of-freedom trajectory weld, not free balance |
| Current planning mass | 9.879813509 kg; 0.120186491 kg below the 10 kg ceiling; no as-built mass or adequate reserve demonstrated |
| Hip pitch/roll | LIGHT4 4:1 on four axes; the old 1.5:1 pitch / 2:1 roll allocation rows are explicitly superseded |
| First test candidate | `R_ANKLE_PITCH`, XM430-W350-R with the LD-25 2.5:1 drive; decision experiment, not approved hardware |
| Other systems | Existing electrical, harness and software packages remain candidates; cross-system build-release reconciliation is open |

The 9.928 kg base ledger and the earlier control-successor result are not the selected LIGHT4 mass/control evidence. The older allocation CSV is reused for its unchanged ankle definition, not adopted wholesale as the active hip allocation. The checker records those four supersessions explicitly.

## Reproduce this sprint's checks

Python 3.10+; standard library only. No network, hardware connection, CAD toolchain, or simulator is invoked.

```sh
python tools/check_hr30_build_baseline.py
python -m unittest discover -s tests -p 'test_hr30_build_baseline.py' -v
# Optional: verify the nine referenced larger assets, if present locally.
python tools/check_hr30_build_baseline.py --full-assets
```

Default execution verifies the exact SHA-256 of three small source files, checks all 23 rotary demand rows and the reduced-leg allocation, reproduces the mass and joint-selection arithmetic, and totals the budget. The two grippers are not silently counted as rotary torque rows. `--full-assets` hashes additional files; even that does not validate geometry, structural capacity, or physics.

On 2026-09-25, the default audit ran against three connector-retrieved source snapshots whose bytes matched the existing source-manifest hashes. **31 synthetic software tests passed**, including stale hashes, missing/duplicate axes, NaN, invalid ratios, authority promotion, wrong adapters, and budget errors. See [the generated audit result](hr30/build-release/validation.json). No complete clone, large-asset audit, CAD rebuild, simulation rerun, physical test or independent engineering approval occurred in this sprint.

## The decision-driving finding

The pinned ideal-fixture table gives right ankle pitch 6.433 Nm peak and 5.645 Nm RMS, about 85% of its linear current-limited endpoint. The [manufacturer](https://robotis.us/products/dynamixel-xm430-w350-r) lists 0.82 Nm as an **estimated** continuous motor torque, explicitly calculated as 20% of stall torque. At the model's 2.5:1 reduction and assumed 85% efficiency, that heuristic becomes 1.7425 Nm at the joint. The modeled RMS demand is approximately 3.24 times that value.

This is a significant sizing question, not a proven thermal failure or a test acceptance limit. Fixture-assisted demand, joint RMS torque, motor current and real thermal duty are not interchangeable. The next physical decision is whether to retain or revise this actuator/transmission combination after independent load-profile review and measurement. No full-leg or whole-robot bulk order is justified by the present endpoint pass.

## First-tranche planning cost

The [budget](hr30/build-release/first-tranche-budget.json) records $392.16 in displayed catalog prices for one actuator, U2D2 and hub. Including explicitly unquoted allowances for review, a guarded joint fixture, drivetrain parts, laboratory access, execution, protection and one rebuild gives **roughly $3,500–$8,600 before tax/shipping**. This is a scope-planning range, not a supplier quote or spending request. Availability and exact product revisions are unconfirmed; existing owned equipment has not been verified.

## Work boundaries and next gate

The test package states the required inputs and decisions for a qualified mechanical/electrical integration partner. It is review-ready as a brief, **not ready to fabricate or energize**. A priced supplier scope, reviewed load waveform, fixture/protection design, numeric abort/acceptance limits and Amy's explicit spending/fabrication approval are still required.

Do not change firmware to permit motion, remove physical holds, order parts, rewrite Git history, or revive the archived arm-only analysis chain in response to this source audit passing. Children remain outside preliminary powered test areas; any later child-adjacent use is a separately reviewed end state.

The [previous full README](README.pre-build-release-2026-09-25.md) is preserved byte-for-byte using its existing Git blob. Its relative links retain their original repository-root context. All historical models, traces, rejection evidence and guides remain in place. This sprint adds no generated STEP/GLB or duplicate release bundle.
