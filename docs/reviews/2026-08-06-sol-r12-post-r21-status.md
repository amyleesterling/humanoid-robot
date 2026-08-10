# Sol R12 Findings Rechecked Against R21

> **PRELIMINARY - NOT APPROVED FOR FABRICATION OR ENERGIZATION**

Date: 2026-08-06

Current configuration: `HR-30-SYS-R0.2`, Electrical `V3-P0.4`, firmware `HR-V0-FW-P0.1`, mechanical `HR-V0-MECH-R0.1-PRELIMINARY`

## Scope and independence

This is a project-owned status reconciliation, not a new independent review. The Sol analysis resupplied on 2026-08-06 is the existing R12 review: 18 BLOCKER, 30 MAJOR, 8 MINOR, 62 draft requirements, 106 unresolved Electrical V2.1 selections, and no approved executed verification evidence on the reviewed baseline. It remains logged once as R12.

Sol has not independently reviewed R13-R21. This document may identify historical claims made stale by later source additions, but it cannot close Sol's findings or alter their original totals.

## Material R21 correction

R20 incorrectly carried a single symmetric PCD22 hole-pattern assumption into three proposed production parts. Current primary manufacturer evidence distinguishes the interfaces:

- the H101 output frame uses the actuator output/idler interface represented by the selected eight-hole PCD22 candidate;
- the S102 body frame presents a separate four-hole 32 x 16 mm tapped rectangle on its broad face; and
- no gripper mounting interface has been selected.

R21 therefore corrects `MV0-001` to H101-to-S102, corrects `MV0-003` to S102, and removes invented distal holes from `MV0-002`. It adds the separate nonstructural `MV0-FC02` S102 coupon, `INSPECT-MECH-004`, per-hole inspection rows, official kit-content schedules, and a receiving template. Nominal H101-frame plus link thickness is recorded as 6.75 mm, and the 2.5 mm actuator tap depth gives an absolute nominal geometric under-head bound of 9.25 mm. That bound is not a screw selection: thread engagement, tolerance stack, washer use, grade, torque, retention, received-part dimensions, and manufacturer application acceptance remain unresolved.

The calculation pipeline now refreshes `SOURCE-MANIFEST.csv` after writing `mechanical-checks.json`, preventing a generated calculation from being left outside the final hash state.

## Current disposition

| Sol R12 conclusion | R21 status |
|---|---|
| No buildable HR-V0 mechanical definition | **Still open.** R21 corrects a real topology defect and improves executable inspection controls, but received-part fit, gripper interface, fasteners, hard stops, guards, cable paths, anchoring, tolerance analysis, mass properties, strength/proof tests, assembly sequence, and qualified review remain incomplete. |
| Authoritative repository lacks native implementation | **Partly stale.** The correction branch contains native ECAD, source-level firmware, and preliminary mechanical source. None is a build or energization release. |
| HR-V0 energization is prohibited/not ready | **Still correct.** The E2 gate checker still reports 21 applicable unresolved gates: 13 partial and 8 open, with zero closed. |
| HR-30W walking is plausible but unproved | **Still correct.** R21 adds no full-body mass, continuous leg-torque, power-loss, restraint, or walking-test evidence. |

## Verdict

R21 prevents fabrication from proceeding with a false shared-interface assumption and creates a controlled route to collect received-part evidence. It does not make HR-V0 fabrication-ready or energization-ready. Only unpowered coupon fabrication, receiving inspection, and qualified preliminary review are within the present package boundary.
