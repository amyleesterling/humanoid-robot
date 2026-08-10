# R159 validation record

> **PRELIMINARY - NOT APPROVED FOR SUPPLIER UPLOAD, QUOTATION, PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, MOTION, OR ENERGIZATION**

- Carrier: `HR-V0-DXL-PROT-CARRIER-P0.3`
- Manufacturing inquiry: `HR-V0-DXL-PROT-DFM-P0.1`
- Date: 2026-08-09

## Verified corrections

- R158's exact RPW copper/mask/paste primitive geometry is retained.
- Native mask-dam rule is 0.100 mm instead of P0.2's under-enforcing 0.050 mm.
- Native minimum and default copper-clearance rules are both 0.100 mm.
- Three board-only global fiducials exist at the controlled coordinates with exact 1.0 mm copper / 2.0 mm mask geometry and are absent from BOM/position outputs.
- Canonical P0.2/P0.3 fingerprints match across tracks, vias, non-fiducial pads/nets, Edge.Cuts, zones, layer count and thickness.
- MacroFab capability evidence is recorded as a live, revisionless provider page accessed 2026-08-09; it is not represented as supplier acceptance.
- 24 capability rows, 24 unsent questions, 23 hash-bound proposed files and 18 blank first-article checks are synchronized.
- Every provider, upload, quotation, purchase, fabrication, assembly, connection, energization and safety-credit flag is false.

## Executed checks

- KiCad 10.0.5 ERC: 0 errors / 0 warnings across five sheets.
- KiCad 10.0.5 DRC: 0 violations / 0 unconnected pads / 0 footprint errors.
- Native R159 checker: PASS for geometry, board rules, fiducials, metrics, file hashes, source copies, denial state and non-closure of EG-003/004/014/015/024.
- Complete non-`pcbnew` repository sweep: 104/104 checkers passed.
- Native KiCad/PCB checker sweep: 10/10 passed under the KiCad 10.0 Python runtime.
- Staged release manifest: 2,472 controlled package files passed before commit.
- Desktop rendered-guide QA: PASS at 1280 px; no horizontal overflow, no broken images, 18 px body/warning text and 14 px metadata. The mobile stylesheet preserves a 16 px body floor and 14 px metadata; the active browser backend did not honor its temporary narrow-viewport override, so a 390 px rendered screenshot is not claimed.
- Physical articles: 0.
- Physical tests: 0.
- Provider responses: 0.
- Qualified approvals: 0.

Full repository regression and staged-manifest results are appended before commit. Clean ERC/DRC and provider-published capability do not establish build release or energization readiness.
