# R162 validation record

> **PRELIMINARY - NOT APPROVED FOR SUPPLIER UPLOAD, QUOTATION, PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, MOTION, OR ENERGIZATION**

Date: 2026-08-09

Package: `HR-V0-DXL-CARRIER-MOUNT-IF-P0.1`

## Deterministic result

`tools/check_hr_v0_dxl_carrier_mount_if_p01.py` passes:

- three re-centered 100 x 60 mm carrier envelopes inside P0.6 BP-026;
- twelve unique center-only mounting coordinates with every panel diameter held;
- one exact 10 mm M3 standoff candidate and one exact M3 x 6 mm screw candidate, totaling 12 standoffs and 24 screws;
- nine nominal stack/edge calculations, with all tolerance and physical evidence caveats preserved;
- eight clearance screens, including three intentionally unresolved connector/cover/rear-clearance rows;
- seven primary/repository source records with document revision/date or an explicit no-revision/access-date record;
- fourteen unresolved selections, ten unexecuted metrology rows and twelve open unsigned acceptance rows;
- synchronized engineering/release records and deterministic per-package file manifests; and
- every supplier, quotation, procurement, fabrication, assembly, connection, motion, energization and safety-credit flag false.

The checker also confirms the native P0.3 source still records a 1.6 mm thickness candidate and the four mounting-hole plus two VH-header references. Passing results prove repository arithmetic, membership, hashes and fail-closed state only.

The complete repository regression passed 118/118 checker programs using the controlled CAD and KiCad runtimes. The regenerated release manifest controls 2,630 package files.

Browser QA at 1280 x 720 confirmed a 16.64 px computed body font, 14 px SVG annotation text, no horizontal document overflow, both preliminary warnings, all controlled-file links and the LIM1/LIM2/LIM3 selector. The first rendering exposed SVG text inheriting the board highlight stroke; the selector was narrowed to board rectangles and the corrected rendering was rechecked. The source also retains the explicit narrow-screen table reflow and 16 px SVG annotation rule. No physical or dimensional conclusion is inferred from browser rendering.

No received article, tolerance stack, connector sweep, torque/load proof, drilling/process acceptance, enclosure closure, physical test or qualified signoff exists.
