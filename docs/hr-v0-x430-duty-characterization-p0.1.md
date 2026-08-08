# HR-V0 X430 continuous/cyclic duty characterization P0.1

> **PRELIMINARY — NOT APPROVED FOR POWERED TEST, MOTION, CONNECTION, OR ENERGIZATION.**

Configuration identifier: `HR-V0-X430-DUTY-P0.1`

Parent comparison: `HR-V0-ARM-ARCH-P1.1-X430-LOWERED-FOREARM-CANDIDATE`

## Decision

This package supplies the configuration-specific evidence route for R96 `LOAD-OPEN-08`: continuous/cyclic X430 torque, current and temperature. It contains no executed physical data, releases no current register value, supplies no continuous rating, and does not select P1.1 or the XM430-W350-T.

The older generic current-envelope and dynamic-characterization packages remain useful architectural inputs, but their J2 rows describe an XM540 candidate. They are not evidence for the nonselected P1.1 X430 elbow. `HR-V0-X430-DUTY-P0.1` therefore creates a separate X430/J2 traveler instead of silently relabeling historic rows.

## Manufacturer evidence and limit on its use

The current ROBOTIS XM430-W350 e-Manual was checked on 2026-08-08. The visible live page does not publish a formal document revision. It provides:

- 82 g catalog mass;
- 4.1 N·m at 12.0 V and 2.3 A as a **stall torque** endpoint;
- 46 rev/min at 12.0 V as a no-load endpoint;
- 10.0–14.8 V input range, with 12.0 V recommended;
- −5…80 °C operating-temperature range;
- Current Limit (38) range 0…1193 at 2.69 mA/raw;
- Present Current (126) at 2.69 mA/raw;
- Present Input Voltage (144) at 0.1 V/raw;
- Present Temperature (146) at 1 °C/raw; and
- Hardware Error Status (70).

ROBOTIS explicitly states that stall torque differs from continuous output and expected real-world performance, and that actual performance is generally closer to the performance graph. The 1193 register maximum is only a control-table range; it is not a released Project Button current and must not be treated as safe continuous current. Likewise, 80 °C is a product-envelope endpoint/default limit, not an acceptable Project Button case, contact, cable, enclosure or human-contact temperature.

## Analytical sensitivity, not a selection

`current-torque-sensitivity.csv` evaluates 100…700 raw units using:

`I_nominal = raw × 2.69 mA`

`T_ideal = I_nominal × (4.1 N·m / 2.3 A)`

The ideal stall-line calculation is a comparison aid only. It omits speed, losses, drive behavior, thermal equilibrium, unit variation, supply drop and real load dynamics. No row is a command, limit, continuous rating or proof target. The R96 incomplete 0.483257699 N·m gravity result and 1.087329823 N·m 2.25× screen remain incomplete analytical references, not released fixture loads.

## Primary evidence channels

Fifteen channels are controlled in `instrument-channel-register.csv`:

- external actuator-branch current;
- actuator-terminal voltage at the received connector;
- calibrated force plus measured perpendicular lever arm;
- case, connector, moving-cable and ambient temperatures;
- external joint angle and fixture deflection;
- hardware synchronization;
- DYNAMIXEL current, voltage, temperature and hardware-error telemetry; and
- command, permit, safety and physical branch-power state.

External electrical, mechanical and thermal channels are primary. DYNAMIXEL telemetry is supplemental correlation evidence. Sampling rate, bandwidth, accuracy, placement, calibration and uncertainty remain `SELECTION REQUIRED`.

## Fixture and sequence

Twelve fixture controls require a reviewed load path, independent catch, full moving-volume guard, measured torque arm, aligned force sensor, non-human load application, independent branch interruption, reviewed external and register current limits, reverse-energy disposition, retained temperature sensors, controlled cable routing and witnessed preflight.

The twelve-stage traveler begins with configuration binding, unpowered proof, sensor calibration and control-only communication. Stages `DUT-04` through `DUT-10` are powered and explicitly `BLOCKED`. They may not be executed until all prerequisites applicable to that stage close and separate powered-work authorization is signed. The blank twelve-row result form contains no current, duty, thermal or acceptance value.

## Twelve open holds

1. complete accepted moving mass, COM and inertia;
2. frozen speed, acceleration, dwell, duty, cycle count and trajectory;
3. reflected drive inertia, efficiency, backlash and compliance;
4. received XM430-W350-T identity, firmware and connector interface;
5. approved branch source, protection, conductor, connector and reverse-energy limits;
6. released external current/PWM/velocity/acceleration limits;
7. calibrated instruments, acquisition characteristics and uncertainty budget;
8. buildable reviewed fixture drawing, catch, guard and proof evidence;
9. qualified temperature-rise, slope and cool-down limits;
10. accepted abort logic and independent branch-power interruption;
11. payload-retention and gripper-force evidence for payload stages; and
12. signed powered-work authorization by the required qualified reviewers.

## Acceptance structure

The package defines equations for external current RMS, torque, case/connector rise, late-window thermal slope, telemetry correlation, actuator-terminal voltage, repeatability, cool-down and fault-free completion. Every actual acceptance limit remains `SELECTION REQUIRED`; none is inferred from a manufacturer endpoint or historic draft.

## Controlled files

- generator: `tools/generate_hr_v0_x430_duty_characterization.py`;
- checker: `tools/check_hr_v0_x430_duty_characterization.py`;
- registers and guide: `release/hr-v0/x430-duty-characterization-p0.1/`;
- blank traveler: `tests/forms/hr-v0-x430-duty-characterization-template.csv`;
- independent review request: `docs/reviews/2026-08-08-x430-duty-characterization-p0.1-independent-review-request.md`.

Passing the checker proves only internal source binding, arithmetic, blank records and fail-closed state. `LOAD-OPEN-08`, X430/P1.1 selection, fabrication, powered test, motion, connection and energization remain open or false.
