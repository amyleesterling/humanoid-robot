# HR-V0 DXL star manufacturing review P0.2

Status: **PRELIMINARY—NOT APPROVED FOR SUPPLIER UPLOAD, QUOTATION, PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, MOTION, OR ENERGIZATION**

Identifier: `HR-V0-DXL-STAR-MFG-P0.2`

Review round: R164

Date: 2026-08-09

## Purpose

R164 supplies current, source-bound manufacturing-review evidence for `DXL-STAR-P0.2-CARRIER-CANDIDATE`. It replaces the R163 statement that current P0.2 CAM is absent. The R151 P0.1 package remains historical and must not be used to fabricate P0.2.

## Generated evidence

KiCad 10.0.5 generated directly from the controlled P0.2 board:

- ten Gerber/job files covering copper, paste, silkscreen, mask, outline and job metadata;
- separate plated and non-plated Excellon drill files, two SVG drill maps and a drill report;
- IPC-D-356 review netlist;
- native DRC report with zero violations, zero unconnected pads and zero footprint errors;
- raw KiCad position export for seven connector references;
- board statistics;
- exact source/output SHA-256 registers;
- exact placement parity for seven connectors;
- exact terminal-to-pad parity for all eighteen connector terminals, including `JC1:2` as deliberately no-net/no-copper; and
- four native NPTH mounting-feature records.

The raw position export is not supplier-normalized XYRS and is prohibited from machine import.

## Remaining release holds

All eighteen holds remain open. They include provider and process selection, material/stackup/copper/finish/mask/legend, tolerances, panelization, bare-board test, connector application, mating harnesses, conductor/crimp definition, protection coordination, the JST EH versus XM540 current conflict, signal integrity, no-backfeed, grounding/shielding, thermal/load validation, first article, HIL/fault/EMC evidence, qualified review and separate work authorization.

The package contains no supplier upload archive. It establishes current encoded manufacturing evidence only; it does not establish manufacturability, electrical performance, safety, or permission to perform physical work.

Machine-readable and web-readable records are in `release/hr-v0/dxl-star-manufacturing-p0.2/`.
