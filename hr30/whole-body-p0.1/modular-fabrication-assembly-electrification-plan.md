# HR-30 modular fabrication, assembly and staged-electrification plan P0.1

**PRELIMINARY - CONFIGURATION AND PACKAGING CAD ONLY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, POWERED TESTING, MOTION, OR ENERGIZATION**

The authoritative modules are: H01 head/screen/audio/vision; N01 two-axis neck; T01 torso/frame/compute; P01 pelvis/power/restraint; A01/A02 left/right arms; G01/G02 left/right grippers; L01/L02 left/right legs; F01/F02 left/right feet; C01 local controller; S01 independent safety enclosure; and HN01 segmented harness. Each has a released interface-control drawing, mass ceiling, connector boundary, datum set and revision before fabrication.

Fabrication route: machine the load-bearing joint side plates, shafts and bearing lands from released metal stock; print only removable shells, ducts, fixtures and non-credited covers from a selected process/material; buy exact bearings, reductions, actuators, fasteners and connectors; inspect received identities and material certificates; then perform first-article dimensional inspection. Library/makerspace CNC capability may support prototype plates only after DFM, fixturing, tool-access, tolerance and supervision review. Safety-credited or fall-load parts require a qualified supplier/reviewer disposition.

Assembly order: feet -> ankle modules -> shins -> knees -> thighs -> pelvis -> restraint interface -> torso -> neck/head -> arms -> grippers -> stationary harness -> moving-joint service loops -> covers. At every module boundary, complete fastener torque witness, free-motion/stop check, encoder sign/zero, continuity/isolation, pull/retention and mass record before adding the next module.

Electrification stages are deliberately separate:

1. **E0 unpowered:** dimensional/assembly inspection, bonding plan, continuity/isolation, connector keying, E-stop contact inspection and manual motion.
2. **E1 controls only:** current-limited auxiliary supply; no actuator rail connected; boot, logging, watchdog and all failure-state tests.
3. **E2 one actuator on a bench:** mechanical joint removed from the body or rigidly restrained; characterize current, torque proxy, thermal, comms and power removal.
4. **E3 one suspended limb:** branch protection and local stop limits; no ground contact.
5. **E4 suspended whole body:** all buses enumerated with outputs disabled, then one axis at a time under approved test authorization.
6. **E5 restrained standing:** overhead arrest and guarded zone, double support only.
7. **E6 walking development:** only the S2-S6 sequence in the walking architecture.

Every stage requires an explicit, signed test authorization tied to exact as-built hardware. P0.1 supplies architecture, not that authorization.
