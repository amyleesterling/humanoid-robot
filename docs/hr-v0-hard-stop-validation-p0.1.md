# HR-V0 Hard-Stop Validation Procedure P0.1

**PRELIMINARY - NOT AUTHORIZED FOR EXECUTION WITH ACTUATOR POWER UNTIL THE E2 REVIEW GATE CLOSES.**

Related procedures: `INSPECT-MECH-006`, `TEST-MECH-002`

Record template: `tests/forms/hr-v0-hard-stop-validation-template.csv`

Design basis: `docs/hr-v0-hard-stop-design-basis-p0.1.md`

## INSPECT-MECH-006 - unpowered geometry and retention

1. Verify the immutable repository commit, CAD/source hashes, actuator/frame serials, stop-part revisions and inspection-equipment calibration.
2. Keep all actuator power physically disconnected and apply lockout identification at the disconnected branch.
3. Establish J1 and J2 coordinate zero using the released fixture and method; record uncertainty.
4. Move each joint by hand through its permitted range. Record the first software-limit datum, first bumper contact, positive-catch contact if separately measurable, and first cable/connector/guard/self-contact angle.
5. Measure both directions for each stop to capture backlash. Repeat after ten unpowered contacts and after removing/reinstalling each serviceable bumper.
6. Verify that every stop fastener has the released part, torque/locking condition and witness mark, and that adjustment cannot drift or rotate.
7. Reject any configuration in which a cable, connector, actuator cover or guard contacts before the stop, the positive catch is absent, the 5 degree nominal separation is consumed by uncertainty, or the joint can bypass the stop.

This inspection may close only geometric/retention evidence. It does not prove impact capacity.

## TEST-MECH-002 - guarded incremental stop characterization

This test may begin only after the exact joint article, current limit, bumper, bracket, instrumentation, risk controls and test sequence receive qualified written approval. No child or uninvolved person may enter the test area.

1. Mount one joint in a rigid guarded fixture with a secondary physical restraint and remote emergency stop. Remove the payload or use the released surrogate mass.
2. Instrument joint angle/speed/current/voltage at the released sample rate, stop reaction force or calibrated bumper displacement, and high-speed video. Preserve synchronized raw data.
3. Start below setup speed and below the released current limit. Approach one stop once, remove power, inspect, and compare measured contact angle and peak response with the approved bound.
4. Increase only through the approved matrix. Do not jump directly to automatic speed, maximum payload, or a drive-into-stop fault.
5. After every step inspect bumper set/cracking, bracket deformation, fastener movement, witness marks, parent-frame damage, gearbox backlash/noise and encoder zero shift.
6. Execute the approved single-fault cases separately, including bumper removed/degraded, worst tolerance, watchdog/permit drop latency and current persisting for the measured cutoff interval.
7. Stop on any bound exceedance, permanent deformation, fastener movement, cracked bumper, abnormal sound, increased backlash, loss of calibration, data dropout or guard/restraint event.
8. Repeat the released cycle count and environmental cases only after the preceding severity passes.

Acceptance limits for peak force, bumper stroke, rebound, deformation, zero shift, backlash growth, cycle count and temperature remain `SELECTION REQUIRED`. Until they are released and passed, `TEST-MECH-002` remains `NOT EXECUTED` and the hard-stop gate remains open.
