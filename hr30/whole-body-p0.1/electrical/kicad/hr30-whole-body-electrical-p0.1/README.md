# HR-30 whole-body electrical P0.1

**PRELIMINARY - NOT APPROVED FOR CONNECTION, FABRICATION, MOTION OR ENERGIZATION**

This is the native KiCad 10 whole-body architecture for the current 25-axis HR-30 candidate. It contains a root index plus twelve populated child sheets. Five RS-485 and three TTL actuator segments match the whole-body bus allocation exactly.

AX_* actuator terminals use current official ROBOTIS actuator-side pin numbers. All `LOG-*` terminal identifiers are functional ports, not physical connector or IC pin numbers. Controller/interface pins, exact devices, order codes, fuse/limiter values, conductors, connectors, grounding, shield treatment, safety allocation, stopping time and physical behavior remain unresolved. The historical mixed HR-V0/HR-30 project is not incorporated as verified wiring.

## Sheets

1. `01_energy_precharge_conversion.kicad_sch` — Energy, service disconnect, precharge and conversion
2. `02_estop_permit_contactors.kicad_sch` — Dual-channel E-stop, monitored reset, permit and redundant interruption
3. `03_compute_motion_watchdog.kicad_sch` — Conversational compute, deterministic motion controller and watchdog
4. `04_eight_actuator_bus_interfaces.kicad_sch` — Five isolated RS-485 and three protected TTL interface channels
5. `05_left_leg_rs485.kicad_sch` — Left-leg RS-485 and protected branch
6. `06_right_leg_rs485.kicad_sch` — Right-leg RS-485 and protected branch
7. `07_left_arm_rs485.kicad_sch` — Left proximal-arm RS-485 and protected branch
8. `08_right_arm_rs485.kicad_sch` — Right proximal-arm RS-485 and protected branch
9. `09_waist_rs485.kicad_sch` — Waist RS-485 and protected branch
10. `10_left_distal_ttl.kicad_sch` — Left wrist/gripper TTL and protected branch
11. `11_right_distal_ttl.kicad_sch` — Right wrist/gripper TTL and protected branch
12. `12_head_ttl_sensors_hmi.kicad_sch` — Head TTL, sensing, display and audio

KiCad ERC checks encoded passive-pin connectivity and annotation only. It grants no functional-safety credit and no authority to order, fabricate, connect, power, move or energize the robot.
