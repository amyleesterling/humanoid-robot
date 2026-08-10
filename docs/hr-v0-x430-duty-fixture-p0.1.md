# HR-V0 X430 duty-fixture topology P0.1

> **PRELIMINARY — DIMENSIONED REVIEW CANDIDATE ONLY — NOT APPROVED FOR QUOTATION, PROCUREMENT, FABRICATION, ASSEMBLY, POWERED TEST, MOTION, CONNECTION, OR ENERGIZATION.**

Configuration identifier: `HR-V0-X430-FIXTURE-P0.1`

Parent evidence route: `HR-V0-X430-DUTY-P0.1`

## Decision

Use a stationary reaction-torque sensor in the fixed-case load path as the preferred external torque-evidence topology. Retain a force sensor at a measured 100 mm perpendicular arm only as an independent static cross-check. Do not use motor current or DYNAMIXEL current telemetry as primary torque evidence, and prohibit human-held scales, straps or force application inside the stored-energy or swept volume.

FUTEK TFF400 item `FSH04015` is the exact reaction-torque **evaluation candidate**. Its catalog capacity is 100 in-lb / 11 N·m. This identity is not a selection, purchase release, operating limit, structural allowable or proof that the candidate fits the application. FUTEK application review, bidirectional system calibration, the received serial/certificate and the entire instrument chain remain required.

## What is modeled

The controlled model contains:

- the exact repository-controlled ROBOTIS X430, FR12-S102 and FR12-H101 STEP solids;
- a drawing-derived TFF400 envelope at the J2 axis;
- a 400 × 600 × 12.7 mm base envelope;
- a 12.7 × 300 × 300 mm upright envelope;
- an unresolved upper-bridge active-adapter envelope from the TFF400 active face to the exact S102 axes at Y = ±11 mm and Z = 32 mm relative to J2;
- a 160 mm fixture load-arm envelope and unresolved end-load envelope; and
- six red datum-axis markers that are explicitly **not holes**.

The sensor envelope is derived from FUTEK drawing FI1251-F. No manufacturer TFF400 CAD file is controlled. The custom interface envelope omits hole diameters, threads, pilots, counterbores, material, tolerance, edge treatment, fasteners, engagement, locking and tools. Those omissions are intentional: the package must not masquerade as fabrication data.

The model does not contain a buildable base/upright joint, bench anchor pattern, independent catch, full guard/access closure, controlled load device, cable route or sensor-retention definition. `DUTY-HOLD-08` therefore remains open.

## Why reaction torque is preferred

The TFF400 is stationary. Its fixed face connects to the fixture upright and its active face connects to the X430/FR12 fixed assembly. This preserves continuous external reaction-torque measurement while the output frame moves. It avoids the changing tangent and alignment problem of a single force sensor at a rotating arm.

Reaction torque is not automatically equal to payload torque. The measurement can include rotor/gear dynamics, fixture compliance, internal losses and any loads carried by the fixed-side adapter. Output-torque interpretation therefore requires a defined free-body model, tare/zero method, calibration, phase/timing evidence and uncertainty budget.

The alternative `FSH04097` LSB205 25 lb / 111 N candidate at an as-built 100 mm perpendicular arm produces an ideal nominal 11.1 N·m full-scale moment. That arithmetic does not credit its M3 threads, alignment, off-axis response, arm deflection, load introduction or sensor protection. It remains a static cross-check candidate only.

## Non-authorizing arithmetic screens

- `11 / 4.1 = 2.682927`: TFF400 catalog capacity divided by the ROBOTIS 12 V stall-torque endpoint.
- `16.5 / 4.1 = 4.024390`: published 150% safe-overload value divided by that endpoint.
- `11 / 1.087329823 = 10.116531`: TFF400 capacity divided by the incomplete P1.1 2.25× gravity screen.
- `111 N × 0.100 m = 11.1 N·m`: ideal LSB205 static cross-check moment.
- `3.0 / 2.3 = 1.304348`: JS220 published continuous-current range divided by the XM430 12 V stall-endpoint current.

None is an allowable, command, acceptance limit, continuous rating, overload plan or proof margin. The ROBOTIS endpoint is stall data, the P1.1 load model is incomplete, safe overload is not an operating region, and the current-instrument comparison omits source transients, regenerated energy, connector/wire limits and timing.

## Candidate measurement chain

1. `FSH04015` TFF400 reaction-torque sensor, with separately quoted clockwise and counterclockwise system calibration.
2. `FSH04461` IAA100 strain-gauge amplifier.
3. LabJack T7 differential analog acquisition for torque and other external channels.
4. `JS220-K000` as an exact branch-current/voltage candidate, only if the accepted source, transients, duty and connection remain inside its current documentation.
5. A qualified surface-temperature chain. OMEGA SA1-K is a family reference only; the exact order code, length, termination, cold-junction compensation and attachment remain `SELECTION REQUIRED`.

The FUTEK TFF400 has a four-pin LEMO receptacle and the IAA100 has a four-function sensor input. That functional correspondence does not release a cable. The exact mating cable/order code, shield/chassis treatment and system calibration must come from FUTEK; no pin-to-pin harness is inferred here.

The T7 provides 14 analog inputs or seven adjacent differential pairs and software-selectable ranges, but it uses a multiplexed measurement chain. Scan list, range, resolution, settling, source impedance, rate, hardware timing and cross-instrument synchronization remain open. The JS220 is not assumed to be time-aligned to the T7 merely because both record data.

## Fourteen blocking holds

All fourteen rows in `open-hold-register.csv` remain `OPEN`:

1. FUTEK application confirmation;
2. exact sensor, calibration, amplifier and cable configuration;
3. fixed-side adapter detail;
4. active-side adapter detail and received S102/X430 fit;
5. complete material, fastener, locking and manufacturing definition;
6. qualified structural, shock, fatigue, deflection and overload analysis;
7. Boston bench survey, permission, anchors, installation and proof;
8. an independent physical catch;
9. full guard/access/impact closure;
10. a non-human controlled load device and retention method;
11. cable and temperature-sensor routing;
12. acquisition, synchronization, calibration and uncertainty closure;
13. branch interruption, abort, source limits, overload and regenerated-energy controls; and
14. as-built inspection, unpowered proof, qualified review and separate powered-work authorization.

## Controlled files

- generator: `tools/generate_hr_v0_x430_duty_fixture.py`;
- checker: `tools/check_hr_v0_x430_duty_fixture.py`;
- STEP, GLB, readable SVG and registers: `test-fixtures/hr-v0/x430-duty-fixture-p0.1/`;
- responsive interactive guide: `release/hr-v0/x430-duty-fixture-p0.1/index.html`;
- blank fourteen-row inspection record: `tests/forms/hr-v0-x430-duty-fixture-inspection-template.csv`;
- independent review request: `docs/reviews/2026-08-08-x430-duty-fixture-p0.1-independent-review-request.md`.

Passing the checker proves only source binding, arithmetic, expected row counts, blank execution evidence and fail-closed release flags. It does not validate the sensor application, structure, guard, catch, anchors, test method, powered controls or suitability for energization.
