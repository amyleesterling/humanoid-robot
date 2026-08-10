# HR-V0 evaluation acquisition and Boston metrology quote packet P0.1

Document ID: **HR-V0-EVAL-ACQ-P0.1**

Date: 2026-08-08

Parents: `HR-V0-MECH-EVAL-P0.1`, `HR-V0-JOINT-MET-P0.1`

Requirements: `CFG-003`, `MECH-005`, `MECH-006`, `SAFE-006`, `SAFE-007`, `MASS-002`

Status: **PRELIMINARY - QUOTE AND AUTHORIZATION PACKET ONLY - NO ORDER, ASSEMBLY, MOTION OR ENERGIZATION RELEASE**

## Result

R85 turns R84's physical-acquisition dependency into a controlled purchase-decision and Boston-area metrology quote packet. It contains:

- three exact cost lines covering six physical articles;
- a current official ROBOTIS web-price snapshot of **$1,182.22 before shipping, tax and fees**;
- three purchase-authorization rows, all `NOT AUTHORIZED`;
- four Boston/Massachusetts provider research candidates, all `NOT CONTACTED` and `NOT SELECTED`;
- twenty-four mandatory provider questions;
- ten open commercial, technical and chain-of-custody hold points;
- an unsent capability/quote draft;
- separate authorization and provider-response templates; and
- a responsive web guide plus readable SVG.

No cart was submitted, payment information entered, order placed, provider contacted, quote received, article shipped or work authorized.

## Exact evaluation cost snapshot

| Exact article | Quantity | Official web price snapshot | Extended |
|---|---:|---:|---:|
| ROBOTIS XM540-W270-T, SKU `902-0137-000` | 2 | $482.89 | $965.78 |
| ROBOTIS FR13-H101K Set, SKU `903-0270-300` | 2 | $76.71 | $153.42 |
| ROBOTIS FR13-S102K Set, SKU `903-0269-300` | 2 | $31.51 | $63.02 |
| **Snapshot subtotal** | **6 articles** |  | **$1,182.22** |

Prices were rechecked on the live official product records on 2026-08-08. The subtotal excludes shipping, Massachusetts sales tax or exemption, duties, payment fees, insurance and price changes. The active pages do not establish a reliable allocated-stock commitment for every line. A dated cart or written quotation must close price and availability immediately before any separately authorized purchase.

## Separate decision authorities

Two decisions may not be collapsed:

1. The **program owner** may authorize exact purchase lines and a maximum spend after current total cost, seller, ship-to, payment, return and receiving controls are accepted.
2. A **qualified mechanical/metrology reviewer** may accept a provider, scope, instrument set, calibration traceability, fixture, method and uncertainty budget after reviewing written evidence.

Purchase approval does not select a metrology provider. Provider technical acceptance does not grant payment or shipping authority. Neither decision permits threaded assembly, connection, motion or energization.

## Provider capability screen

### East Coast Metrology / ECM, Topsfield

ECM publishes CMM part inspection/programming, precision measurement and 3D scanning services from Topsfield. A separate calibration page cites ISO/IEC 17025:2017 accreditation and A2LA certificate `3642.01`. The project must not infer that the proposed part inspection is within that accredited scope. The provider must return the current certificate/scope and state which exact quoted results are inside or outside it.

Current role: **primary CMM/dimensional and possible scan quote candidate - not selected**.

### Celero Partners, Woburn

Celero publishes 3D scanning for inspection/overlay and resolution up to `0.0012 in`. Published resolution is not measurement uncertainty, accuracy, traceability or accepted datum capability.

Current role: **envelope/point-cloud quote candidate only - not selected**. Critical axial and attachment faces remain CMM/contact evidence unless a qualified reviewer accepts a complete alternative method.

### 3D ProScan, Clinton

3D ProScan publishes industrial CT, dimensional/CMM inspection, part-to-CAD and assembly-analysis services and states ISO 9001 certification. ISO 9001 is not an ISO/IEC 17025 measurement scope.

Current role: **CT/scan and dimensional quote candidate - not selected**. Exact equipment, calibration, traceability, method validation and result-specific uncertainty remain required.

### Artisans Asylum, Allston

Artisans Asylum publishes machine-shop, metal-shop and tool-training capability. It does not publish the CMM, calibration, uncertainty or accredited-scope evidence needed by R84.

Current role: **fixture/training/loose-inspection capability inquiry only - not selected**. It may not be treated as the traceable metrology provider unless written evidence changes this state and a qualified reviewer accepts it.

## Provider response and work boundary

The quote register requires every candidate to answer `EAR-001..024`, including:

- legal identity, performing facility and responsible technical contact;
- exact equipment/serials, calibration certificates and due dates;
- current accreditation certificate/scope and in-scope/out-of-scope result mapping;
- article receipt, quarantine and chain of custody;
- CMM/scanner/angle/balance methods and uncertainty budgets;
- external mechanical angle/backlash method with no encoder data;
- non-damaging support and fixture method;
- acknowledgment that no threaded connection occurs before the separately signed R84 instruction;
- native/raw data, point clouds, transforms, residuals, processing logs and original photographs;
- nonconformance, teardown, post-inspection and return controls; and
- itemized price, assumptions, shipping, insurance, tax, lead time and expiration.

The generated draft is explicitly `UNSENT`. Sending it later would request information only; it would not authorize shipment or work.

## Controlled artifacts

- `procurement/hr-v0/evaluation-acquisition-p0.1/cost-snapshot.csv`
- `procurement/hr-v0/evaluation-acquisition-p0.1/purchase-authorization-register.csv`
- `procurement/hr-v0/evaluation-acquisition-p0.1/provider-capability-register.csv`
- `procurement/hr-v0/evaluation-acquisition-p0.1/metrology-rfq-question-register.csv`
- `procurement/hr-v0/evaluation-acquisition-p0.1/decision-hold-register.csv`
- `procurement/hr-v0/evaluation-acquisition-p0.1/source-register.csv`
- `procurement/hr-v0/evaluation-acquisition-p0.1/package-status.json`
- `procurement/hr-v0/evaluation-acquisition-p0.1/UNSENT-metrology-rfq-draft.md`
- `procurement/hr-v0/evaluation-acquisition-p0.1/HR-V0_evaluation-acquisition.svg`
- `procurement/hr-v0/evaluation-acquisition-p0.1/HR-V0_evaluation-acquisition-guide.html`
- `tests/forms/hr-v0-evaluation-acquisition-authorization-template.csv`
- `tests/forms/hr-v0-metrology-provider-response-template.csv`
- `tools/generate_hr_v0_evaluation_acquisition.py`
- `tools/check_hr_v0_evaluation_acquisition.py`

## Primary sources

- [ROBOTIS XM540-W270-T](https://robotis.us/dynamixel-xm540-w270-t/), live official product record rechecked 2026-08-08.
- [ROBOTIS FR13-H101K Set](https://robotis.us/fr13-h101k-set/), live official product record rechecked 2026-08-08.
- [ROBOTIS FR13-S102K Set](https://robotis.us/fr13-s102k-set/), live official product record rechecked 2026-08-08.
- [East Coast Metrology measurement services](https://eastcoastmetrology.com/services/), live provider page rechecked 2026-08-08.
- [East Coast Metrology calibration services](https://eastcoastmetrology.com/lp/metrology-calibration-services/), live provider page rechecked 2026-08-08; the cited certificate/scope must be obtained and mapped to the quoted work.
- [Celero Partners 3D scanning services](https://celeropartners.com/3d-scanning-services/), live provider page rechecked 2026-08-08.
- [3D ProScan metrology services](https://www.3dproscan.com/metrology-services.html), live provider page rechecked 2026-08-08.
- [Artisans Asylum tool testing and safety training](https://www.artisansasylum.com/tool-testing-safety-training), live makerspace page rechecked 2026-08-08.

## Release boundary

This packet enables a controlled human decision; it is not the decision. It does not authorize checkout, payment, purchase, provider contact, shipment, metrology work, temporary assembly, production assembly, source connection, encoder readout, motion, fabrication, operation around children or energization.
