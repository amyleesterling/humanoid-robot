# HR-V0 DYNAMIXEL transport and execution boundary P0.1

**PRELIMINARY—SOURCE CANDIDATE ONLY—NOT APPROVED FOR CONNECTION, FLASHING, FABRICATION, OR ENERGIZATION**

Identifier: `HR-V0-DXL-TRANSPORT-P0.1`

Date: 2026-08-07

Parent firmware candidate: `HR-V0-FW-P0.2`

## Result

R65 adds the missing executable boundary between the non-safety supervisor model and a future received U2D2/actuator bus. It does not make the repository runnable on hardware. The controlled `actuator-config.json` still contains unresolved serial-device, received identity, calibration, profile, voltage, temperature and external-current fields. `DynamixelBusController.connect_and_configure()` checks that boundary before calling the transport, so the committed configuration refuses to open a serial port or write a register.

The source contains:

- a small `RegisterTransport` protocol that can be fault-injected without hardware;
- a pinned optional adapter for ROBOTIS DYNAMIXEL SDK `4.0.5` / Protocol 2.0;
- exact common XM430/XM540 register addresses and signedness;
- ordered torque-off, discovery, identity, configuration and readback logic;
- an authority-bound torque-enable sequence that establishes start targets, current/profile candidates and the bus watchdog before enabling torque;
- synchronous goal-position writes tied to one active trajectory ID; and
- telemetry checks that remove torque on communication, watchdog, hardware-error, current, voltage, temperature, calibration or authority failure.

The source has no API for closing K1 or K2 and receives no functional-safety credit.

## Fail-closed sequence

| Stage | Required action | Failure disposition |
|---|---|---|
| 0 | Prove every release selection is numeric/exact, including received model and firmware, serial device, calibration, profile and telemetry envelopes | Port remains unopened |
| 1 | Open the selected device and command `Torque Enable (64) = 0` to every expected ID | Best-effort torque off; close port; latch software-side failure |
| 2 | Broadcast-discover the bus, command torque off to every discovered ID, and require an exact ID/model-number set | Unexpected, missing or substituted devices inhibit configuration |
| 3 | With torque off, clear an existing Bus Watchdog error and write/read back exact Drive Mode, Operating Mode 5, Startup Configuration 0, Current Limit, Goal Current 0 and Bus Watchdog 0 | Any packet or readback mismatch inhibits configuration |
| 4 | Require a fresh matching supervisor trajectory; convert its start pose through released zero/direction/scale calibration; compare Present Position to the released raw tolerance | Torque remains off |
| 5 | Synchronously establish the no-jump start target; write current/profile bounds and Bus Watchdog candidate; enable torque last and read it back | Best-effort torque off on any failure |
| 6 | For each trajectory sample, require unchanged motion authority and trajectory identity, perform one synchronous position write, then poll torque, watchdog, hardware error, current, voltage, temperature, velocity and position | Best-effort torque off and target invalidation |
| 7 | On completion, fault, exception, authority loss or close, command torque off and clear the active trajectory | A fresh RESET/ARM/trajectory sequence is still required by the surrounding architecture |

The ordinary DYNAMIXEL Bus Watchdog is an actuator safeguard, not the credited machine E-stop or restart-prevention function. ROBOTIS documents that it monitors instruction-packet intervals only while torque is enabled, changes to `-1` on expiry and makes goal registers read-only until cleared with `0`. The P0.1 source detects that state and requests torque off; physical HIL must establish actual timing and behavior.

## Controlled software evidence

- `firmware/supervisor/project_button_supervisor/dynamixel_bus.py`
- `firmware/supervisor/project_button_supervisor/sdk_transport.py`
- `firmware/supervisor/dynamixel-sdk-lock.json`
- `firmware/supervisor/tests/test_dynamixel_bus.py`
- `tests/forms/hr-v0-dynamixel-transport-hil-template.csv`

The standard-library test suite proves source behavior for unopened unresolved configuration, torque-off-before-discovery, unexpected IDs and substituted models, ordered configuration, authority-gated torque enable, start-position checks, watchdog expiry, hardware-error/current/voltage/temperature envelope faults, synchronous-write failure, close-time torque removal, raw conversion bounds and signed register encoding. It uses a deterministic fake transport; it does not prove U2D2, Linux serial, USB, packet timing or actuator behavior.

## Primary-source basis

Sources were accessed 2026-08-07:

- ROBOTIS DYNAMIXEL SDK `4.0.5`, release dated 2026-05-06, signed upstream commit `2ded684`: https://github.com/ROBOTIS-GIT/DynamixelSDK/releases/tag/4.0.5
- ROBOTIS Python synchronous read/write tutorial for Protocol 2.0: https://emanual.robotis.com/docs/en/software/dynamixel/dynamixel_sdk/sync_read_write_tutorial/sync_read_write_tutorial_python/
- ROBOTIS XM540-W270 e-Manual control table and Bus Watchdog behavior: https://emanual.robotis.com/docs/en/dxl/x/xm540-w270/
- ROBOTIS XM430-W350 e-Manual control table and Bus Watchdog behavior: https://emanual.robotis.com/docs/en/dxl/x/xm430-w350/

The live product pages expose no controlled page revision. Exact URLs and access date are retained; release must also retain the installed package artifact hash and target-image identity.

## Evidence still required

1. Select and freeze the Raspberry Pi OS/Python image, U2D2 hardware/USB revision, retained USB cable and stable `/dev/serial/by-id/...` device path.
2. Receive each actuator; record model number, firmware version, ID and all configuration readbacks with torque off.
3. Calibrate joint zero, direction, engineering-to-raw scale, raw limits and start tolerances against the accepted mechanical assembly and hard stops.
4. Select profile velocity/acceleration, input-voltage, temperature and external branch-current limits from guarded physical characterization—not catalog maxima alone.
5. Install the exact `dynamixel-sdk==4.0.5` artifact from an approved source; record its SHA-256, dependency tree and immutable deployment image.
6. Execute packet loss, CRC/error, duplicate ID, unexpected ID, unplug/replug, U2D2 reset, Linux process crash, USB latency, bus-watchdog expiry, brownout, actuator reboot and partial-write HIL cases with raw packet and oscilloscope traces.
7. Prove every authority/fault path removes torque and cannot resume the prior target after heartbeat, RESET, ARM, process or hardware restoration.
8. Complete the external-current, connector-temperature, source-regeneration, branch-protection and stopping-time evidence before any assembled mechanism motion.
9. Obtain independent controls, electrical and functional-safety review. No result may assign safety credit to this ordinary software path.

Gate `EG-017` remains **partial**. No target package was installed, no device was opened, no actuator was connected, and no HIL row was executed.

**PRELIMINARY—SOURCE CANDIDATE ONLY—NOT APPROVED FOR CONNECTION, FLASHING, FABRICATION, OR ENERGIZATION**
