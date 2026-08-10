# R109 validation record - official gripper-frame source correction

Status: **PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, MOTION, OR ENERGIZATION**

R109 corrects the current source record for the FR12-G101GM frame set. Six official ROBOTIS payloads for FR12-E170 and FR12-E171 are controlled by manufacturer endpoint, document/access date, exact byte size, SHA-256 hash and real file signature. Both STEP files reproduce as one solid. This is reference-geometry evidence only and closes no complete-mechanism, manufacturing, H104-registration, physical or authorization hold.

## Source and PDF verification

- The live ROBOTIS XH430-V210 e-Manual identifies FR12-E170 and FR12-E171 as the FR12-G101GM frame-set parts and exposes manufacturer download endpoints 637-642.
- All six downloaded payloads were checked for their actual DWG, PDF or ISO-10303-21 signature; no HTML landing page was retained as an engineering file.
- The two one-page A4 PDFs were rendered with Poppler 25.07.0 at 180 dpi and visually inspected at original detail. Both were clear and unclipped, dated 2017-08-31, in millimetres, `NONSCALE` and marked `FOR REFERENCE ONLY`. Material fields are blank; neither sheet shows a general-tolerance block or drawing revision.
- Temporary page renders and the temporary manufacturer-repository history clone were removed after inspection. The source PDFs remain unchanged.

## Geometry verification

The controlled CadQuery runtime imported each STEP as one solid and reproduced the manifest geometry:

- FR12-E170: 37.000000 x 14.000000 x 87.740667 mm bounding box; 5837.452710 mm3 volume.
- FR12-E171: 54.000000 x 47.998711 x 94.848224 mm bounding box; 8322.633440 mm3 volume.

Those values have no material or mass credit. Native coordinate systems are not accepted as an E170-to-E171 assembly transform.

## Web-guide verification

The responsive guide was rendered in the in-app browser at 1440 x 1000 and 390 x 844 CSS-pixel viewports. The E170/E171 selector changed the pressed state and displayed part correctly. Both viewports had document scroll width equal to client width, the computed minimum functional font was 12 px, and targeted screenshot inspection found the warning, source boundary, geometry fields, controls and downloads readable and unclipped. All six download URLs returned HTTP 200 and the controlled byte lengths.

## Repository verification

The complete repository suite passed:

- 61 checker programs: 54 workspace-Python, four CadQuery and three KiCad 10.0.5 runtime checks;
- 47 executable firmware unit tests inside the firmware checker; no target flash or HIL was performed;
- 359 hash-controlled generated CAD artifacts and 16 pre-existing CAD-validation vendor references, plus six new SHA-controlled ROBOTIS gripper-frame payloads;
- 81 requirements, 40 risks, 109 procedures and 56 release/walking-document procedure references; and
- all 30 energization gates unresolved: zero closed, 22 partial and eight open.

The staged `HR-V0-RC-P0.1` manifest passed after regeneration with 1,455 package files. The intentional E2 `--require-ready` check returned exit code 2 with all 21 applicable E0-E2 gates partial; this is the required fail-closed result. A clean post-commit manifest check remains required.

No item was ordered, no supplier was contacted, no article was received and no fabrication, assembly, connection, motion or energization gate closed.
