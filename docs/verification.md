# Verification Plan

Every row in `requirements/requirements.csv` names a test, inspection, analysis, or demonstration ID. Detailed procedures are created under `tests/procedures/` before execution. Raw data is never overwritten; reruns receive new run IDs.

## Test stages

1. **T0 document review:** requirements, hazards, schematics, calculations, CAD interference, and configuration completeness.
2. **T1 power-off inspection:** earth bonding, polarity, continuity, contactor feedback, fastener torque, hard stops, shielding, and cable motion.
3. **T2 safety energization:** actuator branches disconnected; prove E-stop channels, reset behavior, watchdog dropout, K1/K2 feedback, and no automatic restart.
4. **T3 single-joint characterization:** one fused actuator at a time, unloaded then proof-loaded, low current/speed first; determine current and thermal limits.
5. **T4 integrated guarded motion:** empty gripper, then 25 g, 50 g, and 100 g foam payloads.
6. **T5 fixture handoff endurance:** 100 cycles with automatic fault monitoring.
7. **T6 human-contact review:** not authorized by this baseline; requires new risk assessment and release.

HR-30 adds these stages after HR-V0 passes:

8. **T7 upper-body pedestal article:** proof the pedestal and pelvic interface, then energize one power group at a time.
9. **T8 HR-30A integration:** verify all 13 axes, mass, swept envelope, visible states, privacy indication, and two-arm thermal/current budgets.
10. **T9 HR-30B restrained body:** proof the fall restraint before installing the robot; characterize each leg joint separately while the restraint carries the robot.

## Key procedures

- `TEST-SAFE-001`: Trigger each E-stop channel independently and together from maximum validated speed/pose. Measure command cessation, contactor dropout, residual joint travel, and tool-center travel. Pass only if actuator power is removed, no restart occurs on release, and travel is within the shielded clearance budget established by CAD.
- `TEST-SAFE-002`: Interrupt the Pi process, USB bus, and heartbeat wire separately. Each shall reach safe-off and latch before the arm can cross its clearance budget.
- `TEST-MECH-001`: Apply 3× maximum operational static load to each primary structural load path with actuator power off. No fracture, fastener slip, permanent deformation beyond drawing tolerance, or loss of hard-stop function.
- `TEST-THERM-001`: Run the worst validated duty cycle at 28 °C ambient or correct results conservatively. Pass if actuator cases stay below provisional limits and conductors remain below 20 °C rise.
- `TEST-HAND-001`: Run 100 fixture handoffs. Pass with at least 99 successful transfers, zero unsafe faults, zero dropped blocks outside the catch tray, and complete logs.
- `TEST-GRIP-001`: Measure grip force across the allowed object range using a calibrated load cell. Establish the lowest current limit that retains the 100 g foam block under the defined motion profile; verify compliant fingers do not tear or permanently crush the reference foam.
- `TEST-POWER-001`: Measure steady and peak branch currents, supply droop, protective-device temperature, and contactor voltage drop during worst-case motion and stall-fault injection.
- `INSPECT-PROD-001`: Measure floor plane to top-of-shell in the released neutral configuration using a calibrated height gauge. Pass at 762 mm nominal drawing dimension and 740–800 mm measured configuration envelope.
- `TEST-MASS-001`: Weigh the complete tethered robot without external cables supported by the scale. Pass at 10.0 kg or less; a result above the 8.0 kg target opens a mass-margin review.
- `INSPECT-PROD-002`: Reconcile the joint inventory, actuator IDs, software configuration, and CAD. Pass with exactly the 13 HR-30A axes defined in the product specification and all undefined axes mechanically locked.
- `TEST-RESTRAINT-001`: Proof the complete restraint load path without the robot at a minimum static load set by the approved restraint analysis and no less than 5 times as-built robot weight. Inspect for slip, permanent deformation, fastener movement, and loss of clearance. Dynamic arrest testing requires a separate approved procedure and sacrificial test mass.
- `INSPECT-PROD-003`: Probe all covers in every released pose using the approved accessibility probe set. Verify 3 mm minimum edge radii and no access to gears, scissor links, or joint pinch zones without tools.
- `TEST-UI-001`: In the specified ambient lighting, identify ready, setup, fault, and actuator-power-off states from 3 m in front, behind, and each side. Include a color-independent pattern or label check for color-vision accessibility.
- `TEST-PRIV-001`: Remove camera power and simulate software crashes and boot states. The privacy indicator shall illuminate whenever camera power permits capture and shall not depend on the application process.
- `TEST-ELEC-030`: Inspect HR-30A for absence of onboard energy storage, verify extra-low-voltage tether polarity/strain relief, and prove external actuator-power isolation.
- `AUDIT-LEG-001`: Before each leg axis is enabled, require signed records for joint proof load, current/thermal characterization, power-loss behavior, mechanical lock or brake behavior, joint limits, restraint clearance, and fault injection.

## Traceability rule

A requirement does not pass because a design document says it should. It passes only with an approved verification record containing test setup, calibration status, configuration hash, measured result, acceptance comparison, operator, reviewer, date, and attached raw data.
