# HR-V0 complete moving-system mass, COM and inertia closure P0.1

> **PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION**

Identifier: `HR-V0-MOVING-PROP-CLOSURE-P0.1`

Round: R248

State: blank execution contract; no physical result

## Outcome

R248 converts Sol blocker B-010 and R247-H11 from a broad request into an executable, fail-closed physical-evidence contract. It covers all 17 current moving-mass ledger rows, ten mass repeats per row, four assembled configurations, loose-to-assembled mass reconciliation, two orthogonal reaction-force COM measurements, and calibrated J1/J2 bifilar inertia measurements.

It closes neither finding. No received article, measurement, instrument, fixture, calibration, uncertainty, acceptance, motion credit or work authority exists in this package.

## Measurement rules

- Every ledger row must resolve to a received part/lot or an explicitly itemized share. CAD and catalog masses remain planning inputs only.
- Every accepted mass requires raw repeats, tare, instrument identity, configuration hash, calibration evidence and a reproducible expanded-uncertainty statement.
- Each assembled configuration must reconcile its measured mass with the accepted loose-item sum under a limit selected before execution.
- COM is measured in two orthogonal directions from two support reactions. The reaction sum must reconcile with an independent mass measurement.
- Inertia uses NASA's calibrated-pendulum form with two known calibration bodies of similar mass for each axis. The approximate geometry-only bifilar equation is a screening cross-check, not accepted evidence.
- The test article CG must lie on the pendulum rotation axis, parasitic swing must be controlled, and timing must cover 10–50 cycles.
- The calculator refuses a record unless it is explicitly `EXECUTED` and `ACCEPTED`. Its numbers remain nominal calculations; qualified uncertainty and acceptance are separate.

## Primary-source basis

- NISTIR 6969, *Selected Laboratory and Measurement Practices and Procedures to Support Basic Mass Calibrations*, 2019-05-07: <https://doi.org/10.6028/NIST.IR.6969-2019>
- NISTIR 6919, *Recommended Guide for Determining and Reporting Uncertainties for Balances and Scales*, January 2002: <https://www.nist.gov/document/nistir6919pdf>
- NASA/TP-2006-212490-VOL2-PT 2, *Aeroelasticity Handbook, Volume 2: Design Guides, Part 2*, 2006-11-01: <https://ntrs.nasa.gov/citations/20070008370>

The NIST documents support traceable mass practice and a combined/expanded uncertainty statement. NASA supports accurate CG placement, pure rotation, multi-cycle timing and calibration with two known objects. None supplies application approval for this fixture.

## Controlled artifacts

- Interactive guide: `release/hr-v0/moving-properties-closure-p0.1/index.html`
- Source package: `mechanical/metrology/hr-v0-moving-properties-closure-p0.1/`
- Calculator: `tools/calculate_hr_v0_moving_properties_p01.py`
- Deterministic checker: `tools/check_hr_v0_moving_properties_closure_p01.py`
- Configuration reconciliation: `HR-V0-CONFIG-REC-P0.12`

## Remaining closure

Twelve package holds and ten acceptance rows remain open. Qualified reviewers must approve the method, fixtures, uncertainty budgets and results; then torque, stopping, structural and control analyses must be reconciled to the accepted as-built properties. Until that occurs, Sol B-010, R247-H11 and affected gates remain open.
