# Sol R12 finding status after R67

> **PRELIMINARY—NOT APPROVED FOR FABRICATION OR ENERGIZATION.** This is a project-owned disposition, not an independent approval.

Date: 2026-08-07

Input review: Sol R12, 18 BLOCKER / 30 MAJOR / 8 MINOR

Current correction round: R67

Sol's resupplied analysis is the same R12 review and is not counted as a new independent round.

## Material change in R67

R67 closes one analytical subproblem that R12 correctly identified: the current nominal rigid CAD no longer relies only on a sampled collision grid. `HR-V0-ARM-ARCH-P0.6` continuously certifies all 70 non-intentional body pairs through J2=120 degrees with at least 0.75 mm conservative lower-bound separation and locates first nominal contact at 121.643289 degrees.

The former 120-degree candidate command ceiling had only 0.962813 mm exact nominal clearance at the critical pair. R67 therefore lowers the candidate software ceiling to 115 degrees and records an unreleased 118-degree backed-up-stop datum. The allocation reserves 3 degrees for stopping travel and no more than 2.643289 degrees for backlash, compliance, build tolerance, calibration, measurement uncertainty and every other accepted physical term after retaining a 1-degree nominal collision guard.

## R12 findings that remain open

- no physical hard-stop CAD, selected bumper/catch, load proof or measured stopping evidence;
- no received material, FAI, fit, torque/locking/reuse or T-slot proof;
- no complete cable, connector, guard or as-built collision envelope;
- no closed mass/COM/inertia, continuous-duty/thermal or power-loss behavior;
- no qualified safety-requirements allocation, PLr/SIL target, common-cause analysis, stopping-time validation or signed functional-safety review;
- electrical protection, grounding, contactor application, watchdog, connector/conductor and physical-panel selections/evidence remain incomplete;
- 30 energization gates remain 0 closed / 22 partial / 8 open; and
- HR-30W remains architecture only with no demonstrated walking drivetrain, balance, fall-protection or energy system.

## Current verdict

`HR-V0-MECH-P0.5` is a stronger preliminary mechanical candidate, not a build or energization release. R67 changes no fabrication, motion, electrical or functional-safety authorization.
