# HR-30 standing and walking-development architecture P0.1

**PRELIMINARY - CONFIGURATION AND PACKAGING CAD ONLY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, POWERED TESTING, MOTION, OR ENERGIZATION**

The whole body has six commanded axes per leg: hip yaw/roll/pitch, knee pitch, and ankle pitch/roll. Pitch joints reserve 1.5:1 belt reductions, dual-supported outputs and output encoders; hip roll reserves a higher-reduction path and remains blocked from direct-drive release. Each foot is 90 x 145 mm with four-corner force sensing and a replaceable compliant sole. The reconciled planning dynamics mass is 16.675 kg with neutral COM Z=0.323 m; these are candidate-volume and allocation values, not measured properties, and major equipment mass remains open.

Control layers are: embedded actuator current/velocity loops; a deterministic local motion controller for joint interpolation, state estimation, support-polygon checks and limits; a separately powered watchdog/permit path with zero safety credit until validated; and a Raspberry Pi/OpenAI conversational layer that can request only named behaviors. Loss or staleness of the conversational layer never becomes a motion request.

Development sequence:

1. **S0 — unpowered/suspended:** verify axes, hard stops, cable sweep, mass, COM, encoder sign and restraint clearances.
2. **S1 — individually powered/suspended:** one joint at a time under current and travel limits; characterize torque, decay, regeneration and thermal behavior.
3. **S2 — restrained double support:** feet on force plates, overhead restraint carrying no nominal weight; establish stand preparation and power-loss capture.
4. **S3 — weight transfer:** slow lateral/fore-aft COM shifts within a measured support margin; no foot lift.
5. **S4 — tethered step initiation:** unload one foot, lift <=10 mm, replace it at the same location, then arrest and inspect.
6. **S5 — tethered capture steps:** predeclared <=50 mm steps on a level guarded surface with stopping and recovery envelopes.
7. **S6 — repeated tethered walking:** only after thermal, power, bus-latency, state-estimation and restraint results close.
8. **S7 — untethered walking:** future program gate; prohibited by P0.1.

The fall-restraint architecture is a rated overhead gantry, swivel, energy-limiting element and torso/pelvis harness attached to a dedicated structural interface. It must prevent head/floor contact throughout the development envelope without becoming a lifting command or destabilizing tether. Exact working-load limit, dynamic arrest load, attachment geometry and qualified inspection remain selection required.
