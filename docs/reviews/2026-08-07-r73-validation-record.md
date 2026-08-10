# R73 validation record - unpowered mechanical evaluation reconciliation

Date: 2026-08-07

Configuration: `HR-V0-BOM-P0.1` plus `HR-V0-MECH-EVAL-P0.1`; controlled mechanical configuration remains `HR-V0-MECH-P0.6` / `HR-V0-ARM-ARCH-P0.7`

Status: **PRELIMINARY - PROGRAM-OWNER APPROVAL REQUIRED BEFORE PURCHASE - UNPOWERED EVALUATION ONLY - NOT APPROVED FOR FABRICATION, MOTION, OR ENERGIZATION**

## Defect corrected

R53 removed the S102 body-frame purchase while the arm interface was unresolved. R69 subsequently froze the current P0.7 architecture around two exact FR13-S102K sets, but Evaluation Batch A remained stale. The receiving plan therefore could not produce physical fit evidence for A00 and A04.

## R73 result

- verified the current official ROBOTIS identity `FR13-S102K Set`, SKU `903-0269-300`, and its X540 compatibility and published package contents;
- moved `BOM-023` from `exact_candidate_hold` to `evaluation_candidate`;
- restored `EVA-013` with quantity two and the required receiving route;
- raised Evaluation Batch A from 16 to 17 exact evaluation-only lines;
- added `HR-V0-MECH-EVAL-P0.1`, a seven-line subset covering nine actuator/frame/gripper articles for unpowered receiving and metrology;
- added checker assertions for exact parent/order-code/quantity parity, complete subset membership, and the unpowered/program-owner-approval boundary; and
- retained `EG-003` as partial.

## Automated validation

```text
python tools/generate_hr_v0_bom_closure.py
python tools/check_hr_v0_bom.py
python tools/check_energization_gates.py --through-stage E2
```

Controlled result:

```text
73 system BOM groups
17 evaluation candidates
20 exact candidate holds
28 selection-required groups
EG-003 PARTIAL
0 of 21 gates through E2 closed
```

## Release boundary

No purchase has been approved or placed. No hardware has been received. No article may be connected, powered, torque-enabled, or used in an assembly. The published kit contents do not establish fastener material, grade, torque, allocation, structural capacity, or Project Button suitability. Physical inspection, fit, mass, metrology, proof, nonconformance closure, and qualified review remain required.
