# HR-V0 compute and compute-power selection P0.1

> **PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, CONNECTION, OR ENERGIZATION.**

Identifier: `HR-V0-COMPUTE-SEL-P0.1`

Electrical baseline: `Project Button Electrical V3-P1.14`

Date: 2026-08-08

## Decision

R119 resolves two order-code fields without releasing either item:

- `PI1` / `BOM-001`: Raspberry Pi 5, 8GB RAM, unit only, stock code `SC1112`.
- `PSU3` / `BOM-002`: Raspberry Pi 27W USB-C Power Supply, US Type A, black, stock code `SC1158`.

The identities come from Raspberry Pi's own current product configurators. With the Pi 5 configurator set to **8GB RAM - Unit only** and **United States**, a manufacturer-generated approved-reseller link identifies `SC1112`. With the 27W supply configurator set to **US Type A**, **black**, and **United States**, manufacturer-generated DigiKey and Mouser links identify `SC1158`. The visible Product Information Portal family lists corroborate that both are Raspberry Pi stock codes, but those lists alone do not map memory, region, or color; the project does not infer the mapping from list order.

## What remains open

Exact identity does not close application suitability. The package still requires received markings and revision, approved purchase trace, active cooling, storage and image control, cable/harness parts, mechanical retention, site/receptacle review, USB-C strain relief, installed load, USB PD negotiation, startup/inrush/brownout/recovery, thermal/airflow, grounding/EMC, GPIO runtime, heartbeat timing/fault behavior, physical tests, and qualified review.

The Raspberry Pi heartbeat remains ordinary control with **zero functional-safety credit**. It cannot restore motion eligibility by itself. E-stop recovery still requires the separately modeled monitored RESET and later ARM/EDM sequence.

## Configuration effects

Electrical V3 advances from P1.13 to P1.14 only for the `PI1` and `PSU3` identity/evidence fields. The direct dual-channel E-stop, watchdog-gated `SR1:A1`, RESET, ARM/EDM, contactor, actuator-power and PCB connectivity are unchanged. PCB-P0.6 remains tied to its controlled Electrical V3-P1.13 topology and is not a fabrication release.

`BOM-001` and `BOM-002` advance from grouped selection-required entries to exact-candidate holds. `EG-003` and `EG-010` remain partial because received/application evidence and the rest of the machine BOM are incomplete.

## Controlled artifacts

- `electrical/vendor/raspberry-pi/compute-r119/source-manifest-p0.1.csv`
- `bom/hr-v0-compute-selection-p0.1.csv`
- `electrical/interfaces/hr-v0-compute-power-selection-p0.1.csv`
- `tests/forms/hr-v0-compute-receiving-template-p0.1.csv`
- `release/hr-v0/compute-selection-p0.1/index.html`
- `tools/check_hr_v0_compute_selection_p01.py`

Passing ERC or repository checks proves only modeled consistency. It is not approval to buy, connect, power, test, fabricate, or energize anything.
