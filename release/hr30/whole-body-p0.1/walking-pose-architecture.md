# HR-30 articulated whole-body pose architecture P0.1

**PRELIMINARY - CONFIGURATION AND PACKAGING CAD ONLY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, POWERED TESTING, MOTION, OR ENERGIZATION**

This package converts the S2–S5 standing and walking-development prose into 10 complete rigid-link whole-body configurations. The generator reads the active tether-first 25-axis `hr30_tether.urdf` rather than the rejected onboard-envelope mass alias, applies explicit joint targets, shifts the floating base to keep the declared support foot or feet on Z=0, transforms every link inertial COM, constructs the convex support polygon and exports recognizable full-body CAD with head, screen face, arms, two-finger hands, legs, ankles and feet. Both legs have mirrored weight-transfer, lift and capture-step candidates.

The register is deliberately fail-closed: values are pose candidates, not executable commands. A positive projected-COM margin is only a quasistatic geometry screen. It does not include contact-force distribution, compliance, backlash, actuator limits, rate limits, zero-moment point, capture point, state-estimation error, floor variation, cable forces, fall-restraint forces or physical correlation.

The S4 lift targets are capped below 10 mm in the generated geometry. The S5 forward placements remain within the 50 mm development class. Exact metrics are machine-readable in `pose-support-metrics.csv`.
