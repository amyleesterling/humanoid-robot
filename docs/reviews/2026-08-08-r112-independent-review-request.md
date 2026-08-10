# R112 independent engineering review request

Status: **PRELIMINARY - NOT AN APPROVAL REQUEST - NOT RELEASED FOR PROCUREMENT, FABRICATION, CONNECTION, MOTION, OR ENERGIZATION**

Please review the R112 direct-gripper adapter and protected ordinary-control interface for accuracy, completeness and fail-closed configuration management.

## Mechanical review

- Reproduce the Pololu item 3551 STEP transform and the two `diameter 4.2 mm` manufacturer axes.
- Challenge the 6061 clevis topology, `0.300 mm` nominal cheek clearance, `0.500 mm` rear gap, two M5 beam axes and two transverse M4 axes.
- Recalculate the `9,366.558784 mm3` volume, `25.289709 g` calculated mass and incomplete `117.619291 g` remaining headroom.
- Independently review the 1x/10x gravity screens; identify missing static, shock, fatigue, misuse and proof cases.
- Do not accept the POM ears without material/strength or physical proof evidence. Challenge the exact fastener, tolerance, guard, cable, DFM, FAI and received-metrology holds.

## Electrical/control review

- Open both native KiCad sheets and reproduce ERC 0/0 and the netlist.
- Confirm the gripper branch is downstream of both actuator contactors and that no fuse value, connector, conductor or pad order is inferred.
- Review D24V22F6 input/output, EN-unconnected and open-drain PG treatment against current official Pololu documentation.
- Review Micro Maestro USB/servo-power separation, CH0/CH1/CH2 allocation, empty-script/no-run-on-startup requirement, startup/error Off behavior and nonzero serial-timeout hold.
- Challenge the claim that E-stop release/manual reset cannot itself issue PWM. Require executed USB-disconnect, brownout, power-restoration and HIL/fault evidence.
- Confirm zero functional-safety credit and identify any additional safety-requirements, PLr/SIL, common-cause or stopping-time consequences.

## Required output

Return BLOCKER / MAJOR / MINOR findings with exact artifact, reference, logical terminal or net; primary-source citation and document revision/date; proposed correction; evidence needed to close; and an explicit statement of what remains unverified. Do not approve fabrication or energization.
