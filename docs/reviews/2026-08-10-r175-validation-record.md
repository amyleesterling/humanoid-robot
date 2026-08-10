# R175 validation record

R175 issues `HR-V0-DYN-INST-P0.1`, an evaluation-only acquisition-backbone candidate for future HR-V0 characterization and stopping/reset evidence.

- Ten equipment rows name four exact evaluation candidates and retain six open or rejected branches.
- All fifteen `DCH-001` through `DCH-015` channels are mapped.
- Eight interface records prohibit unresolved direct connection and give the DAQ/test computer zero safety-function credit.
- The ground-referenced LabJack divide-by-5 accessory is rejected as a completed isolated 24 V primary event interface.
- Fifteen selection holds remain open with release effect `NONE`.
- Four receiving/calibration rows remain blank and `NOT EXECUTED`.
- `EG-025` remains open and `EG-026` remains partial.
- Procurement, connection, powered-run and physical-evidence counts remain zero.

## Primary-source verification

Eight records were checked against current official LabJack, LEM and Teledyne Vision Solutions documentation on 2026-08-10. The register records each stated revision/date. Live manufacturer pages that state no revision or publication date are explicitly labeled that way rather than assigned an inferred revision.

The exact-product records are candidates, not accepted instruments. No manufacturer maximum, nominal value or product availability has been converted into a project acceptance limit.

## Browser validation

The interactive guide was checked at 1280 x 720 and 390 x 844.

- body and table text: 16 px;
- desktop two-column and mobile one-column candidate cards;
- no page-level horizontal overflow at either width;
- the wide channel table owns its horizontal scroller at mobile width;
- mobile warning, candidate cards, no-connect warning and table header/rows are legible; and
- no console warnings or errors were recorded.

The browser's stitched full-page capture compressed the layout while its viewport capture and DOM geometry remained correct; signoff therefore used viewport screenshots plus measured DOM bounds at both target widths.

## Repository validation

- Non-native repository checks: **118/118 passed**.
- Native KiCad checks under KiCad 10.0: **13/13 passed**.
- Pre-manifest total: **131/131 passed**.
- The staged release-manifest check brings the controlled total to **132 checks**.

Automated success proves source consistency, candidate identity records, no-connect boundaries and repository invariants only. It does not prove range suitability, isolation, grounding, sensor response, calibration, timing uncertainty, physical stopping behavior, functional-safety performance or permission to procure, connect, test, move or energize.
