# R174 independent review request

Review `HR-V0-DYN-TRACE-P0.1` as an analysis and rejection-path candidate, not physical test evidence or an energization release.

1. Inspect `tools/analyze_hr_v0_dynamic_trace_p01.py` for event-edge, sustained-window, direction, residual-travel, endpoint-clearance, reset-observation, data-integrity and numerical-integration errors.
2. Reproduce the nominal synthetic results: 0.030 s total stop time, 0.435 degree residual travel and 6.065 degree endpoint clearance.
3. Confirm the reset-motion and too-early-start fixtures fail `DTA-007`, and the index/drop fixture fails `DTA-001`.
4. Challenge the required physical-run columns and identify any missing signal needed to distinguish commanded, achieved and power-path state.
5. Confirm every physical numeric input remains `SELECTION REQUIRED` and the unresolved template is rejected.
6. Confirm a computed pass can produce only `HOLD - QUALIFIED REVIEW REQUIRED`, never a release or approval.
7. Identify the required repetition, confidence, uncertainty, load, pose and single-fault matrix for eventual `EG-026` closure.

Return `BLOCKER / MAJOR / MINOR` findings with exact file, rule, field and line references. Do not infer physical evidence, functional-safety performance, test authorization, motion authority or permission to energize.
