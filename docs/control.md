# Control, Permissions, and Fault States

## Layering

1. The hardware safety layer removes actuator energy independently of software.
2. A watchdog microcontroller owns the `WATCHDOG_PERMIT` relay and requires a monotonic heartbeat at least every 100 ms. Three missed heartbeats drop permit and latch a restart-required fault.
3. The Raspberry Pi runs the motion supervisor, trajectory executor, sensor processing, and logger.
4. DYNAMIXEL internal loops execute bounded current-based position commands and report position, velocity, current, voltage, temperature, hardware error, and bus-watchdog state.

AI perception or language software may propose a high-level action in a later revision, but it never writes an actuator register. Only the deterministic motion supervisor can execute a versioned, signed trajectory whose preconditions are satisfied.

## Command contract

Every motion command contains `trajectory_id`, configuration hash, mode, starting-pose tolerance, ordered samples, velocity/acceleration limits, joint limits, timeout, payload class, and expected terminal state. Commands with an unknown hash, stale timestamp, wrong starting pose, or unmet receiver state are rejected.

Every inter-controller message also contains a monotonic sequence number, source timestamp, validity deadline, sender state, and configuration hash. Receivers reject duplicates, out-of-order messages, expired messages, unknown states, and configuration mismatches. No layer may silently continue the last velocity or trajectory after its deadline.

## Canonical operating state machine

The same state names apply to HR-V0 and HR-30. Product-specific modes are subordinate to these states; they do not create alternate meanings for reset, arm, or drive enable.

| State | Actuator energy | Motion authority | Exit condition |
|---|---|---|---|
| `POWER_OFF` | removed | none | control power applied |
| `SAFE_DISABLED` | removed | none | safety inputs healthy |
| `RESET_REQUIRED` | removed | none | physical reset edge and EDM healthy |
| `SAFE_READY` | removed | none | deliberate software `ARM` request |
| `ARMED` | available but no motion command accepted yet | bounded supervisor only | fresh trajectory preconditions pass |
| `DRIVE_ENABLED` | available | deterministic real-time controller only | commanded completion, deadline expiry, stop, or fault |
| `CONTROLLED_STOP` | conditional and time-bounded | released stop trajectory only | stopped safely or control authority becomes invalid |
| `FAULT_LATCHED` | removed when required by the fault response | none | cause removed, inspection complete, physical reset required |
| `ENERGY_REMOVED` | removed | none | return through `RESET_REQUIRED` |

Reset never produces torque. `ARM` never produces motion. Linux cannot transition the system directly to `DRIVE_ENABLED`; only the deterministic controller may do so after validating a fresh command and all preconditions. An interrupted trajectory is invalidated and is never resumed after reset. Every state transition is logged with cause and timestamp.

Emergency-stop, watchdog, or safety-circuit faults bypass `CONTROLLED_STOP` when the released risk response requires immediate hazardous-energy removal. A software preference for standing or kneeling may never weaken the hardware safety function.

## Provisional software limits

| Limit | J1 | J2 | Gripper |
|---|---:|---:|---:|
| Position | -20° to +70° | 15° to 125° | CAD-defined 20–75 mm stroke |
| Auto speed | 30°/s | 30°/s | 20 mm/s |
| Setup speed | 10°/s | 10°/s | 10 mm/s |
| Command age | 100 ms | 100 ms | 100 ms |
| Temperature fault | 65 °C provisional | 65 °C provisional | 60 °C provisional |

Current limits are intentionally not frozen until single-joint characterization. The characterization procedure starts low and establishes the smallest current that completes the proof trajectory with margin. It may never exceed the actuator manufacturer's permitted setting.

## Fault response table

| Event | Immediate response | Latched? | Actuator rail |
|---|---|---:|---:|
| E-stop channel opens | hardware contactors drop | yes | off |
| Watchdog heartbeat lost | watchdog permit drops | yes | off |
| Bus communication lost | DYNAMIXEL bus watchdog torque-off; supervisor requests permit drop | yes | off |
| Joint position exceeds software limit | zero-velocity/torque-off request, then permit drop | yes | off |
| Overtemperature | controlled stop if safe, then permit drop | yes | off |
| Overcurrent/current tracking fault | torque-off and permit drop | yes | off |
| Receiver state unexpected | stop trajectory and hold only within validated thermal/current window; otherwise safe-off | yes | conditional |
| Pi process crash | heartbeat expires | yes | off |
| Compute undervoltage | heartbeat considered invalid | yes | off |

Fault reset requires the cause to be absent, arm visually inspected, trajectory cleared, operator outside the exclusion zone, safety reset pressed, and a separate software `ARM` action. Restart never resumes the interrupted trajectory.

## Logging

At 100 Hz minimum, record synchronized command and feedback for position, velocity, current, voltage, temperature, mode, safety inputs, watchdog sequence, trajectory ID, and fault bits. E-stop and watchdog transition timestamps require 1 ms resolution. Logs are immutable session artifacts linked to the exact configuration hash.

Each released test log shall also record state transitions, message sequence/deadline failures, controller and bus timing, estimator age, selected calibration hashes, and any encoder disagreement. Logging requirements are evidence requirements; they are not proof that the implementation exists.
