# R198 independent review request

> **PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION**

Review `HR-V0-RUNTIME-P0.1` and the corrected `HR-V0-HOST-DEPLOY-P0.1` source boundary.

1. Confirm every selected backend import occurs after pure-file preflight and exact supervisor/actuator selection closure.
2. Review heartbeat-disallow ordering on startup, every exception, SIGTERM/SIGINT and shutdown.
3. Challenge torque-off-before-discovery, torque/goal-current state invariants and received-position conversion.
4. Review the RESET/ARM/no-command, stale-command, dropout and process-restart authority boundaries.
5. Challenge the sample-lateness scheduler, terminal-target refresh and execution-deadline interaction.
6. Review all nineteen source-to-target overlay mappings, ownership/modes and the service sandbox against the eventual GPIO/serial access needs.
7. Define the target tests needed for GPIO startup state, timing/jitter, serial latency/loss/unplug, power loss, rollback and corrupted input.
8. Confirm zero functional-safety credit and no installation, connection, HIL, motion or energization authority.
