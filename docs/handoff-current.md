# Project Button Current Engineering Handoff

Handoff date: 2026-08-07
Package baseline: **HR-30-SYS-R0.2**  
Electrical package: **Project Button Electrical V2.1 reviewed baseline; V3-P1.2 / PCB-P0.5 / DXL-STAR-P0.1 correction candidates**
Mechanical package: **HR-V0-MECH-R0.1-PRELIMINARY quote geometry plus guard/catch/cable space study**
Firmware package: **HR-V0-FW-P0.1 source/test candidate; no released binary**
Status: **PRELIMINARY - NOT APPROVED FOR ENERGIZATION**

## Authority and presentation

- Authoritative engineering repository: `https://github.com/amyleesterling/humanoid-robot`
- Interactive presentation: `https://project-button-workshop.amysterling.chatgpt.site/`
- Configuration and identifier rules: `docs/configuration-management.md`
- Complete review history: `docs/review-ledger.md`
- Authoritative native ECAD: `electrical/kicad/project-button-v2/project-button-v2.kicad_pro`
- ECAD source manifest: `electrical/kicad/project-button-v2/SOURCE-MANIFEST.csv`
- Connected correction candidate: `electrical/kicad/project-button-v3/project-button-v3.kicad_pro`
- DYNAMIXEL star-injection candidate: `electrical/kicad/hr-v0-dxl-star/hr-v0-dxl-star.kicad_pro`
- V3 generator/checker: `tools/generate_hr_v0_electrical_v3.py`; `tools/check_hr_v0_electrical_v3.py`
- Firmware source/checker: `firmware/`; `tools/check_hr_v0_firmware.py`

The authoritative repository controls engineering intent and contains the reviewed Electrical V2.1 KiCad source plus the separate V3-P1.2 system schematic, PCB-P0.5 watchdog board and DXL-STAR-P0.1 actuator-interface correction candidates. The website is a synchronized presentation and must not override the source specification. Individual documents retain their own revisions; neither electrical identifier replaces the `HR-30-SYS-R0.2` systems-package baseline. V3 does not supersede V2.1 until its open selections, calculations, tests, and qualified reviews close.

## Current program inputs and fabrication route

- Build and use region: Boston, Massachusetts, USA.
- HR-V0 is a light-duty, adult-operated bench demonstrator for a soft 100 g maximum payload; it is not a high-payload robot.
- A local library makerspace may have CNC access, but metal capability is unverified and is not part of the release basis.
- The baseline custom-metal route uses four flat 6061-T6 part definitions: one upper link, one forearm link, one shoulder adapter, and two copies of the bench-anchor plate. SendCutSend is the primary quotation route; Xometry is the comparison/3-D-machining fallback; Artisans Asylum is the nearby supervised inspection and secondary-work option.
- See `docs/hr-v0-build-site-basis.md` and `docs/hr-v0-fabrication-sourcing-boston.md`. No cutting order is authorized until the fit coupon, fastener, bench-survey, drawing, inspection, and qualified-review gates close.

## Current controlled counts

- 68 draft requirements
- 85 controlled verification procedure records
- 40 open risks
- six staged releases: HR-V0, HR-30A, HR-30B, HR-30C, HR-30D, and HR-30W
- 15 native KiCad sheets
- 142 electrical components
- 181 total KiCad nets, including 13 auto-generated unconnected nets
- 168 named electrical nets
- 106 unresolved electrical selections/interfaces
- KiCad 10.0.5 ERC: 0 errors and 0 warnings

The V3-P1.2 candidate separately contains thirteen native pages, 76 component blocks, 295 modeled terminals, 100 native nets (64 named connected nets plus 36 deliberate auto-generated unconnected nets), 259 unique wire labels, 63 unresolved component/interface rows, and 24 `TBD-*` terminal designations. It retains the exact watchdog/safety architecture through P1.1 and replaces three undefined inline actuator-injection modules with one exact 18-terminal `INJ1` central-star boundary. The separate DXL-STAR-P0.1 native project has seven proposed headers, 18 terminals, three mutually isolated positive rails, common TTL data/return, `JC1:2` no-net/no-copper, 17 routed segments, one return zone and native ERC/DRC 0/0. PCB-P0.5 remains a 42-reference, 201-segment, 56-via watchdog candidate with three filled B.Cu zones. R36's protection register still carries zero released fuse ampere ratings and blocks the XM540 branches on the 4.4 A stall versus 3 A JST EH conflict. Cable construction, protection, source-side current division, physical continuity/isolation/no-backfeed, thermal, waveform, crimp/retention, RESET/ARM terminals, panel human factors, supplier acceptance, HIL/fault evidence and qualified review remain open. Neither PCB has fabrication outputs. KiCad 10.0.5 ERC/DRC, native exports and the exact-net, protection and PCB checkers pass; those checks do not establish physical suitability. These V3 counts must not be substituted for the independently reviewed V2.1 counts above.

ERC validates modeled connectivity and annotation only. It does not establish physical pinouts, ratings, protection coordination, functional safety, buildability, or permission to energize.

## Review history and independent findings

Thirty-nine review/control rounds are complete and recorded in `docs/review-ledger.md`. R11 Fable and R12 Sol were commissioned independently against GitHub `main` at `ee276af...` before the R13/R14 corrections. R11 reported 7 BLOCKER, 11 MAJOR, and 12 MINOR findings. R12 reported 18 BLOCKER, 30 MAJOR, and 8 MINOR findings; the resupplied analysis is the same R12 verdict and is not double-counted. R13-R39 are controlled project responses, not independent approvals. R37 freezes the DXL-star board pin allocation and native routing but does not close its cable, protection, thermal, waveform, no-backfeed or physical-evidence gates. R38 adds a fail-closed actuator readback/current test candidate while explicitly leaving the branch-current and connector application conflict open. R39 adds exact Pico GPIO binding, publisher-pinned tools and reproducible target artifacts while keeping target execution and HIL open.

## Principal unresolved engineering blockers

1. HR-V0 now has native parametric quote geometry, four custom-part DXF/STEP/STL sets, readable drawings, vendor CAD provenance, a GLB/STEP assembly-space model, preliminary plate/column screens, three controlled interface coupons, checked hard-stop datums/load cases, a proposed exact RM-X52 gripper parent kit/allocation, a generated guard/catch envelope with five cable zones, and a 13-row moving-mass ledger plus unpowered/guarded validation procedures. The mass ledger supports 565.4 g known and leaves 184.6 g for every unresolved moving frame, fastener, stop, cable and gripper item; it is not a pass. The 900 x 400 x 950 mm guard space and its 25 mm stopping/clearance values are provisional, not a safety distance. Received fit, exact fasteners, complete sweep/stopping/drop evidence, guard/receiver/harness parts, force/current limit, fabricable stops, bench anchoring, measured mass/COM/inertia, proof tests, and independent mechanical review remain open. HR-30 has no released mechanical CAD.
2. Joint continuous/cyclic/impact/thermal performance, drivetrain efficiency, backlash, and structural margins are not physically validated.
3. Safe actuator-power-loss behavior remains unresolved; a walking robot may collapse when hazardous drive energy is removed.
4. Mass, center of mass, inertia, wiring mass, and reserve are not closed against released CAD and measured components.
5. V3 records exact E-stop, RESET/ARM, safety-relay, watchdog-relay, ISO1212 feedback-receiver and support-passive, source, contactor, U2D2, actuator, frame, JA1 project-side, DC1 regulator and DXL-star candidates where primary evidence permits. Twenty-four V3 terminals remain deliberately `TBD-*`. The star-board project freezes its board-side connector allocation and omits U2D2 VDD, but cable construction, protection/current, connector application, thermal, waveform, no-backfeed, received proof, RESET/ARM terminals and enclosure remain unreleased.
6. Battery, BMS, fuse, precharge, service disconnect, charging interlock, regeneration, telemetry isolation, and enclosure remain topology only.
7. RS-485 transceivers, harnesses, shielding, termination, biasing, separation, waveform margin, and physical fault tests remain open.
8. Sensor sheets are functional interfaces, not complete production circuits or released PCB designs.
9. `HR-V0-FW-P0.1` now supplies a fail-closed source-level state-machine candidate, `HR-V0-ACT-P0.1` register-readback rules and 25 unit tests. `HR-V0-WD-BUILD-P0.1` supplies an exact Pico GPIO binding plus byte-identical target artifacts from two clean, publisher-pinned builds. The binary has not been flashed or executed on received hardware, and there is still no Raspberry Pi deployment, DYNAMIXEL transport, received actuator identity, external branch-current limit, selected kinematics, bus timing measurement, HIL evidence, or reset-to-motion fault trace. Raw 800/300 current values are guarded test candidates only. HR-30 still lacks its selected real-time implementation.
10. No physical release-gate test has passed; fixtures, calibrated instrumentation, raw records, accountable owners, approvers, FMEA/FTA, and common-cause review remain incomplete.

R11 and R12 added material blockers or invalidated assumptions. R14 records the failed arm/leg mass screen, removes the fixed 4S and 14.8 V sizing basis, blocks direct-drive hip roll, reduces initial walking speed to 0.10-0.14 m/s, makes TCP speed governing, defines 61 verification procedures, and creates a preliminary safety-function register. R15 makes the processor-ownership boundary explicit and records every Sol finding without treating R14 as part of Sol's reviewed baseline. The Electrical V2.1 watchdog restoration path is corrected in the V3 modeled topology, but no functional-safety credit or physical validation has been established. Mass closure, battery/rail, joint selection, protection, CAD, safe power loss, restraint dynamics, response time/stopping distance, PLr/SIL determination, real-time implementation, and physical testing remain open. See `docs/reviews/2026-08-06-fable-review-disposition.md`, `docs/reviews/2026-08-06-sol-r12-review-disposition.md`, `docs/r11-engineering-calculations.md`, and `docs/hr-v0-electrical-v3-candidate.md`.

Sol's R12 conclusions have also been rechecked against the controlled R18 state in `docs/reviews/2026-08-06-sol-r12-post-r18-status.md`. This is a project-owned disposition update, not a new independent review or approval. It preserves the original 56-finding count, records which baseline claims are stale, and confirms that 21 of 21 gates applicable through E2 remain unresolved.

The R19 status reconciliation is `docs/reviews/2026-08-06-sol-r12-post-r19-status.md`. It records the ISO1212 circuit evidence and the corrected `RSENSE` connection without presenting R19 as a new Sol review or reducing Sol's original finding totals.

The R20 status reconciliation is `docs/reviews/2026-08-06-sol-r12-post-r20-status.md`. It records the bounded fit-coupon correction, keeps Sol's mechanical and energization verdict open, and confirms that the resupplied analysis is R12 rather than a duplicate independent round.

The R21 status reconciliation is `docs/reviews/2026-08-06-sol-r12-post-r21-status.md`. It records the corrected H101/S102 topology and frame-kit evidence controls, explicitly states that the earlier symmetric PCD22 production geometry was invalid, and keeps all fabrication and energization conclusions open.

The R22 status reconciliation is `docs/reviews/2026-08-06-sol-r12-post-r22-status.md`. It records the hard-stop kinematic and load-case evidence, the missing reflected-inertia/bumper inputs, and the still-open stop-part and impact-test release.

The R23 status reconciliation is `docs/reviews/2026-08-06-sol-r12-post-r23-status.md`. It records the controlled 13-row HR-V0 mass ledger, the 565.4 g known subtotal, the 184.6 g unresolved headroom, and the still-open measured mass/COM/inertia release.

The R24 status reconciliation is `docs/reviews/2026-08-06-sol-r12-post-r24-status.md`. It records the proposed orderable gripper parent kit, allocated mechanism schedule, `MV0-FC03` interface evidence route, local-guard requirement, and still-open physical fit, force, mass, fastener and proof evidence.

The R25 status reconciliation is `docs/reviews/2026-08-06-sol-r12-post-r25-status.md`. It records the generated guard/catch space reservation, five cable zones, three new requirements/procedures, explicit provisional assumptions, and still-open exact hardware, stopping/drop/sweep, inspection and proof evidence. Through E2, 0 of 21 gates are closed; 14 are partial and 7 remain open.

The R26 status reconciliation is `docs/reviews/2026-08-06-sol-r12-post-r26-status.md`. It records Electrical V3-P0.5, the distinct IDEC operator order codes, the official Raspberry Pi US regional model, one new receiving procedure/form, full regeneration/visual QA, and unchanged E2 gate status: 0 closed, 14 partial and 7 open.

The R27 status reconciliation is `docs/reviews/2026-08-06-sol-r12-post-r27-status.md`. It records Electrical V3-P0.6, the controlled S0 right/left terminal-position mapping, the IDEC HW old/new production-transition constraint, synchronized regeneration, and no energization-gate closure.

The R28 status reconciliation is `docs/reviews/2026-08-06-sol-r12-post-r28-status.md`. It records Electrical V3-P0.7, the JA1 Molex housing/HCS contact/tool and DC1 TRACO regulator candidates, required current-division/thermal/brownout evidence, synchronized regeneration, and no energization-gate closure. It is a project-owned reconciliation, not a new Sol review.

The R29 status reconciliation is `docs/reviews/2026-08-06-sol-r12-post-r29-status.md`. It records Electrical V3-P0.8, the exact VO618A heartbeat path, separate TPL7407LPWR driver packages, physical test controls, synchronized regeneration, and no energization-gate closure. It is a project-owned reconciliation, not a new Sol review.

The R30 status reconciliation is `docs/reviews/2026-08-06-sol-r12-post-r30-status.md`. It records Electrical V3-P0.9, the exact feedback passive order codes and receiving/derating control while keeping PCB, physical validation and every energization gate open. It is a project-owned reconciliation, not a new Sol review.

The R32 reconciliation is `docs/reviews/2026-08-06-sol-r12-post-r32-status.md`. It records Electrical V3-P1.0 and the corrected, explicitly unrouted PCB-P0.2 source while preserving Sol's physical-build, functional-safety and energization blockers. It is also a project-owned reconciliation, not a new independent review.

The R33 reconciliation is `docs/reviews/2026-08-06-sol-r12-post-r33-status.md`. It records PCB-P0.3's routed-copper and connectivity evidence while preserving Sol's fabrication, physical-build, functional-safety and energization blockers. It is also a project-owned reconciliation, not a new independent review.

The R34 reconciliation is `docs/reviews/2026-08-06-sol-r12-post-r34-status.md`. R35 records PCB-P0.5's 6 mil fabrication envelope; R36 records the machine-controlled protection inputs and connector/rating conflict; R37 records the native DXL-star correction; R38 records the actuator configuration/current-envelope candidate and still-open external-current evidence; and the current R39 reconciliation is `docs/reviews/2026-08-07-sol-r12-post-r39-status.md`. R39 records the Pico target and reproducible build while retaining unexecuted hardware/HIL evidence. All are project-owned reconciliations, not new independent reviews, and all preserve Sol's physical-build, fabrication-release, functional-safety and energization blockers.

## Requested independent-review output

Use `docs/reviews/2026-08-06-electrical-v3-independent-review-request.md` for the controlled V3-P1.2 / PCB-P0.5 / DXL-STAR-P0.1 electrical review scope and reproduction commands. Use `docs/reviews/2026-08-06-firmware-p0.1-independent-review-request.md` for the watchdog, reproducible Pico build and supervisor review scope.

Reviewers must provide BLOCKER / MAJOR / MINOR findings with exact document, requirement, risk, component, net, terminal, or KiCad-sheet references. Calculations must show assumptions and units. Component claims must cite current primary manufacturer documents with revision/date. Every missing input or unresolved selection must state the evidence needed for closure.

Each review must separately assess:

- HR-V0 design and fabrication readiness;
- HR-V0 energization readiness;
- HR-30A design readiness;
- HR-30W walking feasibility;
- readiness for qualified mechanical review;
- readiness for qualified electrical review; and
- readiness for functional-safety review.

No reviewer should interpret clean ERC, traceability, simulation, website publication, or a correction disposition as physical verification or approval.

## Next controlled action

Submit V3-P1.2, PCB-P0.5, DXL-STAR-P0.1, the R36 protection package, HR-V0-ACT-P0.1 and HR-V0-FW-P0.1 for detailed independent electrical, routed-layout, controls and functional-safety review. Do not generate fabrication outputs until the selected suppliers accept final archives and the physical test-access, protection, schematic-parity, CAM and independent-layout gates close. Acquire and receive-inspect the frame, gripper and actuator kits; make all three coupons; and execute the controlled unpowered mechanical inspections. Receive S0/S1/S2 and the JA1/DC1 test articles under their controlled procedures. Before selecting a fuse, close the protection analysis and guarded single-axis fixture plan, including the XM540/JST conflict and external branch-current measurement. After separate reviewed fabrication releases, inspect both boards, build only controlled harness test articles, then execute DXL continuity/isolation/no-backfeed/thermal/waveform tests and disconnected-load watchdog HIL. Freeze the 24 unresolved terminals and every remaining protection/conductor/interface selection; compile reproducible firmware binaries. Do not issue a build or energization release until every applicable gate record closes.
