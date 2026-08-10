# HR-V0 Actuator Current and Torque Envelope P0.1

> **PRELIMINARY—NOT APPROVED FOR FABRICATION OR ENERGIZATION**

System baseline: `HR-30-SYS-R0.2`  
Configuration candidate: `HR-V0-ACT-P0.1`  
Date: 2026-08-07

## Decision

The two XM540 branches remain **SELECTION REQUIRED**. The published 12 V stall endpoint is 4.4 A while JST rates the EH series at 3 A AC/DC with AWG 22. A fuse cannot make normal operating current comply with a connector rating, and a DYNAMIXEL internal current limit is not a direct measurement or guaranteed limit of the actuator-branch supply current.

This document introduces a deliberately conservative **test candidate**, not a released operating limit:

| Axis | Actuator | Current Limit (38) candidate | Goal Current (102) maximum candidate | Nominal internal-current conversion | Ideal stall-line torque screen at 12 V |
|---|---|---:|---:|---:|---:|
| J1 shoulder | XM540-W270-T | 800 raw | 800 raw | 800 × 2.69 mA = 2.152 A | 2.152 A × 2.409 N·m/A = 5.18 N·m |
| J2 elbow | XM540-W270-T | 800 raw | 800 raw | 800 × 2.69 mA = 2.152 A | 5.18 N·m |
| Gripper | XM430-W350-T | 300 raw | 300 raw | 300 × 2.69 mA = 0.807 A | 0.807 A × 1.783 N·m/A = 1.44 N·m |

The XM540 screen is 1.35 times the preliminary 3.83 N·m shoulder intermittent load screen. This is only an ideal linear interpolation from a stall endpoint. It is not a continuous-duty rating, efficiency model, available-output guarantee, or connector-compliance proof. The gripper value is a low-energy starting point whose usable grip force remains unmeasured.

## Primary-source basis

- ROBOTIS, **XM540-W270-T/R e-Manual**, live page checked 2026-08-07, no document revision shown: 10.6 N·m at 12.0 V and 4.4 A is a stall endpoint; Current Limit (38), Goal Current (102), and Present Current (126) use approximately 2.69 mA per raw unit; Operating Mode 5 is current-based position control. <https://emanual.robotis.com/docs/en/dxl/x/xm540-w270/>
- ROBOTIS, **XM430-W350-T/R e-Manual**, live page checked 2026-08-07, no document revision shown: 4.1 N·m at 12.0 V and 2.3 A is a stall endpoint; Current Limit (38) range is model-specific and uses approximately 2.69 mA per raw unit. <https://emanual.robotis.com/docs/en/dxl/x/xm430-w350/>
- JST, **EH connector product page**, live page checked 2026-08-07, no document revision shown: 3 A AC/DC at AWG 22, AWG 32–22 conductor range, and −25 °C to +85 °C temperature range. <https://www.jst-mfg.com/product/index.php?lang=2&series=58>

ROBOTIS identifies the TTL actuator connector as JST EHR-03/B3B-EH-A with SEH-001T-P0.6 contacts and states 21 AWG for DYNAMIXEL wire. JST's EH series page lists a maximum conductor size of AWG 22. That apparent wire-size discrepancy, the construction of the received factory harness, and the applicable current rating for the exact mated pair remain receiving-inspection and manufacturer-application questions. No wire size is inferred from appearance.

## Configuration contract before any torque-enable request

The executable candidate is `firmware/supervisor/actuator-config.json`; its fail-closed readback validator is `project_button_supervisor/actuator_config.py`.

With actuator power current-limited and the mechanism physically restrained, the commissioning implementation shall:

1. keep `Torque Enable (64) = 0` and verify it by readback;
2. read and record Model Number (0), Firmware Version (6), ID (7), Drive Mode (10), Operating Mode (11), Current Limit (38), Startup Configuration (60), Hardware Error Status (70), Goal Current (102), Present Current (126), Present Position (132), Present Input Voltage (144), and Present Temperature (146);
3. reject an unexpected identity, firmware, ID, mode, configuration bit, limit, hardware error, or already-enabled torque state;
4. with torque off, set and read back Operating Mode (11) = 5, Startup Torque On bit = 0, Torque On by Goal Update bit = 0, and the candidate Current Limit (38);
5. set and read back Goal Current (102) no higher than the axis candidate, then set and verify the separately released profile velocity and acceleration;
6. apply software position limits and physical hard stops because ROBOTIS states that Min/Max Position Limit registers are not used in Operating Mode 5;
7. require the complete supervisor authority sequence and a fresh trajectory before writing `Torque Enable (64) = 1`; and
8. on any mismatch, communication loss, hardware-error bit, overcurrent, overtemperature, over/undervoltage, missed deadline, or authority loss, reject torque enable, invalidate the target, and latch the defined fault response.

Changing operating mode resets Goal Current to Current Limit and resets Profile Velocity and Profile Acceleration. Therefore a mode change invalidates the prior configuration evidence and requires the complete torque-off write/readback sequence again. EEPROM-area writes are prohibited while torque is enabled.

## External measurement and acceptance route

The first characterization is a guarded fixture test with one actuator branch at a time. It is not an assembled-robot motion test. Instrumentation and bandwidth remain subject to the qualified test-plan review, but shall include a calibrated external branch current probe or shunt, branch voltage at the actuator, connector-contact temperature, actuator temperature, synchronized register telemetry, commanded position/current, load/torque, ambient temperature, and raw oscilloscope capture sufficient to resolve startup and reversal transients.

Each J1/J2 branch is exercised at candidate raw limits 200, 400, 600, and 800 through: torque-off idle, enabled hold at several loads, slow bidirectional motion, released maximum acceleration/deceleration, repeated duty cycle, restrained limit approach, communications loss, protective power interruption, and regeneration/reversal cases. Direct uncontrolled shorting and deliberate prolonged stall are prohibited.

Release requires all of the following:

- the received actuator, cable, housing, contacts, crimps, and conductor construction are identified and accepted;
- the external branch-current ceiling is selected by qualified electrical review and is no greater than the rating of the weakest connector/conductor/terminal after all application derating and measurement uncertainty;
- every measured instantaneous and duty-cycle current case remains below that released ceiling;
- voltage drop and connector/conductor temperature rise remain within signed limits for the released ambient, bundling, cable length, and duty cycle;
- measured torque/force is sufficient for the released load cases without using a stall endpoint as continuous capability;
- current limiting, branch protection, source limiting, regeneration behavior, and contactor interruption are coordinated; and
- fault injection proves that configuration mismatch or loss cannot enable or resume motion.

If any branch exceeds the released envelope, the permitted corrective paths are: reduce the raw current limit and revalidate; reduce load/inertia/acceleration; add counterbalance or mechanical advantage; or redesign the power/current-limiting architecture using selected, reviewed hardware. Raising a fuse value is not a corrective path.

## Remaining unresolved evidence

- received model numbers, firmware versions, IDs, exact factory cable and contact construction;
- external branch-current ceiling and measurement uncertainty/bandwidth;
- cable lengths, ambient, bundling, duty cycle, voltage-drop and temperature-rise limits;
- actual torque/current/temperature curves and gripper force;
- current-limit tolerance, transient response, regeneration and supply-current relationship;
- profile velocity/acceleration and joint start tolerances;
- source fault-current/current-limit behavior, fuse ratings, clearing curves and conductor/terminal selections;
- compiled transport, timing, HIL and fault-injection evidence; and
- qualified electrical, controls, mechanical and functional-safety review.

No actuator may be connected or energized from this candidate alone.

