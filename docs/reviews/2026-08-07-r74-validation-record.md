# R74 validation record — fixed guard and receiver candidate

**PRELIMINARY—NOT APPROVED FOR FABRICATION, MOTION, CONNECTION, OR ENERGIZATION.**

Date: 2026-08-07

Round: R74

Candidate: `HR-V0-GUARD-P0.2`

Parent mechanical configuration: `HR-V0-MECH-P0.6` / `HR-V0-ARM-ARCH-P0.7`

## Scope

R74 responds to the continuing Sol R12 blockers for an unspecified transparent enclosure, incomplete dynamic containment and stale guard verification inputs. It does not reclassify Sol's original review and it does not claim that a guard safety distance, structural assembly or impact rating has been established.

## Controlled changes

- Generated native STEP and GLB enclosure/receiver geometry from a checked Python source.
- Added a readable SVG and a responsive HTML guide with 16 px minimum functional text.
- Added a four-line, sixteen-piece 20 × 20 mm profile-envelope cut schedule and represented the Y–Z radial reservation as a 400 mm-deep extruded disk rather than an unsupported full sphere.
- Added a four-line, eight-piece nominal 6 mm transparent-panel envelope schedule.
- Added eight interface controls, four source records, three calculation screens and twelve fail-closed holds.
- Replaced obsolete guard inspection inputs with the current P0.7 J1 `-20..70°`, J2 command `15..115°`, and J2 continuous-certificate `120°` cases.
- Bound `HR-V0-GUARD-P0.2` into the mechanical release-candidate supporting identifiers.

## Validation performed

1. `generate_hr_v0_guard_receiver.py` completed and exported STEP/GLB/SVG/HTML/CSV/JSON artifacts.
2. `check_hr_v0_guard_receiver.py` passed the exact artifact membership, dimensional, selection-state, hold, source-boundary, inspection-form, warning, legibility and neutral-format checks.
3. The legacy CAD checker was updated only to recognize the expanded twelve-case guard template; its historical P0.1 geometry checks remain unchanged.
4. All 25 `tools/check_*.py` validators passed. The DXL-star and watchdog-PCB checks used KiCad 10.0's Python because they import `pcbnew`; the remaining checks used the controlled CAD Python environment.
5. Traceability passed at 81 requirements, 40 risks and 104 procedures. The gate register remained fail-closed at 0 closed, 22 partial and 8 open.
6. The staged release manifest expanded from 775 to 792 files and passed exact membership/hash validation. Clean-clone reproduction is recorded against the final commit before push.

## Visual QA boundary

The generated SVG was inspected structurally for a 1600 × 1080 view box, minimum 18 px drawing text and unclipped coordinate bounds. The HTML enforces 16 px body/table/code text and a mobile single-column table reflow. The in-app browser refused local `file:` navigation under its URL policy, so no claim is made that an interactive browser screenshot was captured. A reviewer should open the committed HTML locally or through a safe static host and test desktop and narrow viewports.

## Result

R74 advances `EG-008` design evidence but does not close it. The 450 mm reserved radius is still not a safety distance. Exact profile, sheet, joints, clamps, fasteners, anchors, cable entry, complete sweep, stopping, access, impact, stability, detached-part containment, physical tests and qualified review remain open. No procurement, cutting, drilling, fabrication, installation, motion, connection or energization authority is created.
