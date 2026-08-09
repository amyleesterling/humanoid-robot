# Sol R12 status after R158

> **PRELIMINARY - NOT APPROVED FOR FABRICATION, ASSEMBLY, CONNECTION, MOTION, OR ENERGIZATION**

R158 is a project-owned correction prompted while responding to Sol's buildability verdict. It is not a new Sol review and does not change the original `18 BLOCKER / 30 MAJOR / 8 MINOR` totals.

The pass found that the R156 P0.1 RPW0010A footprint was materially inconsistent with TI drawing `4225183/A`. P0.1 is now explicitly superseded/prohibited for supplier use. The separate P0.2 candidate corrects eight drawing-parity defects and passes native KiCad ERC/DRC plus an exact-primitive checker.

This closes only the known internal footprint-transcription defect. Independent footprint review, selected assembler/stencil DFM, first-article AOI/X-ray, physical electrical/thermal tests and all fifteen other carrier holds remain open. The circuit is still an evaluation vehicle with unresolved reverse current, regeneration, protection coordination and application suitability. Sol's fabrication, physical-evidence, qualified-review, functional-safety and energization blockers remain open.
