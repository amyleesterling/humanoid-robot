# Sol R12 Findings Rechecked Against R20

> **PRELIMINARY - NOT APPROVED FOR FABRICATION OR ENERGIZATION**

Date: 2026-08-06

Current configuration: `HR-30-SYS-R0.2`, Electrical `V3-P0.4`, firmware `HR-V0-FW-P0.1`, mechanical `HR-V0-MECH-R0.1-PRELIMINARY`

## Scope and independence

This is a project-owned status reconciliation, not a new independent review. The Sol analysis resupplied on 2026-08-06 matches the existing R12 verdict: 18 BLOCKER, 30 MAJOR, 8 MINOR, 62 draft requirements, 106 unresolved Electrical V2.1 selections, and no approved executed verification evidence on Sol's reviewed baseline. It is therefore logged once as R12 rather than counted again.

Sol has not independently reviewed R13-R20. Later project evidence may make a historical claim stale, but it does not backdate closure or alter Sol's original finding totals.

## R20 change

R20 addresses one bounded part of `B-003` and `M-004`: the proposed ROBOTIS broad-face hole pattern now has a native nonstructural fit-coupon definition (`MV0-FC01`), synchronized DXF/STEP/STL, a dimension-controlled 1:1 A4 overlay, X/Y print-scale checks, SHA-256 coverage, an unpowered per-hole procedure (`INSPECT-MECH-003`), and a controlled record template.

The manufacturer reference drawings for FR13-H101K and FR13-S102K are dated 2026-01-07, marked `NONSCALE` and `FOR REFERENCE ONLY`, and call out eight 2.5 mm through holes on a 22 mm pitch circle at 45-degree equal spacing on the relevant broad face. R20 keeps the project hole at candidate 2.70 mm clearance and explicitly makes the received parts govern the inspection.

## Current disposition

| Sol R12 conclusion | R20 status |
|---|---|
| No buildable HR-V0 mechanical definition | **Still open.** Coupon source and procedure now exist, but physical fit has not been executed and the production assembly, datums, tolerances, fasteners, hard stops, guards, cable paths, gripper, anchoring, mass properties, calculations, proof tests, and qualified review remain incomplete. |
| Authoritative repository lacks native implementation | **Partly stale.** Native ECAD, preliminary firmware, and preliminary mechanical quote geometry now exist on the correction branch. None is a released build baseline. |
| HR-V0 energization is prohibited/not ready | **Still correct.** The E2 checker reports 21 applicable unresolved gates: 13 partial and 8 open, with zero closed. |
| HR-30W is plausible but unproved | **Still correct.** R20 adds no walking-hardware evidence. |

## Verdict

R20 improves traceability and makes the first physical frame-interface check executable after the two frames are acquired. It does not make HR-V0 fabrication-ready or energization-ready. The package remains appropriate for qualified preliminary review and controlled unpowered evidence gathering only.
