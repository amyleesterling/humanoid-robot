# HR-V0 E2 control-only grounding and bonding boundary P0.1

> **PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION**

Identifier: `HR-V0-E2-GND-BOUNDARY-P0.1`

Review/control round: R227

Date: 2026-08-11

## Outcome

This package freezes one narrow, configuration-specific interpretation for the future E2 control-only commissioning stage:

- the two factory AC adapters remain intact and outside the project enclosure;
- only the 24 V control domain through `J24` and the 5.1 V compute domain through USB-C may enter the project enclosure;
- no project mains conductor or protective-earth conductor enters the modeled E2 enclosure;
- `PSA1`, its AC cord, `JA1`, all actuator-power plugs and every `ACT_12V*` conductor are physically absent, disconnected or protected and must remain at zero volts;
- `SP1` remains DNP and prohibited;
- `JFRAME1` remains DNP for E2;
- `SAFETY_0V` and `COMPUTE_0V` remain separate and have no project-defined bond to each other, frame, shields or PE; and
- panel metalwork receives no protective-bonding or insulation safety credit from this document.

This is a controlled design boundary, not permission to plug in either adapter. The exact premises, received hardware, physical installation, continuity/insulation limits, first-fault analysis, results and qualified authorization remain open.

## Native ECAD reconciliation

The exact `PSA1`, `PSU2`, `J24`, `PSU3`, `SP1` and `JFRAME1` connector-schedule subset contains 26 rows and is identical between current P1.15 and unaccepted P1.18.

Five grounding-relevant named nets were compared separately:

| Net | P1.15 connections | P1.18 connections | Disposition |
|---|---:|---:|---|
| `ACT_0V_PE_BONDED` | 24 | 24 | Identical; outside energized E2 boundary |
| `SAFETY_0V` | 41 | 49 | P1.18 intentionally adds `XD0:LINE` and `XD0:01..07` distribution terminals |
| `COMPUTE_0V` | 5 | 5 | Identical; USB-shell physical relationship remains open |
| `ROBOT_FRAME` | 1 | 1 | Identical one-terminal placeholder |
| `CABLE_SHIELD_TERM` | 1 | 1 | Identical one-terminal placeholder |

Therefore the package does not falsely assert full-net identity. It records the exact eight-terminal `SAFETY_0V` P1.18 topology addition while preserving P1.15 as current and P1.18 as unaccepted.

## Source facts and limits

Current primary records were rechecked on 2026-08-11:

- GlobTek's live exact-model record for `WR9QI1660YL4NKITR6B` identifies 24 V, 1.66 A, 40 W, Q-series input, YL4/C40337 output, pin 1 `+V`, pin 3 `-V (Shield)`, and Double Insulation. The exact specification is Rev B. These records do not prove the received unit, blade retention, installed polarity or final-machine compliance.
- Raspberry Pi's 27 W product brief was published October 2023 and the portal record was updated 2025-10-06. It identifies the US/Canada Type-A plug and the 5.1 V/5 A USB-C family. The US-model UL authorization and CB certificate are dated 2023-09-20. None establishes the received SKU, condition, retention or USB-shell/DC-return continuity.
- MEAN WELL `GST280A-SPEC`, dated 2026-04-03, still identifies the C14 actuator source and its manufacturer-internal `-V`/AC-FG relationship. That domain is prohibited and physically absent at E2; the record does not close later actuator-domain grounding or application review.

## What the E2 boundary does not prove

The statement “no project PE conductor enters the E2 enclosure” is conditional on the exact modeled configuration: no mains source or conductor inside, external factory adapters unmodified, and the complete actuator source/domain absent. It is not a conclusion that metalwork never requires bonding, that protective bonding is unnecessary for later stages, or that the configuration complies with every applicable code.

Before any controlled E2 run, a qualified reviewer must accept:

1. the exact Boston premises/receptacle/branch/OCPD/GFCI/grounding facts;
2. received PSU2 and PSU3 identities, marks, condition and manufacturer cords/blades;
3. physical absence of the entire actuator power domain;
4. DNP proof for `SP1` and `JFRAME1`;
5. the complete metalwork and exposed-conductive-part inventory;
6. numeric continuity/insulation/zero-voltage limits, instruments and uncertainty;
7. the measured USB-shell, return, frame and shield relationships;
8. the control-domain electric-shock, fire, fault-clearing and noninterference first-fault analysis; and
9. the configuration-specific EG-022 authorization with all prerequisite evidence current and accepted.

Fifteen inspection/test records remain `UNEXECUTED`; all result and evidence fields are blank. Twelve holds remain open. `EG-001`, `EG-004`, `EG-016` and `EG-022` remain partial.

## Controlled artifacts

- [Interactive guide](../release/hr-v0/e2-grounding-boundary-p0.1/index.html)
- [Engineering register](../electrical/grounding/hr-v0-e2-grounding-boundary-p0.1/)
- [Gate evidence supplement](../requirements/hr-v0-gate-evidence-supplement-r227.csv)
- [R227 validation record](reviews/2026-08-11-r227-validation-record.md)
- [Independent review request](reviews/2026-08-11-r227-independent-review-request.md)

No procurement, fabrication, assembly, connection, powered testing, motion, functional-safety approval or energization authority is created.
