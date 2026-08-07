# Project Button Current Engineering Handoff

Handoff date: 2026-08-07
Package baseline: **HR-30-SYS-R0.2**  
Electrical package: **Project Button Electrical V2.1 reviewed baseline; V3-P1.8 / PCB-P0.5 / DXL-STAR-P0.1 correction candidates**
Control-panel package: **HR-V0-CP-P0.4 corrected physical allocation plus exact SD1 catalog candidate; no holes, cuts, wires, fuse links, lockout procedure, protection ratings, bonds, cable entries, PCB outputs, assembly, or energization release**
Mechanical package: **HR-V0-MECH-P0.3 hold plus fabrication-defined HR-V0-ARM-ARCH-P0.4 adapter candidate; no supplier packet or buildable mechanical release**
Firmware package: **HR-V0-FW-P0.2 source/test candidate with DYNAMIXEL transport P0.1; reproducible watchdog P0.2 artifacts; no installed target SDK, opened device, connected actuator, released or flashed binary**
Safety package: **HR-V0-FSA-P0.1 allocation candidate; ordinary DF-01 heartbeat has zero safety credit; no PLr, SIL, or achieved PL assigned**
Configuration package: **HR-V0-RC-P0.1 deterministic candidate; immutable merge/acceptance and signatures remain open**
Commissioning package: **HR-V0-E2-SEQ-P0.1 procedure candidate; 15 steps and five forms; all records NOT EXECUTED; authorization NOT AUTHORIZED**
BOM package: **HR-V0-BOM-P0.1 closure candidate; 16 evaluation-only lines; 21 exact candidates on hold; 28 selection-required groups; no complete procurement release**
Status: **PRELIMINARY - NOT APPROVED FOR ENERGIZATION**

## Authority and presentation

- Authoritative engineering repository: `https://github.com/amyleesterling/humanoid-robot`
- Interactive presentation: `https://project-button-workshop.amysterling.chatgpt.site/`
- Configuration and identifier rules: `docs/configuration-management.md`
- Deterministic release-candidate control: `docs/hr-v0-release-candidate-p0.1.md`; `release/hr-v0/release-candidate.json`
- BOM closure/evaluation boundary: `docs/hr-v0-bom-closure-p0.1.md`; `bom/hr-v0-bom-closure.csv`; `bom/hr-v0-evaluation-batch-a.csv`
- Complete review history: `docs/review-ledger.md`
- Authoritative native ECAD: `electrical/kicad/project-button-v2/project-button-v2.kicad_pro`
- ECAD source manifest: `electrical/kicad/project-button-v2/SOURCE-MANIFEST.csv`
- Connected correction candidate: `electrical/kicad/project-button-v3/project-button-v3.kicad_pro`
- DYNAMIXEL star-injection candidate: `electrical/kicad/hr-v0-dxl-star/hr-v0-dxl-star.kicad_pro`
- Physical control-panel candidate: `electrical/panel/hr-v0-control-panel-p0.4/`; `docs/hr-v0-control-panel-p0.4.md`
- V3 generator/checker: `tools/generate_hr_v0_electrical_v3.py`; `tools/check_hr_v0_electrical_v3.py`
- Control-panel checker: `tools/check_hr_v0_control_panel.py`
- Firmware source/checker: `firmware/`; `tools/check_hr_v0_firmware.py`

The authoritative repository controls engineering intent and contains the reviewed Electrical V2.1 KiCad source plus the separate V3-P1.8 system schematic, PCB-P0.5 watchdog board, DXL-STAR-P0.1 actuator-interface, HR-V0-CP-P0.4 physical-panel correction, and HR-V0-SD-P0.2 exact-candidate/application hold. The website is a synchronized presentation and must not override the source specification. Individual documents retain their own revisions; neither electrical identifier replaces the `HR-30-SYS-R0.2` systems-package baseline. V3 does not supersede V2.1 until its open selections, calculations, tests, and qualified reviews close.

## Current program inputs and fabrication route

- Build and use region: Boston, Massachusetts, USA.
- HR-V0 is a light-duty, adult-operated bench demonstrator for a soft 100 g maximum payload; it is not a high-payload robot.
- A local library makerspace may have CNC access, but metal capability is unverified and is not part of the release basis.
- R53 invalidated the active custom-metal arm route. Exact ROBOTIS STEP coordinates showed that the H101 moving frame and S102 bottom frame do not present the coplanar interfaces assumed by MV0-001/MV0-003. MV0-001 through MV0-003, the 44/160/160 mm datum chain and all three RFI ZIPs remain withdrawn. Their earlier bytes remain recoverable in Git history, but no current supplier packet exists.
- R57 supersedes R56/P0.3 with `HR-V0-ARM-ARCH-P0.4`. It preserves the 9.525 mm nominal adapter and 202.550/129.050 mm datum chain while adding exact OnlineMetals `1249` stock, current Accu/MISUMI fasteners, a controlled drawing/DXF, ten FAI controls, receiving forms and ten analytical screens. Candidate gravity screens remain 1.858/0.498 N·m; the project proof-load candidate is 12.5385 N·m. None is a released allowable or physical proof result.
- The 221-pose screen finds first nominal contact at 122°. The 120° ceiling is provisional until a physical hard stop, stopping-overtravel/uncertainty margin and continuous collision proof close. Adapter local strength, exact M2.5 stacks, received fit, cables, proof, FAI and qualified review also remain open.
- `SHKL-M5-20-A2-R360`, `SCB2.5-20` and `HNN-M2.5-A2` are the current exact fastener candidates on hold. The analytical screens pass their project thresholds, but received MTR/fit, qualified allowable/method acceptance, stack/tolerance measurements, torque/locking/reuse rules and physical proof remain open. Source reference properties are not allowables.
- `MECH-005` / `AUDIT-MECH-012` / `INSPECT-MECH-014` / `INSPECT-MECH-015` and `MECH-006` / `INSPECT-MECH-013` therefore remain open. No arm quotation can resume from R57.
- `MV0-004` and the base/frame candidate remain on their separate exact-Boston-bench, physical-fit, torque and proof holds.
- R59 issues `HR-V0-FAB-SRC-P0.2`, which corrects the Boston sourcing page to the current four-adapter/two-member R57 candidate. Xometry and Protolabs remain one-stop CNC/DFM candidates; Artisans Asylum is the leading local capability/inspection candidate; SendCutSend is research-only because no current hole-free upload artifact exists; BPL and FabVille remain nonstructural/training routes. Eight route records are held or excluded and all seven inquiry rows are unexecuted.
- R60 issues `HR-V0-CP-P0.1`, a physical allocation candidate for Hammond `PJU181610H` / `P1868`, the V3 devices, two source PCB envelopes, six XT1 positions, six cable-entry zones and all 66 bounded V3 wire endpoints. Exact rail/duct/terminal/H1 catalog candidates are on hold; inlet, protection, disconnect, conductors, terminations, glands and bonding remain `SELECTION REQUIRED`. No hole, cut, wire, PCB fabrication, assembly or energization record is released or executed.
- R61 issues Electrical `V3-P1.5`, freezing H1 as amber IDEC `HW1P-1FQD-A-24V`, removing the misleading `SAFE ELIGIBLE` and `+/-` labels, and retaining `TBD-HA/TBD-HB` as project placeholders. Fourteen H1 receiving/characterization records are `NOT EXECUTED`; no terminal, polarity, current, brightness, wiring, safety credit or energization release is claimed.
- R63 issues Electrical `V3-P1.7` and `HR-V0-CP-P0.3`, freezing Phoenix `D-ST 4` item `3030420` as the FSR group end-cover candidate while retaining all six fuse links, received accessory compatibility/grouping, coordination, conductors, holes, thermal/depth proof, bonding and assembly as unresolved. `HR-V0-SD-P0.1` screens Blue Sea `6004200` but leaves SD1 `SELECTION REQUIRED` because fault/load-break, conductor/lug, lockout, placement and jurisdiction evidence remain open.
- R64 issues Electrical `V3-P1.8`, `HR-V0-CP-P0.4`, `HR-V0-SD-P0.2` and protection P0.4. It freezes active Littelfuse `75920-01` only as the exact SPST high-side SD1 catalog candidate, retains `TBD-IN/TBD-OUT`, and adds one unreleased right-side-wall option. Conductor/lug, source fault, load-break, touch protection, cutout, zero-energy/padlock procedure, human factors, Boston application review and all 15 physical records remain open.
- R65 issues `HR-V0-FW-P0.2` and `HR-V0-DXL-TRANSPORT-P0.1`. It pins ROBOTIS DYNAMIXEL SDK 4.0.5, adds torque-off-before-discovery, exact bus identity/configuration readback, authority-bound synchronous writes, telemetry checks and fault-triggered torque removal. The repository still refuses to open a serial port because its device path, received identities, calibration, profiles, voltage/temperature and external-current limits are unresolved. Nine HIL rows remain `NOT EXECUTED`; no hardware was connected.
- See `docs/hr-v0-build-site-basis.md`, `docs/hr-v0-fabrication-sourcing-boston.md`, and the explicitly withdrawn historical `docs/hr-v0-flat-plate-manufacturing-p0.1.md`. No portal upload, quote request against geometry, cutting order, or first article is authorized until the named route holds close.

## Current controlled counts

- 81 draft requirements
- 103 controlled verification procedure records
- 40 open risks
- six staged releases: HR-V0, HR-30A, HR-30B, HR-30C, HR-30D, and HR-30W
- 15 native KiCad sheets
- 142 electrical components
- 181 total KiCad nets, including 13 auto-generated unconnected nets
- 168 named electrical nets
- 106 unresolved electrical selections/interfaces
- 73 system BOM groups: 16 evaluation candidates, 21 exact candidates on hold, three grouped-component holds, 28 selection-required groups, four historical/DNP exclusions, and one integrated item
- KiCad 10.0.5 ERC: 0 errors and 0 warnings
- E2 gate status: 21 applicable, 0 closed, 21 partial; all five new physical/authorization records remain unexecuted
- full energization-gate register: 30 gates, 0 closed, 22 partial, 8 open
- control-panel candidate: 25 BOM rows, 20 backplate allocations, five door rows, one held sidewall option, six XT1 positions, 66 V3 wire endpoints, six unreleased cable-entry zones, twelve thermal/space screens, and 22 unexecuted evidence rows

The V3-P1.8 candidate separately contains thirteen native pages, 76 component blocks, 295 modeled terminals, 100 native nets (64 named connected nets plus 36 deliberate auto-generated unconnected nets), 259 unique wire labels, 63 unresolved component/interface rows, and 24 `TBD-*` terminal designations. It retains the exact watchdog/safety, DXL-star and contactor architecture through P1.3, P1.4's received-lot terminal-control boundary for RESET and ARM, P1.5's exact amber H1 with placeholder terminals, P1.7's Phoenix `3030420` end-cover candidate, and P1.8's exact Littelfuse `75920-01` SD1 catalog identity. Both SD1 physical terminals and its installed application remain held; both FSR fuse links, received compatibility/grouping and all coordination stay open. Schneider's critical-current application question for the 11.1 A HR-V0 screen remains open. DXL-STAR-P0.1 has seven proposed headers, 18 terminals, three mutually isolated positive rails, common TTL data/return, `JC1:2` no-net/no-copper, 17 routed segments, one return zone and native ERC/DRC 0/0. PCB-P0.5 remains a 42-reference, 201-segment, 56-via watchdog candidate with three filled B.Cu zones. R64's P0.4 panel allocation retains the demonstrated P0.1 fit correction but still lacks received depth, heat, duct-fill, conductor, protection, entry, SD1 touch/placement and PE/bonding evidence. The protection register carries zero released fuse ampere ratings and still blocks XM540 branches on the 4.4 A stall versus 3 A JST EH conflict. Cable construction, protection, contactor duty, source-side current division, physical continuity/isolation/no-backfeed, thermal, waveform, crimp/retention, RESET/ARM/H1 terminals, panel fit/bonding/human factors, supplier acceptance, HIL/fault evidence and qualified review remain open. Neither PCB has fabrication outputs. KiCad 10.0.5 ERC/DRC, native exports and the exact-net, protection, PCB and panel checkers pass; those checks do not establish physical suitability.

ERC validates modeled connectivity and annotation only. It does not establish physical pinouts, ratings, protection coordination, functional safety, buildability, or permission to energize.

## Review history and independent findings

Sixty-five review/control rounds are complete and recorded in `docs/review-ledger.md`. R11 Fable and R12 Sol were commissioned independently against GitHub `main` at `ee276af...` before the R13/R14 corrections. R11 reported 7 BLOCKER, 11 MAJOR, and 12 MINOR findings. R12 reported 18 BLOCKER, 30 MAJOR, and 8 MINOR findings; the resupplied analysis is the same R12 verdict and is not double-counted. R13-R65 are controlled project responses, not independent approvals. R65 adds only a fail-closed source transport/execution boundary; it closes no physical gate and does not authorize connection or energization.

## Principal unresolved engineering blockers

1. HR-V0 has `HR-V0-ARM-ARCH-P0.4` under the `HR-V0-MECH-P0.3` hold. It supplies deterministic STEP/GLB/SVG/DXF, exact-source transforms, interface schedules, controlled adapter tolerances, exact stock/fastener candidates on hold, a 221-pose collision sweep and analytical screens. It is not buildable: received MTR/FAI/fit, qualified calculation acceptance, torque/locking rules, cables, continuous collision proof, a physical hard stop and demonstrated stopping-overtravel/uncertainty margin below first contact, physical proof and qualified review remain open. The base frame still requires received-part fit, tool access, actual-joint torque, slip/proof, exact Boston bench anchors and qualified disposition. HR-30 has no released mechanical CAD.
2. Joint continuous/cyclic/impact/thermal performance, drivetrain efficiency, backlash, and structural margins are not physically validated.
3. Safe actuator-power-loss behavior remains unresolved; a walking robot may collapse when hazardous drive energy is removed.
4. Mass, center of mass, inertia, wiring mass, and reserve are not closed against released CAD and measured components.
5. V3 records exact E-stop, RESET/ARM, safety-relay, watchdog-relay, ISO1212 feedback-receiver and support-passive, source, contactor, U2D2, actuator, frame, JA1 project-side, DC1 regulator and DXL-star candidates where primary evidence permits. The ordinary heartbeat path is now classified only as diagnostic function `DF-01` with zero safety credit and assumed failure. Candidate safety functions `SF-01` E-stop and `SF-03` prevention of unexpected restart still require qualified risk reduction, PLr/category, achieved PL or SIL, common-cause and validation evidence; the fixed guard/catch is physical protective measure `PG-01`, not an SRP/CS. Twenty-four V3 terminals remain deliberately `TBD-*`. PCB/harness bridging and conductive-contamination faults that could impair the independent safety path remain open. The star-board project freezes its board-side connector allocation and omits U2D2 VDD, but cable construction, protection/current, connector application, thermal, waveform, no-backfeed, received proof, RESET/ARM terminals and enclosure remain unreleased.
6. Battery, BMS, fuse, precharge, service disconnect, charging interlock, regeneration, telemetry isolation, and enclosure remain topology only.
7. RS-485 transceivers, harnesses, shielding, termination, biasing, separation, waveform margin, and physical fault tests remain open.
8. Sensor sheets are functional interfaces, not complete production circuits or released PCB designs.
9. `HR-V0-FW-P0.2` supplies a fail-closed source-level state machine, `HR-V0-ACT-P0.1` register/readback rules and `HR-V0-DXL-TRANSPORT-P0.1`. The transport is pinned to official SDK 4.0.5 and source-tests ordered torque-off, discovery, configuration, authority, synchronous-write and fault behavior. Combined executable tests now total 39. The committed configuration refuses to open a port; no target SDK/image, U2D2, actuator, received identity, calibration, external branch-current limit, selected kinematics, bus timing, HIL or reset-to-motion trace exists. Watchdog P0.2 remains unflashed. Raw 800/300 current values are guarded test candidates only. HR-30 still lacks its selected real-time implementation.
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

The R34 reconciliation is `docs/reviews/2026-08-06-sol-r12-post-r34-status.md`. R35 records PCB-P0.5's 6 mil fabrication envelope; R36 records the machine-controlled protection inputs and connector/rating conflict; R37 records the native DXL-star correction; R38 records the actuator configuration/current-envelope candidate and still-open external-current evidence; R39 records the Pico target and reproducible build; R40 records the clock-semantics fix and compiled-C/model differential evidence; R41 records current contactor evidence while retaining the Schneider application, protection, received and loaded-test blockers; R42 through R60 have their matching post-round files. R42 keeps EG-011 partial. R43, R50, R51 and R59 keep EG-006 partial. R44 keeps EG-012 partial. R45 keeps EG-002 partial. R46 advances EG-003 to partial. R47-R57 preserve mechanical physical holds. R58 supplies E2 templates without authorization. R60 supplies panel allocation without a fabrication or wiring release. All are project-owned reconciliations, not new independent reviews, and all preserve Sol's physical-build, fabrication-release, functional-safety and energization blockers.

## Requested independent-review output

Use `docs/reviews/2026-08-06-electrical-v3-independent-review-request.md` for the controlled V3-P1.8 / PCB-P0.5 / DXL-STAR-P0.1 / HR-V0-CP-P0.4 / HR-V0-SD-P0.2 electrical and physical-panel review scope and reproduction commands. Use `docs/reviews/2026-08-07-firmware-p0.2-independent-review-request.md` for the corrected watchdog, compiled-C evidence, reproducible Pico build, supervisor and DYNAMIXEL transport review scope.

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

Submit V3-P1.8, PCB-P0.5, DXL-STAR-P0.1, HR-V0-CP-P0.4, HR-V0-SD-P0.2, the R64 protection package, HR-V0-ACT-P0.1, HR-V0-FW-P0.2, HR-V0-DXL-TRANSPORT-P0.1 and watchdog P0.2 evidence for detailed independent electrical, physical-layout, routed-layout, controls and functional-safety review. Close JC1, all six fuse links, received end-cover compatibility/grouping, the complete SD1 installed application, conductor/termination, cable-entry and bonding selections from measured inputs; then update the panel with received depth, bend/service, duct-fill and thermal evidence. Do not drill or generate fabrication outputs until supplier archives, physical test access, protection, schematic parity, CAM and independent-layout gates close. Acquire and receive-inspect the frame, gripper and actuator kits; make all three coupons; and execute controlled unpowered mechanical inspections. Receive S0/S1/S2/H1, enclosure/backplate and JA1/DC1 test articles under their controlled procedures. Before selecting any fuse, close the protection analysis and guarded single-axis fixture plan, including the XM540/JST conflict and external branch-current measurement. Obtain Schneider's identifiable K1/K2 application disposition after measuring the actual break/regeneration envelope. After separate reviewed fabrication releases, inspect both boards, build only controlled harness test articles, then execute DXL continuity/isolation/no-backfeed/thermal/waveform tests, target transport HIL and disconnected-load watchdog P0.2 HIL. Freeze the 24 unresolved terminals and every remaining protection/conductor/interface selection. Do not issue a build or energization release until every applicable gate record closes.
