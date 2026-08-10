# R194 validation record

> **PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION**

Artifact: `HR-V0-BOSTON-SITE-P0.2`

Date: 2026-08-10

## Controlled content

- Eight jurisdiction/program records distinguish controlled inputs, current official authority routes and the project-specific applicability hold.
- Eight source records identify the current Massachusetts, Boston, BPL, Watertown Library and controlled Project Button fabrication-route evidence, with access dates and exclusions.
- Six site-role records separate the unknown assembly/energization premises from nonstructural prototype resources and commercial CNC candidates.
- Twenty premises inputs remain intentionally blank and `SELECTION REQUIRED`.
- Eight site holds remain open.
- EG-001 and EG-022 remain partial. No requirement, Sol R12 finding or energization gate closes.

The dedicated fail-closed checker passed:

`python tools/check_hr_v0_boston_site_p02.py`

`HR-V0 Boston site P0.2 check passed: 8 jurisdiction facts, 8 sources, 6 site roles, 20 blank premises inputs and 8 open holds`

## Current primary-source recheck

The current Massachusetts electrical-code page states that 527 CMR 12.00 is based on the 2026 edition of NFPA 70 and became effective 2026-04-24. The current Boston electrical-permit page and Massachusetts electricians FAQ preserve the licensed-work, permit, inspection and local-authority route without deciding Project Button's exact applicability. The current BPL pages publish MakerBot/design resources and no reviewed CNC structural-metal capability. The current Watertown Library pages publish Hatch Makerspace and a laser-cutter learning route but do not close Project Button's material, tolerance or inspection requirements.

## Repository regression

- Governance regenerated and passed over 81 requirements, 40 risks and 30 gates, with 66 compound screens, nine open holds and zero approvals.
- Traceability passed over 81 requirements, 40 risks, 110 procedures and 57 release/walking-document procedure references.
- The build traveler regenerated and passed with 14 phases, 85 steps, 21 through-E2 gates, zero authorized steps and zero executed steps.
- The full standard-runtime checker set passed **138/138** after final staging and release-manifest regeneration.
- All **13/13** native KiCad `pcbnew` checkers passed under KiCad 10.0.5.
- The final staged release manifest contains **3,351 package files** and passed its dedicated content/hash checker.
- `check_energization_gates.py --through E2 --require-ready` returned non-ready as required: all 21 applicable gates remain partial and none are closed.

The initial standard sweep correctly exposed only a stale build-traveler source hash and the expected not-yet-staged release manifest. The traveler was regenerated from the changed gate register. No checker failure was suppressed or reclassified.

## Interactive-guide QA

The R194 guide was loaded from a local HTTP server in the in-app browser. At 1280 x 720, body text was 16 px, warning text 16 px, metadata 14 px and page-level horizontal overflow was zero. The role filter was exercised and displayed only the assembly/energization card when selected. At 390 x 844, the same text floors held, all five cards reflowed, page-level horizontal overflow remained zero and the wide evidence table used its intentional internal scroller. The browser console reported no warnings or errors. The temporary viewport was reset and the preview server was stopped.

## Boundary

This package supplies evidence structure and current-source provenance. It does not select a premises, provide written site permission, determine legal applicability, inspect a branch or receptacle, accept a bench/restraint, qualify a fabrication provider, receive external adapters, execute a physical test, authorize E2, or establish functional-safety performance.

**PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION**
