# Sol R12 status after R86

Date: 2026-08-08

Reference review: Sol R12, `18 BLOCKER / 30 MAJOR / 8 MINOR`

Current correction: `HR-V0-WD-CCF-P0.1`

R86 advances Sol `B-005`/`B-006` from a broad watchdog concern to an exact dependent-failure package. It preserves zero safety credit for DF-01, maps 18 V3 paths, expands the controlled FMEA to 32 cases, and defines common-cause, separation and fault-injection evidence.

The review also identifies an additional exact blocker rather than closing the finding: KWD A1/21 carries `SAFETY_24V` in the same ordinary relay module whose 11-14 contact returns to SR1 after an E-stop NC contact. An internal or panel short to terminal 14 could inject voltage downstream of S0. No fault exclusion, redesign, physical test or qualified architecture disposition exists.

Sol R12's overall verdict remains accurate. HR-V0 is not build-ready and energization remains prohibited. R86 is a project-owned correction pass, not a new independent review or approval.
