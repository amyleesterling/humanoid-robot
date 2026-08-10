# R157 independent review request

> **PRELIMINARY - NOT APPROVED FOR FABRICATION, ASSEMBLY, CONNECTION, MOTION, OR ENERGIZATION**

Please independently review `HR-V0-BRANCH-FAULT-P0.1` against Electrical V3-P1.14 and the controlled protection, contactor, grounding, DXL and dynamic-characterization packages.

Check at minimum:

1. every case reference, terminal and net against native KiCad and the current wire/connector schedules;
2. whether the four-stage ordering keeps unpowered, limited-energy, guarded-fault and configured tests separated;
3. whether any fault case can bypass `F0/F1/F2/F3/FSR1/FSR2`, unexpectedly energize another branch, or conceal U2D2/controller-cable VDD;
4. whether the backfeed and regenerative cases correctly preserve the unresolved R156 reverse-current/source-sink problem;
5. whether contactor-opening and feedback-discrepancy cases require the missing SRS/PLr, DC application and numeric stopping evidence instead of claiming safety credit;
6. whether every reset/recovery path proves that clearing the fault cannot itself command motion;
7. whether any wording implies a direct uncontrolled short, robot-first fault testing, executed evidence, selected protection, or authorization;
8. whether the CSV, blank form, guide, gate register and checker stay synchronized and readable.

Report BLOCKER / MAJOR / MINOR findings with exact artifact, case, reference/net and proposed correction. Do not approve fabrication, connection, motion or energization.
