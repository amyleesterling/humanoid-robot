# R153 validation record - DXL harness allocation

> **PRELIMINARY - NOT APPROVED FOR SUPPLIER UPLOAD, QUOTATION, PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, MOTION, OR ENERGIZATION**

Date: 2026-08-09  
Identifier: `HR-V0-DXL-HARNESS-ALLOC-P0.1`  
Round: R153

## Controlled result

- 86 system BOM groups: 17 evaluation candidates, 40 exact candidates on hold, three grouped-component holds, 19 selection-required groups, four exclusions and three integrated items.
- Three factory-included 180 mm JST-JST X3P branch cables are integrated as `BOM-086`; no separate purchase is released.
- Loose allocation is two EHR-3 housings and four SEH contacts for one custom controller cable only.
- U2D2 pin 1 GND maps to JC1.1; pin 3 DATA maps to JC1.3; cavity 2 is empty at both ends and JC1.2 remains no-net/no-copper.
- Six duplicate housings and eighteen duplicate contacts were removed.
- Eight manufacturer questions remain unsent, ten acceptance rows remain blank and fourteen residual holds remain open.

## Automated validation

- 100 standard repository checkers passed using the controlled HR-V0 CAD Python environment.
- 7 native KiCad checkers passed using KiCad 10.0 Python.
- The R153 checker verifies package membership, hashes, BOM quantities/classes, source records, controller pin mapping, native/system JC1.2 omission, blank forms, open holds and all false work-authority flags.
- The release-manifest checker is executed after the final staged manifest is generated and is recorded in the commit handoff.

## Web visual QA

The interactive guide was inspected at 1280 x 720 and 390 x 844. Both views retained 14 px minimum functional text, four status cards, fourteen visible holds and no page-level horizontal overflow. The harness table is readable at desktop width and intentionally gains local horizontal scrolling at 390 px. The sky-blue, dark-blue and gold presentation retained the preliminary warning and did not clip the controlled content.

## Disposition

The zero-check result validates internal structure and annotation only. It does not prove physical connector current capacity, conductor selection, crimp quality, cable construction, routing, protection coordination, thermal performance, voltage drop, communication integrity, received identity or correct assembly.

The JST EH 3 A published condition versus the XM540 4.4 A published stall-current endpoint remains open. R153 is a project-owned correction and validation pass, not an independent review or approval. Sol's resupplied summary remains R12 and is not double-counted.
