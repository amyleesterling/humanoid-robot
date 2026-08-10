# R137 conventional drawing validation record

> **PRELIMINARY - NOT APPROVED FOR QUOTATION, FABRICATION, ASSEMBLY, MOTION, OR ENERGIZATION.**

Date: 2026-08-09

Configuration: `HR-V0-MECH-DWG-P0.1`

Nonselected candidate: `HR-V0-ARM-ARCH-P0.8-DWG-CANDIDATE`

Controlled architecture: `HR-V0-ARM-ARCH-P0.7`

## Result

- Generated five conventional SVG drawings and five finished-profile/feature DXFs.
- Hash-bound each drawing/DXF pair to one STEP identity: R136 P0.8 candidate STEP for C01/C04/C06/C07 and unchanged P0.7 STEP for C05.
- Independently re-imported each STEP as one solid and each DXF with `ezdxf`.
- STEP/DXF finished-profile bounding extents match at zero reported delta for all five parts.
- C01/C04/C05 contain four finished-profile LINE entities each.
- C06/C07 contain twelve finished-profile LINE plus twelve finished-profile ARC entities each; their R2 contours are no longer represented by pre-fillet construction lines.
- All 26 R134 source controls map to explicit drawing content; schedule-bound control count is zero.
- Five ICF-01 inspection-coordinate rows define +Y-face constraint plus rigid four-hole X/Z registration while explicitly withholding formal ASME Y14.5 datum status.
- All 30 first-article operations are bound to exact drawing/DXF/STEP hashes and remain `UNEXECUTED / NOT REVIEWED / FALSE` for next-work authority.
- Dedicated generator/checker passed; global generated-CAD manifest and CAD checker passed with 438 hashed generated artifacts.
- Repository domain checker suite: **88/88 passed** with the three PCB-native checks run under KiCad 10.0.5 bundled Python; zero failures.
- Through-E2 readiness check exited **2** as required: **0 closed, 21 partial, 0 open** among the 21 applicable gates. The package is **NOT READY through E2**.
- Visual QA of all five 1600-pixel-wide drawing renders found readable text, complete borders/tables, no clipped control content and no profile/title overlap after correction. Minimum drawing text is 14 px; ordinary drawing text is 16 px.
- The interactive guide is statically link-checked by the package checker. Live local browser QA is not claimed because the in-app browser blocks `file://` navigation.

- Release-candidate manifest regenerated from the staged index with **1,872 package files**; manifest validation passed.

Passing file checks does not establish supplier capability, physical fit, strength, safety or permission to work.
