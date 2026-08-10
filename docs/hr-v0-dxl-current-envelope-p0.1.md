# HR-V0 DXL current envelope P0.1

> **PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, MOTION, OR ENERGIZATION**

Identifier: `HR-V0-DXL-CURRENT-ENV-P0.1`
Round: R154
Date: 2026-08-09

## Engineering decision

ROBOTIS documents an approximately 2.69 mA Current Limit/Goal Current unit. The existing XM540 raw-800 candidate therefore screens to 2.152 A internally; the gripper raw-300 candidate screens to 0.807 A. Compared arithmetically with JST's published 3 A EH basis at AWG 22, the XM540 screen is 0.848 A lower. That difference is not a tolerance, transient allowance, external branch-current limit or application approval.

R154 retains the present internal-current-limit plus branch-fuse architecture for guarded qualification only. An ATOF fuse is rejected as the sole connector-overload control because its time-current behavior does not create an instantaneous 3 A ceiling. Per-branch hardware current limiting and a changed actuator/power architecture remain explicit fallback options if physical evidence cannot close the present path.

## Firmware correction

The actuator configuration now binds accepted current-envelope evidence before its release selections can close. During every motion-sample poll, the supervisor re-reads Current Limit and Goal Current. Any drift from the configured candidate raises a bus fault, removes torque on a best-effort basis and invalidates the active trajectory. Source tests inject both faults. This is defense-in-depth with zero functional-safety credit.

## Physical closure still required

The [interactive guide](../release/hr-v0/dxl-current-envelope-p0.1/index.html) contains three derived axis screens, eight runtime/configuration invariants, four architecture choices, eleven staged measurement steps, fourteen blank acceptance rows and fourteen open holds. Closure still requires received cable identity, calibrated synchronized external-current data, connector/cable/board/actuator thermal evidence, voltage drop, regeneration/no-backfeed behavior, exact fuse selection and clearing, representative duty, DXL integrity, received-HIL fault injection, qualified review and separate written authorization.
