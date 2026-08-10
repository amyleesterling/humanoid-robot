# HR-V0 host deployment candidate P0.1

> **PRELIMINARY - NOT APPROVED FOR INSTALLATION, CONNECTION, POWERED TEST, MOTION, OR ENERGIZATION.**

This package defines a reviewable, disabled-by-default Raspberry Pi host-service overlay for Project Button HR-V0. It does not install itself and it contains no GPIO or serial implementation.

The controlled launcher runs a pure-file preflight before it may start any future runtime. The current `host-deploy-config.json` intentionally fails that preflight because the runtime backend, exact package lock, service identity, target paths, configuration hashes, HIL evidence, authorization and approvers remain unresolved. The failure occurs before `subprocess.run` and before any GPIO or actuator-bus library is imported.

`overlay-manifest.csv` maps controlled repository sources to proposed target paths and modes. `systemd/00-project-button.preset` disables the service by default, the unit uses `Restart=no`, and no install/enabling script is supplied.

Passing repository checks proves only source consistency and fail-closed reference behavior. It does not prove the target OS, systemd version, user/group permissions, GPIO waveform, serial device, DYNAMIXEL behavior, timing, power-loss recovery, rollback, HIL behavior, or functional-safety integrity.
