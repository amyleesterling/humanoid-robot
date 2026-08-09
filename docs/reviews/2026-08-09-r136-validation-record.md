# R136 countersink MBD validation record

> **PRELIMINARY - NOT APPROVED FOR QUOTATION, FABRICATION, ASSEMBLY, MOTION, OR ENERGIZATION.**

Date: 2026-08-09

Configuration: `HR-V0-CSK-MBD-P0.1`

Controlled source: `HR-V0-ARM-ARCH-P0.7`

Nonselected candidate: `HR-V0-ARM-ARCH-P0.8-CSK-MBD-CANDIDATE`

## Result

- Preserved all P0.7 STEP files and hashes without modification.
- Generated four separate P0.8 candidate STEP parts for C01/C04/C06/C07.
- Corrected eight candidate countersinks from the P0.7 solid's Ø11.40 x 3.10 mm / 87.159469° derived geometry to the drawing nominal Ø11.30 x 2.90 mm / 90.000000° geometry.
- Re-imported every candidate STEP as one solid and confirmed all four source/candidate bounding envelopes are identical.
- Calculated 0.195715 g total added material across the four candidates at the project screening density of 2.70 g/cm³.
- Retained Ø11.40 maximum-diameter and 3.10 mm maximum-depth values only as separate conservative calculation/inspection screens.
- Dedicated generator/checker passed: four candidate parts, eight countersinks, five unresolved decisions and three open findings.
- Repository domain checker suite: **87/87 passed** with the three PCB-native checks run under KiCad 10.0.5 bundled Python; zero failures.
- Through-E2 readiness check exited **2** as required: **0 closed, 21 partial, 0 open** among the 21 applicable gates. The package is **NOT READY through E2**.
- Candidate selection, supplier contact, quotation, fabrication, assembly, motion and energization remain false.
- Static guide checks confirm 16 px body text, 14 px helper text, 13 px badges, the four candidate cards, search handler, evidence links and warning text. Live local desktop/mobile browser QA was not executed because the in-app browser blocks `file://` navigation by policy; no visual or interactive browser-pass claim is made for R136.

- Release-candidate manifest regenerated from the staged index with **1,848 package files**; manifest validation passed.

Clean software checks will not establish physical fit, strength, safety or permission to work.
