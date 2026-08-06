# Humanoid Robot Program

Package baseline: **HR-30-SYS-R0.2**  
Status: **concept systems baseline, not approved for fabrication, procurement, or energization**  
Baseline date: 2026-08-06

This repository is the engineering source of truth for a staged **30-inch (762 mm) humanoid-robot program**. The first build is **not a walking humanoid**. It is HR-V0, a bench-mounted, guarded handoff demonstrator with one shoulder axis, one elbow axis, and one parallel gripper. Its validated architecture then becomes HR-30, a child-sized but not child-safe robot.

## Program sequence

1. HR-V0 proves the power, communications, watchdog, emergency-stop, joint-control, thermal, and handoff-test architecture on a bench.
2. HR-30A adds a 13-DOF head, torso, two arms, and two grippers on a bolted child-height pedestal.
3. HR-30B adds the full 30-inch silhouette and supported legs, with fall restraint attached at all times.
4. HR-30C proves powered stance and weight transfer after structural, thermal, fall, and safety gates pass.
5. HR-30D demonstrates dynamic walking under a slack overhead fall-arrest tether.
6. HR-30W is the required end-state: untethered level-floor walking in a controlled test area. Human-facing walking requires a later safety release.

No child may enter the test area during V0. Any later child-adjacent demonstration requires an independent risk assessment, qualified mechanical/electrical review, validated force and stopping limits, and a new released revision.

## Start here

- [Configuration management and revision hierarchy](docs/configuration-management.md)
- [Current engineering handoff](docs/handoff-current.md)
- [Complete review ledger](docs/review-ledger.md)
- [System specification](docs/system-specification.md)
- [30-inch product specification](docs/full-body-specification.md)
- [Dimension-control specification](docs/dimension-control.md)
- [Full-body load and power budget](docs/full-body-loads.md)
- [R11 independent engineering calculations](docs/r11-engineering-calculations.md)
- [Sub-meter humanoid benchmark](docs/architecture-benchmark.md)
- [Walking-system specification](docs/walking-system.md)
- [Walking verification matrix](docs/walking-verification.md)
- [Mechanical concept and load model](docs/mechanical.md)
- [HR-V0 native CAD and quote geometry](cad/hr-v0/README.md)
- [HR-V0 Mechanical R0.1 preliminary baseline](docs/hr-v0-mechanical-r0.1.md)
- [HR-V0 PCD22 fit-coupon procedure P0.1](docs/hr-v0-fit-coupon-procedure-p0.1.md)
- [Electrical and safety architecture](docs/electrical.md)
- [Safety-function requirements](docs/safety-functions.md)
- [Actuator and harness interface constraints](docs/actuator-interface.md)
- [Native KiCad Electrical V2.1 source](electrical/kicad/project-button-v2/README.md)
- [Native KiCad Electrical V3-P0.4 correction candidate](electrical/kicad/project-button-v3/README.md)
- [HR-V0 Electrical V3 candidate architecture](docs/hr-v0-electrical-v3-candidate.md)
- [HR-V0 Boston build-site basis](docs/hr-v0-build-site-basis.md)
- [Boston fabrication and custom-metal sourcing](docs/hr-v0-fabrication-sourcing-boston.md)
- [Control and fault-state specification](docs/control.md)
- [HR-V0 Firmware P0.1 implementation candidate](docs/hr-v0-firmware-p0.1.md)
- [HR-V0 watchdog hardware interface P0.2](docs/hr-v0-watchdog-interface-p0.2.md)
- [HR-V0 calculated watchdog feedback receiver P0.1](docs/hr-v0-watchdog-feedback-p0.1.md)
- [Firmware source area](firmware/README.md)
- [Verification plan](docs/verification.md)
- [Verification scope and applicability](docs/verification-scope.md)
- [Verification procedure registry](tests/procedures/procedure-registry.csv)
- [Open decisions](docs/open-decisions.md)
- [Evidence maturity dashboard](docs/evidence-maturity.md)
- [Independent review disposition](docs/independent-review-disposition.md)
- [Fable R11 review and disposition](docs/reviews/2026-08-06-fable-review-disposition.md)
- [Sol R12 review and disposition](docs/reviews/2026-08-06-sol-r12-review-disposition.md)
- [Sol R12 findings rechecked against R17](docs/reviews/2026-08-06-sol-r12-post-r17-status.md)
- [Sol R12 findings rechecked against R18](docs/reviews/2026-08-06-sol-r12-post-r18-status.md)
- [Sol R12 findings rechecked against R19](docs/reviews/2026-08-06-sol-r12-post-r19-status.md)
- [Sol R12 findings rechecked against R20](docs/reviews/2026-08-06-sol-r12-post-r20-status.md)
- [Electrical V3-P0.4 independent review request](docs/reviews/2026-08-06-electrical-v3-independent-review-request.md)
- [Firmware P0.1 independent review request](docs/reviews/2026-08-06-firmware-p0.1-independent-review-request.md)
- [Requirements](requirements/requirements.csv)
- [HR-V0 energization gate register](requirements/hr-v0-energization-gates.csv)
- [Proposed bill of materials](bom/bom.csv)
- [Risk register](safety/risk-register.csv)

Run `python tools/check_traceability.py` from this directory to ensure every requirement has at least one verification method and all risk controls reference valid requirements. Run `python tools/check_hr_v0_cad.py` after regenerating mechanical artifacts to verify part sets, readable warnings, vendor hashes, assembly exports, and the deliberately open calculation status. Run `python tools/generate_hr_v0_electrical_v3.py --validate` and `python tools/check_hr_v0_electrical_v3.py` to regenerate and cross-check the V3 native candidate. Run `python tools/check_energization_gates.py --through-stage E2 --require-ready` before claiming readiness for control-only first energization; it must remain nonzero until every applicable gate is evidenced and closed.

## Review history

Twenty review/control rounds are complete: R01-R20. R11 Fable and R12 Sol are independent parallel reviews of the same pre-correction baseline. The resupplied Sol verdict is the same R12 analysis and is not double-counted. Correction and disposition passes are recorded separately from independent reviews.

| Round | Review or control pass | Result |
|---|---|---|
| R01 | Initial evidence and public-claim audit | Established that the concept site was not a build package. |
| R02 | Integrated-site accuracy review | Rechecked claims, artifacts, warnings, links, and legibility. |
| R03 | Fable preliminary electrical review | Found zero connected symbols/nets and 368 ERC violations. |
| R04 | Connected electrical V2 review | Introduced reviewable native ECAD and identified residual blockers. |
| R05 | Independent Fable V2 review | Reproduced improvements and found monitored-reset and selection gaps. |
| R06 | Electrical V2.1 correction review | Reached connected 15-sheet ERC 0/0 while preserving 106 unresolved items. |
| R07 | Independent Sol system review | Identified collapse-on-power-loss, drivetrain, CAD, mass, sensing, and governance blockers. |
| R08 | Sol finding disposition pass | Added requirements, risks, gates, evidence controls, and explicit unresolved decisions. |
| R09 | Independent Fable claim/configuration audit | Confirmed electrical counts and found revision and deployment drift. |
| R10 | Systems-baseline correction | Established `HR-30-SYS-R0.2` and synchronized the corrected deployment. |
| R11 | Independent Fable engineering review | Complete: 7 BLOCKER, 11 MAJOR, and 12 MINOR findings; disposition recorded. |
| R12 | Independent GPT Sol engineering review | Complete: 18 BLOCKER, 30 MAJOR, and 8 MINOR findings against the same baseline as R11. |
| R13 | ECAD provenance correction | Added the controlled native KiCad V2.1 tree and hash manifest to the authoritative repository. |
| R14 | R11 engineering correction pass | Corrected mass, torque, speed, battery, TCP, watchdog, safety-function, verification, interface, and public-fabrication-control defects without releasing unresolved hardware. |
| R15 | R12 archival and reconciliation pass | Preserved Sol's complete dossier, dispositioned all 56 findings, and corrected processor ownership, duplicate release evidence, and qualitative IMU labeling. |
| R16 | Native Electrical V3 candidate correction | Added and validated the ten-page connected V3-P0.1 candidate while retaining 29 unresolved interfaces and no energization approval. |
| R17 | Restart-chain and firmware implementation candidate | Moved watchdog contacts into the two SR1 input returns, added fail-closed watchdog/supervisor source, 17 executable unit tests and a source manifest; compiled binaries and HIL remain open. |
| R18 | Watchdog terminal and feedback-interface correction | Froze official Phoenix/Pico terminals, removed a modeled 24 V-to-GPIO path, and added explicit unreleased feedback-interface blocks as Electrical V3-P0.3. |
| R19 | Watchdog feedback circuit correction | Replaced the opaque blocks with an exact ISO1212DBQ pinout and calculated threshold, wetting, filter, GPIO and decoupling networks as Electrical V3-P0.4; PCB, order codes and physical evidence remain open. |
| R20 | Mechanical frame-interface evidence correction | Added a hashed `MV0-FC01` PCD22 coupon package, controlled 1:1 overlay, unpowered inspection procedure and record template; execution and production release remain open. |

See [the review ledger](docs/review-ledger.md) for dates, configurations, evidence, reviewer independence, and counting rules. No review has approved fabrication or energization.

## Release rule

Only revisions tagged `BUILD-RELEASE-*` after the review gates in the system specification may be fabricated or energized. Documents labeled concept, draft, or preliminary are planning artifacts, not assembly instructions.
