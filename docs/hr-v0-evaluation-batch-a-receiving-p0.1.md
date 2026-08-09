# HR-V0 Evaluation Batch A unit receiving campaign P0.1

**PRELIMINARY - NOT APPROVED FOR FABRICATION, CONNECTION, MOTION, OR ENERGIZATION**

Identifier: `HR-V0-EVAL-BATCH-A-RCV-P0.1`

Date: 2026-08-09

Round: R146

## Result

R146 converts the 17 controlled Evaluation Batch A lines into 21 pre-identified physical-unit records. Each unit has one deterministic quarantine label, twelve receiving-traveler records and seven evidence-file placeholders. The generated package therefore contains:

- 21 unit records;
- 252 unit/step traveler records;
- 147 evidence placeholders;
- 21 quarantine-label records; and
- zero authorized, ordered, received, executed or machine-accepted units.

This removes the generic instruction to duplicate an anonymous receiving row after delivery. It does not claim that a shipment, article, nameplate, serial number, lot, measurement, photograph or qualified disposition exists.

## Twelve-step receiving sequence

Every unit is bound to the same fail-closed sequence: authority/baseline verification, shipment intake, unopened-package evidence, count/allocation, identity capture, visible-condition inspection, package-content inventory, item-specific unpowered route, evidence hashing, independent identity check, qualified disposition, and controlled storage/handoff.

At `RCV-07`, only separately authorized unpowered observations may be executed. Connector mating, source connection, encoder access, torque enable, commanded motion, installation and machine acceptance remain outside this campaign.

## Evidence and quarantine rule

Each unit receives seven expected evidence categories: shipment/container, manufacturer label/order code, whole-unit overview with scale, unit markings, unmated connector/terminal view, included contents, and damage/final disposition. The template requires raw filenames, SHA-256 values, UTC capture times and named recorders. Missing or ambiguous identity opens a deviation and leaves the unit quarantined.

The printable labels begin in `NOT RECEIVED - HOLD`. A label is an identity-control aid, not a disposition. Only a completed record with a named qualified reviewer may state `ACCEPTED FOR NAMED UNPOWERED EVALUATION ONLY`; no R146 outcome can release machine installation, wiring, connection, motion or energization.

## Controlled artifacts

- `tests/receiving/hr-v0-evaluation-batch-a-receiving-p0.1/receiving-unit-register.csv`
- `tests/receiving/hr-v0-evaluation-batch-a-receiving-p0.1/receiving-traveler.csv`
- `tests/receiving/hr-v0-evaluation-batch-a-receiving-p0.1/evidence-file-manifest-template.csv`
- `tests/receiving/hr-v0-evaluation-batch-a-receiving-p0.1/quarantine-label-register.csv`
- `tests/receiving/hr-v0-evaluation-batch-a-receiving-p0.1/package-status.json`
- `tests/forms/hr-v0-evaluation-batch-a-unit-receiving-template-p0.1.csv`
- `release/hr-v0/evaluation-batch-a-receiving-p0.1/index.html`
- `tools/generate_hr_v0_evaluation_batch_a_receiving.py`
- `tools/check_hr_v0_evaluation_batch_a_receiving.py`

## Gate effect

`EG-003` remains **partial**. R146 supplies an executable evidence scaffold but no received identity, measurement, application acceptance, released machine BOM or signed configuration review. All other energization gates are unchanged.
