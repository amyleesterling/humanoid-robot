# HR-V0 PNOZ path conformance P0.1

Status: **PRELIMINARY - NOT APPROVED FOR FABRICATION OR ENERGIZATION**

Document ID: **HR-V0-PNOZ-CONF-P0.1**

Date: 2026-08-08

Electrical configuration: **Project Button Electrical V3-P1.13**

Components: proposed `SR1` and `SRA1`, Pilz PNOZ s4 24 VDC, order code `750104`

## Decision

The native V3-P1.13 net model is consistent with the terminal functions and example circuits in Pilz operating manual `21396-EN-23` for the specific paths checked in `safety/hr-v0-pnoz-path-conformance-p0.1.csv`. This is a source-to-schematic conformance result only. It is not Pilz application approval, a functional-safety validation, a wiring release, or permission to energize.

The controlled manufacturer PDF is `electrical/vendor/pilz/pnoz-s4-750104-r116/PNOZ_s4_21396-EN-23.pdf`. Its SHA-256 is `4B6E4768CEFAEDAF54F006347D32A8A04964B59A16F3616D8AC43698D3626BB4`. The document edition is `21396-EN-23`; PDF metadata records creation on 2026-06-17, the Pilz portal file date was 2026-06-22, and the file was acquired on 2026-08-08. Those dates describe the source record, not the project design revision.

## Exact controlled paths

| Function | Encoded V3-P1.13 path | Source relation | Status |
|---|---|---|---|
| SR1 channel 1 | `SR1:S11 -> S0:R-1/R-2 -> SR1:S12` | Manual page 13 dual-channel E-stop example | Partial; received device, routing and fault tests open |
| SR1 channel 2 | `SR1:S21 -> S0:L-1/L-2 -> SR1:S22` | Manual page 13 dual-channel E-stop example | Partial; received device, routing and fault tests open |
| SR1 RESET | `SR1:S12 -> S1:TBD-R1/TBD-R2 -> SR1:S34` | Manual pages 13 and 15 falling-edge monitored start | Partial; S1 terminal mapping and physical tests open |
| SR1 to SRA1 channel 1 | `SRA1:S11 -> SR1:13/14 -> SRA1:S12` | Safety contact 13-14 gates channel loop | Partial; protection/application evidence open |
| SR1 to SRA1 channel 2 | `SRA1:S21 -> SR1:23/24 -> SRA1:S22` | Safety contact 23-24 gates channel loop | Partial; protection/application evidence open |
| SRA1 ARM and EDM | `SRA1:S12 -> S2:TBD-A1/TBD-A2 -> K1:21/22 -> K2:21/22 -> SRA1:S34` | Manual pages 15-16 monitored manual start with external-device feedback | Partial; received terminals, mirror-contact application and physical tests open |
| K1 coil command | `SAFETY_24V -> SRA1:13/14 -> FSR1 -> K1:A1` | Safety output; protection required | Open; FSR1 link and coordination are `SELECTION REQUIRED` |
| K2 coil command | `SAFETY_24V -> SRA1:23/24 -> FSR2 -> K2:A1` | Separate safety output; protection required | Open; FSR2 link and coordination are `SELECTION REQUIRED` |
| ordinary heartbeat gate | `SAFETY_24V -> KWD1:11/14 -> KWD2:11/14 -> SR1:A1` | A1 supply is switched by a project ordinary-control gate | Open; **ZERO SAFETY CREDIT** and application/fault evidence required |

## Restart consequence

Releasing S0 cannot command motion. Restoring heartbeat cannot command motion. RESET can restore only SR1 eligibility; it does not feed either contactor coil. SRA1 remains dropped until a later, distinct falling-edge ARM action passes through both K1/K2 NC mirror contacts. Even then, software must require a fresh validated trajectory before torque or motion. These are encoded design intentions that still require physical fault-injection and total-response validation.

The two-stage sequence is:

`cause absent -> heartbeat gate healthy -> release and actuate RESET -> SR1 eligible -> release and actuate ARM through K1/K2 EDM -> SRA1 eligible -> fresh trajectory validation -> possible torque`

## Unclosed application evidence

- received identity and terminal-by-terminal continuity for SR1, SRA1, S0, S1, S2, K1 and K2;
- received S1/S2 terminal mapping, which remains `TBD-*` because the order-code transition does not prove the shipped internal assembly;
- physical protected or separate routing for both start/feedback returns, because the PNOZ s4 does not detect shorts or cross-shorts there;
- selector position, seal and independent inspection on both PNOZ devices with power removed;
- FSR1/FSR2 fuse links, prospective fault current, conductor limits, interrupting capacity and protection coordination;
- KWD switched-A1 contact application, contact duty, brownout/recovery behavior, physical separation and internal-fault analysis;
- K1/K2 low-current electronic/regenerative DC interruption application and mirror-contact use;
- executed restart, held-control, welded-contact, short/cross-short, brownout, dropout, rail-decay and total stopping-time tests; and
- qualified ISO 12100 risk assessment, PLr/category allocation, ISO 13849 calculation/validation or accepted IEC 62061 route, common-cause analysis and signed review.

The matrix contains no `CLOSED`, `RELEASED`, `APPROVED`, or executed-pass disposition. Clean ERC does not close any item above.

## Primary source

- Pilz, *PNOZ s4 operating manual*, edition `21396-EN-23`, controlled PDF metadata creation 2026-06-17, portal file date 2026-06-22, acquired 2026-08-08: https://www.pilz.com/download/open/OM_PNOZ_s4_21396-EN-23.pdf

This document authorizes no ordering, wiring, fabrication, connection, motion, test, or energization.
