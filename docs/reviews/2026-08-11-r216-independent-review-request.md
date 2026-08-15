# R216 independent E2 evidence-parity review request

> **PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION.**

Review exact commit and package `HR-V0-E2-EVIDENCE-P0.2`. Do not treat the historical P0.1 unpowered-configuration or authorization template as current, and do not treat either hardware traces or software logs as independently sufficient.

## Required review

1. Independently verify all seven recorded SHA-256 values and the eight controlled configuration identities.
2. Confirm the P0.2 unpowered form has exactly 32 columns and one 32-value blank row; `HR-V0-RC-P0.1` must occupy `release_candidate_id` and `file_manifest_sha256` must remain blank.
3. Confirm the P0.2 authorization form has exactly 43 columns and requires exact configuration, hardware slice, evidence contract, both EG-021 records, actuator-source/branch exclusion, shutdown, expiry, revocation, four roles, competence and independence.
4. Check every E2-SL-001 through E2-SL-020 pairing against both source forms.
5. Confirm trajectory is `NONE`, torque-enable request is `FALSE` and stale replay is `REJECTED` for every case.
6. For E2-SL-005 and E2-SL-019, confirm an ON coil path cannot be interpreted as actuator-power or motion authority because the actuator source must be physically absent and every actuator branch disconnected and covered.
7. Review the relationship between RESET, distinct ARM, hardware permissive state and fresh-command authority. Confirm RESET/ARM alone cannot create a trajectory or torque request.
8. Confirm EG-018 through EG-022 remain partial and enumerate every additional physical, site, method, numerical-limit, instrument, reviewer and execution input needed before a qualified E2 authorization could even be considered.
9. Confirm the package makes no loaded-interruption, stopping-distance, PL/SIL, functional-safety, fabrication or energization claim.
10. Review the desktop/mobile guide for legibility, ambiguity, link integrity and warning prominence.

## Required response

Return BLOCKER / MAJOR / MINOR findings with exact file, row, field and case references. Distinguish repository-definition findings from physical evidence that only qualified execution can supply. Do not mark the machine approved for connection, powered test, motion or energization.
