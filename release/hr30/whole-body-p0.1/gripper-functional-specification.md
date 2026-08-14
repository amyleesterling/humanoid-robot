# HR-30 two-hand gripper functional specification P0.1

**PRELIMINARY - CONFIGURATION AND PACKAGING CAD ONLY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, POWERED TESTING, MOTION, OR ENERGIZATION**

Each wrist terminates in a visible, one-DOF, symmetric two-finger gripper: a 50 x 58 x 36 mm palm, two 18 x 44 x 46 mm broad fingers, and two replaceable 16 x 48 x 8 mm compliant-pad lands. The commanded closure axis is robot X. The palm packages one transversely mounted XC330-class compact actuator and a visible symmetric-coupler candidate; the final linkage and compliance element remain selection required.

The required behaviors are **grasp**, **hold**, **present**, and **release** a lightweight foam block. P0.1 provisional limits are a 26 mm coupled stroke, 0.25 speed scale, 20 N total normal-force ceiling, 0.5 kg object-mass ceiling, and mandatory current/force/position disagreement shutdown. These are development limits, not validated capability. Narrow scissor points, trapping gaps below the guarded minimum, self-locking closure without a manual release, and any cloud-originated raw position/current command are rejected.

Closure requires dimensioned linkage CAD, output-force/current calibration, compliant pad force-stroke and wear evidence, breakaway/manual-release test, object-presence sensing, pinch probe tests, holding-power-loss behavior, and supervised grasp/present/release trials.
