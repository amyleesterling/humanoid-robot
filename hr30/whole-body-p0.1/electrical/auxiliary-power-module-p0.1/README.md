# HR-30 auxiliary-power module P0.1

**PRELIMINARY - UNBUILT AUXILIARY-POWER MODULE CANDIDATE - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, WALKING OR ENERGIZATION**

This package replaces the former undefined pelvis converter with a dimensioned **120 x 58 mm three-rail carrier candidate**. Three current RECOM `REC30E-2405SZ` modules separately supply compute, face/HMI and deterministic-control positive rails. Their isolated output returns meet only at the explicit `AUX_0V_STAR`; the single possible PE bond remains unselected.

The HMI rail has **zero margin** against the current coarse 30 W peak budget, so the architecture is not released. Every fuse, reverse-polarity/inrush block, trim network, harness, PE bond, thermal result and physical test remains open. Native KiCad, STEP, GLB, contact maps and test registers are included.
