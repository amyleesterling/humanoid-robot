# R134 mechanical DFM-data validation record

> **PRELIMINARY - NOT APPROVED FOR QUOTATION, FABRICATION, ASSEMBLY, MOTION, OR ENERGIZATION.**

Date: 2026-08-09

Configuration: `HR-V0-MECH-DFM-DATA-P0.1`

Controlled architecture: `HR-V0-ARM-ARCH-P0.7`

## Result

- Generator completed: `tools/generate_hr_v0_mechanical_dfm_data.py`.
- Package checker passed: five parts, fifteen hashed geometry files, twenty-six source controls, thirty unexecuted first-article operations, twelve unsent DFM questions and fifteen open holds.
- Every provider/contact/upload/quotation/purchase/first-article/fabrication/assembly/motion/energization flag is false.
- The X430 comparison is recorded as available through nonselected P1.1; P0.7 remains controlled.
- Repository checker suite: **86/86 checkers passed**; zero checker failures.
- Through-E2 energization readiness command exited nonzero as required for an unreleased configuration: **0 closed, 21 partial, 0 open** among the 21 applicable gates. The package is **NOT READY through E2**.
- Interactive-guide QA passed at the default desktop viewport and a 390 x 844 mobile override: 16 px body, 14 px helper and 13 px badge text; no horizontal overflow; five part cards; search reduced the view to the intended C06 card and reset to all five; all eleven drawing/data links returned HTTP 200; no console errors or warnings.
- Release-candidate manifest regenerated with **1,820 package files**; manifest checker passed against the staged index before commit.

Automated checks prove only file identity, register completeness and fail-closed status. No provider accepted the definition and no physical result or qualified release exists.
