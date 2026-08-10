# R76 validation record — guard retention and mass branch correction

**PRELIMINARY—NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, MOTION, CONNECTION, OR ENERGIZATION.**

Date: 2026-08-07

Round: R76

Candidate: `HR-V0-GUARD-RET-P0.1`

## Scope

R76 responds to the mass and panel-retention holds exposed by R75. It does not select a thinner guard panel or claim impact containment.

## Corrections

- Excludes the drill-through `20-2496` route from the current retention baseline because Plaskolite prefers avoiding through-fastening glazing and the project has no thermal/retention proof.
- Adds exact 80/20 `12004` only as a continuous-gasket candidate for a nominal 3 mm outer-panel evaluation branch.
- Retains the nominal 6 mm receiver in the preferred evaluation branch.
- Adds four mass branches, 32 edge pieces, an eleven-stock-length packing screen, three retention decisions, three thermal screens and eight open controls.
- Corrects P0.3 panel dimensions to enclosure envelopes rather than released cut/hole dimensions.
- Changes BOM-078 to a nonselected retention-study group without changing the 78-group closure count.

## Validation boundary

The preferred evaluation branch reduces the known subtotal from 30.799798 kg to 19.415878 kg, a planning reduction of 11.383920 kg. Manufacturer typical density is not released evidence, and gasket/hardware/anchor mass remains excluded.

The generator/checker require exact artifact membership, four mass branches, 32 gasket edge pieces totaling 20,980 mm, eleven nominal 2 m stock lengths, 1,020 mm offcut before kerf, three retention decisions, eight non-closed controls and five dated primary-source records.

Full repository, manifest and clean-clone results are recorded against the final commit before push. No physical gate is closed.

## Validation results

- The P0.3 guard generator/checker passed after converting all thirteen sheet rows from `finished_*` to `envelope_*` fields and synchronizing the R76 retainer exclusion.
- The R76 generator/checker passed at four mass branches, 32 gasket pieces, eleven stock lengths, three decisions, three thermal screens, eight non-closed controls and five dated primary-source rows.
- The BOM generator/checker passed at 78 system groups, 17 evaluation candidates, 24 exact-candidate holds and 29 selection-required groups.
- All 28 repository `tools/check_*.py` validators passed. The DXL-star and watchdog-PCB checks used KiCad 10.0 Python; the other checks used the controlled CAD Python environment.
- Traceability passed at 81 requirements, 40 risks and 104 procedures.
- The gate checker remained fail-closed at 0 closed, 22 partial and 8 open.
- The staged release manifest contains 825 package files and passed exact membership/hash validation. Clean-clone reproduction is recorded after the final commit.

## Interactive-guide QA

The guide uses 16 px body/table/code text and larger headings. A 1440 × 1000 desktop render was visually checked. The in-app browser then applied an exact 390 × 844 viewport: `innerWidth` was 390 px, document `scrollWidth` was 375 px, body text was 16 px and the summary cards reflowed to one 339 px column. The warning, title and cards were readable without horizontal overflow. The temporary viewport was reset and the QA tab/server were closed.

A passing checker or responsive render establishes internal consistency and legibility only. It does not establish containment, structural capacity, functional safety or permission to build or energize.
