# Independent review request - HR-V0 governance control P0.1

> **PRELIMINARY - NOT APPROVED FOR FABRICATION, CONNECTION, MOTION, OR ENERGIZATION.**

Review `HR-V0-GOV-P0.1` against `requirements/requirements.csv`, `safety/risk-register.csv`, `requirements/hr-v0-energization-gates.csv`, `tests/procedures/procedure-registry.csv`, `GOV-001` and Sol R12 B-018/N-004.

Please independently check:

1. Exact coverage of all 81 requirements, 40 risks and 30 gates.
2. Whether every requirement preserves its source status and verification ID.
3. Whether every risk preserves its source status and linked requirements.
4. Whether every gate preserves its source owner, status, stage and required evidence.
5. Whether candidate accountable/approver roles are sensible and sufficiently independent without being misrepresented as named assignments.
6. Whether any evidence pointer could be misread as executed or accepted evidence.
7. Whether the conservative 66-row compound screen misses any compound requirement or incorrectly implies that the other 15 are approved as atomic.
8. Whether the nine holds cover named people, qualifications, independence, decomposition, row-level history, immutable evidence, approval decisions, residual-risk decisions and baseline acceptance.
9. Whether the source hashes and release-candidate binding fail closed on drift.
10. Whether the interactive register remains readable and unambiguous on desktop and mobile.

Return BLOCKER / MAJOR / MINOR findings with exact file, record and field references. Do not approve fabrication, connection, powered testing, motion or energization.
