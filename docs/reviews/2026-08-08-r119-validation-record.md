# R119 validation record

Status: **PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, CONNECTION, TESTING, OR ENERGIZATION**

## Scope

R119 issues `HR-V0-COMPUTE-SEL-P0.1` and Electrical V3-P1.14. It resolves only the exact held identities for PI1/BOM-001 (`SC1112`) and PSU3/BOM-002 (`SC1158`). Sol's supplied verdict remains independent round R12 and is not double-counted.

## Primary-source control

Seven current Raspberry Pi source records are controlled. The manufacturer product configurator set to Raspberry Pi 5 8GB RAM unit-only and United States exposes an approved-reseller TME link containing `SC1112`. The manufacturer supply configurator set to US Type A, black and United States exposes approved DigiKey and Mouser links containing `SC1158`. PIP family lists corroborate both stock codes but are explicitly not used to infer memory, region or color from list order.

The Raspberry Pi 5 product brief supports the product-family 40-pin header and 5 V / 5 A USB-C input. The 27W supply product brief `RP-008245-DS-1`, published October 2023 and portal-updated 2025-10-06, supports the US/Canada Type-A family, 5.1 V / 5 A output and captive 1.2 m 17 AWG cable. The current USB-PD whitepaper `RP-009856-WP-1` supplies profile context. None supplies Project Button application approval.

## Configuration and ECAD results

The system BOM remains 78 groups. BOM-001/BOM-002 move from broad selection-required groups to exact-candidate holds, producing 17 evaluation candidates, 27 exact-candidate holds, three grouped-component holds, 26 selection-required groups, four historical/DNP exclusions and one integrated item.

Electrical V3-P1.14 contains 13 native pages, 76 component blocks, 296 modeled terminals, 64 connected named nets, 39 deliberate unconnected nets, 257 unique wire labels and 63 unresolved component/interface rows. The P1.13 net/terminal/safety topology is unchanged. KiCad 10.0.5 parses the project and reports ERC 0 errors / 0 warnings. Native PDF and 13 SVG pages regenerate successfully.

## Evidence controls and guide QA

The interface register has twelve rows: two exact candidates, one partial application field and nine open fields. The receiving template has sixteen rows, all `NOT_EXECUTED` and `NOT_AUTHORIZED`, with blank actual values and evidence hashes.

The interactive guide rendered at 1440 x 1000 and 390 x 844 with zero page-width overflow. Computed body text was 16 px, metadata 14 px and badges 12 px. Desktop and mobile captures plus changed KiCad sheets 01 and 09 were visually inspected; exact identities, warnings and nets were legible and unclipped.

## Repository and readiness validation

All **72 unique repository checker programs passed**, including the final deterministic-manifest check. The intentional command `tools/check_energization_gates.py --through-stage E2 --require-ready` returned the required exit code `2`: all 21 gates applicable through E2 remain partial and none is closed.

Cooling, storage/image, heartbeat and USB-C harnesses, retention, site/receptacle, installed load, PD negotiation, startup/inrush/brownout/recovery, thermal/airflow, grounding/EMC, runtime, HIL, received hardware, physical test and qualified review remain open. `EG-003` and `EG-010` remain partial. No result authorizes purchase, fabrication, connection, powered testing, motion or energization.
