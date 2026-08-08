# Independent review request - gripper CAD acquisition and datum control

Review configuration: `HR-V0-GRIP-CAD-ACQ-P0.1` supporting `HR-V0-GRIP-P0.2`
Date: 2026-08-07
Status: **PRELIMINARY - NOT APPROVED FOR FABRICATION, MOTION, OR ENERGIZATION**

Please independently review the package for accuracy, completeness, and fail-closed behavior. This is not a request to approve fabrication or energization.

## Controlled inputs

- `docs/hr-v0-gripper-cad-acquisition-p0.1.md`
- `cad/hr-v0/gripper-source-availability-p0.1.csv`
- `cad/hr-v0/gripper-datum-control-p0.1.csv`
- `tests/forms/hr-v0-gripper-cad-acquisition-template.csv`
- `tests/forms/hr-v0-gripper-datum-metrology-template.csv`
- `tests/procedures/procedure-registry.csv` row `AUDIT-GRIP-002`
- `tools/check_hr_v0_gripper_cad_acquisition.py`
- parent package `docs/hr-v0-gripper-architecture-p0.2.md`

## Review questions

1. Does the source-state register accurately distinguish assembly context, page metadata, visual/collision meshes, native manufacturing geometry, and a released datum definition?
2. Are the publisher-file and received-part-metrology routes sufficient to close the full mechanism definition without guessed dimensions?
3. Does the datum-control register cover all six rigid-transform quantities, mounting/thread interfaces, moving/guard envelope, opening, mass, and local COM?
4. Could any template, wording, or checker output be misread as evidence that a source file, measurement, tolerance, guard, fit, or assembly has been accepted?
5. What additional raw evidence, instruments, uncertainty treatment, drawing controls, assembly residuals, or qualified competence is required before merging the gripper into the P0.7 collision and load model?
6. Confirm that `GRH-001`, `GRH-002`, `MECH-005`, `MASS-002`, fabrication, motion, and energization remain open.

Report BLOCKER / MAJOR / MINOR findings with exact file, row, datum, requirement, or hold references. Cite current primary manufacturer sources with document revision/date where available. Do not infer missing geometry, ratings, order codes, tolerances, or approval.
