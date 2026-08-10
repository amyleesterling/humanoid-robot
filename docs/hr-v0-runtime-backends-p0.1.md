# HR-V0 runtime backend source candidates P0.1

> **PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION**

Artifact: `HR-V0-RUNTIME-BACKENDS-P0.1`

Configuration: `HR-V0-HOST-DEPLOY-P0.1` / `HR-V0-RUNTIME-P0.1` / `HR-V0-SUP-P0.3`

Review/control round: R199

## Result

R199 replaces two abstract host interfaces with exact, hash-bound source candidates while preserving a fail-closed deployment. It does not allocate a Raspberry Pi pin, release an observation circuit, select a package version, install a service, connect hardware or authorize motion.

The proposed host overlay now contains 21 exact source-to-target mappings. The committed pure-file preflight returns exit 78 with 50 explicit holds. The host hold register remains 17 open records and one partial record; all 21 execution-evidence rows remain `NOT_AUTHORIZED / NOT_EXECUTED`.

## GPIO and heartbeat candidate

`project_button_host.gpiod_hardware` is a libgpiod 2.x source candidate with:

- import only after successful pure-file preflight;
- exact distribution, version, chip, line, polarity and timing configuration requirements;
- disabled input bias and an exact nine-input runtime schema;
- a monotonic heartbeat edge scheduler rather than a static permission level; and
- forced inactive output on disable, missed edge deadline, clock reversal, startup failure and close.

The scheduler corrects an R198 modeling error: `heartbeat_allowed` is permission to generate edges, not the waveform itself. Unit tests prove the source model only. They do not prove Linux scheduling, GPIO startup state, voltage levels, waveform tolerance, watchdog response, isolation, noninterference or fault behavior.

## Command-source candidate

`project_button_host.unix_command_source` is a local AF_UNIX datagram source candidate with:

- no TCP/IP listener;
- Linux `SO_PASSCRED` / `SCM_CREDENTIALS` checking against exact selected UID and GID;
- a bounded datagram size;
- an exact JSON field set with no extra fields;
- finite numeric parsing that rejects NaN and infinity; and
- conversion to the typed `TrajectoryCommand` already subjected to session, sequence, state, configuration-hash, pose, rate, kinematic, duration and deadline checks.

The sender identity, UID, GID, process confinement, producer protocol, queue/flood behavior and target execution remain unreleased.

## Resource and time bounds

R199 adds three mandatory supervisor selections: maximum trajectory sample count, maximum trajectory duration and maximum execution slack. All remain `null` in the committed configuration. The existing maximum sample-lateness selection also remains unresolved. Repository construction therefore fails closed rather than inventing target limits.

## Critical physical-interface gap

The runtime requires nine physical observations: control power, E-stop health, watchdog health, EDM health, compute undervoltage, SR1 ready, SRA1 armed, K1 feedback and K2 feedback. No released Raspberry Pi allocation or connected input circuit exists for these signals.

The electrical candidate contains potential status sources such as SR1 and SRA1 auxiliary/semiconductor outputs and K1/K2 auxiliary contacts, but R199 does not connect them. Closure requires a qualified electrical design defining every terminal, isolation/input receiver, loading, protection, cable, connector, grounding, startup state, GPIO allocation, diagnostic coverage and noninterference argument, followed by received-hardware inspection and fault-injection evidence. No pin, polarity or circuit may be inferred from this source package.

## Evidence state

- 75 firmware tests pass: 64 supervisor/runtime tests and 11 watchdog tests.
- 16 host tests pass, including eight backend-source tests.
- 21 overlay rows are controlled and not authorized.
- 50 committed preflight holds are reported before backend import.
- zero target, HIL, waveform, serial, power-loss, stopping or physical-motion tests have been executed.
- zero functional-safety credit is claimed.

No Sol finding, requirement, physical gate, qualified-review gate or work-authorization gate closes.

## Primary implementation references

- libgpiod Python API 2.3 documentation, accessed 2026-08-10: <https://libgpiod.readthedocs.io/en/v2.3/python_misc.html>
- libgpiod line request 2.3 documentation, accessed 2026-08-10: <https://libgpiod.readthedocs.io/en/v2.3/python_line_request.html>
- Linux `unix(7)` manual page, accessed 2026-08-10: <https://man7.org/linux/man-pages/man7/unix.7.html>
- Python 3 socket library documentation, accessed 2026-08-10: <https://docs.python.org/3/library/socket.html>
- Raspberry Pi GPIO documentation, accessed 2026-08-10: <https://www.raspberrypi.com/documentation/computers/raspberry-pi.html>
