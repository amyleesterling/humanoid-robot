# HR-30 whole-body electrical P0.1

**PRELIMINARY - NOT APPROVED FOR CONNECTION, FABRICATION, MOTION OR ENERGIZATION**

This is the native KiCad 10 whole-body architecture for the current 25-axis HR-30 candidate. It contains a root index plus eighteen populated child sheets. Five RS-485 and three TTL data-only segments match the whole-body bus allocation exactly; all 25 actuators have distinct protected-feed boundaries. Individual head HMI devices, pelvis IMU, bilateral four-point foot sensing and a separate isolated onboard-later energy sheet are also represented.

The actuator interface is now a pin-level candidate, not eight abstract boxes. STM32H743ZIT6 LQFP144 package pins are allocated to all eight UART channels; Carrier A contains four ISOW1432DFMR isolated RS-485 candidates; Carrier B contains one ISOW1432DFMR plus three SN74LVC1T45DCKR 3.3/5 V single-wire TTL translators. The logic-only controller connectors remain JST GH; the eight data-only field ports are JST PA through-hole secure-lock candidates whose published contact ranges include the planning conductors. The field connectors intentionally contain no actuator VDD contact.

Sheet 01 now encodes the tether-first controlled 12 V source, three regulated 9 V TTL rails and a deliberately disconnected onboard-later battery/charger path. Sheet 02 encodes two independently commanded series contactor coils, linked-auxiliary EDM candidates, dual-channel E-stop, monitored reset, charger inhibit and an ordinary-watchdog inhibit that has zero safety credit. Reset restores eligibility only and cannot command motion.

AX_* actuator terminals use current official ROBOTIS actuator-side pin numbers. Remaining `LOG-*` identifiers are unresolved functional ports elsewhere in the architecture. Standard ROBOTIS cables carry VDD, so the 25 distinct feeds require a custom/de-pinned data-only harness or breakout. Fuse/limiter values, conductors, connector selections, grounding, safety allocation, timing and physical behavior remain unresolved. The historical mixed HR-V0/HR-30 project is not incorporated as verified wiring.

## Sheets

1. `01_energy_precharge_conversion.kicad_sch` — Tether-first energy, regulated rails and onboard-later boundary
2. `02_estop_permit_contactors.kicad_sch` — Dual-channel E-stop, monitored reset, permit and redundant interruption
3. `03_compute_motion_watchdog.kicad_sch` — Conversational compute, deterministic motion controller and watchdog
4. `04_motion_controller_carrier_connectors.kicad_sch` — STM32H743 motion-controller power and carrier connectors
5. `05_carrier_a_four_isolated_rs485.kicad_sch` — Carrier A - four isolated RS-485 channels
6. `06_carrier_b_waist_and_ttl.kicad_sch` — Carrier B - waist RS-485 and three translated TTL channels
7. `07_left_leg_rs485.kicad_sch` — Left-leg RS-485 data bus and individual feeds
8. `08_right_leg_rs485.kicad_sch` — Right-leg RS-485 data bus and individual feeds
9. `09_left_arm_rs485.kicad_sch` — Left proximal-arm RS-485 data bus and individual feeds
10. `10_right_arm_rs485.kicad_sch` — Right proximal-arm RS-485 data bus and individual feeds
11. `11_waist_rs485.kicad_sch` — Waist RS-485 data bus and individual feed
12. `12_left_distal_ttl.kicad_sch` — Left wrist/gripper TTL data bus and individual feeds
13. `13_right_distal_ttl.kicad_sch` — Right wrist/gripper TTL data bus and individual feeds
14. `14_head_ttl_sensors_hmi.kicad_sch` — Head TTL, cameras, face display, audio and cooling
15. `15_pelvis_aux_imu.kicad_sch` — Three-rail auxiliary conversion and pelvis inertial sensing
16. `16_left_foot_load_sensing.kicad_sch` — Left foot four-point load sensing
17. `17_right_foot_load_sensing.kicad_sch` — Right foot four-point load sensing
18. `18_onboard_later_energy_evaluation.kicad_sch` — Onboard-later isolated energy evaluation

KiCad ERC checks encoded passive-pin connectivity and annotation only. It grants no functional-safety credit and no authority to order, fabricate, connect, power, move or energize the robot.
