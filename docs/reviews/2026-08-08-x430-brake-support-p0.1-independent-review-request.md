# Independent review request — HR-V0 X430 brake support P0.1

> **PRELIMINARY — NOT APPROVED FOR FABRICATION OR ENERGIZATION.**

Please review `HR-V0-X430-BRAKE-SUP-P0.1` for source interpretation, mechanical coherence, load-path completeness and fail-closed evidence boundaries. Do not treat catalog dimensions, simplified CAD, clean exports or ideal arithmetic as physical validation.

Review at minimum:

1. the PT-series correction that `C = 20 mm` is plate thickness and `D = 14.5 mm` is lower slot width;
2. the 15-slot drawing-derived PT profile and omission of countersunk holes/tolerances;
3. whether `4866` is correctly identified as the HB/MHB-450M metric pillow-block inquiry route;
4. interpretation of 4866 dimensions O/P/Q/R/S/T/U/V/W/X/Y;
5. whether the simplified 4866 envelope and explicit nonfabrication Ø50 visual clearance could mislead;
6. the 104 mm pillow-block versus 100 mm PT pitch mismatch and need for an adapter;
7. FX104-C01's 90 × 160 × 24 mm allocation, candidate axes and nominal 120 mm center height;
8. missing material, GD&T, thread, fastener, T-nut, slip, fatigue, DFM, FAI and proof evidence;
9. the exact HB mounting face, 3 × M5 pattern, Ø32 h3 boss, shaft/key and nominal placement;
10. the brake-weight envelope moment and ideal torque-couple arithmetic;
11. alignment, coupling-bearing, guarding, brake-control, thermal, instrumentation, anchoring and site holds;
12. continued need for the final configured FR12-H101 test; and
13. whether any artifact could be mistaken for quotation, procurement, machining, assembly, powered-test or energization authority.

Return BLOCKER / MAJOR / MINOR findings with exact file, record and field references. Identify every unsupported assumption and the evidence required to close it. Do not approve fabrication or energization.

Primary artifacts:

- `docs/hr-v0-x430-brake-support-p0.1.md`
- `cad/vendor/magtrol/hb-450m-r102/`
- `cad/vendor/magtrol/pt-series-r104/`
- `test-fixtures/hr-v0/x430-brake-support-p0.1/`
- `release/hr-v0/x430-brake-support-p0.1/index.html`
- `tools/generate_hr_v0_x430_brake_support.py`
- `tools/check_hr_v0_x430_brake_support.py`
