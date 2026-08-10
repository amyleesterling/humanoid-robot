# R154 independent review request - DXL current envelope

> **PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, MOTION, OR ENERGIZATION**

Independently review `HR-V0-DXL-CURRENT-ENV-P0.1` against current official ROBOTIS XM540/XM430, JST EH and Littelfuse ATOF documentation, the controlled actuator configuration, supervisor source and existing protection architecture.

Recalculate each raw-current screen. Challenge the conclusion that fuse-only protection is insufficient as a connector overload ceiling and the conditional retention of internal Current Limit plus continuous readback plus branch fuse for guarded qualification. Inspect whether Current Limit and Goal Current drift force torque-off in source tests without being misrepresented as safety-rated behavior. Review all eleven physical measurement stages and fourteen acceptance groups for completeness, including current-probe bandwidth, RMS windows, temperature stabilization, voltage drop, regeneration, no-backfeed, fuse clearing, DXL errors and simultaneous duty.

Report BLOCKER / MAJOR / MINOR findings with exact file, row, register, test and primary-source evidence. Do not infer a fuse value, external current limit, connector approval or permission to energize.
