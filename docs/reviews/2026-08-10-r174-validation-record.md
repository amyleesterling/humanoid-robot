# R174 validation record

R174 issues `HR-V0-DYN-TRACE-P0.1`, an executable trace-analysis candidate for future stopping-time and reset-to-motion evidence.

- Nine stable rules cover integrity, stop edge, dual coil/mirror edges, rail decay, independent motion stop, time/travel/clearance, reset interlock and range reporting.
- Four new common-clock event fields distinguish reset, separate start, supervisor motion request and achieved torque-enable state.
- The unresolved physical template is rejected before trace analysis.
- The nominal synthetic fixture computes 0.030 s total stop time, 0.435 degree residual travel and 6.065 degree endpoint clearance, but remains on qualified `HOLD` with release effect `NONE`.
- The reset-motion fixture fails `DTA-007`.
- The too-early separate-start fixture fails `DTA-007`.
- The sample-index/drop-count fixture fails `DTA-001`.
- Four qualified-disposition rows remain `NOT EXECUTED`, with reviewers `SELECTION REQUIRED` and decisions `HOLD`.
- `EG-026` advances from open to partial; it does not close.

## Browser validation

The interactive guide was inspected at 1280 x 720 and 390 x 844.

- body, table and code text: 16 px;
- desktop five-column evidence flow and mobile one-column reflow;
- table overflow contained inside its own horizontal scroller;
- no page-level horizontal overflow; and
- no console warnings or errors.

## Repository validation

- General repository checks: **103/103 passed**.
- Native KiCad-dependent checks under KiCad 10.0: **13/13 passed**.
- CadQuery geometry checks: **14/14 passed**.
- Pre-manifest total: **130/130 passed**.
- The staged release-manifest check brings the controlled total to **131 checks**.

Automated success proves parser, arithmetic, reference-algorithm and repository invariants only. It does not prove sensor suitability, calibrated timing, physical stopping performance, reset behavior, statistical confidence, functional-safety performance or permission to conduct powered work.
