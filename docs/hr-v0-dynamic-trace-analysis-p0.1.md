# HR-V0 dynamic trace analysis P0.1

> **PRELIMINARY - ANALYSIS CANDIDATE ONLY - QUALIFIED DISPOSITION REQUIRED - NOT APPROVED FOR POWERED TESTING, MOTION, OR ENERGIZATION.**

Identifier: `HR-V0-DYN-TRACE-P0.1`
Date: 2026-08-10

## Purpose

`HR-V0-DYN-CHAR-P0.1` defines what must be measured, and `HR-V0-STOP-BUDGET-P0.1` shows why the current nominal three-degree J2-positive approach has no released stopping margin. This package supplies the missing deterministic analysis contract between those raw measurements and future `EG-026` evidence.

It does not select instruments, thresholds, a safety-function response time, a physical test configuration, or a qualified reviewer. It contains no executed physical run.

## Controlled artifacts

- `tools/analyze_hr_v0_dynamic_trace_p01.py` parses one synchronized CSV trace and one configuration JSON.
- `analysis/hr-v0/dynamic-trace-p0.1/analysis-config-template.json` is the physical-run template. All thirteen numeric acceptance inputs, the stop-event field, the motion direction, and the qualified-acceptance reference remain `SELECTION REQUIRED`; the analyzer rejects this unresolved template.
- `event-channel-extension.csv` adds common-clock reset, separate start, supervisor motion-request, and torque-enable witnesses to the R78 channel set.
- `acceptance-rule-register.csv` defines nine stable `DTA-001` through `DTA-009` rules.
- Four generated synthetic traces exercise a nominal stop, prohibited reset-driven motion, a too-early separate start, and a data-integrity fault.
- `tests/forms/hr-v0-dynamic-trace-disposition-template-p0.1.csv` retains four blank electrical, mechanical, functional-safety, and independent-test dispositions on `HOLD`.
- The interactive guide is at `release/hr-v0/dynamic-trace-analysis-p0.1/index.html`.

## Analysis contract

The analyzer fails closed when required columns are absent, numeric data are invalid, configuration values remain unresolved, the chosen stop edge is absent, or a sustained motion-stop condition cannot be found. For a parseable trace it records:

1. sample-index, timebase, metadata, loss, and saturation integrity;
2. the selected physical stop-event edge;
3. K1 and K2 coil-command falling edges;
4. K1 and K2 mirror-contact opening edges;
5. the first sustained actuator-source rail threshold crossing;
6. the first sustained independent velocity/angle stop window;
7. total stop time, residual travel, worst endpoint, and remaining hard-stop clearance;
8. reset behavior before a separate start command; and
9. peak current, regeneration polarity, force, displacement, and a positive-compression numerical work integral.

The contact-work integral is only a reported numerical quantity. It receives no absorber, structural, impact, or functional-safety credit.

## Reset cannot command motion

`DTA-007` requires a reset edge on the common DAQ timebase. From that edge until either the selected observation interval expires or a separate start edge occurs, all of the following must remain false or within the accepted noise band:

- K1 coil command;
- K2 coil command;
- supervisor motion request;
- actuator torque-enable feedback; and
- independent measured motion.

The generated `fail-reset-trace.csv` violates these conditions and is rejected. This is an algorithm test, not physical proof that the as-built reset circuit or software behaves correctly.

## Synthetic validation

The synthetic configuration uses explicit numbers solely to make the analysis algorithm reproducible. They are not proposed physical acceptance values. The nominal trace produces:

- stop event: 0.050 s;
- motion stop: 0.080 s;
- total stop time: 0.030 s;
- residual travel: 0.435 degrees; and
- endpoint clearance: 6.065 degrees.

Its computed result is `PASS`, but its disposition remains `HOLD - QUALIFIED REVIEW REQUIRED` and its release effect is `NONE`. The reset-motion, early-start, and data-integrity fixtures produce `FAIL` and `REJECT`.

## Evidence still required for a physical run

- immutable as-built configuration and article identities;
- selected isolated measurement interfaces and exact signal polarities;
- accepted sample list, measured sample interval, clock/scan skew, sensor/filter delay, and combined uncertainty;
- traceable installed calibration and overload/range evidence;
- actuator-specific rail-below-torque threshold and dwell;
- accepted independent motion noise, derivative, dwell, and angle-band definitions;
- safety-function response-time allocation, residual-travel limit, hard-stop coordinate, and minimum clearance;
- reset observation interval, repetitions, load/pose/fault matrix, and separate-start semantics;
- complete fixture, guard, secondary restraint, remote-work, abort, and recovery acceptance;
- executed traces and videos with immutable hashes; and
- named competent and independent reviewers with signed configuration-specific disposition.

## Gate effect

`EG-026` advances from `open` to `partial` because a deterministic analysis and rejection path now exists. It does not close: no physical trace, accepted limit, statistical/uncertainty bound, guard-clearance reconciliation, qualified disposition, or reset-to-motion validation exists.

No other gate closes. No procurement, fabrication, assembly, connection, powered testing, motion, energization, operation around children, or HR-30 transfer is authorized.
