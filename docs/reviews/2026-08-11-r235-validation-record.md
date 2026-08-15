# R235 validation record

> **PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION**

Date: 2026-08-11

- Package: `HR-V0-P121-APP-EVID-P0.1`
- Manufacturer questions: 13; all `NOT SENT`, all responses `OPEN`
- Official submission routes: 6; none used
- Response-acceptance controls: 12
- Authorization prerequisites: 10; all open
- Required signals: 15
- Test cases: 18; all `NOT EXECUTED`
- Open holds: 14
- Manufacturer responses: 0
- Powered-test authority: false
- Energization authority: false
- Focused checker: PASS
- Standard repository checker sweep: 178 / 178 PASS
- Native KiCad / pcbnew checker sweep: 18 / 18 PASS
- Supervisor firmware tests: 67 / 67 PASS
- Watchdog reference-model and compiled-C differential tests: 11 / 11 PASS
- Deterministic release manifest at validation: 4,744 package files
- Desktop guide QA: PASS at 1280 x 720; minimum visible text 16 px; no unexpected body overflow
- Mobile guide QA: PASS at 390 x 844; minimum visible text 16 px; wide tables scroll inside their own containers; no body overflow
- Interactive manufacturer filter: PASS; `Pilz` uniquely showed `PILZ-Q01` through `PILZ-Q07`
- Interactive test filter: PASS; `Fault injection` uniquely showed TEST-009 through TEST-013 and TEST-015

The first CAD sweep was run inside a sandbox that could see but not import the temporary CadQuery package directory; its 18 CAD import failures were environment-only. The authoritative read-only rerun used the same 178 checkers with the temporary runtime accessible and passed 178/178. No engineering failure was suppressed.

This package defines evidence collection only. It sends no inquiry, selects no dynamic limit, performs no connection or test, accepts no topology and closes no qualified finding.
