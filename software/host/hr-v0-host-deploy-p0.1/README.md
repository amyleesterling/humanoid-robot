# HR-V0 host deployment candidate P0.1

> **PRELIMINARY - NOT APPROVED FOR INSTALLATION, CONNECTION, POWERED TEST, MOTION, OR ENERGIZATION.**

This package defines a reviewable, disabled-by-default Raspberry Pi host-service overlay for Project Button HR-V0. It does not install itself. R199 adds exact GPIO and command-source code candidates without selecting their target dependencies or physical interfaces. R203 binds heartbeat line 17 and four active-high observation inputs on lines 22 through 25 while leaving the target gpiochip, overlays, package and HIL unresolved.

The controlled launcher runs a pure-file preflight before it may start the configuration-bound runtime entrypoint. R198 added the supervisor/bus execution core. R199 added exact hash-bound libgpiod and local AF_UNIX command-source candidates. R200 corrects the observation semantics to four positive panel status candidates plus five distinct unselected health providers. R203 removes nine source-allocation placeholders. R236 adds a required configuration-bound evidence sink and tightens the candidate cycle period to no more than 10 ms. The current `host-deploy-config.json` intentionally fails with 49 holds because GPIO distribution/version/chip/timing, the physical receiver and harness, health providers, command sender UID/GID, logging/calibration/storage controls, cycle period, package lock, service identity, device, configuration hashes, HIL evidence, authorization and approvers remain unresolved. The failure occurs before backend import or actuator-bus access.

`overlay-manifest.csv` maps 22 controlled sources to proposed target paths and modes. `systemd/00-project-button.preset` disables the service by default, the unit uses `Restart=no`, permits AF_UNIX only, denies IP, and no install/enabling script is supplied.

Passing 86 firmware tests and 16 host tests proves only source consistency and fail-closed reference behavior. It does not prove the target OS, systemd version, user/group permissions, observation circuit, GPIO waveform, serial device, DYNAMIXEL behavior, timing, power-loss recovery, rollback, HIL behavior, or functional-safety integrity.
