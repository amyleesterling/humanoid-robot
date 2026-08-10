# R133 validation record

Status: **PRELIMINARY - NOT APPROVED FOR FABRICATION OR ENERGIZATION**

Date: 2026-08-09

Round: R133

Package: `HR-V0-WD-PCBA-DATA-P0.1`

## Controlled result

- Exact PCB-P0.7 membership is split into 42 populated references and four NPTH mechanical features.
- Sixteen exact-MPN BOM lines total 42 parts with no alternates released.
- Placement data retain 38 SMD and four post-reflow THT references, all top-side.
- The 160.000 x 100.000 mm Edge.Cuts rectangle defines the internal review origin; native KiCad rotation is copied without a supplier transform.
- Polarized/not-keyed/module orientation controls are explicit.
- Ten assembly notes, ten file-state rows and twelve open holds are controlled.
- Supplier-normalized XYRS, CAM, provider selection/contact, upload, fabrication, assembly, physical article and energization flags remain false.

## Validation state

- Dedicated R133 generator/checker: PASS; 42 populated references, sixteen exact-MPN BOM lines totaling 42 parts, 38 SMD / four THT, four NPTH, five coordinate controls, ten notes/file states and twelve open holds.
- R132 inquiry checker after synchronized file-state update: PASS; all four provider routes remain not contacted and all authorization/physical flags remain false.
- Native KiCad DRC: KiCad 10.0.5 exit `0`; zero violations and zero unconnected items in `project-button-v3-r133-audit-drc.rpt`.
- Browser QA: PASS at the available `1280 x 720` viewport; body text `17 px`, smallest visible leaf text `14 px`, no page-level horizontal overflow, warning visible and all 42 initial rows rendered. The SMD filter returned 38 rows, exact-part search returned one ISO1 row, reset restored 42 rows, and the console was clean. Static responsive audit confirms the `max-width:600px` branch retains `16 px` body / `14 px` metadata, wrapping controls and contained horizontal scrolling for the map/table. Temporary tabs were finalized and the local server stopped.
- Full repository checker suite: PASS; 85/85 domain checkers passed using the controlled general/CadQuery interpreter, with the three pcbnew-dependent checkers run under KiCad 10.0.5 Python.
- Fail-closed E0-E2 readiness: expected non-ready exit `2`; all 21 applicable gates remain `partial`, zero are closed and no authorization exists.
- Deterministic release manifest: PASS; 1,806 staged package files hashed in `HR-V0-RC-P0.1-file-manifest.csv`, excluding only the manifest itself to avoid recursive hashing.

No supplier response, manufacturing process acceptance or physical result exists.
