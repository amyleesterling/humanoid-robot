# Project Button Current Engineering Handoff

Handoff date: 2026-08-06  
Package baseline: **HR-30-SYS-R0.2**  
Electrical package: **Project Button Electrical V2.1 reviewed baseline; V3-P0.4 connected correction candidate**
Mechanical package: **HR-V0-MECH-R0.1-PRELIMINARY quote geometry**
Firmware package: **HR-V0-FW-P0.1 source/test candidate; no released binary**
Status: **PRELIMINARY—NOT APPROVED FOR ENERGIZATION**

## Authority and presentation

- Authoritative engineering repository: `https://github.com/amyleesterling/humanoid-robot`
- Interactive presentation: `https://project-button-workshop.amysterling.chatgpt.site/`
- Configuration and identifier rules: `docs/configuration-management.md`
- Complete review history: `docs/review-ledger.md`
- Authoritative native ECAD: `electrical/kicad/project-button-v2/project-button-v2.kicad_pro`
- ECAD source manifest: `electrical/kicad/project-button-v2/SOURCE-MANIFEST.csv`
- Connected correction candidate: `electrical/kicad/project-button-v3/project-button-v3.kicad_pro`
- V3 generator/checker: `tools/generate_hr_v0_electrical_v3.py`; `tools/check_hr_v0_electrical_v3.py`
- Firmware source/checker: `firmware/`; `tools/check_hr_v0_firmware.py`

The authoritative repository controls engineering intent and contains the reviewed Electrical V2.1 KiCad source plus the separate V3-P0.4 correction candidate. The website is a synchronized presentation and must not override the source specification. Individual documents retain their own revisions; neither electrical identifier replaces the `HR-30-SYS-R0.2` systems-package baseline. V3 does not supersede V2.1 until its open selections, calculations, tests, and qualified reviews close.

## Current program inputs and fabrication route

- Build and use region: Boston, Massachusetts, USA.
- HR-V0 is a light-duty, adult-operated bench demonstrator for a soft 100 g maximum payload; it is not a high-payload robot.
- A local library makerspace may have CNC access, but metal capability is unverified and is not part of the release basis.
- The baseline custom-metal route uses four flat 6061-T6 part definitions: one upper link, one forearm link, one shoulder adapter, and two copies of the bench-anchor plate. SendCutSend is the primary quotation route; Xometry is the comparison/3-D-machining fallback; Artisans Asylum is the nearby supervised inspection and secondary-work option.
- See `docs/hr-v0-build-site-basis.md` and `docs/hr-v0-fabrication-sourcing-boston.md`. No cutting order is authorized until the fit coupon, fastener, bench-survey, drawing, inspection, and qualified-review gates close.

## Current controlled counts

- 62 draft requirements
- 40 open risks
- six staged releases: HR-V0, HR-30A, HR-30B, HR-30C, HR-30D, and HR-30W
- 15 native KiCad sheets
- 142 electrical components
- 181 total KiCad nets, including 13 auto-generated unconnected nets
- 168 named electrical nets
- 106 unresolved electrical selections/interfaces
- KiCad 10.0.5 ERC: 0 errors and 0 warnings

The V3-P0.4 candidate separately contains eleven native pages, 55 component blocks, 241 modeled terminals, 87 native nets (62 named connected nets plus 25 deliberate auto-generated unconnected nets), 216 unique wire labels, 43 unresolved component/interface rows, and 64 `TBD-*` terminal designations. P0.4 replaces P0.3's two opaque feedback-interface blocks with an exact ISO1212DBQ pinout and calculated threshold, contact-wetting, filter, GPIO and decoupling networks. Exact passive order codes, PCB, terminals, EMC, thermal and physical fault evidence remain open. KiCad 10.0.5 ERC is 0 errors and 0 warnings, and native netlist/PDF/SVG exports plus the exact-net checker pass. These V3 counts must not be substituted for the independently reviewed V2.1 counts above.

ERC validates modeled connectivity and annotation only. It does not establish physical pinouts, ratings, protection coordination, functional safety, buildability, or permission to energize.

## Review history and independent findings

Twenty review/control rounds are complete and recorded in `docs/review-ledger.md`. R11 Fable and R12 Sol were commissioned independently against GitHub `main` at `ee276af...` before the R13/R14 corrections. R11 reported 7 BLOCKER, 11 MAJOR, and 12 MINOR findings. R12 reported 18 BLOCKER, 30 MAJOR, and 8 MINOR findings; the analysis resupplied on 2026-08-06 is the same R12 verdict and is not double-counted. R13 staged the authoritative-ECAD provenance correction; R14 corrected reproducible engineering and traceability defects; R15 archived and dispositioned Sol's complete dossier; R16 created the V3-P0.1 candidate; R17 corrected the restart chain and added preliminary firmware; R18 corrected the watchdog feedback voltage boundary and froze reviewable Phoenix/Pico terminals; R19 defined and checked the ISO1212DBQ feedback circuit; R20 added a hashed PCD22 fit-coupon package, unpowered inspection procedure, and evidence template. Physical execution and functional-safety blockers remain open.

## Principal unresolved engineering blockers

1. HR-V0 now has native parametric quote geometry, four custom-part DXF/STEP/STL sets, readable drawings, vendor CAD provenance, a GLB/STEP assembly-space model, preliminary plate/column screens, and a hashed `MV0-FC01` PCD22 coupon package with `INSPECT-MECH-003`. It is not a released manufacturing package: the physical frame-fit record, acceptance tolerances, fasteners, hard stops, cable paths, gripper, guard, bench anchoring, mass closure, proof tests, and independent mechanical review remain open. HR-30 has no released mechanical CAD.
2. Joint continuous/cyclic/impact/thermal performance, drivetrain efficiency, backlash, and structural margins are not physically validated.
3. Safe actuator-power-loss behavior remains unresolved; a walking robot may collapse when hazardous drive energy is removed.
4. Mass, center of mass, inertia, wiring mass, and reserve are not closed against released CAD and measured components.
5. V3 records exact E-stop, RESET/ARM, safety-relay, watchdog-relay, ISO1212 feedback-receiver, source, contactor, U2D2, actuator, and frame candidates where primary evidence permits, but their application approval, received terminals, protection, conductors, connectors, enclosure, PCB and ratings remain selection-dependent. Sixty-four V3 terminals remain deliberately `TBD-*`; the feedback IC pins are now exact, while every passive order code and the physical board/interface remain unreleased.
6. Battery, BMS, fuse, precharge, service disconnect, charging interlock, regeneration, telemetry isolation, and enclosure remain topology only.
7. RS-485 transceivers, harnesses, shielding, termination, biasing, separation, waveform margin, and physical fault tests remain open.
8. Sensor sheets are functional interfaces, not complete production circuits or released PCB designs.
9. `HR-V0-FW-P0.1` now supplies a fail-closed source-level state-machine candidate and 17 unit tests, but no released RP2040 binary/GPIO binding, Raspberry Pi deployment, DYNAMIXEL transport, selected kinematics, bus timing measurement, HIL evidence, or reset-to-motion fault trace exists. HR-30 still lacks its selected real-time implementation.
10. No physical release-gate test has passed; fixtures, calibrated instrumentation, raw records, accountable owners, approvers, FMEA/FTA, and common-cause review remain incomplete.

R11 and R12 added material blockers or invalidated assumptions. R14 records the failed arm/leg mass screen, removes the fixed 4S and 14.8 V sizing basis, blocks direct-drive hip roll, reduces initial walking speed to 0.10-0.14 m/s, makes TCP speed governing, defines 61 verification procedures, and creates a preliminary safety-function register. R15 makes the processor-ownership boundary explicit and records every Sol finding without treating R14 as part of Sol's reviewed baseline. The Electrical V2.1 watchdog restoration path is corrected in the V3 modeled topology, but no functional-safety credit or physical validation has been established. Mass closure, battery/rail, joint selection, protection, CAD, safe power loss, restraint dynamics, response time/stopping distance, PLr/SIL determination, real-time implementation, and physical testing remain open. See `docs/reviews/2026-08-06-fable-review-disposition.md`, `docs/reviews/2026-08-06-sol-r12-review-disposition.md`, `docs/r11-engineering-calculations.md`, and `docs/hr-v0-electrical-v3-candidate.md`.

Sol's R12 conclusions have also been rechecked against the controlled R18 state in `docs/reviews/2026-08-06-sol-r12-post-r18-status.md`. This is a project-owned disposition update, not a new independent review or approval. It preserves the original 56-finding count, records which baseline claims are stale, and confirms that 21 of 21 gates applicable through E2 remain unresolved.

The R19 status reconciliation is `docs/reviews/2026-08-06-sol-r12-post-r19-status.md`. It records the ISO1212 circuit evidence and the corrected `RSENSE` connection without presenting R19 as a new Sol review or reducing Sol's original finding totals.

The R20 status reconciliation is `docs/reviews/2026-08-06-sol-r12-post-r20-status.md`. It records the bounded fit-coupon correction, keeps Sol's mechanical and energization verdict open, and confirms that the resupplied analysis is R12 rather than a duplicate independent round.

## Requested independent-review output

Use `docs/reviews/2026-08-06-electrical-v3-independent-review-request.md` for the controlled V3-P0.4 electrical review scope and reproduction commands. Use `docs/reviews/2026-08-06-firmware-p0.1-independent-review-request.md` for the source-level watchdog and supervisor review scope.

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

Submit V3-P0.4 and HR-V0-FW-P0.1 for detailed independent electrical, controls and functional-safety review. Acquire the two FR13 frames, make `MV0-FC01`, and execute `INSPECT-MECH-003` while completing the missing hard-stop, cable, gripper, guard, fastener, bench-anchor, mass, and proof-test design. In parallel, design/review the ISO1212 PCB, freeze its passive order codes plus the 64 unresolved terminals and all protection/conductor/interface selections, select the firmware platform/toolchain/kinematics, compile reproducible binaries, and prepare disconnected-load HIL procedures. Do not issue a build or energization release until the applicable gate records close.
