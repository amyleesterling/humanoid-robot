# R232 validation record

> **PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION**

- Date: 2026-08-11
- Artifact: `HR-V0-P120-WD-INTERLOCK-P0.1`
- Native ECAD candidate: `V3-P1.20-WATCHDOG-INTERLOCK-CANDIDATE`

## Configuration and topology results

- P1.15 remains the current electrical product. P1.18, P1.19 and P1.20 remain unaccepted.
- All 13 native P1.20 KiCad sheets parse and export with KiCad 10.0.5.
- Native ERC result: **0 errors / 0 warnings**.
- All 84 native component reference/value/footprint identities are unchanged from P1.19.
- All 340 terminal identities remain present; 333 terminal/net assignments are unchanged and exactly seven changed.
- Structural native-netlist parsing confirms exactly seven changed named-net memberships matching the seven schedule moves.
- BOM remains 82 rows, the wire table 301 rows, the named-net schedule 106 rows and unresolved selections 63 rows.
- S0, S1, S2, SRA1, K1, K2, FSR1 and FSR2 terminal/net assignments are unchanged.
- The P1.20 source topology places KWD1 in the SR1:14-to-SRA1:S12 return and KWD2 in the SR1:24-to-SRA1:S22 return while returning SR1:A1 directly to SAFETY_24V.

## Fault-screen and visual results

- All 12 controlled fault screens are present.
- Either single KWD 11-14 weld is defeated in the modeled topology by the other channel opening.
- Three cases remain `HAZARDOUS_UNRESOLVED`: dual KWD weld/bypass, shared controller/driver command holding both relays on, and both field interlock paths bypassed.
- Every fault row retains `safety_credit=NONE`; all nine closure holds remain open.
- Sheets 02 and 03 were inspected as full native KiCad SVGs. The changed SR1, KWD1 and KWD2 labels are separated and readable; the page warning, revision and title metadata remain present. The remaining eleven sheets inherit P1.19 geometry and were not electrically changed.
- Desktop guide QA passes at 1,265 CSS pixels: all 12 rows render, body text is 16 px, code is 14 px and no body-level overflow exists.
- Mobile guide QA passes at requested 390 x 844: the document width is 375 CSS pixels, body text remains 16 px, body-level overflow is absent and the wide fault table scrolls locally.
- The hazardous filter exposes exactly three rows.

## Repository and software validation

- Focused P1.20 checker: **PASS**.
- Standard repository checker sweep using the controlled CadQuery-capable interpreter: **175 / 175 PASS**.
- Native KiCad/pcbnew checker sweep using KiCad's bundled Python: **18 / 18 PASS**.
- Supervisor firmware source tests: **67 / 67 PASS**.
- Watchdog reference-model and compiled-C differential tests: **11 / 11 PASS**.
- Final staged deterministic release manifest: **PASS with 4,591 controlled package files**.

An initial pcbnew sweep used the CAD virtualenv and failed because that interpreter does not contain KiCad's `pcbnew` module. The authoritative rerun used `C:\Program Files\KiCad\10.0\bin\python.exe` and passed 18/18. An initial firmware attempt used interpreters without pytest; the suites are standard-library `unittest` suites, and the authoritative unittest runs passed 67/67 and 11/11.

## Boundary

R232 materially addresses the single-watchdog-contact source topology in Sol B-005. It does not supply qualified closure of B-005. Common-cause and dependent-failure analysis, exact PNOZ/KWD application confirmation, protected physical routing, received/installed evidence, calibrated fault injection, stopping evidence, PLr/SIL allocation, independent review, qualified signatures and separate work authorization remain open. Source consistency, ERC and fault screens do not authorize procurement, fabrication, assembly, connection, powered testing, motion or energization.
