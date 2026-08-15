# R223 validation record

**PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION**

Date: 2026-08-11

Artifacts: `HR-V0-PANEL-NODE-PLACEMENT-P0.1`; `HR-V0-CONFIG-REC-P0.4`

## Digital checks

- 33 backplate layout records including `DR5`, `WD4` and five topology nodes;
- five node envelopes inside the 533.4 x 685.8 mm planning boundary with no mutual overlap;
- 55 route-status records matching the R222 conductor IDs exactly;
- 37 planning-envelope distance screens, all prohibited as cut lengths;
- rail residual 86.2 mm before kerf and duct residual 20.8 mm before kerf;
- 95 covered BOM groups with `BOM-092/093/094` held and `BOM-095` selection-required;
- P1.15 retained as current and P1.18 retained as unaccepted;
- twelve placement holds and 26 integrated configuration holds open;
- no released hole, cut, wire, physical result or work authority.

## Validation results

- dedicated panel-placement checker: PASS;
- dedicated configuration P0.4 checker: PASS;
- BOM closure checker: PASS;
- pre-manifest full standard-check sweep: 163 / 166 PASS; the two live-BOM compatibility assertions were then corrected and passed independently, leaving only the expected unstaged-manifest failure before final synchronization;
- native KiCad checker sweep using KiCad 10 Python: 18 / 18 PASS;
- supervisor firmware tests: 67 / 67 PASS;
- watchdog firmware tests: 11 / 11 PASS;
- responsive browser inspection: PASS at 1440 x 900 desktop and 390 x 844 requested mobile viewport (375 CSS-pixel content width); no body-level horizontal overflow, minimum computed text size 14 px, and the 820 px conductor table is contained in an explicit horizontal-scroll region;
- final standard-check sweep: 166 / 166 PASS;
- final release-manifest check: PASS with 4,273 package files; the check correctly retains `EG-002` as partial until merge and formal acceptance.

These results prove deterministic catalog-envelope arithmetic and configuration consistency only. They do not prove received fit, access, fill, separation, thermal performance, protection coordination, functional safety or permission to perform physical work.
