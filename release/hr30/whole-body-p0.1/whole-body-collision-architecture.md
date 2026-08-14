# HR-30 whole-body self-collision architecture P0.1

**PRELIMINARY - CONFIGURATION AND PACKAGING CAD ONLY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, POWERED TESTING, MOTION, OR ENERGIZATION**

This package evaluates every nonexcluded pair of posed URDF link envelopes in all 8 S2–S5 configurations. Direct joint interfaces and explicitly named nested shoulder, hip and ankle structural interfaces are excluded in `collision-exclusion-register.csv`; no broad same-limb exemption is used. All other pairs are evaluated with OpenCascade B-Rep distance. Pairs at zero distance are evaluated for common volume.

The planning preference is **5.0 mm** between nonadjacent rigid envelopes. A value below that threshold is not automatically a collision, but it remains a packaging hold for covers, cable sweep, tolerance and tracking error. Zero common volume is required for every checked pair.

| Pose | Checked pairs | Interferences | Minimum clearance | Closest checked pair |
|---|---:|---:|---:|---|
| Neutral double support | 290 | 0 | 7.82 mm | `R_upper_arm::base_link` |
| Crouched double support | 290 | 0 | 7.82 mm | `R_upper_arm::base_link` |
| Left weight transfer | 290 | 0 | 24.85 mm | `L_forearm::L_gripper` |
| Right foot lift | 290 | 0 | 24.85 mm | `L_forearm::L_gripper` |
| Right capture-step candidate | 290 | 0 | 7.21 mm | `R_upper_arm::base_link` |
| Right weight transfer | 290 | 0 | 24.85 mm | `L_forearm::L_gripper` |
| Left foot lift | 290 | 0 | 24.85 mm | `L_forearm::L_gripper` |
| Left capture-step candidate | 290 | 0 | 7.19 mm | `R_upper_arm::base_link` |

This is a nominal rigid-envelope result. It does not cover manufacturing tolerance, cover deflection, belt/cable sweep, connector backshells, fastener protrusion, encoder wiring, tracking error, joint compliance, impacts, floor variation, fall restraint, or physical correlation. It grants no motion or safety credit.
