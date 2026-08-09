# R141 validation record - HR-V0 governance control P0.1

> **PRELIMINARY - NOT APPROVED FOR FABRICATION, CONNECTION, MOTION, OR ENERGIZATION.**

Date: 2026-08-09

Controlled product: `HR-V0-GOV-P0.1`

## Result

R141 adds a source-hash-bound governance-control layer over every current requirement, risk and gate. It assigns only candidate roles and keeps named people, qualifications, independence, evidence, signatures, decisions and prior row-level history open.

- The governance checker passed: 81 requirements, 40 risks, 30 gates, 151 total records, 66 compound screens, 15 atomic candidates and 9 open holds.
- The complete HR-V0 checker suite passed: **92** domain checkers including five KiCad-native checks and the release-manifest checker.
- The final release-manifest checker passed for **1943** hash-bound package files.
- Traceability passed: 81 requirements, 40 risks, 110 procedures, and 57 release/walking-document procedure references resolved.
- Strict through-E2 readiness failed closed as required: 21 applicable gates, 0 closed and 21 partial.
- `git diff --check` passed before commit.

## Interactive-guide QA

The R141 register was inspected at 1280 x 720 desktop and in a 390 x 844 mobile viewport. Desktop body and functional text is 16 CSS pixels, page-level horizontal overflow is absent, the wide table uses controlled horizontal scrolling, and the mobile warning wraps without clipping. Type filtering returned exactly 30 gate rows. Searching `EG-021` returned one exact record with its source owner, E2 stage, evidence requirement, candidate approver role and `NOT APPROVED` decision.

## Open evidence

All nine governance holds remain open. Sixty-six compound requirements still need stable atomic child IDs; the other fifteen remain candidates pending independent requirements review. No named accountable person, named approver, competence record, independence record, immutable executed evidence URI, residual-risk decision, signature or prior row-level history has been accepted.

`GOV-001` and Sol R12 B-018/N-004 remain open. No gate closed in R141. No reviewer authorized procurement, fabrication, assembly, connection, powered testing, motion, energization, functional-safety credit, untethered use, or operation around children.
