# R116 validation record

Status: **PRELIMINARY - NOT APPROVED FOR FABRICATION OR ENERGIZATION**

## Scope

R116 issues `HR-V0-PNOZ-CONF-P0.1`, synchronizes the current Electrical V3-P1.13 safety-relay narrative with its native nets, and records the anonymous complete-gripper source route exhausted without a CAD payload. Sol's resupplied verdict is reconciled as the existing R12 review and is not double-counted.

## Manufacturer-source control

The controlled Pilz `PNOZ_s4_21396-EN-23.pdf` is 2,428,340 bytes and hashes to `4B6E4768CEFAEDAF54F006347D32A8A04964B59A16F3616D8AC43698D3626BB4`. It begins with a PDF signature. The source manifest distinguishes document edition `21396-EN-23`, PDF metadata creation date 2026-06-17, portal file date 2026-06-22 and access date 2026-08-08.

The source-to-project matrix has fourteen sequential rows, all `PARTIAL` or `OPEN`. No row is `CLOSED`, `RELEASED`, `APPROVED` or an executed pass.

## Native ECAD validation

The V3 generator rebuilt all thirteen native pages and synchronized outputs. The exact-net checker passed with 76 component blocks, 296 modeled terminals, 64 named connected nets, 39 deliberate unconnected nets, 257 unique wire labels and 64 unresolved component/interface rows. KiCad ERC remains 0 errors / 0 warnings. This is connectivity and annotation evidence only.

The new checker proves the following current V3-P1.13 facts directly from `net-schedule.csv`:

- KWD terminals are absent from `SR1_S12` and `SR1_S22`;
- SR1 RESET runs from S12 through `S1:TBD-R1/TBD-R2` to S34;
- SR1 13-14 and 23-24 separately gate SRA1's two input channels;
- SRA1 ARM/EDM runs through `S2:TBD-A1/TBD-A2`, K1 21-22 and K2 21-22 to S34; and
- the two KWD NO contacts gate only `SR1:A1` and receive zero functional-safety credit.

## Visual and interactive QA

The regenerated V3 E-stop/RESET and ARM/watchdog pages were rendered from the native PDF at 180 dpi and visually inspected. Warnings, titles, component references, terminal numbers, net labels, wire numbers, notes and title blocks are readable and unclipped. The pages clearly show S0 direct to SR1, RESET unable to command K1/K2, the two-contact SR1 A1 gate and the distinct SRA1 ARM/EDM stage.

Installed Google Chrome rendered the responsive guide at `1440 x 1000` and `390 x 844`. Both layouts had zero page-width overflow. Computed body/control text was 16 px, warning text 18 px, metadata 14 px and badges 12 px. All six cards were visible in the unfiltered view; the Open evidence filter showed exactly two cards. Desktop and mobile captures were visually inspected and were legible and unclipped.

## Repository and readiness validation

All **69 unique repository checker programs passed**, including the final deterministic-manifest check. Traceability resolves 81 requirements, 40 risks, 110 procedures and 57 release/walking-document procedure references. The deterministic release manifest contains **1,563 package files** before final clean-commit reproduction.

The intentional command `tools/check_energization_gates.py --through-stage E2 --require-ready` returned the expected exit code `2`: zero of the 21 gates applicable through E2 are closed, all 21 remain partial, and all 30 total gates remain unresolved. The package correctly refuses an energization-readiness claim.

Received terminals, physical protected routing, selector settings, FSR1/FSR2 links, protection coordination, KWD switched-A1 application, K1/K2 interruption and mirror-contact application, fault injection, total stopping time, PLr/category allocation, ISO 13849 validation and signed qualified review remain open. No validation result authorizes ordering, wiring, fabrication, connection, motion, testing or energization.
