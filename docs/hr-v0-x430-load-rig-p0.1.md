# HR-V0 X430 horizontal load-rig route P0.1

> **PRELIMINARY — LOAD-RIG/RFI CANDIDATE ONLY — NOT APPROVED FOR QUOTATION, PROCUREMENT, MACHINING, ASSEMBLY, CONNECTION, POWERED TEST, MOTION, OR ENERGIZATION.**

Identifier: `HR-V0-X430-LOAD-RIG-P0.1`

Parents: `HR-V0-X430-DUTY-P0.1`; `HR-V0-X430-FIXTURE-IF-P0.2`; `HR-V0-X430-FIXTURE-SUP-P0.1`

Date: 2026-08-08

## R104 controlled dimensional erratum

R102 originally modeled the PT-series plate as 14.5 mm thick. Visual reinspection of the official `PT SERIES - US 02/2022` profile shows that `C = 20.0 mm` is the plate thickness and `D = 14.5 mm` is the lower T-slot width. The current generated R102 envelope is corrected to 600 × 375 × 20 mm. R104 controls the drawing-derived slot profile and brake-support interface. No earlier 14.5 mm thickness model may be used for layout, quotation or fabrication.

## Decision

Use a common-bed, coaxial actuator/brake topology as the preferred **inquiry route** for controlled X430 characterization. The current candidate chain is:

1. the stationary FUTEK reaction-torque stack from P0.2;
2. exact repository-controlled X430/FR12 geometry;
3. a proposed ROBOTIS `HN12-N101` output horn;
4. a custom HN12-to-15 mm adapter that is not yet defined;
5. a Ruland `MJC33-15-A` / `JD21/33-92Y` / `MJS33-15-A` jaw-coupling set;
6. a standard metric Magtrol `HB-450M-2` hysteresis brake; and
7. a Magtrol `PT-600` T-slot base-plate envelope.

None is selected or released. The Magtrol brake and ROBOTIS/FR12 files are controlled vendor review geometry. The PT-600 and coupling are catalog envelopes. The custom output adapter and brake riser deliberately omit attachment holes and other fabrication features.

## What this test could establish

After every hold closes, the rig could measure externally timed reaction torque, current, position, speed and temperatures against a regulated non-human load. It would support characterization of continuous/cyclic operating points, thermal rise, controller response and shutdown transients.

It would **not** prove the final HR-V0 elbow assembly. Direct horn coupling does not reproduce the final FR12-H101 frame load path, gravity, bearings, cables, inertia or moving mass. The configured horizontal FR12-H101 test remains mandatory and `configured_h101_test_still_required` is locked `true`.

## Catalog screens and their limits

Magtrol publishes 3.2 N·m minimum torque at rated current for `HB-450M-2`, with 442 mA, 50 ohm, 22.1 V, 9.8 W coil data, 8,000 rpm maximum speed and 670/160 W five-minute/continuous heat-dissipation figures. These are catalog inputs, not selected operating limits. The current datasheet warns that heat dissipation depends on mounting and cooling and calls for a flyback diode across the brake coil.

ROBOTIS publishes 4.1 N·m as a 12 V stall endpoint for X430-W350; it is not continuous torque. Therefore `3.2/4.1 = 0.780488` is only a catalog comparison. The brake does not cover the entire stall endpoint, and no current or torque command may be inferred from it.

Ruland publishes 3.96 N·m rated and 7.9 N·m peak torque for the 92A-spider 15×15 mm candidate. `3.96/3.2 = 1.2375` is a narrow catalog ratio and requires written application acceptance. `7.9/4.1 = 1.926829` is an accidental comparison only. It is not an operating, proof or fault capacity.

At 3.2 N·m and 30 rpm, ideal dissipation is `Tω = 10.053096 W`. This does not select a duty point or establish surface temperature. Catalog torsional stiffness gives approximately 1.269841° coupling twist at 3.2 N·m, which must be included in any angle/uncertainty model. PT-series mass arithmetic gives `15.07 kg/m × 0.600 m = 9.042 kg`; it does not establish anchoring or support adequacy.

## Mechanical and electrical boundaries

The standard HB-450M is flange-mounted. Its exact base/riser route remains open. Magtrol identifies `HB-451` as a base-mounted special for the imperial HB-450 family; that statement is not transferred to the metric `HB-450M-2`. The RFI asks Magtrol for a controlled metric identity or an accepted riser configuration.

Correct coaxial alignment and flexible coupling are required. Shaft fits, bearing support, runout, axial gap, extraneous loads, reversals, clamp/key strategy and proof remain open. A 5.85 kg brake may not be cantilevered from the R101 pedestal without a qualified load-path design.

The brake requires its own selected, current-regulated and protected source. It may not be carried on the robot 24 V control rail. Flyback suppression, interruption behavior, source isolation, fault energy, regenerated/mechanical energy, current measurement, temperature sensing, dwell/cooldown and interlocks are all `SELECTION REQUIRED`.

The common bed must be attached to a qualified support at the actual Boston test site. T-slot hardware, anchors, substrate, edge distances, installation permission and proof are unknown. A complete fixed guard around the rotating coupling and shafts, an independent catch, access prevention and a qualified abort scheme remain mandatory.

## Evidence state

The package contains four topology dispositions, eight BOM rows, six bounded calculations, six open interfaces, five alignment controls, six power/thermal controls, eight unsent RFIs, six primary-source records and fourteen open holds.

Controlled Magtrol files:

- `HB-450M_B_EF.step` — SHA-256 `2EE1136C6CA3B2202A13BC11DEA1A18EEB9D261B7E7D776EE940699C7F89EDE1`;
- `hb-450m-rev-a.pdf` — SHA-256 `B60AE3A2B5E4CB18BA8F9875AD1C44B6AD78002DC2E2E880331C67FFE1FEB77F`.

Current primary records were checked on 2026-08-08: Magtrol HB/MHB datasheet ©2025; Magtrol HB-450M installation drawing Rev A dated 2004-01-29; Magtrol PT-series record US 02/2022; current Magtrol product and special-design pages; current Ruland MJC33 product data; and the current ROBOTIS HN12-N101 product record. Manufacturer facts are evidence inputs, not approvals.

All quotation, procurement, machining, assembly, connection, powered-test, motion, energization, safety-credit and build-release flags remain false.
