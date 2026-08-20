# HR-30 auxiliary-power module P0.1

**PRELIMINARY - UNBUILT AUXILIARY-POWER MODULE CANDIDATE - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, WALKING OR ENERGIZATION**

This package replaces the former undefined pelvis converter with a dimensioned **150 x 58 mm three-rail carrier candidate**. Two current RECOM `REC30E-2405SZ` modules supply compute and deterministic control; one current TRACO POWER `TEN 40-1211E` supplies the face/HMI rail. Their isolated output returns meet only at the explicit `AUX_0V_STAR`; the single possible PE bond remains unselected.

The HMI rail now has **10 W coarse peak headroom** against the current 30 W planning envelope. That removes the zero-margin architecture defect but is not a load, transient, thermal, EMC or physical validation. Every fuse, reverse-polarity/inrush block, trim network, harness, PE bond and physical test remains open. Native KiCad, STEP, GLB, contact maps and test registers are included.
