# R124 independent review request - stopping budget and active J2 limit

Status: **PRELIMINARY - NOT APPROVED FOR FABRICATION, MOTION OR ENERGIZATION**

Please independently review `HR-V0-STOP-BUDGET-P0.1` against the current controlled configuration, not against historical 120/125/130-degree studies.

Review at minimum:

1. Confirm `docs/control.md`, `firmware/supervisor/actuator-config.json`, `HR-V0-LIMITS-P0.2` and the current mechanical narrative consistently use J2 `15..115 deg` for command screening.
2. Confirm 125 degrees appears only as an explicitly outside-limit or historical collision-analysis value.
3. Recalculate the 3-degree approach from the 115-degree software ceiling to the 118-degree nominal positive metal backup.
4. Recalculate the 300/100 ms traversal screens at 10/30 degrees per second.
5. Confirm a 300 ms heartbeat-detection term corresponds to 3/9 degrees at those speeds before downstream delay and cannot receive stopping-distance or safety credit.
6. Confirm the 24 ms Schneider datum is treated only as one component term and not as total stopping time or DC interruption approval.
7. Confirm J1 minimum, J1 maximum and J2 minimum remain motion-prohibiting `DESIGN REQUIRED` boundaries.
8. Check the sixteen-case form for missing timing channels, fault cases, uncertainty, guard reconciliation or configuration controls.
9. Confirm no statement assigns PLr/SIL, validates a safety function, releases a speed/profile or authorizes powered work.

Report findings as `BLOCKER`, `MAJOR` or `MINOR`, with the exact file, row or field and the evidence needed to close each issue.

Primary artifacts:

- `docs/hr-v0-stopping-budget-p0.1.md`
- `controls/hr-v0-stopping-budget-p0.1.csv`
- `tests/forms/hr-v0-stopping-time-template-p0.1.csv`
- `release/hr-v0/stopping-budget-p0.1/index.html`
- `tools/check_hr_v0_stopping_budget_p01.py`
- `requirements/hr-v0-energization-gates.csv` (`EG-026`)

This request is not an approval request for motion or energization; it is a request to find remaining defects in the candidate evidence chain.
