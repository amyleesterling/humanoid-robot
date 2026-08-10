# HR-V0 complete Evaluation Batch A acquisition decision P0.1

**PRELIMINARY - EVALUATION ACQUISITION DECISION ONLY - NOT APPROVED FOR FABRICATION, CONNECTION, MOTION, OR ENERGIZATION**

Identifier: `HR-V0-EVAL-BATCH-A-ACQ-P0.1`

Round: R145

Date: 2026-08-09

## Result

R145 reconciles every line in controlled `EVALUATION-BATCH-A` into one acquisition decision package. The packet contains 17 evaluation lines, 21 physical units and four independently authorizable lots:

| Lot | Purpose | Lines | Units | Known current manufacturer-price floor | Quote-required lines |
|---|---|---:|---:|---:|---:|
| LOT-A | Joint-stack metrology articles | 5 | 6 | $1,182.22 | 0 |
| LOT-B | Bench mechatronics and gripper articles | 3 | 3 | $662.07 | 0 |
| LOT-C | Safety and control evaluation articles | 7 | 10 | $20.44 | 6 |
| LOT-D | External power-source evaluation articles | 2 | 2 | $0.00 | 2 |
| **Total** |  | **17** | **21** | **$1,864.73** | **8** |

The dollar result is a price floor, not a budget or landed-cost estimate. It includes only unit prices visible on current official manufacturer pages on 2026-08-09. It excludes every quote-required line, shipping, Massachusetts sales tax or exemption, duties, payment fees, insurance and later price changes. A `$0.00` known extension means no current manufacturer price was exposed; it never means the article is free.

## Decision boundary

Every lot and line remains `NOT AUTHORIZED`, `NOT ORDERED` and `NOT RECEIVED`. Before a human purchase decision, the packet requires a dated cart or written quote, allocated-stock confirmation, seller identity, quote expiration, ship-to location, receiving owner, exact approved lot/line IDs and maximum spend.

If later approved, the permitted action is limited to receipt, quarantine, identification, inventory, photography and the separately authorized unpowered receiving/evaluation procedure. Purchase approval does not authorize production use, fabrication, wiring, source connection, encoder access, torque enable, motion, child access or energization.

## Current official-source observations

- [ROBOTIS U2D2](https://www.robotis.us/u2d2/) exposed SKU `902-0132-000` and $36.92.
- [ROBOTIS XM540-W270-T](https://robotis.us/dynamixel-xm540-w270-t/) exposed SKU `902-0137-000` and $482.89 each.
- [ROBOTIS XM430-W350-T](https://www.robotis.us/dynamixel-xm430-w350-t/) exposed SKU `902-0124-000` and $310.39.
- [ROBOTIS OpenMANIPULATOR-X Frame Set](https://www.robotis.us/openmanipulator-x-frame-set-rm-x52/) exposed SKU `905-0023-000` and $314.76.
- [ROBOTIS FR13-H101K Set](https://robotis.us/fr13-h101k-set/) exposed SKU `903-0270-300` and $76.71 each.
- [ROBOTIS FR13-S102K Set](https://www.robotis.us/fr13-s102k-set/) exposed SKU `903-0269-300` and $31.51 each.
- [IDEC black HW1B-M1F10-B](https://www.idec.com/en-us/switches-indicator-lights/switches-pushbuttons/pushbuttons-pilot-lights/hw-22mm-heavy-duty/hw1b-m1f10-b) exposed $20.44 MSRP.
- The current official Pilz, Schneider Electric, IDEC E-stop/green button, Raspberry Pi, Phoenix Contact, Mean Well and GlobTek records support exact identity but did not expose a complete current manufacturer price usable here. Those eight lines remain `QUOTE REQUIRED`.

Page presence and an add-to-cart control do not prove allocated stock, lead time, application acceptance, received identity or total cost.

## Controlled outputs

- `procurement/hr-v0/evaluation-batch-a-acquisition-p0.1/line-register.csv`
- `procurement/hr-v0/evaluation-batch-a-acquisition-p0.1/lot-register.csv`
- `procurement/hr-v0/evaluation-batch-a-acquisition-p0.1/purchase-authorization-register.csv`
- `procurement/hr-v0/evaluation-batch-a-acquisition-p0.1/source-register.csv`
- `procurement/hr-v0/evaluation-batch-a-acquisition-p0.1/package-status.json`
- `procurement/hr-v0/evaluation-batch-a-acquisition-p0.1/index.html`
- `tests/forms/hr-v0-evaluation-batch-a-authorization-template.csv`
- `tools/generate_hr_v0_evaluation_batch_a_acquisition.py`
- `tools/check_hr_v0_evaluation_batch_a_acquisition.py`

This packet closes no release or energization gate. It supplies the controlled human decision surface needed to begin acquiring physical evidence.
