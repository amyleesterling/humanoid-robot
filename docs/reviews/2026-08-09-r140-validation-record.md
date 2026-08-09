# R140 validation record - HR-V0 frame/sign convention P0.1

> **PRELIMINARY - NOT APPROVED FOR FABRICATION, MOTION, CONNECTION, OR ENERGIZATION.**

Date: 2026-08-09

Controlled product: `HR-V0-FRAME-CONV-P0.1`

## Result

R140 adds one right-handed HR-V0 coordinate/sign convention, a fail-closed raw-calibration boundary, machine-readable registers, and an interactive review guide. It does not add physical datum, calibration, motion, fabrication, functional-safety, or energization evidence.

- All 85 standard `check_hr_v0_*.py` checkers outside the release-manifest and five KiCad-native checkers passed.
- The final release-manifest checker passed, for **1929** hash-bound package files.
- Traceability passed: 81 requirements, 40 risks, 110 procedures, and 57 release/walking-document procedure references resolved.
- Strict through-E2 readiness failed closed as required: 21 applicable gates, 0 closed and 21 partial.
- The coordinate checker passed: six frames, four proper transforms, three engineering axes, four legacy mappings, six blank calibration records and ten open holds.
- Native KiCad checks retained ERC/DRC-clean modeled scope and retained every fabrication/CAM/energization prohibition.
- `git diff --check` passed before commit.

## Interactive-guide QA

The R140 guide was inspected at 1280 x 720 desktop and in a 390 x 844 mobile viewport. Body and functional text remain at least 16 CSS pixels, the page does not overflow horizontally, the frame table uses controlled horizontal scrolling on the narrow viewport, and the pose explorer updated the rendered endpoint at both ordinary and limit values. The explorer remains explicitly a sign/kinematic teaching view, not a collision, stop, calibration, or motion release.

## Open evidence

All ten coordinate-convention holds remain open. Required evidence includes physical datum marking and survey, received actuator identity, raw direction/scale/zero calibration with uncertainty and witnesses, H104/gripper/TCP registration, successor guard coordinates, CFG-002 fault execution, a separate HR-30 left/right convention, and qualified mechanical/controls review.

No gate closed in R140. No reviewer authorized procurement, fabrication, assembly, connection, powered calibration, motion, energization, functional-safety credit, untethered use, or operation around children.
