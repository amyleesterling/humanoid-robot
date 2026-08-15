# R196 independent review request

> **PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION**

Please review `HR-V0-STALE-AUTH-P0.1` against `SAFE-008`, `CTRL-007`, `TEST-SAFE-003`, `TEST-E2-002`, the current supervisor source and E2 hardware boundary.

1. Does the supervisor clear every active trajectory on all relevant dropout and fault paths?
2. Does retaining `last_sequence` across fault acknowledgement prevent replay of the pre-drop command?
3. Can RESET, ARM, heartbeat restoration, process restart or bus restoration create a torque request without a new session-valid command?
4. Are the twenty software-authority expectations consistent with the existing E2 hardware-state form, especially `E2-SL-019`?
5. What deployed-image, HIL, timing, logging, fault-injection and physical evidence is still required?
6. Confirm that the package assigns zero functional-safety credit and grants no test or energization authority.
