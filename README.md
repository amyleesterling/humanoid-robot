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
- [Sub-meter humanoid benchmark](docs/architecture-benchmark.md)
- [Walking-system specification](docs/walking-system.md)
- [Walking verification matrix](docs/walking-verification.md)
- [Mechanical concept and load model](docs/mechanical.md)
- [Electrical and safety architecture](docs/electrical.md)
- [Control and fault-state specification](docs/control.md)
- [Verification plan](docs/verification.md)
- [Open decisions](docs/open-decisions.md)
- [Evidence maturity dashboard](docs/evidence-maturity.md)
- [Independent review disposition](docs/independent-review-disposition.md)
- [Requirements](requirements/requirements.csv)
- [Proposed bill of materials](bom/bom.csv)
- [Risk register](safety/risk-register.csv)

Run `python tools/check_traceability.py` from this directory to ensure every requirement has at least one verification method and all risk controls reference valid requirements.

## Review history

Ten review/control rounds are complete; two parallel independent engineering reviews are requested. Correction passes are recorded separately from independent reviews.

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
| R11 | Independent Fable engineering review | Requested; accuracy and completeness review pending. |
| R12 | Independent GPT Sol engineering review | Requested; accuracy and completeness review pending. |

See [the review ledger](docs/review-ledger.md) for dates, configurations, evidence, reviewer independence, and counting rules. No review has approved fabrication or energization.

## Release rule

Only revisions tagged `BUILD-RELEASE-*` after the review gates in the system specification may be fabricated or energized. Documents labeled concept, draft, or preliminary are planning artifacts, not assembly instructions.
