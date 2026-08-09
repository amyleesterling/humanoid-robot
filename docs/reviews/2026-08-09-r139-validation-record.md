# R139 watchdog native identity and current assembly-data validation record

> **PRELIMINARY - NOT APPROVED FOR FABRICATION, ASSEMBLY, CONNECTION, TESTING, OR ENERGIZATION.**

Date: 2026-08-09

Configuration: `HR-V0-WD-PCBA-DATA-P0.2 / PCB-P0.9 / Electrical V3-P1.14 / HR-V0-E2-HW-P0.3`

## Result

- Added seven exact hidden identity/control fields to each of the 42 populated native KiCad footprints: manufacturer, exact manufacturer part number, assembly description, process class, no-alternate policy, assembly-process state, and preliminary fabrication state. That is 294/294 base fields. The 36 deeper R138 evidence fields remain on `UDRV1`, `UDRV2`, `UFB1`, and `ISO1`.
- Reconciled the current native board to sixteen exact-MPN BOM lines totaling 42 parts, 42 placement-reference rows, four NPTH mechanical features, 38 SMD references, and four manual post-reflow THT references.
- Proved 46/46 reference-level assembly parity between historical PCB-P0.7 data and current PCB-P0.9. A field-excluded structural comparison between PCB-P0.8 and PCB-P0.9 remains identical at SHA-256 `dc1f86c067e9617aed7e82b177bc7e1b0fb61b25cc3ab878e6c4440889c4c5ea`.
- Regenerated the native board and V3 exports under KiCad 10.0.5. Watchdog native DRC remains **0 violations / 0 unconnected pads / 0 footprint errors**. Electrical V3 ERC remains **0 errors / 0 warnings** within modeled scope.
- Synchronized the control-only commissioning hardware slice to `HR-V0-E2-HW-P0.3`. Its 23 configuration rows, six XT1 terminal rows, three source rows, and twelve blocking holds all remain controlled; the actuator-power domain remains physically excluded at E2.
- All 84 standard-runtime HR-V0 domain checkers passed. All five PCB-native checkers passed under KiCad 10.0.5 bundled Python. After release-manifest regeneration, the complete suite is **90/90 passed**.
- Traceability passed with **81 requirements, 40 risks, 110 procedures, and 57 release/walking-document procedure references**.
- Strict through-E2 readiness intentionally exited **2**: **0 closed / 21 partial / 0 open** among 21 applicable gates. The package is **NOT READY through E2**.
- Browser QA passed for both the P0.2 assembly guide and P0.3 E2 hardware guide at 1280 x 720 and within a 390 x 844 narrow viewport. Minimum rendered text is 16 px; page-level horizontal overflow is absent; the assembly table uses controlled horizontal scrolling; and assembly filter/search interaction returned 4 THT rows and one exact `JWP1` search result.
- Release-candidate manifest regenerated from the staged index with **1,912 package files**; manifest validation passed.

Supplier-normalized XYRS, stencil/paste/process definition, current CAM, provider selection, quotation, fabrication, assembly, physical article, test execution, qualified electrical/PCBA review, functional-safety credit, and every work authorization remain open or false. Clean native ECAD, DRC, ERC, identity fields, parity, traceability, repository checks, and browser QA do not establish physical correctness or permission to energize.
