# HR-V0 Boston bench survey and anchor-release procedure P0.1

**Status:** **PRELIMINARY - SURVEY NOT EXECUTED - NO ANCHOR, FABRICATION OR ENERGIZATION RELEASE**

## Scope

This procedure converts the unspecified Boston workbench into controlled mechanical input. It does not permit drilling, through-bolting or mounting. The facility owner or responsible operator must first identify the exact bench and document what work is permitted.

Use [`tests/forms/hr-v0-boston-bench-survey-template.csv`](../tests/forms/hr-v0-boston-bench-survey-template.csv) for `INSPECT-MECH-011`.

## Survey sequence

1. Record the site, exact bench identity, owner/contact and written permission reference.
2. Photograph the top, every edge, underside, supports, existing holes, obstructions and intended robot footprint.
3. Identify the top material and construction. Measure thickness only where direct access or an approved method exists; do not infer a hidden sandwich or core.
4. Measure usable width/depth, intended footprint, edge distances, top/underside access and obstruction clearances.
5. Record whether drilling and through-bolting are each permitted. Blank, unknown or verbal-only permission is a failed survey.
6. Record the instrument and calibration reference for every dimensional result. Flatness method and acceptance remain subject to qualified mechanical definition.
7. Leave anchor type, backing plate, design shear/tension loads and proof load `SELECTION REQUIRED` until the final machine load cases and substrate evidence are reviewed.

## Engineering disposition after survey

A qualified mechanical reviewer shall:

- select an exact anchor, bolt, washer, backing plate and retention method compatible with the actual substrate;
- calculate shear, tension, overturning, edge-distance, bearing, pull-through and local bench/support loads for normal, stop, jam, impact and foreseeable misuse cases;
- set numerical installation torque, proof load, proof duration, slip/deflection and damage acceptance limits;
- determine whether the bench itself and its floor attachment can carry the loads;
- revise or replace `MV0-004` and its drawing from the resulting interface; and
- issue a separate first-article and proof-test authorization.

No generic anchor rating may be substituted for the actual substrate, thickness, edge geometry, installation and load direction. No proof test may begin without facility permission, a guarded test method and written load/acceptance limits.

## Acceptance boundary

`INSPECT-MECH-011` remains open until the survey, calculation, exact anchor selection, controlled drawing, installation record, proof record and qualified disposition all exist for the same bench and repository configuration. Passing the survey alone does not close `EG-005`, `EG-006`, `EG-007`, `EG-008` or authorize energization.
