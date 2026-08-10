# HR-V0 runtime execution boundary P0.1

> **PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION**

Artifact: `HR-V0-RUNTIME-P0.1`

Configuration: `HR-V0-HOST-DEPLOY-P0.1` / `HR-V0-SUP-P0.3` / `HR-V0-DXL-TRANSPORT-P0.3` / `HR-V0-KIN-P0.1`

Review/control round: R198

## Correction

The R171 host overlay stopped safely but its target entrypoint was `SELECTION REQUIRED` and no source connected hardware observation, supervisor authority, heartbeat permission, sample scheduling and the actuator bus. R198 adds that missing executable boundary rather than treating a launcher as a runtime.

The proposed overlay now maps nineteen exact repository sources: seven host/systemd files, eight supervisor modules, three configurations and the pinned SDK lock. `runtime_entrypoint.py` has an exact target path and SHA-256. The hold register now has seventeen open records and one partial record: `HOST-006` advances from open to partial on source evidence only.

## Runtime sequence

The committed configuration still returns exit 78 during pure-file preflight. A future isolated-HIL configuration can proceed only after all required hashes, approvals and selections close. The entrypoint then:

1. reloads preflight and refuses before selected backend import on any hold;
2. loads the exact supervisor, kinematic and actuator configurations;
3. requires every configuration selection and physical acceptance hash to close;
4. binds the process to a boot-unique session identifier;
5. verifies host and actuator serial-device parity;
6. imports only the selected GPIO/hardware-observation and authenticated command-source factories;
7. starts with heartbeat disallowed and opens the actuator bus torque-off;
8. observes received positions and physical state before applying supervisor authority;
9. accepts only a fresh session-valid trajectory after the distinct hardware RESET and ARM sequence;
10. writes one due sample at a time within a released lateness bound;
11. re-sends the final target while checking the received terminal pose; and
12. removes heartbeat permission, torque enable and goal current on dropout, bus fault, missed timing, shutdown or process failure.

The active bus invariant was corrected during integration: torque-off now requires `Torque Enable = 0` and `Goal Current = 0`; motion requires the configured goal-current bound. Received raw position is converted through the same released zero, scale and direction used for command conversion.

## Executable evidence

The firmware suite now has 72 executable tests, including runtime startup, RESET/ARM without motion, ordered trajectory execution, hardware dropout, missed-sample failure, shutdown ordering, inverse calibration, independent terminal tolerance and torque/goal-current clearing. The host package has eight tests, including committed preflight refusal, no child process, no backend import and exact entrypoint hash binding.

## Remaining evidence

The repository still selects no GPIO backend, authenticated command source, cycle period, serial device, service identity, package lock, target interpreter, accepted runtime configuration or approval. There is no installed image, target execution, waveform, serial trace, physical HIL, power-loss, rollback, stopping or qualified evidence. All 21 host evidence rows remain `NOT_AUTHORIZED / NOT_EXECUTED`; EG-017 remains partial. The general-purpose runtime and heartbeat receive zero functional-safety credit. No finding, requirement or energization gate closes.
