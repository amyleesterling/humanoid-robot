# HR-V0 unpowered mechanical evaluation subset P0.1

Document ID: **HR-V0-MECH-EVAL-P0.1**

Date: 2026-08-07

Parent: `HR-V0-BOM-P0.1` / Evaluation Batch A

Status: **PRELIMINARY - PROGRAM-OWNER APPROVAL REQUIRED BEFORE PURCHASE - UNPOWERED EVALUATION ONLY**

## Purpose

R53 removed FR13-S102K from Evaluation Batch A while the body-frame architecture was unresolved. R69 later froze `HR-V0-ARM-ARCH-P0.7` around two exact FR13-S102K body-frame sets, but the evaluation batch was never reconciled. That made the planned receiving and fit evidence incapable of covering the current controlled arm.

R73 restores `EVA-013` with two ROBOTIS FR13-S102K sets, SKU `903-0269-300`. The current official ROBOTIS product page identifies the set as a bottom/side frame for the X540 series and lists one frame, four FWB M2.5x17 bolts, eight WB M2.5x5 bolts, ten WB M2.5x4 bolts, and ten spacer rings per set. Those published contents are expected inventory only; they do not establish fastener material, grade, torque, allocation, structural strength, fit, or approval for Project Button.

## Controlled subset

`bom/hr-v0-unpowered-mechanical-evaluation.csv` extracts seven Evaluation Batch A lines covering nine physical articles:

- two XM540-W270-T actuators;
- one XM430-W350-T actuator;
- one RM-X52 gripper mechanism/frame set;
- two FR13-H101K moving-frame sets; and
- two FR13-S102K body-frame sets.

The subset contains no power source, U2D2, energized test article, custom metal, guard, receiver, or released fastener installation. Each line remains `PROGRAM OWNER APPROVAL REQUIRED` and may only be received, quarantined, inventoried, photographed, weighed, and dimensionally inspected after separate purchase approval. Receipt does not authorize assembly use.

## Evidence sequence

1. Record the purchase approval and purchase order against each received unit in `tests/forms/hr-v0-evaluation-batch-a-receiving-template.csv`.
2. Quarantine every article. Record exact markings, model, lot/date, contents, condition, photographs, received mass, and discrepancies.
3. Execute `INSPECT-MECH-005` for every H101/S102 frame item and fastener. Do not assume the included fasteners are allocated to the P0.7 project interfaces.
4. Execute the R72 gripper receiving, CAD-acquisition, and datum-metrology forms for RM-X52/XM430 without power.
5. Correlate received actuator/frame geometry to the frozen manufacturer STEP sources and record model-to-article residuals and fit-coupon results.
6. For the two XM540/H101/S102 joint allocations, execute the staged `HR-V0-JOINT-MET-P0.1` traveler. No threaded temporary stack is permitted until its screw-length, mounting-depth, spacer, fixture and temporary-torque hold points are signed.
7. Keep every article quarantined until its item-specific nonconformances and qualified dispositions close.

## Release boundary

This correction makes the evaluation plan configuration-complete for unpowered actuator/frame/gripper receiving. It does not authorize a purchase, connection, torque enable, custom fabrication, assembly use, motion, or energization. `EG-003`, `EG-005` through `EG-009`, `MECH-005`, `MASS-002`, and all gripper holds remain open or partial.

Primary source: [ROBOTIS FR13-S102K Set](https://robotis.us/fr13-s102k-set/), SKU `903-0269-300`, accessed 2026-08-07.
