# R235 independent review request

> **PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION**

Please review `HR-V0-P121-APP-EVID-P0.1` against the unaccepted P1.21 native KiCad candidate and current primary manufacturer documentation.

Check, at minimum:

1. Whether all 13 questions accurately describe Pilz 750104, Phoenix Contact 2967060 and the exact P1.21 A1 supply-gate topology without asking either manufacturer to approve the complete robot.
2. Whether any missing question could materially change A1 power-cycle, brownout, monitored-start, contact endurance, protection or diagnostic conclusions.
3. Whether the six current US support routes and source revision/date records are correct.
4. Whether the 12 response controls prevent ambiguous, verbal, wrong-product or incomplete answers from being treated as acceptance.
5. Whether all ten prerequisites must close before the proposed low-energy control-only test.
6. Whether the 15 signals and 18 tests cover power-up, power-down, heartbeat recovery, fresh ARM, E-stop independence, each single contact fault, dual diagnostic bypass, 24 V/0 V loss, ramps, off-time, bounce and asynchronous opening.
7. Whether any test could create an unintended energized, mains, actuator, motion or stored-energy path.
8. Whether every unresolved numeric dynamic limit correctly remains `SELECTION REQUIRED`.
9. Whether the package preserves P1.15 as current, P1.21 as unaccepted, DF-01 at zero safety credit and every work authority false.

Please return findings as BLOCKER / MAJOR / MINOR with exact file, row/ID, primary-source basis and proposed correction. Do not mark P1.21 approved and do not authorize sending, connection, powered testing or energization.
