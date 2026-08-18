# HR-30 MuJoCo dynamics validation P0.1

**PRELIMINARY - IDEAL-FIXTURE SIMULATION ONLY - NOT APPROVED FOR CONNECTION, POWERED TESTING, MOTION, WALKING, OR ENERGIZATION**

MuJoCo 3.10.0 compiles the corrected 9.831 kg active tether-first model with 32 generalized positions, 31 velocities, 25 torque/force inputs, 35 named interface exclusions, 12 walking keyframes and one numerical six-degree-of-freedom trajectory fixture. Both 10.72 s sequences are integrated at 2 ms with torque-limited numerical tracking control.

The ideal fixture is deliberately conspicuous: it can apply arbitrary load to keep the pelvis on its prescribed path. This package therefore validates model integration, positive mass/inertia, declared foot/floor contact topology, bounded numerical tracking and explicit failure metrics. It does **not** validate free balance, a physical tether, continuous actuator capacity, electrical current, thermal behavior, firmware, stopping, recovery, safety or walking.
