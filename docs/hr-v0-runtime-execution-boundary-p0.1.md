# HR-V0 runtime execution boundary P0.1

> **PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION**

Artifact: `HR-V0-RUNTIME-P0.1`

Configuration: `HR-V0-HOST-DEPLOY-P0.1` / `HR-V0-SUP-P0.3` / `HR-V0-DXL-TRANSPORT-P0.3` / `HR-V0-KIN-P0.1`

Review/control round: R198; backend correction R199; observation correction R200; GPIO allocation correction R203

## Correction

The R171 host overlay stopped safely but its target entrypoint was `SELECTION REQUIRED` and no source connected hardware observation, supervisor authority, heartbeat permission, sample scheduling and the actuator bus. R198 added that missing executable boundary rather than treating a launcher as a runtime. R199 corrects the heartbeat contract and adds exact GPIO/command-source candidates.

The proposed overlay now maps 21 exact repository sources, including hash-bound `gpiod_hardware.py` and `unix_command_source.py`. `runtime_entrypoint.py` has an exact target path and SHA-256. R203 binds source-level heartbeat line 17 and four active-high diagnostic lines 22 through 25. The committed preflight reports 36 holds and exits 78. The hold register has sixteen open records and two partial records: `HOST-004` and `HOST-006` remain partial on source evidence only.

## Runtime sequence

The committed configuration still returns exit 78 during pure-file preflight. A future isolated-HIL configuration can proceed only after all required hashes, approvals and selections close. The entrypoint then:

1. reloads preflight and refuses before selected backend import on any hold;
2. loads the exact supervisor, kinematic and actuator configurations;
3. requires every configuration selection and physical acceptance hash to close;
4. binds the process to a boot-unique session identifier;
5. verifies host and actuator serial-device parity;
6. imports only the exact hash-bound GPIO/hardware-observation and authenticated command-source factories;
7. starts with heartbeat inactive, then services a monotonic edge schedule only while ordinary heartbeat permission remains true, and opens the actuator bus torque-off;
8. observes received positions and physical state before applying supervisor authority;
9. accepts only a fresh session-valid trajectory after the distinct hardware RESET and ARM sequence;
10. writes one due sample at a time within a released lateness bound;
11. re-sends the final target while checking the received terminal pose; and
12. removes heartbeat permission, torque enable and goal current on dropout, bus fault, missed timing, shutdown or process failure.

The active bus invariant was corrected during integration: torque-off now requires `Torque Enable = 0` and `Goal Current = 0`; motion requires the configured goal-current bound. Received raw position is converted through the same released zero, scale and direction used for command conversion.

## Executable evidence

The firmware suite now has 78 executable tests. The host package has 16 tests, including committed preflight refusal, no child process, no backend import, exact source hashing, heartbeat edge scheduling, lateness/time-reversal shutdown, input polarity, kernel credential checking and strict finite command parsing.

## Remaining evidence

The repository now controls backend source identities plus line/polarity allocation, but selects no libgpiod package/chip path/timing, command sender UID/GID, cycle period, serial device, service identity, package lock, target interpreter, accepted runtime configuration or approval. Four positive status semantics have source-level Pi allocations; five health providers remain unselected and no physical observation harness or connected circuit exists. There is no installed image, target execution, waveform, serial trace, physical HIL, power-loss, rollback, stopping or qualified evidence. All 21 host evidence rows remain `NOT_AUTHORIZED / NOT_EXECUTED`; EG-017 remains partial. The general-purpose runtime and heartbeat receive zero functional-safety credit. No finding, requirement or energization gate closes.

## R199 supplement

`HR-V0-RUNTIME-BACKENDS-P0.1` records the exact backend-source hashes, 50 fail-closed preflight holds and the unresolved physical observation interface. Three new trajectory limits—maximum samples, maximum duration and maximum execution slack—remain `null` and therefore prevent release construction. A source-level GPIO adapter is not a schematic, wiring allocation, installed driver or HIL result.
