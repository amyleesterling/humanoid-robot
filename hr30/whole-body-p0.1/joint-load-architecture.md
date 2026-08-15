# HR-30 whole-body joint-load architecture P0.1

**PRELIMINARY - CONFIGURATION AND PACKAGING CAD ONLY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, POWERED TESTING, MOTION, OR ENERGIZATION**

This artifact covers all **25 axes** in the current floating-base URDF. It provides a reproducible static architecture screen for deciding which actuator packages should remain in P0.1; it is not an actuator release or gait simulation.

For each non-yaw rotary axis, the generator sums the current descendant link masses using a posture-independent triangle-inequality radius bound. A 100 g object is added at each downstream hand. Leg support axes also receive a deliberately explicit single-support screen based on the full 11.936 kg planning model: 25 mm lateral COM offset, 35 mm fore-aft COM offset, or a 60 mm equivalent knee moment arm. The governing static value is multiplied by 1.50 only as an architecture endpoint screen.

The comparison column uses current official ROBOTIS **12 V stall torque**, transmission ratio and an 0.85 efficiency assumption for reduced axes. ROBOTIS explicitly warns that stall torque is momentary and differs from continuous and real-world output. Consequently no row claims continuous capability. Accepted trajectories, current limits, duty cycle, N-T curves, temperature, inertia, contact, stopping and physical correlation remain mandatory.

The two elbows and two shoulder-roll axes retain the 82 g XM430 candidate. Each wrist uses the 23 g XC330 candidate because its direct-drive published-stall endpoint remains more than four times the current factored static screen. Each ankle uses the 82 g XM430 with a 2.0:1 roll or 2.5:1 pitch reduction. The knee reduction is raised from 1.5:1 to 2.0:1. These are whole-body packaging candidates pending continuous-duty, belt, thermal, dynamic and physical testing.

0 axes have less than 1.50 ratio between the effective published stall endpoint and the factored development screen. They are explicitly marked narrow and may not be downsized. Yaw and gripper axes retain separate unresolved inertia/mechanism requirements rather than receiving invented torque values.

Primary manufacturer pages were accessed 2026-08-14 and expose no page revision/date. Exact values are recorded in `actuator-endpoint-source-register.csv`. The MISUMI 5GT/EV5GT catalogues identify the configured 16/20/30/40-tooth pulley candidates and 225/250/255 mm by 9 mm belt candidates used by the installed-drive package; capacity, hub/adapter design, tensioning and guarding remain selection required.
