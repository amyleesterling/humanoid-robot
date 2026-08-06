# HR-30 Walking Verification Matrix

Walking tests use a progression that cannot be skipped by a successful simulation.

## W0 — simulation and test articles

- Reproduce the released mass/inertia model in simulation.
- Demonstrate bounded standing and gait trajectories under ±20% mass/inertia and modeled latency variation.
- Characterize one primary pitch joint through continuous torque, cyclic torque, backlash, efficiency, thermal, hard-stop, and power-loss tests.
- Verify output-side absolute sensing over the full joint range and temperature/load envelope; inject belt slip, pulley release, lost calibration, reversed polarity, stale data, and motor/output disagreement.
- Characterize a complete foot sensor over the full load and center-of-pressure region.
- Produce a byte-level packet budget and measure worst-case command/feedback latency, jitter, utilization, retries, and failure traffic on the proposed physical bus and harness.

## W1 — restrained single leg

- Mount one complete leg to a rigid instrumented fixture.
- Execute the full joint workspace without collision or cable strain.
- Apply the released axial, lateral, and moment proof loads.
- Reproduce one walking cycle at full speed and load for the thermal-duration requirement.

## W2 — double-leg gantry

- The restraint carries the robot while joint polarity, kinematics, force sensing, and controlled kneel are validated.
- Progressively unload the restraint until feet carry 100% of static weight.
- Demonstrate 120 s quiet standing and 100 controlled weight shifts.

## W3 — HR-30D slack-tether walking

- Prove the tether is slack and carries less than 2% robot weight except during an arrest.
- Complete ten 10 m trials, both 90° turn directions, start/stop transitions, and 10 min cumulative motion.
- Inject loss of high-level planner, one missed foot sensor, degraded IMU, low supply voltage, and commanded stop. Verify the defined response.
- Inject IMU saturation, foot-sensor saturation, encoder disagreement, configuration mismatch, bus retry storm, regenerative overvoltage, and sudden drive-energy loss from every released pose and mode.
- Conduct separate tether-arrest tests with a sacrificial mass before any robot fall test.

## W4 — fall characterization

- Use a padded, instrumented enclosure with no person in the fall zone.
- Characterize forward, rearward, and lateral low-energy falls, first with a mass surrogate and then with the de-energized robot.
- Powered fall-response testing begins only after head, battery, connector, and finger containment pass the passive tests.

## W5 — HR-30W untethered acceptance

The robot passes only when it:

1. stands for 120 s without external support;
2. starts, walks 25 m at 0.10–0.20 m/s, stops within two steps, and remains standing;
3. performs five left and five right 90° turns within five steps each;
4. completes 30 min cumulative walking without exceeding thermal or energy limits;
5. repeats the course ten times with at least nine complete successes and no hazardous failure;
6. logs every required state and matches the released configuration;
7. stays within the marked test corridor and never contacts the padded boundary.

Passing W5 authorizes controlled engineering operation only. It does not authorize walking among people.
