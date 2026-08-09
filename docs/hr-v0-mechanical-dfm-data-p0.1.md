# HR-V0 mechanical DFM data P0.1

> **PRELIMINARY - NOT APPROVED FOR QUOTATION, FABRICATION, ASSEMBLY, MOTION, OR ENERGIZATION.**

Identifier: `HR-V0-MECH-DFM-DATA-P0.1`

Round: R134

Controlled architecture: `HR-V0-ARM-ARCH-P0.7`

## Outcome

The current five custom aluminum candidates now have one deterministic internal qualified-review dataset: five exact part records, fifteen SHA-256-bound STEP/DXF/SVG identities, 26 source inspection controls, thirty unexecuted first-article operations, twelve unsent DFM questions and fifteen open holds.

This corrects the stale R91 statement that an exact-coordinate X430 comparison still had to be produced. P0.8 through P1.1 comparison evidence now exists. P1.1/X430 remains nonselected because moving mass/COM/inertia, continuous duty, tolerances, stops, interfaces and physical evidence are incomplete. P0.7 remains the controlled architecture.

## Manufacturing boundary

- Candidate material is 6061-T651 aluminum, 9.525 mm nominal and 9.00..10.00 mm finished.
- One high-requirement 3-axis CNC route remains the screened process for C01/C04/C05/C06/C07.
- The earlier 4.75 mm SendCutSend route remains rejected. SendCutSend may only be reconsidered as a separately controlled blank source; it is not a finished-part route.
- No provider has accepted a tolerance, material, inspection plan, workholding method or file.
- Every FAI operation is `UNEXECUTED`; every hold is `OPEN`; every external-action flag is false.

## Controlled artifacts

- [Interactive review guide](../release/hr-v0/mechanical-dfm-data-p0.1/index.html)
- `release/hr-v0/mechanical-dfm-data-p0.1/part-register.csv`
- `release/hr-v0/mechanical-dfm-data-p0.1/geometry-file-register.csv`
- `release/hr-v0/mechanical-dfm-data-p0.1/inspection-control-register.csv`
- `release/hr-v0/mechanical-dfm-data-p0.1/first-article-plan.csv`
- `release/hr-v0/mechanical-dfm-data-p0.1/dfm-question-register.csv`
- `release/hr-v0/mechanical-dfm-data-p0.1/hold-register.csv`
- `release/hr-v0/mechanical-dfm-data-p0.1/package-status.json`

## Permitted next action

Qualified mechanical reviewers may inspect and redline the exact controlled files and registers. Provider contact, file upload, quotation, purchase, first-article machining, fabrication, assembly, motion and energization remain prohibited until separately authorized after the applicable holds close.

Automated consistency proves file identity and internal completeness only. It does not prove machinability, strength, fit, stopping behavior, safety or readiness for fabrication or energization.
