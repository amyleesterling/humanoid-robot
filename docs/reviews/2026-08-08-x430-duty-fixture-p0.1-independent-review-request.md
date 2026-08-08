# Independent review request — HR-V0 X430 duty fixture P0.1

> **PRELIMINARY — NOT APPROVED FOR QUOTATION, PROCUREMENT, FABRICATION, ASSEMBLY, POWERED TEST, MOTION, CONNECTION, OR ENERGIZATION.**

Please review `HR-V0-X430-FIXTURE-P0.1` as a dimensioned topology and evidence-route candidate, not as a fixture release.

## Review scope

1. Confirm that stationary reaction-torque measurement is appropriate for this X430/FR12 characterization purpose and state exactly which torque components it measures.
2. Verify FUTEK `FSH04015` range, overload, mounting, bidirectional calibration and side-load assumptions against current manufacturer evidence and the proposed dynamic profile.
3. Review the drawing-derived TFF400 envelope and the exact ROBOTIS geometry registration; independently inspect the STEP/GLB and datum axes.
4. Determine whether the active-side upper-bridge topology can connect the TFF400 to the exact S102 fixed frame without interfering with the received X430, H101 motion, fasteners, cables or tools.
5. Require a complete free-body/load-path model including tare, fixture compliance, rotor/gear dynamics, shock, fatigue, local stress, deflection and sensor overload protection.
6. Review the `FSH04461`/T7 acquisition chain, exact cable and shield/chassis treatment, range, gain, bandwidth, settling, common mode, calibration, synchronization and uncertainty.
7. Review whether `JS220-K000` can be inserted in the accepted actuator branch without exceeding voltage/current/transient limits or defeating source/protection/reverse-energy controls.
8. Review the LSB205 100 mm force-arm route only as an independent static cross-check; check off-axis load, thread/load introduction, arm deflection and alignment.
9. Reject any implied build authority from the base/upright/adapter envelopes. Require material, joints, holes, fits, tolerances, fasteners, anchors, manufacturing drawings, FAI and proof.
10. Require a complete independent catch, full swept-volume guard/access closure, non-human load device, cable routing, temperature-sensor retention, abort logic and branch interruption before any powered stage.
11. Confirm all fourteen holds and every release flag remain open/false.

## Exact artifacts

- `docs/hr-v0-x430-duty-fixture-p0.1.md`
- `test-fixtures/hr-v0/x430-duty-fixture-p0.1/HR-V0_X430_duty_fixture_P0.1_review.step`
- `test-fixtures/hr-v0/x430-duty-fixture-p0.1/HR-V0_X430_duty_fixture_P0.1_review.glb`
- `test-fixtures/hr-v0/x430-duty-fixture-p0.1/dimensioned-topology-review.svg`
- all CSV and JSON records in that directory
- `release/hr-v0/x430-duty-fixture-p0.1/index.html`
- `tests/forms/hr-v0-x430-duty-fixture-inspection-template.csv`
- `tools/generate_hr_v0_x430_duty_fixture.py`
- `tools/check_hr_v0_x430_duty_fixture.py`

Please report `BLOCKER`, `MAJOR` and `MINOR` findings with exact file/row/interface references and current primary-source links. Do not approve fabrication or energization.
