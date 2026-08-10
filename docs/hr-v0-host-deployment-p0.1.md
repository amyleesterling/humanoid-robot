# HR-V0 fail-closed host deployment candidate P0.1

> **PRELIMINARY - NOT APPROVED FOR INSTALLATION, CONNECTION, POWERED TEST, MOTION, OR ENERGIZATION.**

Identifier: `HR-V0-HOST-DEPLOY-P0.1`
Review round: R171; runtime correction R198; backend correction R199; GPIO allocation correction R203
Date: 2026-08-09
Parent image: `HR-V0-RPI-OS-LITE-P0.1`
Storage candidate: `HR-V0-COMPUTE-STORAGE-P0.2` / Kingston `SDCIT2/64GBSP` on hold

## Result

R171 added the host-side deployment definition between the pinned Raspberry Pi OS image and the supervisor model. R198 added the executable runtime boundary. R199 adds exact hash-bound libgpiod and AF_UNIX command-source candidates, corrects heartbeat permission into a monotonic edge scheduler, and adds trajectory resource/time holds. R203 freezes BCM/RP1 heartbeat line 17 and four active-high diagnostic inputs on lines 22 through 25 while retaining the target gpiochip, boot-overlay, harness and HIL holds. It remains a **source candidate**, not an installable or promoted machine image.

The committed configuration has 36 explicit preflight failures after the R203 GPIO-allocation correction. The launcher and the runtime entrypoint both return exit code 78 before importing a backend. The package supplies no install script, disables its systemd service by preset, uses `Restart=no`, restricts the candidate service to AF_UNIX with IP denied, and retains `motion_authority: NONE` and `functional_safety_credit: NONE`.

This improves the digital evidence behind `EG-017`; it does not close that gate.

## Controlled startup sequence

1. systemd may invoke only the controlled launcher if a separately authorized image-builder installs and enables the candidate.
2. the launcher runs pure-file preflight first;
3. preflight verifies release/authorization state, exact configuration paths and hashes, backend identities, interpreter/package hashes, HIL/recovery/rollback evidence hashes and approval hashes;
4. any absent, malformed, changed or unresolved input exits 78;
5. only a future separately released configuration can reach the exact hash-bound runtime entrypoint;
6. the entrypoint loads the same accepted supervisor, kinematic and actuator configuration, verifies a boot-unique session and device parity, and only then imports selected backends;
7. the runtime forces heartbeat inactive, opens/configures the bus torque-off, observes hardware, applies supervisor authority, services a monotonic heartbeat edge schedule, schedules one bounded trajectory sample at a time, verifies the received terminal pose and removes torque; and
8. any hardware, bus, scheduling, authority or process failure removes the ordinary heartbeat request and bus torque request.

Reset or E-stop release cannot command motion through the runtime model: the executive never enables torque without an accepted fresh command and the supervisor retains the replay barrier. That source-level result is not physical proof of reset behavior, watchdog timing, backend behavior or actuator interruption.

## Proposed target overlay

`software/host/hr-v0-host-deploy-p0.1/overlay-manifest.csv` maps 21 repository sources to proposed target paths, including the two backend candidates. All 21 rows are `NOT_AUTHORIZED`. The `project-button` account/group names in the systemd candidate are proposed names only; account creation, UID/GID, supplementary device groups and least-privilege permissions remain `SELECTION REQUIRED` under `HOST-003`.

The service hardening candidate includes a strict read-only system boundary, private temporary storage, no new privileges, no automatic restart and writable access only to proposed state/log directories. Target systemd compatibility and required device access must be tested; these directives are not assumed compatible with the final GPIO/serial backend.

## Evidence still required

The eighteen-line hold register now contains sixteen open holds and two partial holds. `HOST-004` is partial because the source backend, line numbers and polarities exist; `HOST-006` is partial because source, target path and entrypoint hash exist. Target gpiochip identity, installation, backend integration, timing and HIL are still absent. Remaining evidence requires, at minimum:

- exact target package versions, repositories, lock hash, interpreter and binary hash;
- exact target libgpiod package and stable RP1 gpiochip identity/permissions; the GPIO17 and GPIO22-25 line allocation is source-bound but not target-validated;
- released supervisor, actuator and compute-interface configurations with exact hashes;
- a released 1..50 ms runtime cycle period, exact libgpiod package/chip/timing allocation, exact command sender UID/GID and measured resource/time bounds;
- a qualified physical observation circuit and harness for the four positive status inputs plus distinct providers for five health semantics, including terminal allocation, isolation/loading, protection, cable, grounding, startup state and noninterference proof;
- controlled image download, write, full readback and promoted image manifest;
- disabled-start, missing/malformed/hash-mismatch, GPIO waveform, U2D2, torque-off-before-discovery, stale-command, reset-no-motion and heartbeat-loss HIL;
- filesystem, logging, abrupt-power-loss, recovery and offline rollback evidence;
- security/access disposition; and
- signed controls, electrical, test, configuration and work-authorization decisions.

All 21 execution rows in `tests/forms/hr-v0-host-deployment-template-p0.1.csv` remain `NOT_AUTHORIZED / NOT_EXECUTED`.

## Configuration boundary

The official Raspberry Pi image hash remains only a publisher-provided candidate value. It has not been downloaded or locally reproduced. The Kingston card has not been purchased, received, inserted, written, booted or tested. No target package lock, filesystem policy, service UID/GID, gpiochip path/label, observation harness/circuit or serial device path has been selected. Source-level GPIO lines and polarities exist; their target dependencies and physical interfaces do not.

The general-purpose compute, heartbeat, launcher, supervisor and watchdog diagnostic function retain **zero functional-safety credit**. Physical safety functions, PLr/SIL allocation, qualified validation and a separate written work authorization remain mandatory.

## Controlled artifacts

- `software/host/hr-v0-host-deploy-p0.1/host-deploy-config.json`
- `software/host/hr-v0-host-deploy-p0.1/project_button_host/`
- `software/host/hr-v0-host-deploy-p0.1/systemd/`
- `software/host/hr-v0-host-deploy-p0.1/overlay-manifest.csv`
- `software/host/hr-v0-host-deploy-p0.1/hold-register.csv`
- `software/host/hr-v0-host-deploy-p0.1/SOURCE-MANIFEST.csv`
- `tests/forms/hr-v0-host-deployment-template-p0.1.csv`
- `requirements/hr-v0-gate-evidence-supplement-r171.csv`
- `release/hr-v0/host-deployment-p0.1/index.html`
- `tools/check_hr_v0_host_deploy_p01.py`

Passing repository tests proves file integrity and reference-model behavior only. The current preflight has 36 holds, the overlay has 21 rows, the hold register has sixteen open plus two partial records, and all 21 execution records remain blank. The 78 firmware tests and 16 host tests are not target/HIL evidence. This package does not authorize installation, imaging, connection, powered testing, motion or energization.
