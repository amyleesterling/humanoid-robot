# R240 validation record

> **PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION**

Date: 2026-08-11
Package: `HR-V0-P121-ROUTING-P0.1`

## Executed evidence

- Dedicated R240 generator/checker: PASS.
- P1.21 source binding: six exact wire-number/net rows checked.
- Route delta: 7/7 records generated; three stale P0.7 meanings explicitly corrected.
- Coordinate-bound routes: 9/9 within the 533.4 x 685.8 mm planning frame.
- Hot-versus-credited crossing screen: 14/14 pairs; zero nominal centerline crossings.
- Physical inspections: 0/8 executed; all evidence blank.
- Open holds: 9/9 OPEN.
- Pre-manifest standard repository checker sweep: 182/183 PASS; only the expected release-manifest rejection of the new untracked R240 files failed.
- Native KiCad `pcbnew` checker sweep: 18/18 PASS; R240 changes no ECAD or PCB source.
- Interactive guide browser QA at 1280 x 720: PASS. The SVG loaded, seven delta rows rendered, body-level horizontal overflow was absent, zoom/reset controls worked, body/buttons rendered at 16 CSS px and code at 14 CSS px. A visual pass corrected overlapping KWD labels and the top-corridor label before final validation.
- Final staged standard repository checker sweep: 183/183 PASS using the controlled Python/CadQuery environment.
- Deterministic release manifest: 4,877 package files; manifest checker PASS before commit.

## Boundary

The route screen is ideal planning geometry only. It is not a released wiring drawing, cut-length schedule, terminal layout, separation proof or first-fault/common-cause acceptance. P1.15 remains current, P1.21 remains unaccepted and no work authority exists.
