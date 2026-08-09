# R117 independent review request

Status: **PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, TESTING, OR ENERGIZATION**

Review `HR-V0-K1K2-APP-P0.2` for source accuracy, load-envelope completeness, manufacturer-query readiness and fail-closed authorization control. This is not a request to approve LC1D25BD, a test, wiring, functional safety or energization.

## Review artifacts

- `electrical/vendor/schneider/lc1d25bd-r117/source-manifest-p0.1.csv`
- `electrical/contactor/hr-v0-lc1d25bd-application-inputs-p0.2.csv`
- `tests/forms/hr-v0-contactor-interruption-characterization-template-p0.1.csv`
- `docs/vendor-queries/schneider-lc1d25bd-dc-application-p0.1.md`
- `docs/hr-v0-contactor-application-p0.2.md`
- `release/hr-v0/contactor-application-p0.2/index.html`
- `tools/check_hr_v0_contactor_application_p02.py`

## Questions

1. Do the current Schneider source identities, dates, sizes and hashes agree with the official records?
2. Are the `5.4 W / 24 V = 0.225 A` coil screen and `50 mA / 5 mA = 10` EDM current screen arithmetically correct and narrowly labeled?
3. Does any source support treating the product-name `25 A` or catalog 32 A / 24 V row as a released 12 V electronic/regenerative breaking rating?
4. Are forward, opening, reverse/regenerative current, contact voltage, capacitance, time constant, source response and prospective fault current all required before the supplier query?
5. Does the query expose the catalog critical-current warning, exact three-poles-per-device series chain, two-device redundancy and required life?
6. Are protection, conductors, ambient, orientation, cycles/hour and stopping-time requirements explicit rather than inferred?
7. Do all twelve test stages remain `NOT EXECUTED` and `NOT_AUTHORIZED`?
8. Is the prepared query unmistakably `UNSENT`, with program-owner approval required before external contact?
9. Could any source fact, arithmetic screen, clean checker or future Schneider response be mistaken for functional-safety approval or energization permission?

Return BLOCKER / MAJOR / MINOR findings with exact file, row, field, component, terminal, source-page and gate references. State separately whether the packet is ready to collect physical measurements, ready to send to Schneider, ready for qualified review, and whether any physical work is authorized.
