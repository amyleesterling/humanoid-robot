# R132 validation record

Status: **PRELIMINARY - NOT APPROVED FOR FABRICATION OR ENERGIZATION**

Date: 2026-08-09

Round: R132

Package: `HR-V0-WD-PCBA-RFI-P0.1`

## Controlled result

- Current PCB-P0.7 supersedes PCB-P0.6 only for the exact TP1-TP16 Harwin rectangular-copper correction; land size, centroid, placement and net remain unchanged.
- 46/46 source footprints are bound to the R89 current-board land audit.
- Nine primary-source reconciliation groups cover all 21 retained R89 corrections plus sixteen R132 Harwin corrections; no further current copper edit is justified, while nine passive references retain an explicit reflow-process choice and RTH1/RTH2 retain the IPC-7351-basis/date-code evidence hold.
- Extracted process split: 38 SMD, four post-reflow THT and four NPTH.
- Four current official provider capability routes are screened; none is selected or contacted.
- Twenty requirements, twenty-four blank `NOT SENT` questions, ten withheld/not-released supplier-file rows, fourteen holds and twenty-four `NOT EXECUTED - NO ARTICLE` first-article rows are controlled.
- Every contact, upload, quote, CAM, fabrication, assembly, physical-article and energization flag is false.

## Validation state

- Dedicated package checker: PASS; 46 references, 38 SMD / four post-reflow THT / four NPTH, nine current-geometry groups covering 21 retained R89 corrections plus sixteen R132 Harwin corrections, four provider routes, twenty requirements, twenty-four unsent questions and fourteen holds.
- Current native KiCad DRC: KiCad 10.0.5 exit `0`; zero violations, zero unconnected pads and zero footprint errors in `project-button-v3-r132-audit-drc.rpt`.
- Browser QA: PASS at `1440 x 1000` and `390 x 844`; no page-level horizontal overflow, body text `17 px` desktop / `16 px` mobile, smallest visible leaf text `14 px` desktop / `13.333 px` mobile, warning visible, mobile flow reflowed to a column, and no console warning/error. The temporary viewport was reset and the temporary tab finalized.
- Full repository checker suite: PASS; 84/84 domain checkers passed using the controlled general/CadQuery interpreter, with the three pcbnew-dependent checkers run under KiCad 10.0.5 Python.
- Fail-closed E0-E2 readiness result: expected non-ready exit `2`; all 21 applicable gates remain `partial`, zero are closed and no authorization exists.
- Deterministic release manifest: PASS; 1,788 staged package files hashed in `HR-V0-RC-P0.1-file-manifest.csv`, excluding only the manifest itself to avoid recursive hashing.

No physical result or supplier response exists in R132.
