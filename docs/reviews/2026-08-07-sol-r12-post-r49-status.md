# Sol R12 status after R49 frame-geometry correction

**PRELIMINARY—NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, OR ENERGIZATION**

Date: 2026-08-07

Independent source review: Sol R12, 18 BLOCKER / 30 MAJOR / 8 MINOR on the pre-correction baseline

Current project response: R49 / `HR-V0-FRAME-P0.2`

## Disposition

Sol's verdict remains correct: Project Button is a strong preliminary systems architecture, not yet a buildable or energizable machine. R49 corrects physical contradictions inside the candidate frame definition; it closes no physical release gate.

| Sol concern | R49 disposition | Still required |
|---|---|---|
| no buildable mechanical definition | corrected the base/upright member envelopes so square-cut members abut without positive-volume overlap | received-part CAD/fit, tolerances, bracket/gusset/tool access, exact remaining fasteners, FAI and released load-path CAD |
| unsuitable frame-joint candidate | superseded two-slot-wide `40-4334` with six single-face `40-4332` candidates | manufacturer/application disposition, received identity, dry fit and qualified acceptance |
| unspecified joint placement | six bracket ridges and controlled member faces are explicit in `frame-joint-placement-p0.2.csv` | physical access, real bracket envelope, tolerance and assembly-order evidence |
| unspecified fastener quantity | twelve `75-3422` assemblies enumerated, two per bracket | lot/pack evidence, crimp-free mechanical receiving, torque/proof and damage inspection |
| no joint load screen | 574.5 N one-bracket and 287.25 N ideal-shared screens recorded from 11.49 N m / 20 mm | real load distribution, prying, preload, slip, shock, fatigue, allowables and proof factors |

## Defects found in the project-owned R48 pass

- `40-4334` requires two adjacent slot positions and cannot be treated as a one-slot-per-face `40-4040` bracket for this topology.
- 320 mm transverse rails overlapped the longitudinal rails in four corner volumes.
- the upright began at Z=20 mm and overlapped the left rail through Z=40 mm.
- the prior X-face column bracket orientation did not align with the transverse rail top slot.
- the prior 287.25 N couple screen was tied to the incorrect geometry and did not bound a one-bracket load case.

R49 preserves the defective P0.1 record as superseded history rather than rewriting it as though it had been valid.

## What remains unchanged

- HR-V0 build readiness: **NOT READY**.
- HR-V0 energization readiness: **PROHIBITED**.
- all 72 requirements remain draft and no requirement has approved executed verification evidence.
- the 21 gates applicable through E2 remain 0 closed, 16 partial and 5 open.
- the ordinary heartbeat diagnostic receives zero safety credit.
- HR-30W walking remains a later feasibility program, not a demonstrated capability.

The Sol R12 finding totals remain the snapshot of Sol's independently reviewed baseline. R49 is a project-owned correction and is not a new independent review.
