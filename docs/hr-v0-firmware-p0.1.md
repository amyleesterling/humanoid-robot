# HR-V0 Firmware P0.1 Implementation Candidate

> **PRELIMINARY—NOT APPROVED FOR FABRICATION OR ENERGIZATION**

Identifier: `HR-V0-FW-P0.1`  
System baseline: `HR-30-SYS-R0.2`  
Electrical dependency: `Project Button Electrical V3-P1.0` candidate

## Purpose and authority boundary

This candidate implements the first executable watchdog and HR-V0 supervisor state logic. It is not released firmware and receives no functional-safety credit.

The V3 hardware architecture uses a monitored physical RESET followed by a separate deliberate physical ARM action. The supervisor cannot close K1 or K2. Its only motion-related output is a non-safety torque-enable request that remains false until:

1. the process has observed `RESET_REQUIRED -> SAFE_READY -> ARMED` in order;
2. SR1, SRA1, K1 and K2 diagnostic states are mutually consistent;
3. a fresh trajectory has the selected configuration and kinematic hashes;
4. sequence, time, start pose, joint position, joint speed, gripper speed, computed TCP speed and terminal-state checks pass; and
5. no latched software fault exists.

RESET and physical ARM never create or resume a trajectory. Every fault invalidates the stored target. Hardware restoration cannot resume it; a fresh command is required.

## Watchdog candidate

`firmware/watchdog/src/pb_watchdog.c` is portable C state logic. `firmware/watchdog/platform/pico/main.c` is the compiled Raspberry Pi Pico 1 / RP2040 P0.1 binding; it is a source candidate, not released firmware. The executable specification is `firmware/watchdog/reference_model.py`.

The candidate is default-off, requires three valid heartbeat edges, drops both output commands when the edge age reaches 300 ms, and requires three new edges after a timeout. It checks each relay's NC diagnostic feedback after a provisional 25 ms settling interval. Too-fast edges or feedback disagreement latch a service fault and drop both outputs.

The 20 ms minimum-edge threshold and 25 ms feedback-settling threshold are preliminary configuration values, not verified ratings. The latter is screened against the Phoenix Contact page's 8 ms typical pickup and 10 ms typical release data, but voltage, temperature, input conditioning, actual relay samples and complete response-time measurements remain open.

Watchdog heartbeat recovery may make the two ordinary watchdog relays healthy again. It cannot by itself restore K1/K2 because SRA1 has dropped and the monitored physical ARM path must be exercised again. This separation is a hardware claim requiring review and HIL traces; firmware is not credited as the restart interlock.

## Supervisor candidate

`firmware/supervisor/project_button_supervisor/model.py` implements the authority state machine and trajectory checks. The repository configuration intentionally contains unresolved configuration/kinematic hashes and `null` start-pose tolerances. Therefore the repository configuration fails closed and cannot accept any trajectory.

`firmware/supervisor/actuator-config.json` now defines `HR-V0-ACT-P0.1`, a fail-closed register-readback candidate. It requires Operating Mode 5, startup torque off, torque-on-goal-update off, torque initially off, and raw current candidates of 800 for J1/J2 and 300 for the gripper. Received model numbers, firmware versions and the external branch-current ceiling are deliberately unresolved, so the repository candidate still inhibits torque. See `docs/hr-v0-actuator-current-envelope-p0.1.md`.

The candidate has no DYNAMIXEL transport, trajectory interpolator, Raspberry Pi service wrapper, real-time scheduler or released kinematic model. Those are required before bench motion.

## Current validation evidence

Run:

```text
python tools/check_hr_v0_firmware.py
```

The current checker executes 25 standard-library unit tests covering:

- default-off startup and stuck heartbeat;
- exact 300 ms timeout and three-edge recovery;
- too-fast heartbeat and both relay-feedback faults;
- RESET/ARM without motion;
- unexpected ARM order;
- stale, future, duplicate, out-of-order and hash-mismatched commands;
- start-pose, joint limit, joint-speed and TCP-speed rejection;
- target invalidation on fault and hardware restoration; and
- execution-deadline and terminal-state behavior.
- fail-closed actuator identity, mode, startup/drive-bit, torque-state, current-limit, goal-current and hardware-error readback.

It also compares portable-C timing constants to `watchdog-config.json`, checks fail-closed source and Pico-platform invariants, verifies the locked toolchain and controlled two-build artifact hashes, and verifies `firmware/SOURCE-MANIFEST.csv` against the source tree.

`HR-V0-WD-BUILD-P0.1` now supplies warning-clean Project Button source compilation, exact GPIO binding, pinned tools, static size/stack evidence and matching ELF/UF2/BIN/HEX/map/canonical-disassembly hashes. See `docs/hr-v0-watchdog-build-p0.1.md` and `firmware/watchdog/output/P0.1/`. The binary has not been flashed or executed on received hardware.

## Evidence still required for release

- received-board default-off/input-conditioning proof for the compiled watchdog GPIO candidate, plus polarity/continuity records;
- released PCB and protected wiring for the proposed VO618A heartbeat path, two separate TPL7407LPWR drivers and ISO1212 feedback interface, plus `TEST-ELEC-005` physical/HIL/fault evidence;
- an independent second-host/container reproduction of the pinned Pico build;
- static analysis beyond compiler diagnostics, unit-test execution against target-compiled C, and full call-chain/runtime stack-margin evidence;
- selected Raspberry Pi deployment image, Python version, service supervision and immutable configuration hash;
- selected kinematic model, tolerance values, DYNAMIXEL transport and compiled torque-off/readback semantics;
- received actuator identity/firmware records plus external branch-current, torque, connector-temperature and duty-cycle evidence under `INSPECT-CTRL-001` and `TEST-CTRL-006`;
- code review by named controls/electrical reviewers;
- HIL fault matrix and raw traces for `TEST-SAFE-001` through `TEST-SAFE-003` and `TEST-CTRL-001` through `TEST-CTRL-006`; and
- qualified functional-safety review of the hardware boundary, diagnostics and common-cause failures.

Gate `EG-017` is therefore only `partial`. Source tests and reproducible binary hashes do not authorize flashing firmware or energizing the robot.
