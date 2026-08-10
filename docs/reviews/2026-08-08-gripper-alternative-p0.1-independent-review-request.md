# Independent review request - HR-V0-GRIP-ALT-P0.1

Status: **PRELIMINARY - NOT SELECTED - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, MOTION, OR ENERGIZATION**

Please review the R111 source-controlled gripper alternative trade study for accuracy and completeness. This is a project-owned candidate comparison, not an approval request and not a fabrication package.

## Reproduce

Run:

`C:\Users\amyle\Documents\New project\.venvs\hr-v0-cad\Scripts\python.exe tools/check_hr_v0_gripper_alternative_p01.py`

Independently verify every file against its current primary manufacturer source and compare SHA-256, byte count and file signature to both source manifests. Import both STEP files in an independent CAD system and report solid count, bounding box, unit interpretation, missing components and any repair or translation warnings.

## Challenge explicitly

1. Is Pololu item 3551 actually a complete, currently orderable kit, and do the source-controlled drawing, STEP and guide match that exact item?
2. Does a controlled 25-30 mm soft foam object remain inside `SYS-002` without weakening the task?
3. Are the 30 g / 32 mm and 101 g claims correctly bounded as catalog data rather than received evidence?
4. Does the mass screen omit or double-count any adapter, guard, pad, cable, hardware or moving component?
5. Can a direct adapter from the current 20-2040 two-M5 end interface be defined without retaining H104, and what exact drawing/received evidence is still absent?
6. Are all pinch, bind, drop, force, wear, cable-retention and fixed-guard hazards represented?
7. Does the proposed post-K1/K2 6 V branch preserve redundant actuator-power interruption, and are any regulator, fuse, conductor, connector, PWM or analog-input facts being inferred?
8. Can E-stop release, manual reset, supervisor boot, PWM-source reset, brownout or feedback failure create motion? Identify every required fault injection.
9. Does changing from DYNAMIXEL to a hobby feedback servo require a requirements, ECAD, firmware, diagnostics, risk or verification change not listed in GAH/GSI?
10. Is `GRIP-002` too solution-specific, and what controlled change is required before candidate selection?

Return BLOCKER / MAJOR / MINOR findings with exact artifact, row, interface and requirement references. Cite only current primary manufacturer documentation with revision/date or an explicit “no revision shown” statement.

The review must not select the gripper, release a purchase, assign functional-safety credit, or authorize fabrication, connection, motion or energization.
