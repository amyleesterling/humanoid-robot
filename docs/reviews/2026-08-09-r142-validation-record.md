# R142 validation record - atomic requirements and governance P0.2

**PRELIMINARY - NOT APPROVED FOR FABRICATION, CONNECTION, MOTION, OR ENERGIZATION**

Date: 2026-08-09

Products: `HR-V0-REQ-ATOMIC-P0.1`, `HR-V0-GOV-P0.2`

## Generated control results

- 66/66 R141 compound parents covered.
- 396 unique, sequential parent-scoped child candidates.
- 2 minimum and 23 maximum children per parent.
- Every child contains one normative `shall` and no semicolon.
- Parent level, priority and verification-procedure binding preserved.
- 8 atomic holds and 9 governance holds remain open.
- 0 named people, 0 executed evidence, 0 approved parents/children/records.

Both `check_hr_v0_atomic_requirements_p01.py` and `check_hr_v0_governance_control_p02.py` passed. The historical P0.1 checker also passed after the release candidate was advanced to P0.2, proving the P0.1 snapshot remained intact and explicitly supported.

## Package validation

All 94 `check_hr_v0_*.py` checkers passed: 89 under the controlled project Python environment and five native PCB checkers under KiCad 10.0's Python/`pcbnew` environment. The aggregate traceability checker passed with 81 requirements, 40 risks, 110 procedure definitions and 57 release/walking-document procedure references resolved.

The through-E2 gate check remains fail closed: 0 of 21 applicable gates are closed and all 21 are partial. This is the expected non-readiness result, not a test failure.

## Visual QA

The atomic-requirement and governance P0.2 web guides were inspected from the local release tree at wide desktop size and through a 390 x 844 mobile viewport. Body/functional text is 16 CSS pixels, the warning is readable and wraps on mobile, desktop has no page-level horizontal overflow, and wide registers use controlled scrolling. No clipping or unreadable functional text was observed.

## Disposition

R142 is internally consistent as a review candidate. It does not establish that the 396 children are complete or atomic; independent review and formal acceptance remain required. `GOV-001`, Sol B-018/N-004, every physical evidence requirement, and all fabrication/connection/motion/energization authorization remain open.
