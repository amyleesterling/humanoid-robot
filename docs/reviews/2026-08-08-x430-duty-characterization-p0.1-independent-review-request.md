# Independent review request — HR-V0 X430 duty characterization P0.1

> **PRELIMINARY — NOT APPROVED FOR POWERED TEST, MOTION, CONNECTION, OR ENERGIZATION.**

Please independently review `HR-V0-X430-DUTY-P0.1` for accuracy, completeness, physical testability and fail-closed authorization boundaries. This is a review request, not permission to execute any stage.

## Review scope

1. Verify the current ROBOTIS XM430-W350-T/R primary-manufacturer page and record its visible revision/date status.
2. Confirm that 4.1 N·m at 12 V / 2.3 A is treated only as a momentary stall endpoint and that no continuous rating is inferred.
3. Verify the control-table addresses, units and ranges used for Current Limit (38), Hardware Error Status (70), Present Current (126), Present Input Voltage (144) and Present Temperature (146).
4. Check every row and equation in `current-torque-sensitivity.csv`; confirm it is an idealized sensitivity and not a command or selection.
5. Verify that the R96 gravity and 2.25× values remain incomplete references and are not released as fixture or acceptance loads.
6. Check all fifteen instrumentation channels, especially external current, terminal voltage, reaction torque, temperature placement, external angle and synchronization.
7. Determine whether the proposed primary-versus-supplemental evidence split is adequate.
8. Check all twelve fixture controls for missing load-path, guarding, catching, force alignment, regenerated-energy, cable, thermal-sensor and human-factor requirements.
9. Review the twelve-stage sequence and confirm every powered stage is blocked until its prerequisites and signed work authorization close.
10. Review the ten acceptance equations and identify the evidence needed to select actual current, voltage-margin, thermal-rise, slope, repeatability, cool-down and abort limits.
11. Check that the blank form and raw schema can capture synchronized evidence without silently omitting resets, shutdowns, fault states or branch-power state.
12. Cross-check `LOAD-OPEN-08`, `LOAD-OPEN-01`…`05`, energization gates, gripper/payload gates and the generic R78 characterization package for configuration conflict.
13. Identify the exact additional drawing, component selection, calculation, calibration or procedure needed to make the fixture buildable.
14. State whether any unpowered stage may proceed and whether any powered stage is ready. Do not infer approval from automation.

## Required verdict

Return prioritized BLOCKER / MAJOR / MINOR findings with exact file/row/channel/stage/hold references, proposed corrections supported by primary sources, and a clear statement of what remains unverified. Do not approve fabrication, powered testing, motion, connection, energization or functional-safety credit.
