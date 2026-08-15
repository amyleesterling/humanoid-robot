# HR-V0 P1.21 SRA1-supply watchdog candidate P0.1

> **PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION**

Identifier: `HR-V0-P121-SRA1-SUPPLY-WD-P0.1`

Round: R234

## Decision

Sol R12 correctly identified the single ordinary watchdog contact as an unsafe architecture dependency in the reviewed baseline. P1.20 improved single-contact fault tolerance but placed uncredited ordinary contacts inside both PNOZ input loops. R234 rejects a contemplated low-side contactor-return alternative because the existing watchdog source may restore its ordinary outputs after three healthy edges; with SRA1 still latched, that arrangement could restore coil power without a new monitored ARM.

P1.21 instead:

- restores direct `SR1:14 -> SRA1:S12` and `SR1:24 -> SRA1:S22` paths;
- keeps `SR1:A1` directly on `SAFETY_24V`;
- series-connects `KWD1:11-14` and `KWD2:11-14` only between `SAFETY_24V` and `SRA1:A1`; and
- leaves separate SRA1 outputs and K1/K2 series actuator-power interruption unchanged.

A successful watchdog dropout therefore power-cycles SRA1. Heartbeat restoration may repower SRA1, but its selected falling-edge monitored start still requires a later physical ARM. A single welded KWD contact is defeated by the other opening. A dual weld, external bypass or shared stuck-valid command loses only the uncredited diagnostic: direct SR1-controlled SRA1 inputs remain the modeled SF-01 authority.

## Evidence produced

- thirteen native KiCad pages, native netlist and PDF export;
- KiCad 10.0.5 ERC: zero errors and zero warnings;
- exactly seven changed terminal assignments and 333 unchanged assignments;
- 84 modeled component blocks, 82 BOM rows, 340 terminal rows and 106 named nets;
- fourteen fault cases;
- four explicit SF-01/SF-03/DF-01/PG-01 allocation boundaries;
- nine source/derived supply-contact screens; and
- eleven open holds.

The Pilz 2.5 W nominal supply figure gives a paper 0.10417 A current at 24 V. Against Phoenix item 2967060's published 5 V/10 mA minimum load and 15 A for 300 ms maximum inrush envelope, the paper screens are 4.8x voltage, 10.42x nominal current, 30x startup current and 60x startup duration. These comparisons do not prove life, wetting, brownout behavior, switching suitability or application approval.

## Still open

P1.21 is not current. P1.15 remains the controlled electrical candidate. Manufacturer/qualified justification for switching the PNOZ A1 supply, protected routing, received identity, brownout/recovery tests, fault injection, stopping response, released guard containment, PLr/SIL/category allocation, independent review, qualified validation and separate work authorization all remain open. Sol's original 18 BLOCKER / 30 MAJOR / 8 MINOR totals remain historical review evidence; zero blocker has qualified closure.

> **PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION**
