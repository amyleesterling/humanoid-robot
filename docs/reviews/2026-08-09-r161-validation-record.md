# R161 validation record

> **PRELIMINARY - NOT APPROVED FOR SUPPLIER UPLOAD, QUOTATION, PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, MOTION, OR ENERGIZATION**

Date: 2026-08-09

Package: `HR-V0-DXL-CARRIER-INTEGRATION-P0.1`

## Native ECAD result

- `V3-P1.15-CARRIER-CANDIDATE`: 13 parsed native pages; KiCad 10.0.5 ERC 0 errors / 0 warnings.
- `DXL-STAR-P0.2-CARRIER-CANDIDATE`: KiCad 10.0.5 ERC 0/0; DRC 0 violations / 0 unconnected pads.
- Native parity checker: candidate footprints, pads, copper tracks, return zone and 100 x 60 mm outline match P0.1 after only `Jx_VDD -> Jx_LIMITED_VDD` mapping.
- P0.3 carrier native screen: 100 x 60 mm outline and four mounting-hole datums confirmed.

## Deterministic integration result

`tools/check_hr_v0_dxl_carrier_integration_p01.py` passes:

- three distinct fused-prelimit and three distinct limited-postcarrier positive rails;
- three four-terminal carrier blocks and 15 controlled transitions;
- three nominal placements and twelve mounting-hole coordinate screens;
- six route screens with every cut length held;
- twelve unresolved selections and 24 open, unexecuted, unsigned acceptance rows;
- synchronized engineering/release records and deterministic package manifests;
- all supplier, fabrication, assembly, connection, motion, energization and safety-credit flags false.

Repository regression passed 103/103 non-native, non-manifest HR-V0 checkers before staging. The final staged sweep passed 106/106 standard checkers, including the repository traceability, energization-gate and release-manifest checks, plus 11/11 KiCad-native checkers. The regenerated release manifest controls 2,601 package files.

Browser QA at a 1280 x 720 viewport confirmed 16 px body/warning text, 14 px metadata and SVG annotation text, no horizontal document overflow in the interactive guide, and a visible preliminary warning. The first rendering exposed overlapping reserve/carrier labels and a crowded Electrical page 06; both were corrected before final validation. The final native export uses a focused page 06 for the three fuse/carrier chains and page 10 for U2D2, DXL-star, actuator ports and bonding. Both were visually rechecked at normal browser scale.

No physical article exists. No drilling, harness cutting, crimping, assembly, continuity, polarity, isolation, current-limit, reverse-energy, fault, thermal, waveform, EMC, motion or energization test was executed.
