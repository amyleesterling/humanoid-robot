# HR-30 two-hand gripper functional specification P0.1

**PRELIMINARY - CONFIGURATION AND PACKAGING CAD ONLY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, POWERED TESTING, MOTION, OR ENERGIZATION**

Each wrist now terminates in a visible and mechanically defined one-DOF symmetric two-finger gripper. The editable candidate uses a 50 x 58 x 40 mm serviceable palm frame, two 4 mm guide rods, two broad sliding finger/carriers, paired module-0.5 rack candidates, a 20-tooth 10 mm pitch-diameter pinion candidate, two replaceable 3 x 30 x 30 mm compliant pads, hard open stops, manual-release access, and one transversely mounted SHA-bound XC330 packaging body.

The CAD-derived coupled stroke is 26 mm: each jaw moves 13 mm from CLOSED to OPEN. The resulting pad gap is 8 mm closed and 34 mm open. The required behaviors remain **grasp**, **hold**, **present**, and **release** a lightweight foam block. P0.1 retains a 20 N total normal-force ceiling, 0.5 kg object-mass ceiling, 0.25 speed scale, guarded closing, and mandatory current/force/position disagreement shutdown.

For the 5 mm pinion pitch radius, equal opposing rack forces give `total normal force = pinion torque / pitch radius`. A 20 N development ceiling therefore corresponds to 0.10 N·m at the pinion. The published 1.0 N·m XC330 12 V stall endpoint would imply 200 N in this ideal geometry and is not a permissible command, continuous rating, or capacity claim. A local deterministic controller must enforce a separately calibrated current/torque limit; the cloud conversational agent never commands raw position, current, or force.

Closure still requires final tooth geometry, rack/guide clearances, actuator horn and mount, material/process selection, compliant-pad force-stroke and wear evidence, force/current calibration, object-presence sensing, breakaway/manual-release test, pinch probes, holding-power-loss behavior, endurance, DFM, FAI, and supervised grasp/present/release trials.
