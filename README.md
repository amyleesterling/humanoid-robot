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
- [HR-V0 S102 fit-coupon procedure P0.1](docs/hr-v0-s102-fit-procedure-p0.1.md)
- [HR-V0 gripper architecture and closure plan P0.1](docs/hr-v0-gripper-architecture-p0.1.md)
- [HR-V0 gripper-kit contents schedule](bom/hr-v0-gripper-kit-contents.csv)
- [HR-V0 guard, receiver and moving-cable architecture P0.1](docs/hr-v0-guard-receiver-cable-p0.1.md)
- [HR-V0 joint-interface and fastener evidence basis](docs/hr-v0-joint-interface-fasteners-p0.1.md)
- [HR-V0 hard-stop design basis P0.1](docs/hr-v0-hard-stop-design-basis-p0.1.md)
- [HR-V0 hard-stop validation procedure P0.1](docs/hr-v0-hard-stop-validation-p0.1.md)
- [HR-V0 frame-kit contents schedule](bom/hr-v0-frame-kit-contents.csv)
- [Electrical and safety architecture](docs/electrical.md)
- [Safety-function requirements](docs/safety-functions.md)
- [Actuator and harness interface constraints](docs/actuator-interface.md)
- [Native KiCad Electrical V2.1 source](electrical/kicad/project-button-v2/README.md)
- [Native KiCad Electrical V3-P1.2 correction candidate](electrical/kicad/project-button-v3/README.md)
- [Native KiCad DXL-STAR-P0.1 injection-board candidate](electrical/kicad/hr-v0-dxl-star/README.md)
- [HR-V0 DYNAMIXEL star-injection evidence basis](docs/hr-v0-dxl-star-injection-p0.1.md)
- [HR-V0 Electrical V3 candidate architecture](docs/hr-v0-electrical-v3-candidate.md)
- [HR-V0 Electrical terminal closure R27](docs/hr-v0-electrical-terminal-closure-r27.md)
- [HR-V0 source-interface closure R28](docs/hr-v0-source-interface-closure-r28.md)
- [HR-V0 heartbeat and relay-driver closure R29](docs/hr-v0-heartbeat-driver-closure-r29.md)
- [HR-V0 watchdog-feedback passive closure R30](docs/hr-v0-watchdog-feedback-passive-closure-r30.md)
- [HR-V0 watchdog PCB constrained-placement candidate P0.2](docs/hr-v0-watchdog-pcb-p0.2.md)
- [HR-V0 watchdog PCB routed-copper candidate P0.3](docs/hr-v0-watchdog-pcb-p0.3.md)
- [HR-V0 watchdog PCB test-access candidate P0.4](docs/hr-v0-watchdog-pcb-p0.4.md)
- [HR-V0 watchdog PCB fabrication-envelope candidate P0.5](docs/hr-v0-watchdog-pcb-p0.5.md)
- [HR-V0 protection and conductor coordination P0.1](docs/hr-v0-protection-coordination-p0.1.md)
- [HR-V0 actuator current and torque envelope P0.1](docs/hr-v0-actuator-current-envelope-p0.1.md)
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
- [HR-V0 moving-mass closure screen](docs/hr-v0-moving-mass-closure-p0.1.md)
- [HR-V0 moving-mass ledger](bom/hr-v0-moving-mass-ledger.csv)
- [Independent review disposition](docs/independent-review-disposition.md)
- [Fable R11 review and disposition](docs/reviews/2026-08-06-fable-review-disposition.md)
- [Sol R12 review and disposition](docs/reviews/2026-08-06-sol-r12-review-disposition.md)
- [Sol R12 findings rechecked against R17](docs/reviews/2026-08-06-sol-r12-post-r17-status.md)
- [Sol R12 findings rechecked against R18](docs/reviews/2026-08-06-sol-r12-post-r18-status.md)
- [Sol R12 findings rechecked against R19](docs/reviews/2026-08-06-sol-r12-post-r19-status.md)
- [Sol R12 findings rechecked against R20](docs/reviews/2026-08-06-sol-r12-post-r20-status.md)
- [Sol R12 findings rechecked against R21](docs/reviews/2026-08-06-sol-r12-post-r21-status.md)
- [Sol R12 findings rechecked against R22](docs/reviews/2026-08-06-sol-r12-post-r22-status.md)
- [Sol R12 findings rechecked against R23](docs/reviews/2026-08-06-sol-r12-post-r23-status.md)
- [Sol R12 findings rechecked against R24](docs/reviews/2026-08-06-sol-r12-post-r24-status.md)
- [Sol R12 findings rechecked against R25](docs/reviews/2026-08-06-sol-r12-post-r25-status.md)
- [Sol R12 findings rechecked against R26](docs/reviews/2026-08-06-sol-r12-post-r26-status.md)
- [Sol R12 findings rechecked against R27](docs/reviews/2026-08-06-sol-r12-post-r27-status.md)
- [Sol R12 findings rechecked against R28](docs/reviews/2026-08-06-sol-r12-post-r28-status.md)
- [Sol R12 findings rechecked against R29](docs/reviews/2026-08-06-sol-r12-post-r29-status.md)
- [Sol R12 findings rechecked against R30](docs/reviews/2026-08-06-sol-r12-post-r30-status.md)
- [Sol R12 findings rechecked against R31](docs/reviews/2026-08-06-sol-r12-post-r31-status.md)
- [Sol R12 findings rechecked against R32](docs/reviews/2026-08-06-sol-r12-post-r32-status.md)
- [Sol R12 findings rechecked against R33](docs/reviews/2026-08-06-sol-r12-post-r33-status.md)
- [Sol R12 findings rechecked against R34](docs/reviews/2026-08-06-sol-r12-post-r34-status.md)
- [Sol R12 findings rechecked against R35](docs/reviews/2026-08-06-sol-r12-post-r35-status.md)
- [Sol R12 findings rechecked against R36](docs/reviews/2026-08-06-sol-r12-post-r36-status.md)
- [Sol R12 findings rechecked against R37](docs/reviews/2026-08-07-sol-r12-post-r37-status.md)
- [Sol supplied review summary](docs/reviews/2026-08-07-sol-independent-engineering-review-summary.md)
- [Sol R12 findings rechecked against R38](docs/reviews/2026-08-07-sol-r12-post-r38-status.md)
- [Electrical V3 independent review request](docs/reviews/2026-08-06-electrical-v3-independent-review-request.md)
- [Firmware P0.1 independent review request](docs/reviews/2026-08-06-firmware-p0.1-independent-review-request.md)
- [Requirements](requirements/requirements.csv)
- [HR-V0 energization gate register](requirements/hr-v0-energization-gates.csv)
- [Proposed bill of materials](bom/bom.csv)
- [Risk register](safety/risk-register.csv)

Run `python tools/check_traceability.py` from this directory to ensure every requirement has at least one verification method and all risk controls reference valid requirements. Regenerate and check the mechanical package in this order: `python cad/hr-v0/src/hr_v0_cad.py`, `python cad/hr-v0/src/mechanical_checks.py`, then `python tools/check_hr_v0_cad.py`. The calculation pass refreshes the generated source manifest after updating its result file. Run `python tools/generate_hr_v0_electrical_v3.py --validate` and `python tools/check_hr_v0_electrical_v3.py` to regenerate and cross-check the V3 native candidate. Run `python tools/check_hr_v0_protection.py` to verify that the six-reference coordination register remains explicit and that no unresolved fuse ampere rating has been released. Run both PCB generators/checkers with KiCad's bundled Python: `"C:\Program Files\KiCad\10.0\bin\python.exe" tools/generate_hr_v0_watchdog_pcb.py`, `"C:\Program Files\KiCad\10.0\bin\python.exe" tools/check_hr_v0_watchdog_pcb.py`, `"C:\Program Files\KiCad\10.0\bin\python.exe" tools/generate_hr_v0_dxl_star.py`, and `"C:\Program Files\KiCad\10.0\bin\python.exe" tools/check_hr_v0_dxl_star.py`. PCB-P0.5 and DXL-STAR-P0.1 are routed source candidates, but both must remain without Gerber/drill outputs until supplier acceptance, protection, physical evidence and independent-review gates close. Run `python tools/check_energization_gates.py --through-stage E2 --require-ready` before claiming readiness for control-only first energization; it must remain nonzero until every applicable gate is evidenced and closed.

## Review history

Thirty-eight review/control rounds are complete: R01-R38. R11 Fable and R12 Sol are independent parallel reviews of the same pre-correction baseline. The resupplied Sol verdict is the same R12 analysis and is not double-counted. Correction and disposition passes are recorded separately from independent reviews.

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
| R21 | Mechanical interface-topology correction | Found and removed an invalid symmetric PCD22 assumption; separated H101 output, S102 body-frame, and unresolved gripper interfaces; added `MV0-FC02`, frame-kit receiving controls, fastener stack math, and manifest-pipeline validation. |
| R22 | Hard-stop kinematic and load-case definition | Added checked stop datums, allocated-mass energy and drive-force screens, an unpowered inspection, and a guarded incremental validation route without inventing a bumper or impact rating. |
| R23 | HR-V0 moving-mass traceability and closure correction | Added `MASS-002`, a 13-row controlled ledger, reproducible 565.4 g known subtotal, 184.6 g unresolved headroom, measurement form, and review procedure while keeping mass closure open. |
| R24 | HR-V0 gripper interface and evidence correction | Selected an orderable ROBOTIS parent kit and exact mechanism allocation, added the `MV0-FC03` 24 x 12 mm physical-fit coupon, guarded-use requirement, receiving/interface records, and primary-source hashes while keeping force, guard, mass, fasteners and proof open. |
| R25 | HR-V0 guard, receiver and moving-cable space correction | Added a generated enclosure/catch STEP envelope, readable layouts, explicit provisional stopping/clearance terms, five cable zones, three requirements, three procedures and unexecuted guard/cable/drop records; no panel, harness or safety distance is released. |
| R26 | Electrical operator and regional-source identity correction | Advanced the connected candidate to V3-P0.5; froze black RESET and green ARM IDEC operator order codes plus the official Raspberry Pi US regional model, added receiving/continuity evidence controls, regenerated all native/exported artifacts, and retained 43 unresolved rows and 64 `TBD-*` terminals. |
| R27 | E-stop terminal-position closure | Advanced the connected candidate to V3-P0.6; replaced four anonymous S0 terminals with controlled right/left NC position designators, retained received positive-opening verification, documented the active IDEC HW production transition, and kept RESET/ARM terminals unresolved. ERC remains 0/0; 43 unresolved rows and 60 `TBD-*` terminals remain. |
| R28 | Source-interface candidate closure | Advanced the connected candidate to V3-P0.7; froze the project-side Molex JA1 housing/HCS contact/tool system and TRACO watchdog-regulator order code/pins, added receiving/current-division/thermal/brownout evidence controls, reduced anonymous terminals to 56, retained 43 unresolved rows, and closed no energization gate. |
| R29 | Heartbeat and relay-driver circuit closure | Advanced the candidate to V3-P0.8; replaced anonymous heartbeat and coil-driver blocks with an exact VO618A optical path, exact passives, two separate TPL7407LPWR packages and COM bypass candidates; added pin/net assertions and a physical HIL/fault test record; retained 47 unresolved evidence rows and closed no energization gate. |
| R30 | Watchdog-feedback passive closure | Advanced the candidate to V3-P0.9; froze exact proposed order codes for all 13 ISO1212 support passives, added pin/value assertions plus a receiving/derating record, retained 47 unresolved evidence rows, and closed no energization gate. |
| R31 | Watchdog PCB boundary and placement-source pass | Advanced the schematic candidate to V3-P1.0; added exact board terminal candidates and project pin allocation, a native 26-reference PCB-P0.1 placement source, custom footprints, DRC/render evidence and an inspection record. The board intentionally has zero tracks/zones and 68 unconnected pads, so fabrication and energization remain blocked. |
| R32 | Watchdog PCB package and constrained-placement correction | Found that P0.1 used a non-matching ISO1212 footprint and placed the field-input network on the wrong side. Issued unrouted PCB-P0.2 with the correct 3.9 x 4.9 mm, 0.635 mm-pitch DBQ candidate, corrected field/control zoning, machine-checked TI placement screens, zero non-routing DRC violations and the same explicit 68-pad routing gate. |
| R33 | Watchdog PCB routed-copper candidate and independent connectivity pass | Issued PCB-P0.3 with 160 segments, 45 vias and one filled return zone; native KiCad DRC is 0/0 and the checker proves every multi-pad net connected, 18 deliberate singleton nets isolated and 89 no-net pads untouched. No fabrication outputs, physical evidence or energization approval were released. |
| R34 | Watchdog PCB test-access and ISO1212 SUB-copper pass | Issued Electrical V3-P1.1 / PCB-P0.4 with 16 Harwin S1751-46R test points, separate 2 mm x 2 mm floating SUB planes, 200 segments, 56 vias and three filled zones. Native DRC remains 0/0 and no fabrication or energization release was issued. |
| R35 | Watchdog PCB fabrication-envelope pass | Issued PCB-P0.5 with every former 0.10 mm feature rerouted at 0.1524 mm minimum and a proposed source-backed OSH Park two-layer process. Native DRC remains 0/0; no fabrication outputs or energization release were issued. |
| R36 | Protection and conductor-coordination input pass | Added exact proposed holder/distribution hardware and fuse family, six machine-checked input rows, three procedures and an unexecuted evidence form while retaining zero fuse ampere ratings. Exposed the XM540 4.4 A stall versus JST EH 3 A series conflict; EG-014 is partial, not closed. |
| R37 | DYNAMIXEL star-injection native-ECAD correction | Issued Electrical V3-P1.2 plus a separate routed DXL-STAR-P0.1 source with three isolated positive branches, common TTL data/return, an unrouted U2D2 VDD pin, ERC/DRC 0/0 and physical evidence controls. Cable, current, thermal, waveform, no-backfeed and fabrication evidence remain open. |
| R38 | Actuator current-envelope and torque-enable configuration correction | Added a guarded raw 800/300 current candidate, exact mode/readback rules, a fail-closed executable validator, eight tests and an external characterization route. Internal current is not treated as branch-current proof; the XM540/JST conflict and all physical gates remain open. |

See [the review ledger](docs/review-ledger.md) for dates, configurations, evidence, reviewer independence, and counting rules. No review has approved fabrication or energization.

## Release rule

Only revisions tagged `BUILD-RELEASE-*` after the review gates in the system specification may be fabricated or energized. Documents labeled concept, draft, or preliminary are planning artifacts, not assembly instructions.
