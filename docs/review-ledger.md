# Project Button Review Ledger

Package baseline: **HR-30-SYS-R0.2**  
Ledger revision: 0.1  
Updated: 2026-08-06  
Status: preliminary; not approved for fabrication, procurement, or energization

This ledger records both independent reviews and controlled correction/validation passes. A correction pass is not an independent review. A clean check closes only the specific issue and configuration identified in its evidence record.

| Round | Date | Type | Reviewer / owner | Configuration reviewed | Principal result | Controlled evidence |
|---|---|---|---|---|---|---|
| R01 | 2026-08-05 | Evidence and public-claim audit | Codex engineering audit | Initial concept website and downloadable artifacts | Determined that the presentation was not a build package; removed unsupported safety, child-use, battery, CAD, and implementation claims. | `project-button/engineering/site-audit.md` |
| R02 | 2026-08-05 | Integrated-site accuracy review | Codex engineering audit | Revised website, mechanical artifacts, and preliminary electrical presentation | Rechecked local links, warnings, component claims, fabrication boundaries, legibility, and consistency after the first blocker corrections. | `project-button/engineering/site-audit-final.md` |
| R03 | 2026-08-05 | Independent preliminary electrical review | Claude Fable 5 | Website commit `df1555a`; 13-file preliminary KiCad set | Found zero schematic symbols, zero real nets, 368 ERC violations, an invalid hand-authored netlist, and safety-relay/reset blockers. Package was not ready for qualified review. | `project-button/engineering/electrical/audits/2026-08-05-preliminary-electrical-review.md`; complete ERC report/JSON |
| R04 | 2026-08-05 | Electrical V2 design review | Codex correction/review pass | First connected 15-sheet KiCad V2 package | Replaced line art with connected ECAD and reviewed E-stop, reset, EDM, watchdog, contactors, mains separation, battery topology, buses, sensors, and schedules. Residual selections remained blocking. | `project-button/engineering/electrical/audits/2026-08-05-v2-electrical-review.md` |
| R05 | 2026-08-05 | Independent electrical V2 review | Claude Fable 5 | Connected V2 package: 136 components, 176 total nets, 97 open selections | Independently reproduced clean ERC and topology improvements; corrected two earlier reviewer claims; identified unverified PNOZ s4 monitored-reset behavior, IDEC evidence, U2D2, pinout, and fuse-coordination issues. | Fable handoff dated 2026-08-05; findings incorporated into V2.1 correction record |
| R06 | 2026-08-05 | Electrical V2.1 correction and validation | Codex engineering pass | V2.1-P0.2: 15 sheets, 142 components, 168 named nets, 106 unresolved selections/interfaces | Verified Pilz reset mode and terminals, removed premature fuse values, corrected U2D2 handling, added protection/suppression placeholders, synchronized schedules/exports, and achieved ERC 0/0. Still not buildable or energizable. | `project-button/engineering/electrical/kicad/project-button-v2/2026-08-05-v2.1-electrical-correction-review.md`; validation directory |
| R07 | 2026-08-05 | Independent full-system engineering review | Sol | HR-30 website, rig, specifications, release gates, walking architecture, BOM/risk files, and 15-sheet electrical package | Identified safe-power-loss collapse as the largest blocker; challenged stall-torque prominence, output sensing, mass/inertia closure, CAD maturity, controls, sensing, timing, governance, and human-facing scope. | Independent Sol engineering verdict supplied 2026-08-05 |
| R08 | 2026-08-05 | Full-system review disposition and correction | Codex engineering pass | Authoritative specification after R07 | Accepted and traced Sol findings into new requirements, risks, gates, evidence maturity, output-sensing baseline, timing contract, governance controls, and operating boundaries without inventing selections. | `docs/independent-review-disposition.md` |
| R09 | 2026-08-06 | Independent claim and configuration audit | Claude/Fable review | Deployed site, website repository, authoritative repository, KiCad outputs, BOM, unresolved register, and traceability data | Independently confirmed the V2.1 counts and ERC status; found stale deployment/commit reporting and conflicting `V2.2`, Revision 0.2, and Revision 0.1 labels. | Reviewer report supplied 2026-08-06 |
| R10 | 2026-08-06 | Configuration-control correction and deployment validation | Codex engineering pass | Systems package and website after R09 | Established `HR-30-SYS-R0.2`, preserved independent document revisions and Electrical V2.1, corrected 62/40 counts, added configuration management, rebuilt/tests/lint, and deployed website version 22. | `docs/configuration-management.md`; website commit `fd440229f4cbe61b0578cef153e4bbe94880c283`; GitHub PR #2 |
| R11 | 2026-08-06 | Independent design accuracy/completeness review | Fable | GitHub `main` at `ee276af…`, deployed presentation, and published Electrical V2.1 package | Complete: 7 BLOCKER, 11 MAJOR, and 12 MINOR findings. New material issues include impossible arm-mass allocation, 4S voltage/torque conflict, missing hip-roll load analysis, knee-speed deficit, watchdog restart topology, verification-ID gaps, and TCP/joint-speed conflict. | `docs/reviews/2026-08-06-fable-independent-engineering-review.txt`; disposition file in same directory |
| R12 | Requested | Independent design accuracy/completeness review | GPT Sol | Current `HR-30-SYS-R0.2` authoritative package | Pending. Same scope as R11; review must be completed without seeing Fable's conclusions. | Evidence record to be added when received |
| R13 | 2026-08-06 | ECAD provenance correction and validation | Codex engineering pass | Authoritative repository after R11 interim finding | Added the controlled native KiCad V2.1 project, 15 schematic sheets, symbol library, schedules, validation records, and generated source-hash manifest to the authoritative tree; corrected electrical release-area and handoff claims. | `electrical/kicad/project-button-v2/`; `electrical/kicad/project-button-v2/SOURCE-MANIFEST.csv`; corrective GitHub PR |

## Counting rule

- Rounds R03, R05, R07, R09, R11, and R12 are independent reviewer passes.
- Rounds R01, R02, R04, R06, R08, R10, and R13 are project-owned audits, correction passes, or validation passes.
- A reviewer follow-up that materially rechecks the controlled package receives a new round. Editorial discussion without checked artifacts does not.
- Superseded findings remain in the ledger; their disposition is recorded rather than erased.

## Current review state

Eleven rounds are complete, including R11; R12 is requested. No round has approved fabrication, procurement, energization, functional safety, untethered operation, or operation around children.
