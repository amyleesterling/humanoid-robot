# R135 mechanical parity validation record

> **PRELIMINARY - NOT APPROVED FOR QUOTATION, FABRICATION, ASSEMBLY, MOTION, OR ENERGIZATION.**

Date: 2026-08-09

Configuration: `HR-V0-MECH-PARITY-P0.1`

Controlled architecture: `HR-V0-ARM-ARCH-P0.7`

## Result

- Independent DXF parser and CadQuery STEP inspection completed for C01/C04/C05/C06/C07.
- Dedicated checker passed: five profile-extents matches, thirty exact nominal hole matches, eight controlled-upper-limit countersink matches, twenty-six drawing-control bindings, six schedule-bound controls and four open findings.
- All four affected STEP countersink openings are Ø11.40 mm while DXF/drawing nominal is Ø11.30 +0.10/-0.00 mm; this is retained as an open MAJOR semantic finding.
- C07 STEP face recess reproduced at 1.000 mm.
- Repository checker suite: **87/87 checkers passed**; zero checker failures.
- Through-E2 energization readiness command exited nonzero as required: **0 closed, 21 partial, 0 open** among the 21 applicable gates. The package is **NOT READY through E2**.
- Interactive-guide QA passed at the default desktop viewport and a 390 x 844 mobile override: five cards and five DXF maps; 16 px body, 14 px helper and 13 px badge text; no horizontal overflow; search isolated C07 and reset to all five; all ten drawing/data links returned HTTP 200; no console errors or warnings.
- Release-candidate manifest regenerated with **1,832 package files**; manifest checker passed against the staged index before commit.

Passing parity proves only the stated bounded nominal relationships. It does not prove manufacturing capability, tolerance, fit, material, strength, stopping, safety or release.
