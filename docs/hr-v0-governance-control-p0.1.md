# HR-V0 governance control P0.1

> **PRELIMINARY - NOT APPROVED FOR FABRICATION, CONNECTION, MOTION, OR ENERGIZATION.**

Date: 2026-08-09

Identifier: `HR-V0-GOV-P0.1`

## Result

R141 places every current requirement, risk and energization gate into one hash-bound governance snapshot:

- 81 requirements;
- 40 risks;
- 30 energization/release gates;
- 151 total controlled records;
- 66 requirements conservatively screened as compound and requiring stable atomic children;
- 15 requirements screened only as atomic candidates requiring independent confirmation;
- 9 open governance holds;
- 0 named accountable people;
- 0 named approvers;
- 0 executed evidence records; and
- 0 approved records.

The package assigns candidate accountable and approver roles so missing responsibility is visible. A role label is not a person, a file path is not executed evidence, and a generated snapshot is not a controlled decision. Every named-person, competence, independence, evidence, signature and prior row-level history field therefore remains fail-closed.

## Governance model

Each requirement record binds its current draft status, verification procedure, procedure-defined evidence, candidate accountable role and candidate approver role. Each risk record binds its linked requirements and proposes a lead role only for independent review. Each gate record retains the source gate owner, stage, required evidence and current status.

No source requirement, risk or gate is rewritten in R141. The source files remain authoritative. The generated registers are a review/control layer and fail if their membership, source status, verification ID, owner role or source hash drifts.

## Atomicity boundary

The atomicity register is a conservative screen, not a decomposition. Sixty-six source requirements contain multiple measurable duties or explicitly coupled conditions. Their child register remains `NOT ISSUED`. Before approval, each must receive stable child IDs with one testable obligation, retained parent trace, a verification method, numeric acceptance where applicable and independent requirements review.

The other fifteen rows are only `ATOMIC CANDIDATE`. Independent review may still require decomposition. No source row becomes approved or passed from this classification.

## Evidence and history boundary

Gate evidence locations are pointers to candidate artifacts, not proof that tests or reviews occurred. Requirement and risk evidence URIs remain `NOT EXECUTED`. The R141 snapshot records its own change, but historical record-level changes have not been backfilled. Git history and the review ledger remain supporting history, not a substitute for a controlled per-record decision trail.

## Controlled artifacts

- `requirements/governance-p0.1/requirement-control-register.csv`
- `requirements/governance-p0.1/risk-control-register.csv`
- `requirements/governance-p0.1/gate-control-register.csv`
- `requirements/governance-p0.1/requirement-atomicity-review.csv`
- `requirements/governance-p0.1/governance-holds.csv`
- `requirements/governance-p0.1/source-register.csv`
- `requirements/governance-p0.1/governance-summary.json`
- `release/hr-v0/governance-p0.1/index.html`
- `tools/generate_hr_v0_governance_control.py`
- `tools/check_hr_v0_governance_control_p01.py`

## Closure route

`GOV-001` and Sol R12 finding B-018 remain open until named people are selected, qualifications and independence are accepted, compound requirements are decomposed, historical row-level changes are controlled, immutable executed evidence is bound to the exact configuration, residual risks are decided, and qualified approvers sign every applicable decision.

No energization gate closes in R141.
