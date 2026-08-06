# Project Button Current Engineering Handoff

Handoff date: 2026-08-06  
Package baseline: **HR-30-SYS-R0.2**  
Electrical package: **Project Button Electrical V2.1**  
Mechanical package: **HR-V0-MECH-R0.1-PRELIMINARY quote geometry**
Status: **PRELIMINARY—NOT APPROVED FOR ENERGIZATION**

## Authority and presentation

- Authoritative engineering repository: `https://github.com/amyleesterling/humanoid-robot`
- Interactive presentation: `https://project-button-workshop.amysterling.chatgpt.site/`
- Configuration and identifier rules: `docs/configuration-management.md`
- Complete review history: `docs/review-ledger.md`
- Authoritative native ECAD: `electrical/kicad/project-button-v2/project-button-v2.kicad_pro`
- ECAD source manifest: `electrical/kicad/project-button-v2/SOURCE-MANIFEST.csv`

The authoritative repository controls engineering intent and now contains the native Electrical V2.1 KiCad source. The website is a synchronized presentation and must not override the source specification. Individual documents retain their own revisions; Electrical V2.1 is independent of the `HR-30-SYS-R0.2` systems-package baseline.

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

ERC validates modeled connectivity and annotation only. It does not establish physical pinouts, ratings, protection coordination, functional safety, buildability, or permission to energize.

## Review history and independent findings

Fifteen review/control rounds are complete and recorded in `docs/review-ledger.md`. R11 Fable and R12 Sol were commissioned independently against GitHub `main` at `ee276af...` before the R13/R14 corrections. R11 reported 7 BLOCKER, 11 MAJOR, and 12 MINOR findings. R12 reported 18 BLOCKER, 30 MAJOR, and 8 MINOR findings. R13 staged the authoritative-ECAD provenance correction; R14 corrected reproducible engineering and traceability defects; R15 archived and dispositioned Sol's complete dossier and corrected three deterministic documentation defects. Physical and functional-safety blockers remain open.

## Principal unresolved engineering blockers

1. HR-V0 now has native parametric quote geometry, four custom-part DXF/STEP/STL sets, readable drawings, vendor CAD provenance, a GLB/STEP assembly-space model, and preliminary plate/column screens. It is not a released manufacturing package: frame fit, fasteners, hard stops, cable paths, gripper, guard, bench anchoring, mass closure, proof tests, and independent mechanical review remain open. HR-30 has no released mechanical CAD.
2. Joint continuous/cyclic/impact/thermal performance, drivetrain efficiency, backlash, and structural margins are not physically validated.
3. Safe actuator-power-loss behavior remains unresolved; a walking robot may collapse when hazardous drive energy is removed.
4. Mass, center of mass, inertia, wiring mass, and reserve are not closed against released CAD and measured components.
5. Exact E-stop devices, contactors, protection, suppression, conductors, connectors, enclosure, mains implementation, and ratings remain selection-dependent.
6. Battery, BMS, fuse, precharge, service disconnect, charging interlock, regeneration, telemetry isolation, and enclosure remain topology only.
7. RS-485 transceivers, harnesses, shielding, termination, biasing, separation, waveform margin, and physical fault tests remain open.
8. Sensor sheets are functional interfaces, not complete production circuits or released PCB designs.
9. No released real-time controller, firmware, state-machine implementation, bus timing measurement, HIL evidence, or reset-to-motion fault test exists.
10. No physical release-gate test has passed; fixtures, calibrated instrumentation, raw records, accountable owners, approvers, FMEA/FTA, and common-cause review remain incomplete.

R11 and R12 added material blockers or invalidated assumptions. R14 records the failed arm/leg mass screen, removes the fixed 4S and 14.8 V sizing basis, blocks direct-drive hip roll, reduces initial walking speed to 0.10-0.14 m/s, makes TCP speed governing, defines 61 verification procedures, and creates a preliminary safety-function register. R15 makes the processor-ownership boundary explicit and records every Sol finding without treating R14 as part of Sol's reviewed baseline. The Electrical V2.1 watchdog restoration path, mass closure, battery/rail, joint selection, protection, CAD, safe power loss, restraint dynamics, response time/stopping distance, PLr/SIL determination, real-time implementation, and physical testing remain open. See `docs/reviews/2026-08-06-fable-review-disposition.md`, `docs/reviews/2026-08-06-sol-r12-review-disposition.md`, and `docs/r11-engineering-calculations.md`.

## Requested independent-review output

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

Merge and post-merge validate the controlled review branch, then complete the HR-V0 physical FR13 fit coupon and the missing hard-stop, cable, gripper, guard, fastener, bench-anchor, mass, and proof-test design. In parallel, freeze exact electrical selections and protection coordination, correct the watchdog restart hardware, perform safety-function PLr/SIL analysis, and implement the control firmware. Do not issue a build or energization release until the applicable gate records close.
