# R241 validation record

> **PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION**

Date: 2026-08-11

Packages: `HR-V0-P121-SEGREGATION-HW-P0.1`; `HR-V0-CONFIG-REC-P0.5`

## Source and generated-package checks

- Current Phoenix Contact US pages for items 3240187 and 3240189 rechecked on 2026-08-11.
- Dedicated R241 generator/checker: PASS.
- 3240187 catalog envelope: 25 x 25 x 2000 mm; 327 mm2 usage cross-section; ten-cable catalog example at 60 percent fill.
- WD5 geometry: x=54.0, y=10.0, length=369.8 mm, height=25.0 mm; nominal 10 mm to DR1 and 20 mm to device region.
- DUCT-A residual: 20.8 mm before kerf, rejected for WD5.
- DUCT-B residual: 1630.2 mm before kerf, planning arithmetic only.
- Seven logical conductor allocations; exact conductor and application fill remain unresolved.
- Nine holds open; eight inspection rows blank and not executed.
- BOM closure: 96 groups; BOM-096 exact-candidate hold.
- P1.15 remains current; P1.21 remains unaccepted.
- Pre-manifest standard repository checker sweep: 183/184 PASS; the only expected failure was the release-manifest rejection of newly added untracked R241 files.
- Native KiCad `pcbnew` checker sweep: 18/18 PASS; R241 changes no ECAD or PCB source.
- Browser QA at 1280 x 720: body/button/minimum rendered text 16 px; seven table rows; SVG loaded; no page-level horizontal overflow; zoom increased the drawing from 1163 px to 1453.75 px and reset returned it to 1163 px.
- Browser visual correction: the first pass exposed WD1/WD2 label collisions; labels were moved outside the narrow duct envelopes with leader lines and the corrected header and diagram were re-inspected without observed clipping or label collision.
- Staged release manifest: 4,932 package files.
- Final staged standard repository checker sweep: 184/184 PASS.

## Completion boundary

Repository and browser checks do not establish received fit, cut quality, installed separation, fill, thermal behavior, fault containment, functional safety or authority. No physical work was performed.
