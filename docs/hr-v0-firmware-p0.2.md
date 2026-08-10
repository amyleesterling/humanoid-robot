# HR-V0 firmware P0.2 implementation candidate

**PRELIMINARY—NOT APPROVED FOR CONNECTION, FLASHING, FABRICATION, OR ENERGIZATION**

Identifier: `HR-V0-FW-P0.2`

System baseline: `HR-30-SYS-R0.2`

Date: 2026-08-07

P0.2 retains the P0.1 supervisor and reproducible watchdog evidence and adds `HR-V0-DXL-TRANSPORT-P0.1`. The committed supervisor configuration remains deliberately incomplete and cannot open the selected serial port or request torque. This is source-level progress toward `EG-017`, not an executable machine release.

## Controlled components

| Component | Current evidence | Release boundary |
|---|---|---|
| ordinary watchdog | Portable C, reference model, Pico binding and reproducible P0.2 artifacts | Not flashed; no received-board or HIL evidence; zero safety credit |
| supervisor authority model | RESET/ARM observation, trajectory freshness, hash, pose, joint, speed, TCP and deadline checks | Repository hashes/tolerances remain unresolved; no deployment service |
| actuator configuration | Exact register/readback contract and guarded raw-current candidates | Received identity, external branch current, calibration and profiles unresolved |
| DYNAMIXEL transport | Pinned SDK adapter, torque-off/configuration sequence, authority-bound sample writer and fault-injection tests | Repository refuses port open; SDK not installed on target; no U2D2/actuator HIL |

See `docs/hr-v0-firmware-p0.1.md` for the historical implementation basis, `docs/hr-v0-watchdog-build-p0.2.md` for the compiled watchdog evidence, `docs/hr-v0-actuator-current-envelope-p0.1.md` for the current/connector boundary and `docs/hr-v0-dynamixel-transport-p0.1.md` for R65.

Release still requires the complete physical and qualified evidence listed in those documents. In particular, source tests do not establish real-time scheduling, serial latency, bus integrity, current limiting, connector suitability, stopping behavior or functional-safety integrity.

`EG-017` remains **partial**.

**PRELIMINARY—NOT APPROVED FOR CONNECTION, FLASHING, FABRICATION, OR ENERGIZATION**
