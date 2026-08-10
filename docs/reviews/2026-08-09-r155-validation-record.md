# R155 validation record

> **PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, MOTION, OR ENERGIZATION**

- Configuration: `HR-V0-DXL-PROT-EVAL-P0.1`
- Date: 2026-08-09

## Executed source checks

- Current official TI TPS25946 datasheet `SLVSGA8B`, revision B dated 2022-04-04, and the active exact `TPS259461LRPWR` orderable page.
- Current official Pololu item 3771 page, accessed 2026-08-09.
- MEAN WELL GST280A series specification dated 2025-03-28.
- Current official JST EH and VH records and ROBOTIS XM540 e-Manual, accessed 2026-08-09.

## Executed repository checks

- KiCad 10.0.5 parsed the root and four child sheets.
- Native ERC: 0 errors / 0 warnings.
- Native PDF and five SVG exports generated.
- Package checker: PASS for five sheets, 47 source BOM rows / 44 counted devices, 104 terminal rows, ten calculations, seven sources, fourteen blank tests, eighteen open holds and both manifests.
- Repository checker sweep before release-manifest freeze: 101 / 101 non-`pcbnew` checkers passed.
- Native KiCad/PCB checker sweep: 7 / 7 passed under the KiCad 10 Python runtime.
- CAD regression: PASS for 447 hashed generated artifacts and 17 vendor references.
- Firmware validation: 48 executable unit tests passed in the repository checker sweep.
- Interactive-guide live QA: PASS at a 1280 x 720 desktop viewport for readable page layout, four sheet controls, initial-sheet rendering and regeneration-clamp sheet switching. Responsive CSS was inspected, but no live narrow-viewport browser result is claimed in this record.
- Robot release baseline: unchanged at Electrical V3-P1.14.
- System BOM: neither evaluation device was inserted.
- Firmware external branch current limit: still `SELECTION REQUIRED`.
- Physical tests executed: 0.
- Qualified approvals: 0.
- Work authorizations: 0.

ERC and source checks do not establish PCB layout suitability, thermal capacity, pulse energy, protection coordination, harness suitability, physical fault response, functional safety or permission to perform work.

- Final staged release manifest: PASS for 2,221 package files.
- Complete final non-`pcbnew` repository sweep: 102 / 102 checkers passed against the staged candidate.
