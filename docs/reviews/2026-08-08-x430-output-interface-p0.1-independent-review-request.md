# Independent review request — HR-V0 X430 output interface P0.1

> **PRELIMINARY — NOT APPROVED FOR FABRICATION OR ENERGIZATION.**

Please review `HR-V0-X430-OUTPUT-IF-P0.1` for mechanical correctness, evidence boundaries and omission of fabrication authority. Do not treat a clean CAD export, nominal noninterference or catalog data as physical validation.

Review at minimum:

1. the HN12-N101 source provenance, transform, nominal seating plane and use of a reference-only drawing;
2. whether the eight Ø2.2 review holes on PCD Ø16 correctly reflect the horn's eight M2 tapped axes without implying fastener selection;
3. the Ø32 × 8 flange and Ø15 × 18 stub allocation, including missing material, fillet, GD&T, surface, fatigue and fault-load definitions;
4. horn serration, thread, screw, preload, locking, joint-slip and reuse failure modes;
5. whether two `MJC33-15-A` clamp hubs plus `JD21/33-92Y` is the appropriate inquiry route;
6. the 14.95/15 mm insertion layout, shaft-fit interpretation, full-bearing-support condition, hub gap and reversals;
7. rejection of the smooth-shaft set-screw route and prohibition of a printed torque adapter;
8. completeness of the bearing-supported fallback route;
9. validity and limits of the ideal screw-load and solid-shaft arithmetic;
10. nominal collision checks and all missing tolerance/received-geometry evidence;
11. continued need for the final configured FR12-H101 gravity/bearing/cable/moving-mass test; and
12. whether any artifact could be mistaken for quotation, machining, assembly, powered-test or energization authority.

Return BLOCKER / MAJOR / MINOR findings with exact file, record and field references. Identify unsupported assumptions and the precise evidence needed to close each finding. Do not approve fabrication or energization.

Primary artifacts:

- `docs/hr-v0-x430-output-interface-p0.1.md`
- `cad/vendor/robotis/hn12-n101-r103/`
- `test-fixtures/hr-v0/x430-output-interface-p0.1/`
- `release/hr-v0/x430-output-interface-p0.1/index.html`
- `tools/generate_hr_v0_x430_output_interface.py`
- `tools/check_hr_v0_x430_output_interface.py`
