# HR-30 whole-body Safety Requirements Specification P0.1

**PRELIMINARY - SAFETY REQUIREMENTS CANDIDATE ONLY - NOT FUNCTIONALLY SAFETY VALIDATED - NOT APPROVED FOR CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION**

## Purpose and boundary

This candidate SRS covers the 762 mm, 25-axis HR-30 whole-body P0.1 through unpowered assembly and the E0-E7 first-energization ladder. Motion stages S1-S7 and public/child interaction are explicitly outside this release. The document provides reviewable requirements; it does not establish conformity, an achieved performance level, or permission to work on hardware.

## Intended use for this revision

- laboratory engineering prototype on a level, guarded site in Boston, Massachusetts;
- trained adults only inside the controlled test process;
- tether-first power architecture with the robot mechanically supported and restrained;
- E0-E7 power states only, with every motion request rejected;
- no lifting or carrying people, no public operation, and no child access;
- no onboard battery or charging during first energization.

## Normative-method candidate

ISO 12100:2010 is the risk-assessment framework candidate. ISO 13849-1:2023 is the SRP/CS design method candidate and does not itself choose the PLr for this robot. ISO 13849-2:2012 is the validation-method candidate. ISO 13850:2015 and IEC 60204-1:2016+AMD1:2021 inform the emergency-stop/electrical boundary. ISO 13482:2014 and its application/test reports are informative service-robot references; the standard is under revision and no conformity claim is made.

## Safety strategy

1. Eliminate motion from first energization: torque, bus transmit, precharge and action-ready outputs remain inactive.
2. Keep people out of the motion/fall envelope and support the complete robot mechanically.
3. Use a hardwired dual-channel emergency-stop and two monitored series interruption devices independently of the AI and standard motion controller.
4. Make reset restore eligibility only; require a fresh, bounded motion command in a later separately released state.
5. Treat the watchdog, actuator firmware, torque-disable commands and conversational layer as standard control with zero safety credit until separately validated.
6. Measure the complete stopping chain before allocating any motion envelope or safeguard distance.

## Candidate allocations

This package contains **24 open hazards** and **12 safety/control functions**. PLr d / Category 3 is a conservative project candidate for the credited E-stop, restart-inhibition, EDM and fail-safe control-power boundaries. It is not approved: MTTFd/B10d, DCavg, CCF, mission time, PFHd, systematic capability, exact category, and independent validation are blank.

## Restart invariant

E-stop release, manual reset, restored power, restored communications, watchdog recovery, or controller reboot shall never create a motion request. They may only restore eligibility. Any later motion requires a fresh request accepted by the deterministic local controller after a separately authorized motion-stage gate.

## Stopping requirement

The total stop time is `T_total = t_input + t_logic + t_output + t_contactor + t_bus + t_torque + t_mechanical`. Every term must be measured with a common time base on the received configuration. Angular and Cartesian overtravel must be computed from measured velocity histories and whole-body kinematics, including gravity, compliance, restraint and fall behavior. No single arbitrary multiplier or component response time may stand in for the system measurement.

## Acceptance boundary

All rows remain NOT VALIDATED. A qualified functional-safety reviewer, electrical reviewer, mechanical reviewer, controls/test lead and configuration owner must accept the same hash-bound as-built configuration and witnessed evidence. Until then, connection, powered testing, motion and energization remain prohibited.
