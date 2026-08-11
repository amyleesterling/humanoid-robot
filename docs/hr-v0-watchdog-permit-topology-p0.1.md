# HR-V0 watchdog permit topology proof P0.1

> **PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION**

Identifier: `HR-V0-WD-PERMIT-TOPOLOGY-P0.1`

Control round: R225

Date: 2026-08-11

## Decision

The current P1.18 source does **not** contain one watchdog permit contact. `KWD1:11-14` and `KWD2:11-14` are two ordinary normally-open contacts in series between `SAFETY_24V` and `SR1:A1`:

```text
SAFETY_24V -> KWD1:11-14 -> WD_SUPPLY_INTERMEDIATE
             -> KWD2:11-14 -> SR1_A1_WD_GATED -> SR1:A1
```

Neither KWD reference appears on the direct E-stop input-loop nets `SR1_S11`, `SR1_S12`, `SR1_S21` or `SR1_S22`. Those nets connect the two S0 normally-closed channels directly to the corresponding SR1 input terminals.

The package machine-checks the native sheet, KiCad 10.0.5 netlist and wire-number table. It also evaluates nine Boolean contact-state cases. A single welded or internally bypassed KWD contact does not preserve the modeled `SR1:A1` supply path when the other series contact opens. A dual weld/bypass can preserve it and remains explicitly hazardous.

## What this does not prove

This topology result does not turn `DF-01`, KWD1 or KWD2 into a safety function. Both relays are ordinary relays and retain zero safety credit. The package does not prove:

- independence from the shared watchdog controller, supply, PCB, enclosure or wiring;
- the contact application's steady, inrush, suppression or endurance suitability;
- received identity, polarity or terminal/contact state;
- protected routing or exclusion of a physical bypass around both stages;
- contact opening, relay release, rail decay, actuator torque decay or stopping time;
- diagnostic coverage, common-cause score, category, PLr, achieved PL or SIL; or
- any physical fault injection or qualified validation.

P1.15 remains the current accepted electrical candidate. P1.18 remains an unaccepted topology candidate. The summarized independent-review assertion is reconciled only against current source; reviewer closure is not claimed.

## Controlled evidence

- interactive guide: `release/hr-v0/watchdog-permit-topology-p0.1/index.html`;
- topology endpoints: `topology-register.csv`;
- nine Boolean cases: `fault-truth-table.csv`;
- current-source review disposition: `finding-reconciliation.csv`;
- six source records and hashes: `source-register.csv`;
- eight open holds: `open-holds.csv`;
- generator/checker: `tools/generate_hr_v0_watchdog_permit_topology_p01.py` and `tools/check_hr_v0_watchdog_permit_topology_p01.py`.

## Primary-source boundary

Phoenix Contact item `2967060`, `PLC-RSC-24DC/21-21`, official product record with data-maintenance date 2026-04-01, rechecked 2026-08-11: <https://www.phoenixcontact.com/en-us/products/relay-module-plc-rsc-24dc21-21-2967060>

The official record supports the candidate terminal/contact identity only. It does not classify the relay as force-guided or safety-rated and does not approve its Project Button application.

## Release consequence

The current-source form of the “single watchdog contact” assertion is contradicted by exact P1.18 connectivity. `EG-004` and `EG-012` receive additional partial evidence but remain partial. Eight physical, allocation and review holds remain open. No physical work or energization authority is created.
