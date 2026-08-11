# HR-V0 P1.21 application-evidence package P0.1

> **PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION**

Identifier: `HR-V0-P121-APP-EVID-P0.1`

Round: R235
Date: 2026-08-11

## Outcome

R235 converts three P1.21 holds into controlled evidence routes instead of treating catalog arithmetic as acceptance:

- 13 exact manufacturer questions: seven for Pilz and six for Phoenix Contact;
- six official US submission routes, all `NOT SENT` or `NOT USED`;
- 12 controls defining what a usable written response must contain;
- ten prerequisites that must all close before any control-only powered test;
- 15 required signals and 18 configuration-bound test cases;
- blank response and result templates that fail closed;
- 14 open holds.

The official Pilz record identifies PNOZ s4 order code 750104 as a 24 V DC, 2.5 W device and lists operating manual 21396-EN-23. The current Phoenix Contact item 2967060 PDF records data maintenance 2026-04-01 and publishes 5 V/10 mA minimum load, 6 A limiting continuous current and 15 A for 300 ms maximum inrush. Those figures support the existing paper screen; they do not answer whether repeated switching of the PNOZ A1 electronic supply is an accepted application or what dynamic/endurance limits apply.

## Controlled use

`submission-cover-note.md` and `manufacturer-question-register.csv` are drafts only. Nothing has been transmitted. A future sender must first complete the unresolved cycle profile, source/protection envelope and configuration-controlled circuit attachment. A manufacturer response does not close the issue unless it passes every row in `response-acceptance-register.csv` and is accepted by qualified reviewers.

`test-procedure.md` is also unexecuted. It requires the actuator source and actuators to be physically absent, observes SRA1 outputs only through an approved isolated low-energy fixture, and forbids execution while any authorization prerequisite or numeric dynamic limit remains unresolved. Passing it would be configuration-specific control evidence only, not loaded interruption, stopping, guard or functional-safety approval.

## Configuration boundary

- Current electrical candidate: `V3-P1.15-CARRIER-CANDIDATE`.
- Application evidence is written for unaccepted `V3-P1.21-SRA1-SUPPLY-WATCHDOG-CANDIDATE`.
- DF-01 retains zero safety credit.
- P1.21 is not promoted by this package.
- No Sol R12 blocker receives qualified closure.

## Files

- Interactive guide: `release/hr-v0/p121-application-evidence-p0.1/index.html`
- Manufacturer questions and routes: `electrical/reviews/hr-v0-p121-application-evidence-p0.1/`
- Safety mirror: `safety/hr-v0-p121-application-evidence-p0.1/`
- Generator/checker: `tools/generate_hr_v0_p121_application_evidence_p01.py`, `tools/check_hr_v0_p121_application_evidence_p01.py`
