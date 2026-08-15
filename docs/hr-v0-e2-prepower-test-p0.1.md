# HR-V0 E2 configuration-bound pre-power verification candidate P0.1

> **PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION**

- Identifier: `HR-V0-E2-PREPOWER-P0.1`
- Review round: R228
- Date: 2026-08-11

## Outcome

This package converts the unaccepted P1.18 point-to-point topology into an exact, fail-closed pre-power verification candidate. It maps all 55 proposed conductors to test rows, adds 16 critical isolation pairs, eight no-backfeed cases and twelve absence-of-voltage points. It does not execute any test, release any numeric limit, accept P1.18 or authorize connection to a source.

The existing one-row generic evidence forms remain unchanged and retain their current evidence-contract identity. The R228 tables are a more complete configuration-specific candidate, not executed evidence and not a silent replacement for an approved procedure.

## Configuration boundary

- Current electrical source: `Project Button Electrical V3-P1.15-CARRIER-CANDIDATE`.
- Test-target candidate: `V3-P1.18-PANEL-TOPOLOGY-CANDIDATE`, still unaccepted.
- The R222 point-to-point schedule supplies exactly 55 from/to conductor candidates.
- Forty-five fixed-internal rows have only a proposed low-energy resistance/identity method.
- Ten moving-door rows remain blocked until exact dynamic-flex conductors, terminals, routes, protection and terminations are selected.
- The E2 hardware slice makes `U1`, `INJ1`, `J1`, `J2`, `J3`, the actuator source, actuator protection and actuator loads physically absent. K1/K2 load poles remain unsourced and unwired.

## Measurement controls

No resistance, isolation, stimulus or absence-of-voltage threshold is released. Numeric limits require the exact conductor and termination model, cable length, lead compensation, instrument uncertainty, connected-device constraints and qualified acceptance.

The Keysight U1282A is an exact meter candidate only. Its current official product page records DC voltage, two-wire resistance and continuity functions, 60,000 counts and CAT III 1000 V / CAT IV 600 V ratings. The exact calibration option, certificate, leads, proving reference, test energy, uncertainty and received condition remain open.

Absence-of-voltage rows use a proposed live-dead-live sequence: prove the accepted meter on an accepted reference, test the exact point, and re-prove the meter. This is consistent with current OSHA de-energized-work language and current Fluke manufacturer guidance, but a qualified person must determine applicability, method and limits for the actual Boston premises and equipment.

## Explicit prohibitions

- Do not apply a megohmmeter or hipot source across connected electronics, sealed adapters, the Raspberry Pi, USB interfaces, relay or contactor coils, indicators or PCBs.
- Do not use a continuity beeper as a quantitative resistance result.
- Do not use a non-contact voltage indicator as the proof of absence of voltage.
- Do not inject any no-backfeed stimulus until its voltage, current, energy, protection and connection fixture are qualified.
- Do not treat visual inspection, source-code checking, ERC, a blank form or this plan as permission to plug in.

## Evidence still required

Ten holds remain open: P1.18 disposition; ten door-conductor selections; 45 fixed-conductor final details; continuity limits; isolation limits; a no-backfeed fixture; absence thresholds; the complete instrument set; executed physical evidence; and signed configuration-specific authorization.

`EG-004`, `EG-019`, `EG-020` and `EG-022` remain partial. There are zero released limits, zero executed results and zero authority for physical probing, source connection, powered testing, motion or energization.

## Controlled artifacts

- Engineering records: `tests/e2/hr-v0-e2-prepower-test-p0.1/`
- Reviewable release copy and interactive guide: `release/hr-v0/e2-prepower-test-p0.1/`
- Gate supplement: `requirements/hr-v0-gate-evidence-supplement-r228.csv`
- Generator: `tools/generate_hr_v0_e2_prepower_test_p01.py`
- Checker: `tools/check_hr_v0_e2_prepower_test_p01.py`

## Primary records rechecked

- OSHA, 29 CFR 1910.333, current page rechecked 2026-08-11: https://www.osha.gov/laws-regs/regulations/standardnumber/1910/1910.333
- Fluke, *Absence of voltage testing*, current page rechecked 2026-08-11: https://www.fluke.com/en-us/learn/blog/electrical/absence-of-voltage-testing
- Keysight U1282A product page, current page rechecked 2026-08-11: https://www.keysight.com/us/en/product/U1282A/handheld-digital-multimeter-4-5-digit-ip67.html
- Keysight U1280 Series data sheet, portal updated 2024-06-07 and rechecked 2026-08-11: https://www.keysight.com/us/en/assets/7018-04867/data-sheets/5992-0847.pdf

These records support only the stated candidate method and instrument-screen facts. They do not supply Project Button limits, executed evidence or work authorization.
