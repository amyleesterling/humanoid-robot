# Sol R12 Findings Rechecked against R38

> **PRELIMINARY—NOT APPROVED FOR FABRICATION OR ENERGIZATION**

Date: 2026-08-07

This is a project-owned reconciliation, not a new independent Sol review. Sol's R12 totals remain **18 BLOCKER, 30 MAJOR and 8 MINOR** against the historical configuration. The user-supplied summary is archived separately at `docs/reviews/2026-08-07-sol-independent-engineering-review-summary.md` without double-counting it.

## R38 correction

R38 adds `HR-V0-ACT-P0.1`, a guarded actuator-current and configuration-readback candidate:

- exact ROBOTIS control-table addresses and fail-off configuration rules for current-based position mode;
- proposed raw internal-current limits of 800 for J1/J2 and 300 for the gripper;
- an explicit calculation showing raw 800 is nominally 2.152 A internal current and an ideal 5.18 N·m XM540 stall-line screen;
- an executable validator that inhibits torque on open selections or identity, firmware, mode, startup/drive-bit, torque-state, current-limit, goal-current or hardware-error mismatch;
- eight new unit tests, bringing the source-level package to 25 passing tests;
- one new requirement, two controlled procedures and an unexecuted current/torque/thermal evidence form; and
- protection-register and gate traceability updates.

## What R38 narrows

- The internal actuator configuration needed before torque enable is now explicit and executable rather than an unspecified future transport behavior.
- The candidate has a reproducible low-current escalation route and rejects startup torque and torque-on-goal-update behavior.
- The ideal XM540 screen indicates that raw 800 could have useful momentary headroom over the preliminary 3.83 N·m shoulder load screen, subject to real efficiency, thermal and dynamic evidence.

## Retained blockers

- The DYNAMIXEL current register describes internal motor current; it is not a guaranteed external branch-supply-current limit. The XM540 4.4 A stall endpoint versus JST EH 3 A rating conflict is **not closed**.
- ROBOTIS states 21 AWG DYNAMIXEL wire while JST publishes AWG 22 as the EH series maximum conductor size. The received harness and manufacturer application basis remain unresolved.
- No actuator, harness or connector has been received, identified, instrumented or tested. Model numbers, firmware versions and the external branch-current ceiling remain deliberately open, so the repository configuration fails closed.
- No continuous torque, efficiency, duty-cycle, voltage-drop, thermal, regeneration, protection-clearing or gripper-force evidence exists.
- There is still no compiled DYNAMIXEL transport, target binary, HIL record or independent source review.
- Every physical-build, mechanical, functional-safety and energization blocker retained in R37 remains open. Through E2 the gate result remains 0 closed, 15 partial and 6 open.

## Disposition

Sol's central verdict remains correct. R38 turns one controls/current-limit ambiguity into reviewable code, calculations and a physical evidence route. It does not make HR-V0 buildable or energizable and does not advance HR-30W walking readiness.

