# HR-V0 DXL harness allocation P0.1

> **PRELIMINARY - NOT APPROVED FOR SUPPLIER UPLOAD, QUOTATION, PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, MOTION, OR ENERGIZATION**

Identifier: `HR-V0-DXL-HARNESS-ALLOC-P0.1`  
Round: R153  
Date: 2026-08-09

## Result

Current ROBOTIS product pages state that each held XM540/XM430 actuator package includes one assembled 180 mm JST-JST X3P cable. R153 therefore allocates three included branch cables as integrated `BOM-086` and removes six duplicate loose EHR-3 housings and eighteen duplicate contacts.

`BOM-061` now covers only one custom U2D2-to-DXL-STAR `JC1` cable. It carries GND from cavity 1 and DATA from cavity 3. Cavity 2 is empty at both ends; the U2D2 must not inject actuator power.

## Boundary retained

JST rates EH contacts at 3 A under the cited series conditions, while ROBOTIS publishes 4.4 A XM540 stall current at 12 V and warns that stall values are momentary. This source comparison is an open qualification conflict, not a project current rating. Harness routing, length, conductor, termination, protection, inrush, duty cycle, bundling, ambient, temperature rise, voltage drop, fault behavior and received-article evidence remain unresolved.

The controlled package is [the interactive guide](../release/hr-v0/dxl-harness-allocation-p0.1/index.html). It includes source records, allocation parity, a controller pin map, eight unsent manufacturer questions, ten blank acceptance rows, fourteen open holds, receiving and current-qualification templates, and deterministic hashes.
