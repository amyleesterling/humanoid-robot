# HR-V0 moving-mass closure P0.1 — R70 study update

> **PRELIMINARY—MASS LEDGER AND SCREEN ONLY—NOT APPROVED FOR FABRICATION, MOTION, OR ENERGIZATION.**

Date updated: 2026-08-07

Requirement: `MASS-002`

Configuration input: `HR-V0-ARM-ARCH-P0.7` / `HR-V0-J2-STOP-P0.1`

Controlled ledger: `bom/hr-v0-moving-mass-ledger.csv`

Measurement form: `tests/forms/hr-v0-moving-mass-measurement-template.csv`

## R69 result

The 750 g moving-assembly ceiling includes the 100 g payload and excludes only the fixed J1 actuator, support, column, base and bench anchors. Every item rotating about J1 must be counted exactly once.

| Known or CAD-estimated item | Mass |
|---|---:|
| C01 + 100 mm upper member + C07 | 190.289 g |
| J2 XM540 actuator | 165.000 g |
| C06 + 50 mm forearm member + C04 | 155.469 g |
| gripper XM430 actuator | 82.000 g |
| maximum permitted payload | 100.000 g |
| **known/estimated subtotal** | **692.758 g** |
| **unresolved headroom to 750 g** | **57.242 g** |

The subtotal consumes 92.37% of the ceiling before either H101 frame/idler set, the S102 frame, the selected bumper/retention, fasteners, spacers, complete gripper mechanism/pads/guard, connectors, guides, strain relief, or any moving cable is counted. The upper-link bucket is already 70.289 g over its 120 g allocation and the forearm bucket is 35.469 g over its allocation.

This is a **mass-budget blocker**, not a pass. The remaining 57.242 g is unlikely to contain all unresolved items, but the project shall measure rather than invent their masses. The response may require a higher justified system mass/torque envelope, lighter C06/C07/link geometry, a lighter gripper, or a different architecture. Any change requires updated torque, inertia, stop-impact, structure, guard and thermal evidence.

## R70 nonselected relief study

`HR-V0-MASS-REDUCTION-P0.1` defines C01R/C04R/C06R/C07R as exact subtractive subsets of the controlled P0.7 adapters. The four-part CAD estimate falls by 57.983 g. If selected after independent review and physical evidence, the incomplete known/CAD-estimated subtotal would become 634.775 g and provisional unresolved headroom would become 115.225 g.

R71's `cad/hr-v0/generated/gripper-integration-p0.2/gripper-mass-load-sensitivity.csv` parameterizes additional gripper mass at the ledger's shoulder/elbow radii. It does not assign an actual gripper-mechanism mass and does not reserve either the 57.242 g controlled headroom or the 115.225 g nonselected-study headroom for the gripper; other unresolved frames, hardware, bumper and moving cables compete for the same total.

This does not close `MASS-002`. The relieved parts are not selected, the additional headroom is still smaller than a controlled allocation for all missing frames/mechanism/fasteners/harness items, and no received mass exists. The controlled ledger therefore continues to record P0.7 C01/C04/C06/C07. See `docs/hr-v0-mass-reduction-study-p0.1.md` and `cad/hr-v0/generated/mass-reduction-p0.1/`.

CAD values assume 2.70 g/cm³ and are estimates pending the exact stock certificate, thickness, finish and first-article measurement. Purchased-member estimates use the published mass per length. Received mass governs.

## Closure procedure

1. Freeze the exact configuration and repository commit.
2. Execute the 17-row measurement form with calibrated equipment; record local COM and uncertainty.
3. Cross-check individual totals against assembled moving subassemblies and investigate discrepancies.
4. Determine inertia using an accepted CAD/physical method, including reflected drivetrain inertia where applicable.
5. Recalculate gravity, acceleration, continuous torque, stop impact, base/guard and thermal cases from the same configuration.
6. Close or formally revise every bucket and the 750 g ceiling; unused allocation may not hide an omitted item.
7. Obtain qualified mechanical review before any torque/current/stop/proof value is released.

No CAD estimate, supplier mass, apparent headroom or unused bucket is permission to omit, fabricate, move or energize hardware.
