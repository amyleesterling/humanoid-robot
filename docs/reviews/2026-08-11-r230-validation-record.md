# R230 validation record

> **PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION**

- Date: 2026-08-11
- Artifact: `HR-V0-P119-VISUAL-CORRECTION-P0.1`
- Native ECAD candidate: `V3-P1.19-VISUAL-CORRECTION-CANDIDATE`

## Configuration and parity results

- P1.15 remains the current electrical product. P1.18 and P1.19 remain unaccepted candidates.
- All 13 native KiCad sheets parse and export with KiCad 10.0.5.
- Native ERC result: **0 errors / 0 warnings**.
- P1.18-to-P1.19 parity is exact for 84 component blocks, 106 native nets, 82 BOM rows, 340 connector-schedule rows, 106 net-schedule rows, 301 wire-table rows and 63 unresolved-selection rows.
- Structural parsing of the native KiCad netlists confirms equal component reference/value/footprint records and equal net-node membership.
- The full warning remains on every native sheet and every review artifact.
- Seven disposition and physical-evidence holds remain open. All work-authority fields remain false.

## Visual correction results

- All 13 P1.19 native sheet exports were inspected at full-sheet scale.
- Dense sheets 01, 02, 03, 07 and 10 use A2 layouts; the remaining child sheets use A3 layouts.
- The P1.18 title-block overflow, clipped edge labels, dense symbol/label collisions and ambiguous crossing/spacing conditions recorded in the R230 sheet register are corrected in P1.19.
- The interactive comparison guide exposes every P1.18/P1.19 sheet pair, supports a sheet-addressable query string and keeps P1.19 visibly unaccepted.
- Desktop browser QA: **PASS**; readable text, responsive side-by-side comparison and no unintended page overflow.
- Mobile browser QA at 390 x 844: **PASS** after responsive reflow; no body-level horizontal scrollbar and no functional text below the repository legibility minimum.

## Repository and software validation

- Focused P1.19 checker: **PASS**.
- Native KiCad/pcbnew checker sweep: **18 / 18 PASS**.
- Standard repository checker sweep using the controlled CadQuery-capable interpreter: **173 / 173 PASS**.
- Supervisor firmware source tests: **67 / 67 PASS**.
- Watchdog reference-model and compiled-C differential tests: **11 / 11 PASS**.
- An initial standard-check attempt used an interpreter without CadQuery and reported environment failures; rerunning under the controlled repository interpreter produced the authoritative 173/173 result above.
- Final staged deterministic release manifest: **PASS with 4,509 controlled package files**.
- Independent electrical and functional-safety disposition: **OPEN**.

These checks establish source consistency, machine-readable parity, clean ERC connectivity/annotation output and corrected visual presentation. They do **not** establish installed conductor suitability, connector or protection selection, grounding effectiveness, contactor application suitability, physical fault response, stopping time/distance, performance level or permission to perform work.
