# R152 validation record - DXL injection allocation binding

**PRELIMINARY - NOT APPROVED FOR SUPPLIER UPLOAD, QUOTATION, FABRICATION, ASSEMBLY, CONNECTION, MOTION, OR ENERGIZATION**

Date: 2026-08-09

Product: `HR-V0-DXL-INJECT-BIND-P0.1`

## Configuration result

- Electrical V3 contains one `INJ1` parent function, and native DXL-STAR-P0.1 contains one parent board implementing three isolated actuator-VDD branches.
- All eighteen Electrical V3 `INJ1` terminals reconcile exactly to the native JC1, JP1-JP3 and JA1-JA3 terminal/net allocation; zero parity failures are recorded.
- JC1.2 remains explicit `NO_NET_NO_COPPER` and is not converted into a powered or signal connection.
- Legacy `BOM-035` is integrated into `BOM-051`; no separate three-module purchase allocation remains.
- `BOM-051` remains an exact candidate hold. System closure counts are 40 exact candidate holds, 19 selection-required groups and two integrated items.
- Twelve residual holds remain open for board fabrication/assembly, connectors, contacts, harnesses, protection, conductors, current conflict, waveform/EMC, no-backfeed/sequencing, thermal/fault validation, qualified review and written work authority.
- Supplier, quotation, fabrication, assembly, physical, connection, motion, energization and safety-credit authorizations remain false.
- `EG-003`, `EG-004` and `EG-015` remain partial; no gate closes.

## Visual QA and automated regression

- The interactive guide was served locally and inspected in the in-app browser at a 1280-pixel-wide viewport. The preliminary warning, 1/3/18/0 cards, allocation statement, allocation table, all twelve residual holds and three artifact links are present and legible.
- Computed minimum functional text is 14 px. The page has no body-level horizontal overflow at the inspected width, and the table is contained in an `overflow:auto` wrapper. Responsive source is present; this record does not claim a physical mobile-device test.
- Ninety-nine standard engineering checkers passed in the controlled CAD environment.
- Seven native KiCad checkers passed under KiCad 10.0.5 Python.
- The release manifest is regenerated and checked after deliberate files are staged. The clean committed-state manifest is rechecked before push. Total regression is 107 engineering checkers: 99 standard, seven native KiCad and one release-manifest checker.

## Independent-review trace

The Sol analysis resupplied during R152 is the already-controlled R12 independent review of the historical pre-correction baseline. Its reviewer-reported totals remain 18 BLOCKER, 30 MAJOR and 8 MINOR findings, 62/62 reviewed requirements draft, 106 unresolved Electrical V2.1 selection records and zero approved executed verification records. It is not counted as a new independent review, and R152 does not reduce those original totals.

## Disposition

R152 closes only the duplicate DXL-injection allocation contradiction. It does not establish manufacturability, connector or harness suitability, protection sizing, current capacity, electrical performance, grounding, thermal behavior, physical correctness, functional safety, build readiness or energization readiness.
