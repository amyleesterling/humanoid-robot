# R260 validation record

> **PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION**

Generated correction: `HR-V0-OBS-MOUNT-STACK-P0.1`.

Controlled scope:

- 108 system BOM groups and exact BOM/closure parity;
- two mounting interfaces advanced to exact-candidate hold;
- 24 candidate hardware pieces across four order-code records;
- eight current primary-manufacturer source records;
- six reproducible nominal stack screens;
- eight mounting-geometry rows, all DO NOT DRILL or NO ASSEMBLY;
- nine open holds, ten unexecuted fit rows and twelve unexecuted acceptance rows; and
- configuration P0.24 with 43 current records, 36 supersession records, 28 BOM integrations, 11 gates, 153 holds and 191 unexecuted acceptances.

## Executed validation

- dedicated R260 checker: **PASS**;
- standard-runtime repository checker sweep: **203/203 PASS**;
- native KiCad/`pcbnew` checker sweep under KiCad 10.0.5 Python: **18/18 PASS**; R260 changes no ECAD source;
- staged release-candidate manifest: **6,044 package files; PASS**; and
- `git diff --check`: **PASS**.

## Responsive browser QA

At 1280 x 720 px, the guide rendered with 16 px body text, 14 px table text, no page-level horizontal overflow, four summary cards, four tables and seven controlled-record links. The runtime/Pi selector changed the visible stack content correctly.

At 390 x 844 px, body text remained 16 px and table text 14 px. Page-level width remained 375 px while each 311 px table wrapper owned its 820 px horizontal overflow. The warning and principal text rendered without clipping. The viewport was reset and the test tab finalized after inspection.

Passing automated checks does not establish orderability, received fit, load capacity, thermal behavior, workmanship, functional safety or authority to perform physical work.
