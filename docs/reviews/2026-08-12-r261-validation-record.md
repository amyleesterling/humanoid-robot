# R261 validation record

> **PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION**

Generated correction: `HR-V0-U2D2-JC1-HARNESS-P0.1`.

Controlled scope:

- 108 system BOM groups;
- five current primary-manufacturer source records;
- three exact cavity rows, with cavity 2 physically empty at both ends;
- six harness BOM/tool rows and seven build characteristics;
- a 500 +/- 5 mm finished-length candidate, 25 +/- 5 mm pair-lay candidate and 15 mm stationary bend-radius floor;
- five route-screen rows, nine unexecuted process rows and seven unexecuted electrical-test rows;
- twelve open holds and thirteen blank acceptance rows;
- corrected BOM-061/107/108 exact-candidate parity; and
- configuration P0.25 with 44 current records, 37 supersession records, 29 BOM integrations, 11 gates, 165 holds and 204 unexecuted acceptances.

## Executed validation

- dedicated R261 checker: **PASS**;
- standard-runtime repository checker sweep: **204/204 PASS**;
- native KiCad/`pcbnew` checker sweep under KiCad 10.0.5 Python: **18/18 PASS**; R261 changes no ECAD source;
- staged release-candidate manifest: **6,098 package files; PASS**; and
- `git diff --check`: **PASS**.

## Web-guide validation boundary

Static inspection confirms a responsive viewport declaration, 16 px minimum body copy, 14 px table text, mobile reflow for the pin diagram, and table-owned horizontal overflow. Direct visual browser QA of the local `file://` artifact was not executed because the browser security policy rejected the local URL. No screenshot-based responsive result is claimed for R261; the guide still requires visual recheck when served from an approved local or hosted URL.

A passing automated record does not establish crimp quality, route fit, electrical performance, suitability, functional safety or authority to perform physical work.
