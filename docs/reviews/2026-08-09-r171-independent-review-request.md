# R171 independent review request

Review `HR-V0-HOST-DEPLOY-P0.1` as a fail-closed source/deployment candidate, not as an installed image or safety function.

1. Confirm the committed HOLD configuration exits before any process spawn, GPIO access, serial open, heartbeat or actuator command.
2. Challenge every preflight input, exact-hash check and missing/malformed/configuration-substitution fault path.
3. Review the systemd unit, disabled preset, ownership/mode proposal and sandbox directives against the eventual selected Raspberry Pi OS/systemd/backend versions.
4. Confirm the package supplies no hidden enabling/install route and cannot resume stale motion.
5. Audit the eighteen holds and 21 blank execution rows for package-lock, device identity, waveform, bus, power-loss, rollback, hardening, qualified-review and authorization completeness.
6. Confirm `EG-003`, `EG-017` and `EG-021` remain partial and that ordinary software retains zero functional-safety credit.

Everything remains **PRELIMINARY - NOT APPROVED FOR INSTALLATION, CONNECTION, POWERED TEST, MOTION, OR ENERGIZATION**.
