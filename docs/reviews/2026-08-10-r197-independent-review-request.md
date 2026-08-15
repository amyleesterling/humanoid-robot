# R197 independent review request

> **PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION**

Review `HR-V0-KIN-P0.1` against the current transform register, supervisor configuration and source.

1. Re-derive 202.550 mm J1-to-J2 and 129.050 mm J2-to-H104 from `TF-002` and `TF-003`.
2. Confirm that the triangle-inequality expression is conservative for the current parallel-axis arm and does not rely on joint-angle cancellation.
3. Challenge the assumption that gripper opening does not translate the selected tool point and identify any selected-tool offset terms that must be added.
4. Confirm that unresolved H104-to-tool reach, acceptance hash, model hash or release state prevents `Supervisor.from_json()` construction.
5. Identify required calibration, as-built geometry, tolerance, backlash, deflection, timing, HIL and independent physical comparison evidence.
6. Determine whether 0.150 m/s is acceptable only after the applicable risk and stopping analyses; do not infer acceptance from this bound.
7. Confirm zero functional-safety credit and no motion or energization authority.
