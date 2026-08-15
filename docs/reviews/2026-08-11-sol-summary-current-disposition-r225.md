# Sol summary: current-source disposition at R225

> **PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION**

Date: 2026-08-11

## Intake boundary

The user supplied Sol's summary containing totals of 18 blockers, 30 major findings and eight minor findings, plus links to a 56-row register and supporting files in Sol's sandbox. Those linked files are not present in this repository, so this document does not pretend to reproduce or close all 56 detailed findings. It reconciles only the consequential findings stated in the supplied summary against the current R225 branch.

| Summary finding | Current-source disposition | Remaining closure evidence |
|---|---|---|
| Authoritative repository lacks native KiCad source. | Corrected on the current review branch: native P1.15/P1.18 projects and validation artifacts are repository-controlled. Merge/formal acceptance remains open. | Accepted immutable commit and independent clone/parity check. |
| Electrical revisions/configuration mismatch. | Controlled, not fully closed: P1.15 is current; P1.18 is explicitly unaccepted and supporting only. | Independent disposition choosing/correcting P1.18 and synchronized accepted configuration. |
| No buildable mechanical definition. | Materially advanced with native CAD, STEP, drawings, BOM bindings and manufacturing-review packages; still not released. | Provider-accepted drawings, complete part definitions, received/FAI/fit/load evidence and qualified release. |
| Single watchdog permit contact can defeat heartbeat removal when welded. | The assertion does not match current P1.18 source. R225 proves two ordinary NO contacts in series before `SR1:A1`; neither enters an E-stop input loop. | Eight R225 holds, including common-cause/dual bypass, physical fault injection and qualified validation. |
| No functional-safety allocation. | Candidate SRS P0.2 now defines `SF-01`, `SF-03`, zero-credit `DF-01`, a first-motion timing/travel candidate and validation cases. Required integrity is still unselected. | Qualified PLr/SIL/category allocation, calculation, validation plan and signature. |
| No total stopping-distance requirement. | Partially corrected for guarded J2-positive setup motion: 2.000° residual travel and 200 ms total-response candidates at 10°/s. Automatic motion remains prohibited. | Measured loaded response, uncertainty/statistics, stop/guard reconciliation and qualified acceptance. |
| Unproven DC contactor duty. | Open. | Exact DC interruption application, manufacturer/qualified disposition, loaded test and endurance evidence. |
| Unresolved PE/grounding. | Open. | Accepted bonding scheme, conductor/terminal selection, received construction and continuity/fault evidence. |
| No closed mass/inertia model. | Analytically advanced but physically open. | Received component masses, assembled mass/COM/inertia measurement and signed reconciliation. |
| Unproven continuous leg torque. | Open for HR-30W; stall figures are not treated as continuous ratings. | Exact drivetrain, duty cycle, thermal/mechanical characterization and dynamic walking evidence. |
| No safe power-loss strategy. | Candidate receiver/collapse-envelope architecture exists; no physical credit. | As-built retention/drop/clearance tests across power-loss cases and qualified review. |
| Insufficient dynamic restraint definition. | Open. | Site/bench identity, anchorage design, load cases, hardware, installation inspection and proof. |
| Battery, sensing, bus and real-time control remain architecture-only. | Open for HR-30 and partly open for HR-V0. | Exact selections, physical integration, power/fault/thermal/EMC tests, HIL and controlled runtime evidence. |

## Net result

The summary's overall verdict remains correct: the project is not yet a buildable or energizable machine. Some stated source/configuration findings were corrected after the review baseline or do not match the current P1.18 source. Physical evidence and qualified review—not another wording pass—remain the controlling blockers.
