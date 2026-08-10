# Independent review request - R200 runtime observation correction

> **PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION**

Review `HR-V0-RUNTIME-OBS-P0.1` against Electrical V3-P1.15 and current primary manufacturer documents.

1. Confirm the exact trace for `SR1_STATUS`, `SRA1_STATUS`, `K1_STATUS` and `K2_STATUS`, including every current load and XT1 terminal.
2. Confirm that control power, E-stop health, watchdog health, EDM health and compute undervoltage cannot be inferred from those four states.
3. Challenge the explicit `None` behavior. Prove no unknown input can enable heartbeat, satisfy readiness, authorize trajectory acceptance or request torque.
4. Confirm that unused 41-42 NC contacts are not inverted into a positive relay-state claim.
5. Recalculate the SR1:Y32 load using the exact received H1 current, worst-case receiver current, rail tolerance, temperature and fault cases. Do not approve connection from typical values.
6. Check K1/K2 auxiliary loading against Schneider's minimum switching current and voltage and the exact receiver envelope.
7. Review an ISO1212-based receiver only as an evaluation architecture. Require exact passives, surge protection, decoupling, thermal/derating, isolation/grounding, connector, cable, layout and GPIO evidence before any connection.
8. Require separate provider designs and semantics for all five unavailable health observations.
9. Confirm the committed preflight still fails before backend import and that all twelve R200 holds remain open.
10. State whether the correction is internally accurate, whether a connected native KiCad interface may now be designed, and what evidence must precede isolated HIL. Do not authorize fabrication, connection, motion or energization.

Primary artifacts:

- `docs/hr-v0-runtime-observation-semantics-p0.1.md`
- `controls/hr-v0-runtime-observation-map-p0.1.csv`
- `controls/hr-v0-runtime-observation-holds-p0.1.csv`
- `firmware/supervisor/project_button_supervisor/model.py`
- `software/host/hr-v0-host-deploy-p0.1/project_button_host/gpiod_hardware.py`
- `release/hr-v0/runtime-observation-p0.1/index.html`
- `electrical/kicad/project-button-v3-p1.15-carrier-candidate/`
