# R234 validation record

> **PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION**

Date: 2026-08-11

- Candidate: `V3-P1.21-SRA1-SUPPLY-WATCHDOG-CANDIDATE`
- Dossier: `HR-V0-P121-SRA1-SUPPLY-WD-P0.1`
- KiCad version: 10.0.5
- Native pages parsed/exported: 13
- ERC: 0 errors / 0 warnings
- Modeled component blocks: 84
- BOM rows: 82
- Terminal rows: 340
- Named nets: 106
- Exact P1.20-to-P1.21 terminal changes: 7
- Unchanged terminal assignments: 333
- Fault cases: 14
- Supply/contact screens: 9
- Open holds: 11
- Focused R234 checker: PASS
- Standard repository checker sweep: 177 / 177 PASS
- Native KiCad / pcbnew checker sweep: 18 / 18 PASS
- Supervisor unit tests: 67 / 67 PASS
- Watchdog unit and differential tests: 11 / 11 PASS
- Release-manifest coverage at validation: 4,694 files
- Interactive-guide desktop QA: PASS at 1280 x 720; minimum visible text 14 px; no unexpected horizontal overflow
- Interactive-guide mobile QA: PASS at 390 x 844; minimum visible text 14 px; authority path and tables intentionally scroll within their own containers; no body overflow
- Interactive-guide filter control: PASS; `DF-01 lost` uniquely selected `FT-005`

The low-side contactor-return concept was not retained because current watchdog source can restore ordinary relay commands after three valid edges, while a still-latched SRA1 could then restore coil power without another monitored ARM. P1.21 instead power-cycles only SRA1 and restores direct SR1-controlled SRA1 input paths.

ERC proves modeled connectivity and annotation only. No received component, installed route, contact life, brownout behavior, fault response, rail/torque decay, stopping performance, guard containment, PLr/SIL/category, qualified review or work authorization has been established. P1.15 remains current; P1.21 is unaccepted.
