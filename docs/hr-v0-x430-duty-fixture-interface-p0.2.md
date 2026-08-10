# HR-V0 X430 duty-fixture adapter interface P0.2

> **PRELIMINARY — RFI/RFQ REVIEW CANDIDATE ONLY — NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TEST, MOTION, OR ENERGIZATION.**

Identifier: `HR-V0-X430-FIXTURE-IF-P0.2`

Parent: `HR-V0-X430-FIXTURE-P0.1`

Date: 2026-08-08

## Decision

The P0.1 active bridge is rejected. It reused the FR12-S102 side-ear axes that belong to the factory S102-to-X430 attachment. P0.2 instead defines two separately identified CNC adapter **review candidates**:

- `FX100-C01`: fixed TFF400 flange adapter; and
- `FX100-C02`: monolithic active flange-and-shelf adapter tied to the exact S102 center-face pattern.

This is a vendor-question and qualified-review package, not a machinist's release. The part STEP files communicate nominal geometry only. The SVG is explicitly marked “DO NOT FABRICATE.”

## Controlled candidate geometry

Both TFF interfaces use a 100 × 100 × 13.0 mm flange, a proposed Ø18.98 ±0.02 mm male pilot 2.50 ±0.05 mm long, and four proposed Ø4.50 ±0.05 mm clearances on a basic 31.75 mm bolt circle. The proposed pattern position is Ø0.10 to the pilot axis. Proposed mating-face flatness is 0.05 mm per 50 mm with Ra 1.6 µm. Every value remains conditional on FUTEK application acceptance and qualified tolerance review.

`FX100-C02` adds a 52.4 × 50.0 × 12.7 mm shelf with four M2.5×0.45 candidate tapped axes at X=±12 mm, Y=±6 mm in the exact S102 center-face coordinate system. It is modeled as one machined 6061-T651 candidate only; material allowables, temper certification, fillets, coating and machining process are unresolved.

The project located no controlled manufacturer STEP for `FSH04015`. The sensor remains a drawing-derived envelope. `RFI-001` therefore requests current controlled CAD, drawing revision and connector orientation before fit credit.

## Nominal B-Rep findings

The generator imports the controlled ROBOTIS X430, FR12-S102 and FR12-H101 STEP sources on every run. At the nominal registered coordinates:

- active adapter versus X430 intersection: 0.000000000 mm³;
- active adapter versus S102 nonmating volume: 0.000000000 mm³;
- fixed adapter versus X430 intersection: 0.000000000 mm³;
- four candidate low-head envelopes versus X430 intersection: 0.000000000 mm³; and
- nominal low-head-to-X430 gap: 1.900000 mm.

These are model-coordinate results, not tolerance or received-part acceptance. The 1.900 mm gap has no adverse-variation allocation and supplies no assembly authority.

## Fastener candidates and arithmetic boundary

The TFF flange stack evaluates Accu `SSC-8-32-3/4-A2-BL` with `HRDW-M4-A2` only as a dimensional candidate. Using the published screw length, proposed 13.0 ±0.05 mm adapter and published 0.50 ±0.05 mm washer gives 4.688–5.650 mm thread engagement. The interpreted minimum remaining depth margin is only 0.446 mm. FUTEK must confirm grade, washer, engagement, thread class and its manual's 25–30 lbf-in installation torque before selection.

The S102 stack evaluates Accu `SHCL-M2.5-12-A2` only as a low-head envelope. Its maximum 1.85 mm head fits the nominal 3.75 mm S102-inner-face/X430 space with the 1.900 mm nominal remainder above. No ROBOTIS installation torque or external-load capacity is inferred.

## Load screens

For equal tangential sharing at the TFF 31.75 mm bolt circle, the calculated demand per screw is 17.12 N at 1.087 N·m, 64.57 N at 4.1 N·m, 173.23 N at 11 N·m and 259.84 N at 16.5 N·m. These are demand values, not bolt or joint allowables.

Using FUTEK EL1065's published coefficient 149 for the 100 in-lb model and assuming the intended torque maps to its Mz term gives approximately:

- 1,434 psi at 1.087 N·m;
- 5,407 psi at 4.1 N·m;
- 14,506 psi at 11 N·m; and
- 21,759 psi at 16.5 N·m.

The 11 N·m arithmetic is close to EL1065's 15,000 psi fully reversing reference. The 16.5 N·m value is a safe-overload accident screen and may never be promoted to a cyclic target. Axis mapping, combined extraneous loads, fixture tare, fatigue spectrum and permissible operating limits require FUTEK confirmation and qualified analysis.

## Source boundary

Current primary records checked on 2026-08-08 are listed in `source-register.csv`, including FUTEK drawing FI1251-F, TFF Series Manual EM1040, extraneous-load record EL1065, application 314, ROBOTIS `FR12-S102K Set` SKU `903-0242-000`, controlled local ROBOTIS geometry, and the exact Accu candidate records. Manufacturer facts are not project selections.

## Closure route

Eight RFI rows are drafted and remain `NOT SENT`. Fourteen holds remain `OPEN`: controlled sensor CAD; FUTEK and ROBOTIS application acceptance; final material/process; qualified FEA/fatigue/deflection; fastener proof; final GD&T; tool/cable access; received metrology; first article; support/anchor; catch/guard/load device; instrumentation; and qualified powered-work authorization.

The fixed adapter's outer support pattern is intentionally absent because the upright/base/anchor structure has not been selected or calculated. Connector and cable keep-outs are absent because FUTEK says connector position may vary. No quote or supplier upload is authorized.

## Artifacts

- `test-fixtures/hr-v0/x430-duty-fixture-p0.2/` — STEP, GLB, two part STEP candidates, SVG and controlled registers;
- `release/hr-v0/x430-duty-fixture-p0.2/index.html` — responsive interactive guide;
- `tools/generate_hr_v0_x430_duty_fixture_interface.py` — deterministic generator; and
- `tools/check_hr_v0_x430_duty_fixture_interface.py` — fail-closed source/status/arithmetic checker.

All procurement, quotation, fabrication, assembly, connection, powered-test, motion, energization, safety-credit and build-release flags remain false.
