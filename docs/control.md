# Control, Permissions, and Fault States

> **PRELIMINARY—NOT APPROVED FOR FABRICATION OR ENERGIZATION**

## Layering

1. The hardware safety layer removes actuator energy independently of software.
2. An ordinary diagnostic watchdog requires a monotonic heartbeat at least every 100 ms. Three missed heartbeats nominally demand hardware-permit dropout. For guarded HR-V0 it is `DF-01`, receives **NO SAFETY CREDIT**, and is assumed capable of failing to operate. Exact physical behavior, routing, output drivers, relays, feedback, restart interaction and fault response remain **SELECTION REQUIRED**. HR-30 requires a separately allocated safety-rated `SF-02` wherever control loss can expose a person.
3. On HR-V0 only, the Raspberry Pi may run the low-rate bench motion supervisor, bounded trajectory executor, non-safety sensor processing, and logger because balance control is outside that release. It never owns the hardware safety function.
4. On HR-30C/D/W, the Raspberry Pi owns behavior, perception, planning, operator UI, and logging. A deterministic real-time controller owns time-critical sensor acquisition, state estimation, whole-body stabilization, gait execution, actuator command generation, deadline enforcement, and all actuator-register writes during balance-critical operation.
5. DYNAMIXEL internal loops execute bounded current-based position commands and report position, velocity, current, voltage, temperature, hardware error, and bus-watchdog state. Their internal loops do not replace the system real-time controller or hardware safety layer.

### Canonical processor-authority matrix

| Function | HR-V0 owner | HR-30 owner | Safety credit |
|---|---|---|---|
| Operator UI, behavior, perception, high-level planning | Raspberry Pi | Raspberry Pi | none |
| Bench trajectory execution | Raspberry Pi, within V0 limits | not permitted for balance-critical motion | none |
| IMU/foot acquisition and timestamping | not applicable or non-safety Pi logging | deterministic real-time controller | none unless separately allocated and validated |
| State estimation and whole-body stabilization | not applicable | deterministic real-time controller | none unless separately allocated and validated |
| Gait trajectory execution and actuator-register writes | not applicable | deterministic real-time controller | none |
| Configuration and deadline validation | Raspberry Pi supervisor plus actuator safeguards | real-time controller; Pi command contract checked again at the boundary | none |
| Session logging | Raspberry Pi | Raspberry Pi with real-time-controller records | evidence only |
| Ordinary heartbeat diagnostic | Raspberry Pi source plus ordinary RP2040/relay path | not credited for walking | none; failure assumed |
| Safety-rated control-loss response | not selected; fixed guard must contain assumed diagnostic failure | selection required before exposed walking | PLr/SIL allocation and validation required |

The Electrical V2.1 arrangement places a normally open watchdog permit downstream of closed PNOZ safety outputs. In that arrangement, restored heartbeat can restore the contactor-coil path without the PNOZ seeing a stop or accepting a new falling-edge reset. That is a release blocker. A watchdog firmware latch is not credited as a safety restart interlock. The released hardware shall keep both contactor coils de-energized after watchdog dropout until the cause is absent, the monitored physical-reset sequence is accepted, and a later, distinct `ARM` action is accepted. Restoring heartbeat, rebooting any controller, clearing a software fault, or holding the reset control shall not satisfy that sequence or re-energize either contactor.

AI perception or language software may propose a high-level action in a later revision, but it never writes an actuator register. Only the deterministic motion supervisor can execute a versioned, signed trajectory whose preconditions are satisfied.

## HR-V0 firmware implementation candidate

`HR-V0-FW-P0.3` provides a portable-C watchdog logic candidate, an executable Python supervisor authority model and `HR-V0-DXL-TRANSPORT-P0.2` under `firmware/`. R68 binds the candidate J2 15–115° envelope to both command validation and engineering-to-raw conversion while leaving its physical acceptance evidence unresolved. The V3 sequence is explicitly a monitored physical RESET followed by a separate deliberate physical ARM action. Software observes that sequence; it has no contactor-closing output. Physical ARM may make the hardware rail eligible, but torque remains off until a later fresh trajectory passes configuration, timing, pose, joint-limit, speed, TCP and terminal-state checks.

The repository supervisor configuration deliberately retains unresolved configuration/kinematic hashes, start-pose tolerances, serial path, received actuator identity, calibration, profiles, input-voltage/temperature envelopes and external branch-current ceiling, so it fails closed. R65 adds a pinned SDK adapter and ordered bus/execution source, but the committed configuration refuses to open a port and no SDK is installed or executed on target. R32 retains the frozen Pico GPIO, exact heartbeat, two-package drivers and ISO1212DBQ feedback passives, and corrects the explicitly unrouted PCB-P0.2 package/placement source. No received/derating evidence, target DYNAMIXEL HIL trace or qualified code/safety review exists. See `docs/hr-v0-firmware-p0.2.md`, `docs/hr-v0-dynamixel-transport-p0.1.md`, `docs/hr-v0-watchdog-feedback-p0.1.md`, `docs/hr-v0-heartbeat-driver-closure-r29.md`, `docs/hr-v0-watchdog-feedback-passive-closure-r30.md`, and `docs/hr-v0-watchdog-pcb-p0.2.md`. No safety credit is assigned to this implementation.

## Command contract

Every motion command contains `trajectory_id`, configuration hash, mode, starting-pose tolerance, ordered samples, velocity/acceleration limits, joint limits, timeout, payload class, and expected terminal state. Commands with an unknown hash, stale timestamp, wrong starting pose, or unmet receiver state are rejected.

Every inter-controller message also contains a monotonic sequence number, source timestamp, validity deadline, sender state, and configuration hash. Receivers reject duplicates, out-of-order messages, expired messages, unknown states, and configuration mismatches. No layer may silently continue the last velocity or trajectory after its deadline.

## Canonical operating state machine

The same state names apply to HR-V0 and HR-30. Product-specific modes are subordinate to these states; they do not create alternate meanings for reset, arm, or drive enable.

| State | Actuator energy | Motion authority | Exit condition |
|---|---|---|---|
| `POWER_OFF` | removed | none | control power applied |
| `SAFE_DISABLED` | removed | none | safety inputs healthy |
| `RESET_REQUIRED` | removed; contactor coils hardware-inhibited | none | cause absent, EDM healthy, and valid physical reset sequence accepted |
| `SAFE_READY` | removed; contactor coils remain inhibited | none | distinct deliberate `ARM` request accepted by the released restart architecture |
| `ARMED` | contactors may be energized; actuator torque remains disabled | bounded supervisor only | fresh trajectory preconditions pass |
| `DRIVE_ENABLED` | available | deterministic real-time controller only | commanded completion, deadline expiry, stop, or fault |
| `CONTROLLED_STOP` | conditional and time-bounded | released stop trajectory only | stopped safely or control authority becomes invalid |
| `FAULT_LATCHED` | removed when required by the fault response | none | cause removed and inspection complete; return through `RESET_REQUIRED` |
| `ENERGY_REMOVED` | removed | none | return through `RESET_REQUIRED` |

Physical reset alone shall not re-energize the contactors in this baseline. Reset never produces torque. `ARM` may release the post-reset contactor inhibit only after the preceding physical reset has been accepted; it never produces torque or motion. Linux cannot transition the system directly to `DRIVE_ENABLED`; only the deterministic controller may do so after validating a fresh command and all preconditions. An interrupted trajectory and every stored torque/position target are invalidated at fault entry and are never resumed after reset. Every state transition is logged with cause and timestamp.

Emergency-stop and credited safety-circuit faults bypass `CONTROLLED_STOP` when the released risk response requires immediate hazardous-energy removal. `DF-01` may nominally request the same dropout, but the risk assessment assumes it can fail. A software preference for standing or kneeling may never weaken a hardware safety function.

## Provisional software limits

| Limit | J1 | J2 | Gripper |
|---|---:|---:|---:|
| Position | -20° to +70° | 15° to 115° | CAD-defined 20–75 mm stroke |
| Auto speed | 30°/s | 30°/s | 20 mm/s |
| Setup speed | 10°/s | 10°/s | 10 mm/s |
| Command age | 100 ms | 100 ms | 100 ms |
| Temperature fault | 65 °C provisional | 65 °C provisional | 60 °C provisional |

Current limits are intentionally not frozen until single-joint characterization. The characterization procedure starts low and establishes the smallest current that completes the proof trajectory with margin. It may never exceed the actuator manufacturer's permitted setting.

The speed rows are provisional planning ceilings, not released DYNAMIXEL profile values. `HR-V0-STOP-BUDGET-P0.1` shows that the J2-positive `115°` software ceiling to `118°` nominal metal backup leaves only `300 ms` at `10°/s` or `100 ms` at `30°/s` before nominal contact. Every actual speed/profile remains inhibited until the missing J1/J2-negative stops, total response, rail decay, residual travel, uncertainty, guard reconciliation and qualified acceptance close. The ordinary 300 ms `DF-01` heartbeat detection consumes the entire three-degree approach at `10°/s` before downstream delay and therefore receives no stopping-distance or safety credit.

## Fault response table

| Event | Immediate response | Latched? | Actuator rail |
|---|---|---:|---:|
| E-stop channel opens | hardware contactors drop | yes | off |
| Ordinary watchdog heartbeat lost | diagnostic requests permit dropout; no safety credit | diagnostic latch | off if diagnostic operates; fixed guard/hard stops assume failure |
| Bus communication lost | DYNAMIXEL bus watchdog torque-off; supervisor requests permit drop | yes | off |
| Joint position exceeds software limit | zero-velocity/torque-off request, then permit drop | yes | off |
| Overtemperature | controlled stop if safe, then permit drop | yes | off |
| Overcurrent/current tracking fault | torque-off and permit drop | yes | off |
| Receiver state unexpected | stop trajectory and hold only within validated thermal/current window; otherwise safe-off | yes | conditional |
| Pi process crash | heartbeat expires | yes | off |
| Compute undervoltage | heartbeat considered invalid | yes | off |

For HR-V0, loss of actuator energy is not assumed to freeze any axis or retain the object. `HR-V0-POWERLOSS-P0.1` selects passive containment as the required strategy: fixed inaccessible guard, passive arm receiver, separate object catch, released bidirectional hard stops and restart prevention. Actuator holding torque, friction, cable tension, software, `DF-01`, a controlled stop and operator action receive no credit. The current `0.750 kg` / `0.360 m` allocation gives a `5.295591 J` gravitational-only bound; it is not an impact rating and excludes continued drive, regeneration, stored energy, detached hardware, receiver behavior and uncertainty. `HR-V0-COLLAPSE-ENV-P0.1` proves the current P0.3 floor tray is 114 mm below the controlled arm envelope and therefore serves only as the object catch; the separate arm receiver remains unimplemented. `EG-009` remains partial until the exact containment system is built and physically validated over every released pose.

Fault recovery requires, in order: cause absent; arm and exclusion zone inspected; trajectory and actuator targets cleared; EDM healthy with both contactors proven dropped; a valid monitored physical-reset action; and a separate, later physical `ARM` action. Heartbeat restoration may only make `DF-01` healthy; it cannot advance this sequence. The credited restart architecture, the diagnostic's non-interference with it, and all physical terminals/routing remain **SELECTION REQUIRED** for qualified validation. Restart never resumes the interrupted trajectory.

## Logging

At 100 Hz minimum, record synchronized command and feedback for position, velocity, current, voltage, temperature, mode, safety inputs, watchdog sequence, trajectory ID, and fault bits. E-stop and watchdog transition timestamps require 1 ms resolution. Logs are immutable session artifacts linked to the exact configuration hash.

Each released test log shall also record state transitions, message sequence/deadline failures, controller and bus timing, estimator age, selected calibration hashes, and any encoder disagreement. Logging requirements are evidence requirements; they are not proof that the implementation exists.
