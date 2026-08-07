# Independent engineering review request — HR-V0 mechanical P0.6/P0.5

> **PRELIMINARY—NOT APPROVED FOR FABRICATION OR ENERGIZATION.** Do not interpret a passing checker as physical validation or work authorization.

Repository: `https://github.com/amyleesterling/humanoid-robot`

Branch/PR at issue: `codex/review-ledger-handoff`, draft PR 4

System baseline: `HR-30-SYS-R0.2`

Mechanical hold: `HR-V0-MECH-P0.5`

Arm candidate: `HR-V0-ARM-ARCH-P0.6`

Stop basis: `HR-V0-HS-P0.2`

## Review objective

Independently assess the accuracy, completeness, reproducibility and buildability of the current HR-V0 mechanical candidate. Do not review presentation quality alone. Re-derive the geometry, interval bounds and allocation mathematics where practical.

## Priority questions

1. Does the adaptive continuous-clearance method conservatively cover the complete stated joint domain and all 70 non-intentional rigid-body pairs without an unsafe exclusion, transform error or non-rigid assumption?
2. Are the chord-displacement bounds additive and valid for the base/forearm two-axis case, including nested rotation about J1 and J2?
3. Are the intentional interface exclusions exactly the four designed H101/body/S102 adjacencies and no more?
4. Is the numerical first-contact result `121.643289 deg` reproducible from the controlled solids and critical pair?
5. Does the proposed `115/118/121.643289 deg` software/stop/contact allocation fail closed? Identify any missing term in the separate 3-degree stopping and 2.643289-degree physical-uncertainty budgets.
6. Is a 1-degree nominal collision guard defensible, or should the provisional command/stop allocation be reduced further before physical testing?
7. What exact stop geometry, material/bumper data, load cases, tolerances, instrumentation and acceptance limits are still required before a qualified reviewer could release a stop article?
8. Do the current native CAD, tables, procedures, release metadata and warnings describe one configuration without promoting candidate values to fabrication or motion limits?
9. Are any Sol R12 mechanical blockers incorrectly shown as closed or omitted from the current handoff/gates?
10. Does the repository retain any current-facing stale P0.4/P0.5 value that could cause the wrong part, motion range or test to be used?

## Controlled evidence

- `docs/hr-v0-arm-architecture-p0.6.md`
- `docs/hr-v0-mechanical-release-p0.5.md`
- `docs/hr-v0-hard-stop-design-basis-p0.2.md`
- `cad/hr-v0/generated/arm-architecture-p0.6/architecture-summary.json`
- `cad/hr-v0/generated/arm-architecture-p0.6/continuous-clearance-analysis.json`
- `cad/hr-v0/generated/arm-architecture-p0.6/continuous-clearance-summary.csv`
- `cad/hr-v0/generated/arm-architecture-p0.6/continuous-clearance-cells.csv`
- `cad/hr-v0/generated/arm-architecture-p0.6/hard-stop-allocation.csv`
- `cad/hr-v0/generated/arm-architecture-p0.6/HR-V0_arm_architecture_candidate.step`
- `cad/hr-v0/generated/arm-architecture-p0.6/HR-V0_arm_architecture_candidate.glb`
- `cad/hr-v0/mechanical-release-data.csv`
- `cad/hr-v0/mechanical-interface-control.csv`
- `requirements/hr-v0-energization-gates.csv`
- `tests/forms/hr-v0-j2-limit-stop-template.csv`
- `tools/generate_hr_v0_arm_architecture.py`
- `tools/check_hr_v0_arm_architecture.py`

## Reproduction

On Windows with the project CadQuery environment:

```powershell
& 'C:\Users\amyle\Documents\New project\.venvs\hr-v0-cad\Scripts\python.exe' tools\generate_hr_v0_arm_architecture.py
& 'C:\Users\amyle\Documents\New project\.venvs\hr-v0-cad\Scripts\python.exe' tools\check_hr_v0_arm_architecture.py
& 'C:\Users\amyle\Documents\New project\.venvs\hr-v0-cad\Scripts\python.exe' tools\generate_hr_v0_mechanical_release.py
& 'C:\Users\amyle\Documents\New project\.venvs\hr-v0-cad\Scripts\python.exe' tools\check_hr_v0_mechanical_release.py
```

The P0.6 generator takes roughly three minutes on the current workstation. Compare a second P0.6 generation byte-for-byte. Do not use the legacy whole-package OCC generator as evidence of byte reproducibility without separately accounting for export timestamps/order/GUID behavior.

## Requested deliverable

Return a BLOCKER / MAJOR / MINOR finding register with exact file, record, pair, joint range, transform or line reference; the reproduced calculations; any counterexample pose; proposed correction; evidence needed to close it; and a final statement distinguishing nominal analytical closure from physical build and energization readiness.

Do not approve fabrication, motion, connection, energization, functional safety or child-adjacent operation.
