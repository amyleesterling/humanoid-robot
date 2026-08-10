# HR-V0 host deployment candidate P0.1

> **PRELIMINARY - NOT APPROVED FOR INSTALLATION, CONNECTION, POWERED TEST, MOTION, OR ENERGIZATION.**

This package defines a reviewable, disabled-by-default Raspberry Pi host-service overlay for Project Button HR-V0. It does not install itself and it contains no selected GPIO, serial or command-source backend.

The controlled launcher runs a pure-file preflight before it may start the configuration-bound runtime entrypoint. R198 adds the real supervisor/bus execution core, exact entrypoint hash and complete 19-file proposed overlay. The current `host-deploy-config.json` still intentionally fails with 24 holds because the cycle period, backends, exact package lock, service identity, device, configuration hashes, HIL evidence, authorization and approvers remain unresolved. The failure occurs before `subprocess.run` and before any selected GPIO or actuator-bus backend is imported.

`overlay-manifest.csv` maps the host modules, complete supervisor source package, three runtime configurations and SDK lock to proposed target paths and modes. `systemd/00-project-button.preset` disables the service by default, the unit uses `Restart=no`, and no install/enabling script is supplied.

Passing repository checks proves only source consistency and fail-closed reference behavior. It does not prove the target OS, systemd version, user/group permissions, GPIO waveform, serial device, DYNAMIXEL behavior, timing, power-loss recovery, rollback, HIL behavior, or functional-safety integrity.
