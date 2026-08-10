# Sol R12 Findings Rechecked Against R23

Date: 2026-08-06

Package baseline: **HR-30-SYS-R0.2**

Status: **PROJECT-OWNED RECONCILIATION - NOT A NEW INDEPENDENT REVIEW OR APPROVAL**

## Review identity

This is a project-owned reconciliation, not a new Sol review. Sol's R12 totals remain 18 BLOCKER, 30 MAJOR and 8 MINOR against the historical 62-requirement baseline. Sol has not independently reviewed R13-R23, and this pass cannot close or renumber those findings. The current controlled package has 63 draft requirements because R23 adds `MASS-002`.

## R23 evidence added

R23 addresses a bounded part of Sol's missing mass/COM/inertia evidence finding by adding:

- `MASS-002`, an explicit 750 g HR-V0 moving-assembly requirement including the 100 g payload and excluding the fixed shoulder actuator/base;
- `bom/hr-v0-moving-mass-ledger.csv`, with 13 controlled component groups that include frames, fasteners, stop parts, connectors, cables and gripper mechanics;
- `tests/forms/hr-v0-moving-mass-measurement-template.csv`, a 13-row unexecuted evidence record;
- `INSPECT-MECH-007` and `REVIEW-MASS-002`; and
- a reproducible calculation in `cad/hr-v0/generated/mechanical-checks.json`.

The current screen supports 565.4 g from two CAD link estimates, the manufacturer-published XM540/XM430 masses, and the 100 g payload ceiling. It leaves 184.6 g for every unresolved moving item. The known subtotal consumes 75.4% of the ceiling, and each 120 g link bucket has only 10.8 g left for its frame, hardware and harness share.

## Disposition against Sol's conclusions

| Sol R12 conclusion | R23 status |
|---|---|
| HR-V0 is not build ready | **Still correct.** The mass evidence route is now controlled, but key moving parts have neither released geometry nor measured mass properties. |
| HR-V0 energization is prohibited | **Still correct.** A ledger and calculation do not provide electrical, functional-safety or physical-test approval. |
| Mass and inertia are not closed | **Still correct, now quantified.** Known subtotal is 565.4 g; 184.6 g remains unresolved; local COM and inertia are unmeasured. |
| No requirement has executed approved verification evidence | **Still correct.** The new form is deliberately `NOT-EXECUTED`. |
| HR-30W walking is plausible but unproved | **Still correct.** R23 covers only HR-V0 moving mass and does not close full-body mass, leg torque, energy, sensing, control or collapse behavior. |

## Closure boundary

R23 converts an unstructured mass concern into an auditable measurement and review problem. It does not prove that the 750 g ceiling can be met. Closure requires the exact configuration, measured mass and local COM for every row, a reviewed inertia method, reconciliation of component and assembly measurements, rerun torque/stop/gripper calculations, and qualified mechanical review. Lighter plates or a controlled allocation change may be necessary.

**PRELIMINARY - NOT APPROVED FOR FABRICATION OR ENERGIZATION.**
