# Verification Plan

> **PRELIMINARY—NOT APPROVED FOR FABRICATION OR ENERGIZATION**

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

- `TEST-SAFE-001` is composite. At E2, `TEST-E2-002` may test only safety-relay, contactor-coil, E-stop-channel, reset/ARM and diagnostic restart logic with the actuator source physically absent and all branches disconnected. It records no stopping-distance or loaded-interruption credit. At the later authorized motion stage, trigger each E-stop channel independently and together from maximum validated speed/pose; measure command cessation, safety-relay response, both contactor dropouts, residual joint travel and tool-center travel. Test channel open, channel-to-channel short, welded/stuck contact simulation, E-stop release and reset held at power-up. Pass the complete verification only if actuator power is removed, release/reset does not restart or command motion, EDM prevents restart after simulated welded contact, and travel remains within the released guard-clearance budget.
- `TEST-SAFE-002`: Interrupt the Pi process, USB bus, heartbeat wire, watchdog supply, watchdog output driver, and permit relay path separately. Each shall reach safe-off before the mechanism can cross the released clearance budget and shall enter a hardware-held restart-required state. While the physical reset remains untouched, restore the heartbeat, reboot all controllers, and restore every software process: K1 and K2 shall remain de-energized. Apply the valid physical reset sequence: K1 and K2 shall still remain de-energized and no torque or motion shall occur. Only a later distinct `ARM` action may permit contactor energization. The old trajectory and every stored actuator target shall remain invalid, and motion shall require a fresh command whose preconditions pass. Record heartbeat timeout, watchdog/relay dropout, each contactor dropout, rail decay, residual travel, and total stopping time.
- `TEST-SAFE-003`: For each latched fault class, verify recovery ordering: cause removed, inspection complete, EDM healthy, valid physical-reset sequence, then separate `ARM`. Inject reset held, reset stuck closed, reset contact bridged, reset pulse shorter than the published minimum, ARM before reset, simultaneous reset/ARM, and stale-trajectory cases. None shall restore contactor power, torque, or motion outside the released order.
- `TEST-SAFE-004`: With power removed, inspect the received PNOZ s4 identity, terminal markings, selector position, and seal. Confirm the manual page-13 lower-row/third-column falling-edge mode. Inspect `S11/S12`, `S21/S22`, the protected `S12 -> reset -> K1 NC -> K2 NC -> S34` route, and safety outputs `13-14`, `23-24`, and `33-34`. Treat `41-42` and `Y32` as diagnostics only. Test the 250 ms falling-edge wait, 100 ms minimum start pulse, stuck reset, induced start/feedback-loop bridge, each mirror contact, and welded-contactor simulation. The protected-routing fault exclusion requires documented physical inspection and qualified acceptance; ERC cannot close it.
- `TEST-MECH-001`: Apply 3× maximum operational static load to each primary structural load path with actuator power off. No fracture, fastener slip, permanent deformation beyond drawing tolerance, or loss of hard-stop function.
- `TEST-THERM-001`: Run the worst validated duty cycle at 28 °C ambient or correct results conservatively. Pass if actuator cases stay below provisional limits and conductors remain below 20 °C rise.
- `INSPECT-OBJ-001`: Before and after endurance testing, identify and measure the exact serialized soft-foam object with a released low-force method. Its accepted mass including uncertainty shall be no more than 100 g and each accepted principal dimension including uncertainty shall be 40-70 mm. Exact material, conditioning, grip axis, measurement force, uncertainty and damage/permanent-set criteria remain `SELECTION REQUIRED`.
- `TEST-HAND-001`: Run exactly 100 guarded fixture-to-fixture transfers using the same object accepted by `INSPECT-OBJ-001`. Pass with at least 99 successful transfers, zero unsafe faults, zero payload escapes from the released catch/guard, complete synchronized per-cycle evidence and a passing post-test object inspection.
- `TEST-GRIP-001`: Measure grip force across the allowed object range using a calibrated load cell. Establish the lowest current limit that retains the 100 g foam block under the defined motion profile; verify compliant fingers do not tear or permanently crush the reference foam.
- `INSPECT-MECH-008`: Use `MV0-FC03` to record all four selected FR12-H104K positions, flat seating, and proposed fastener/nut/tool access on the received frame before cutting `MV0-002`.
- `INSPECT-GRIP-001`: Reconcile every allocated RM-X52 mechanism item, assemble the exact controlled configuration, and probe the fixed local guard to confirm the crank, links, rail and actuator-frame pinch zones are inaccessible.
- `INSPECT-GUARD-001`: Compare the frozen guard against the complete 3D swept/stopping/payload/tolerance envelope in every unpowered-limit and released fault case; record minimum clearances and access-probe results.
- `INSPECT-CABLE-001`: Articulate every controlled cable zone through the entire mechanical range and record bend, twist, tension, clamp, connector-load, abrasion and stop/pinch/guard clearances.
- `TEST-DROP-001`: Verify the fixed catch contains the controlled 100 g foam object after commanded release, gripper fault and actuator-power loss from every released pose; record rebound, slide, escape and damage evidence.
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
- `TEST-POWERLOSS-001`: With the robot restrained and the restraint proven first, remove drive energy in every released HR-30 pose and mode, including single-support and credible fault poses. Measure collapse path, joint backdrive, contact and arrest loads, head/tool trajectories, regenerated-bus voltage, and time to the selected protective state. An unbraked collapse is the conservative assumption until tests prove otherwise. Pass criteria require a selected and reviewed brake, counterbalance, retained-control ride-down, or accepted-fall design with pose-specific clearance and load limits. This test cannot authorize reduced restraint dependence or operation near people.

## Electrical evidence counting convention

- The native KiCad package contains **15 pages total: one root/index sheet plus 14 child schematic sheets**. KiCad ERC output that says “14 sheets checked” is counting the 14 child sheets; it is not a contradictory package total.
- The controlled unresolved-selection count is **106**: the 106 non-header records in `unresolved-selections.csv`. Each record is one unresolved component or interface decision and is uniquely keyed by `(sheet, reference)`. Do not recount terminals, nets, evidence phrases, website cards, or rows from a joined/expanded representation as additional selections. Any other reported total shall identify its source file, filter, join, and grouping rule and shall not replace the controlled 106-item count.
- These counts describe artifact structure and open work only. They do not establish design completeness, functional-safety performance, or permission to fabricate or energize.

## Traceability rule

A requirement does not pass because a design document says it should. It passes only with an approved verification record containing test setup, calibration status, configuration hash, measured result, acceptance comparison, operator, reviewer, date, and attached raw data.
