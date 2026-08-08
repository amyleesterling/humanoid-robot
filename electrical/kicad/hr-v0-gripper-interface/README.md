# HR-V0 gripper ordinary-control candidate HR-V0-GRIP-ELEC-P0.1

**PRELIMINARY - ORDINARY CONTROL ONLY - NOT APPROVED FOR FABRICATION OR ENERGIZATION**

This native KiCad project encodes a proposed post-K1/K2 24 V branch feeding a held fuse, Pololu D24V22F6 6 V regulator candidate, Micro Maestro 6 ordinary controller candidate and Pololu item 3551 feedback-servo gripper candidate. Component terminals are logical functional identifiers, not physical connector pin numbers or pad positions.

The Maestro receives logic power/control over Raspberry Pi USB. Its servo rail receives the separate regulated 6 V branch. CH0 is PWM, CH1 is feedback and CH2 is regulator power-good through a held 10 kOhm pull-up. The D24V22F6 EN terminal has no external connection.

Required fail-passive configuration is not released: empty internal script, run-on-startup disabled, CH0 startup/error Off, CH1/CH2 inputs, and a nonzero serial timeout accepted against the stopping-time budget. E-stop release/reset cannot itself issue a PWM command; actuator power may return only to an Off output until RESET + ARM validation and a deliberate fresh command. All of this remains ordinary control with zero safety credit.

FGRIP1 value/MPN, cable, connectors, carrier, capacitance, thermal/noise/EMC, settings, received mapping and HIL/fault evidence are SELECTION REQUIRED. ERC validates encoded connectivity only. No procurement, PCB/harness fabrication, connection or energization is authorized.
