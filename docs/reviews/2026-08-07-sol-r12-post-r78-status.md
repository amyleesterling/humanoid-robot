# Sol R12 findings rechecked against R78

> **PRELIMINARY—NOT APPROVED FOR FABRICATION, POWERED TESTING, MOTION, CONNECTION, OR ENERGIZATION.**

Sol's resupplied verdict remains the same R12 independent review: 18 BLOCKER, 30 MAJOR and 8 MINOR findings. It is not counted as an additional review round.

## What R78 changes

R78 creates `HR-V0-DYN-CHAR-P0.1`, a controlled route to acquire the missing physical evidence behind several Sol findings:

- measured mass/COM/inertia rather than a catalog endpoint;
- independent angle and velocity rather than bus-only telemetry;
- bidirectional current and bus voltage including source-removal/regeneration behavior;
- reaction force and bumper travel;
- synchronized K1/K2 command and mirror feedback;
- high-speed video and sample-clock proof;
- dropped-scan, calibration and timing-budget evidence; and
- a fail-closed stage sequence with no powered authorization.

## Findings still materially open

R78 does not create buildable released CAD, selected fixture hardware, closed mass/inertia, a safety-requirements specification, PLr/SIL allocation, a validated watchdog safety function, selected contactor duty, grounded/PE physical evidence, stopping-distance acceptance, guard proof, battery closure, walking torque/thermal evidence, dynamic restraint, firmware HIL, or any executed requirement evidence.

The repository remains a strong preliminary engineering package, not a buildable or energizable machine. The next legitimate advances are exact instrument/fixture selection after bounded inputs, unpowered fabrication/inspection evidence, and then qualified gated execution—not a declaration that the robot is ready.
