# HR-V0 host deployment candidate P0.1

> **PRELIMINARY - NOT APPROVED FOR INSTALLATION, CONNECTION, POWERED TEST, MOTION, OR ENERGIZATION.**

This package defines a reviewable, disabled-by-default Raspberry Pi host-service overlay for Project Button HR-V0. It does not install itself. R199 adds exact GPIO and command-source code candidates without selecting their target dependencies or physical interfaces.

The controlled launcher runs a pure-file preflight before it may start the configuration-bound runtime entrypoint. R198 added the supervisor/bus execution core. R199 expands the overlay to 21 files and adds exact hash-bound libgpiod and local AF_UNIX command-source candidates. The current `host-deploy-config.json` intentionally fails with 50 holds because GPIO package/chip/lines/polarities/timing, the nine-input observation circuit, command sender UID/GID, resource bounds, cycle period, package lock, service identity, device, configuration hashes, HIL evidence, authorization and approvers remain unresolved. The failure occurs before backend import or actuator-bus access.

`overlay-manifest.csv` maps 21 controlled sources to proposed target paths and modes. `systemd/00-project-button.preset` disables the service by default, the unit uses `Restart=no`, permits AF_UNIX only, denies IP, and no install/enabling script is supplied.

Passing 75 firmware tests and 16 host tests proves only source consistency and fail-closed reference behavior. It does not prove the target OS, systemd version, user/group permissions, observation circuit, GPIO waveform, serial device, DYNAMIXEL behavior, timing, power-loss recovery, rollback, HIL behavior, or functional-safety integrity.
