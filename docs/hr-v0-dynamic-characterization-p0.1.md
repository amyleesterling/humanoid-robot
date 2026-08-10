# HR-V0 dynamic-characterization input package P0.1

> **PRELIMINARY—MEASUREMENT AND FIXTURE INPUT ONLY—NOT APPROVED FOR POWERED TESTING, MOTION, CONNECTION, OR ENERGIZATION.**

Identifier: `HR-V0-DYN-CHAR-P0.1`

Date: 2026-08-07

Status: generated and repository-checked; no fixture, instrument chain, powered test, motion test, or acceptance value is released.

## Purpose

Sol R12 correctly identified that the Project Button evidence chain stops before fabrication and physical validation. R77 then exposed five quantities that cannot be responsibly closed from catalog endpoints: actual moving mass/COM/inertia, contact speed, current persistence after a stop event, bumper/contact load, and total stopping time. This package defines the evidence chain needed to measure those quantities on a guarded one-axis HR-V0 article.

It does not close `EG-007`, `EG-008`, `EG-023`, `EG-025`, `EG-026`, or `EG-028`. It supplies controlled inputs for future execution after their preceding gates and written authorizations are satisfied.

## What is controlled

The generated package at `test-fixtures/hr-v0/dynamic-characterization-p0.1/` contains:

- a 15-channel measurement register;
- a six-row LabJack T7 evaluation screen;
- twelve fixture and operating controls;
- a twelve-stage sequence from configuration freeze to the still-unauthorized fault matrix;
- eight timing-evidence records;
- a 35-field raw-data schema;
- seven dated primary/project sources; and
- a responsive interactive guide.

The execution template is `tests/forms/hr-v0-dynamic-characterization-template.csv`. Every row is `NOT-EXECUTED`; powered stages `DYN-06` through `DYN-11` remain `NOT AUTHORIZED`.

## Measurement architecture

Primary evidence must come from one hardware-timed acquisition chain with a common physical trigger. The minimum primary or primary-derived quantities are:

1. independent external joint angle and validated velocity derivation;
2. bidirectional branch current, including regeneration polarity;
3. actuator-source bus voltage;
4. reaction force and bumper displacement;
5. K1/K2 coil commands and mirror feedback;
6. stop/E-stop event edges;
7. high-speed video with a visible common trigger; and
8. a sample-clock witness and complete timing/error budget.

The exact sensors, ranges, bandwidths, isolation, grounding, signal conditioning, calibration equipment, scan rate, uncertainty limits, and acceptance values remain `SELECTION REQUIRED`.

## DYNAMIXEL telemetry boundary

The XM540 e-Manual exposes Position, Velocity, Current, Realtime Tick, Temperature and Input Voltage feedback. Realtime Tick has a 1 ms unit and rolls over after 32,767; current uses 2.69 mA per unit, velocity 0.229 rev/min per unit, and position about 0.088 degrees per unit. Present Position can reset on torque, operating-mode, power and reboot transitions and remains affected by Homing Offset.

Those registers are valuable corroboration, but neither the XM540 nor U2D2 documentation publishes a complete host timestamp, polling skew and USB/bus latency guarantee for this test. Therefore `DCH-013` is `SUPPLEMENTAL ONLY`: it receives no primary stopping-time, force, contact or energy credit.

## DAQ evaluation boundary

LabJack's current T-Series documentation makes a base-model T7 a credible evaluation candidate, not a selected instrument:

- the stream clock is hardware-timed;
- the T7 table lists a typical 100 ksample/s maximum for +/-10 V at resolution index 0 or 1;
- eight +/-10 V addresses at resolution index 1 have a listed 12.5 kscan/s maximum;
- scan addresses are sampled sequentially, so interchannel delay must be included; and
- triggered or externally clocked stream modes are documented.

This does not release the T7, any LabJack order code, or any signal-conditioning path. The complete installed chain must be application-reviewed and calibrated. An arbitrary sample rate or timing fraction has not been invented.

## Fixture boundary

The first article is one joint axis using the exact P0.7 received interfaces, not the complete arm. It requires a rigid surveyed bench load path, independent secondary restraint/catch, measured inertial surrogate, remotely accessible stop, and an outer guard that contains debris without carrying intended fixture reaction loads.

No fixture plate, anchor, sensor, bumper or inertial surrogate is released because their exact input loads and received interfaces remain open. The existing Boston bench survey and qualified work control must close before physical work.

## Fail-closed sequence

`DYN-00` through `DYN-05` cover records, unpowered mass/COM inputs, fixture proof, installed calibration, timing injection and a dry run. `DYN-06` starts with actuator-source open-circuit characterization under `EG-019` through `EG-023`. Later stages increment through unloaded holding, low-speed no-contact motion, torque/source removal, lowest released bumper-contact energy and a qualified fault matrix.

Each stage stops on incomplete records, unexpected motion, heat, noise, smoke, data loss, sensor saturation, fixture shift, guard loading, damage or an unbounded result. A successful earlier stage never authorizes the next stage.

## Evidence needed before any powered execution

- immutable configuration and received article serials;
- exact fixture drawings, load-path calculations, bench anchors and secondary restraint;
- released source/protection settings and open-circuit evidence;
- selected sensors and interfaces with calibration and overload evidence;
- accepted scan list, measured rate, interchannel delay and combined timing budget;
- installed guard and remote-work layout;
- written, configuration-specific authorization from the required electrical, mechanical and safety reviewers; and
- an approved procedure with abort, recovery, data-integrity, repetition and acceptance rules.

## Source control

- ROBOTIS, [XM540-W270-T/R e-Manual](https://emanual.robotis.com/docs/en/dxl/x/xm540-w270/), live page with no formal revision shown, accessed 2026-08-07.
- ROBOTIS, [U2D2 e-Manual](https://emanual.robotis.com/docs/en/parts/interface/u2d2/), live page with no formal revision shown, accessed 2026-08-07.
- LabJack, [T-Series Datasheet](https://support.labjack.com/docs/t-series-datasheet), live documentation with no formal revision shown, accessed 2026-08-07.
- LabJack, [Stream Mode](https://support.labjack.com/docs/3-2-stream-mode-t-series-datasheet), live documentation with no formal revision shown, accessed 2026-08-07.
- LabJack, [T7 stream data rates](https://support.labjack.com/docs/a-1-1-stream-data-rates-t-series-datasheet), live documentation with no formal revision shown, accessed 2026-08-07.
- LabJack, [special stream modes](https://support.labjack.com/docs/3-2-2-special-stream-modes-t-series-datasheet), live documentation with no formal revision shown, accessed 2026-08-07.

## Release statement

`HR-V0-DYN-CHAR-P0.1` is a controlled measurement-input package. It does not make HR-V0 buildable, close a physical gate, approve a fixture or DAQ, or authorize procurement, fabrication, assembly, connection, powered testing, motion, energization, operation around children, or transfer to HR-30W.
