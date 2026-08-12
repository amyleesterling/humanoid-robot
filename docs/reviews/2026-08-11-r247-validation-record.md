# R247 validation record

> **PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION**

R247 products: `HR-V0-MECH-SHOP-RFQ-ASSY-P0.1` and `HR-V0-CONFIG-REC-P0.11`.

## Deterministic result

The dedicated checker proves that five successor shop drawings preserve the nominal geometry fingerprints of their P0.1 predecessors and continue to bind the exact five STEP and five DXF hashes in `HR-V0-MECH-BOM-BIND-P0.3`. It verifies the current integrated architecture identifier, complete warning, P0.2 drawing/title controls, separate source-binding and architecture fields, explicit formal-datum/GD&T selection hold, false fabrication authority and unexecuted physical/qualified evidence on every drawing.

It also checks the 15-artifact unsent RFQ payload, fourteen unanswered provider questions, 21 unexecuted zero-energy assembly steps, nine unexecuted joint-verification rows, twelve unresolved tool/consumable selections, eight-step nonconformance workflow, twelve open holds and ten open package acceptances. The P0.11 reconciliation retains 98 BOM groups, 31 current records, 45 holds and 65 unexecuted acceptance rows. P1.15 remains current and P1.21 remains unaccepted.

## Executed results

- Dedicated R247 checker: **PASS**.
- Standard repository checker sweep: **190/190 PASS**.
- Native KiCad 10.0 checker sweep: **18/18 PASS**.
- Global CAD validation: **PASS**, with 595 hash-controlled generated artifacts after R247 integration.
- Release-candidate manifest: **5,280 package files before adding this validation record; the final manifest was regenerated afterward**.
- Desktop browser QA at 1280 x 720: the mechanical guide and P0.11 configuration guide load with the exact warning visible, 16 px body text, 14 px minimum technical text and zero page-level horizontal overflow. Wide tables remain in local scrolling regions. The mechanical guide exposes five drawing links, thirteen downloadable datasets, thirteen tables and 126 body rows. The configuration guide exposes five downloadable datasets, five tables and 170 body rows.
- Five-drawing browser inspection: all five SVGs display the warning, current architecture, open formal-datum/GD&T state, false fabrication authority and a 14 px minimum text size. No text element extends outside its SVG drawing boundary. The 1600 px technical drawing is intentionally horizontally scrollable at a 1280 px viewport rather than being shrunk below the legibility floor.
- Narrow/mobile browser execution: **NOT COMPLETED**. The guide uses a 16 px body floor, 14 px table text and local table overflow; this static responsive behavior is not recorded as an executed mobile visual pass.

## Defects found and corrected during validation

The first full repository sweep failed 1/190 because `cad/hr-v0/generated/SOURCE-MANIFEST.csv` did not yet enumerate the new drawing package. The R247 generator now regenerates that global hash manifest, and the corrected sweep passes 190/190.

The first browser pass found overlapping long identifiers in the three-column shop title block. The title block was reflowed into bounded rows with source binding and architecture on separate lines. Left and right desktop views were re-inspected; the corrected fields are legible and nonoverlapping. The dedicated checker now requires the split controlled fields and the explicit unexecuted physical-evidence state.

These checks establish source/configuration parity, nominal-geometry continuity, repository integrity and desktop legibility only. They do not establish manufacturability, formal GD&T adequacy, provider capability, received material, dimensional conformance, joint integrity, structural capacity, assembled fit, hard-stop behavior, mass/inertia, functional safety or authority to perform physical work.
