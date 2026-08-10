# Sol R12 finding reconciliation after R87

**PRELIMINARY - NOT APPROVED FOR FABRICATION OR ENERGIZATION**

Sol R12 remains the independent review. R87 is a project-owned correction and is not counted as a new independent review.

R87 directly addresses the watchdog-dependent-failure blocker identified during the R86 expansion of Sol's functional-safety concerns. Electrical V3-P1.13 connects both S0 NC channels directly to SR1 and moves the ordinary KWD contacts into a series supply gate on `SR1:A1`. The synchronized P0.5 panel package provides exact route controls, and `HR-V0-WD-SUPPLY-P0.1` carries the current 32-case open FMEA, 28 unexecuted fault cases and ten release holds.

Disposition: the specific source-encoded internal KWD-to-E-stop-return injection path is corrected. The broader Sol blockers are not closed. The design still lacks executed and accepted physical evidence, qualified functional-safety allocation, total stopping limits, protected routing, contact-application confirmation, protection/conductor closure, physical CAD/fabrication release, dynamic/thermal/load evidence and signed authorization. HR-V0 remains not ready to fabricate or energize; HR-30W remains a staged feasibility program rather than a demonstrated walking machine.

The current independent-review target is `docs/reviews/2026-08-08-watchdog-supply-gate-p0.1-independent-review-request.md`.

**PRELIMINARY - NOT APPROVED FOR FABRICATION OR ENERGIZATION**
