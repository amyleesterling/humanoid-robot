# R199 independent review request

> **PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION**

Review `HR-V0-RUNTIME-BACKENDS-P0.1` as source architecture, not as permission to install or connect hardware.

1. Challenge the heartbeat scheduler for startup, first edge, lateness, clock reversal, disable, process exception and close behavior.
2. Confirm that a static permission value can no longer be mistaken for a watchdog waveform.
3. Review the libgpiod 2.x API use, lazy-import boundary, bias-disabled inputs and fail-closed configuration parsing.
4. Review AF_UNIX credential handling, UID/GID comparison, exact JSON schema, finite-number rejection, datagram bounds, queue/flood and producer-failure behavior.
5. Challenge the new maximum-sample, duration, execution-slack, cycle and sample-lateness requirements; propose no numerical release without target measurements.
6. Audit the nine physical observations against the current electrical source. Identify the qualified receiver/isolation, loading, protection, cabling, grounding, line allocation and noninterference evidence needed without inferring a circuit.
7. Confirm backend import remains after pure-file preflight and the exact source hashes match the overlay/configuration.
8. Confirm RESET/E-stop release still cannot command motion and that all target, HIL, physical and qualified evidence remains open.
9. Confirm the ordinary compute, heartbeat and supervisor receive zero functional-safety credit.
