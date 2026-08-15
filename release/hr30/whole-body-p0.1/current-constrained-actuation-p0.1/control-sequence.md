# Deterministic current-constrained control sequence

**PRELIMINARY - CURRENT/TORQUE ARCHITECTURE CANDIDATE ONLY - NOT APPROVED FOR CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION**

1. Keep actuator power interrupted and Torque Enable = 0.
2. Verify the physical bus, actuator model, firmware, unique ID and configured baud rate against the configuration record.
3. With torque disabled, write Operating Mode 5 only where the exact model supports Current-based Position Control; read it back.
4. Write the model-family Current Limit candidate from `actuator-control-register.csv`; read it back twice. Any mismatch latches a fault.
5. Write Goal Current no higher than the approved per-axis candidate; read it back. This value may be reduced by the deterministic local controller but never increased by a conversational agent.
6. Configure the Bus Watchdog only after measured cycle-time evidence establishes a bounded value. Until then the value is SELECTION REQUIRED and no motion is authorized.
7. Verify voltage, temperature, hardware error, position limits and output-encoder plausibility before any torque-enable request.
8. A safety-permit transition only permits the local state machine to consider torque enable. It never creates a position, velocity or current command.
9. Require a fresh, bounded trajectory command issued after the permit transition. High-level OpenAI action requests are schema-checked and converted locally; they never write actuator registers directly.
10. During motion, re-read Current Limit, Goal Current, watchdog, voltage, temperature, hardware error, present current and encoder agreement. Drift or stale communication commands torque-off and removes the motion permit.
11. Reset requires the initiating command to be absent, all faults acknowledged, and another fresh trajectory command. E-stop release or reset cannot resume the previous command.

This sequence is an architecture definition. Exact watchdog time, stop time, temperature limits, current telemetry tolerances and fault reactions require physical validation and qualified review.
