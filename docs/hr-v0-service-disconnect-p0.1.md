# HR-V0 DC service-disconnect application screen P0.1

> **PRELIMINARY - SELECTION REQUIRED - NOT APPROVED FOR PROCUREMENT, FABRICATION, WIRING, OR ENERGIZATION**

Date: 2026-08-07

Document ID: `HR-V0-SD-P0.1`

Applies to: Electrical `V3-P1.7`, reference `SD1`, net path `ACT_12V_FUSED -> SD1 -> K1_P1_IN`

## Decision

`SD1` remains **SELECTION REQUIRED**. It is a manual service-isolation device in the positive 12 V actuator path. It is not the emergency stop, receives no functional-safety credit, and may not be used to bypass `K1`/`K2` or their monitored restart sequence.

Blue Sea Systems `6004200` is a dimensioned screening candidate only. It is not frozen into the BOM or KiCad source because the current evidence does not establish the project's conductor/lug system, available fault current, normal/load-break duty, regeneration behavior, lockout method, installed accessibility, enclosure integration, or Boston/Massachusetts application acceptance.

## Current manufacturer facts

The official Blue Sea Systems page identifies `6004200` as a single-circuit ON/OFF switch with locking key, 48 VDC maximum, 3/8-inch/M10 studs, and a published 300 A continuous rating. The official instructions state that the published rating requires one 4/0 AWG cable per terminal and that reducing cable size reduces the rating. They also instruct the operator to turn loads off before switching OFF and not to switch OFF while an engine is running. Those instructions mean the project may not treat the switch as a proven loaded-interruption or emergency-stop device.

Official drawing `20017 M SWITCH`, revision 0, covers part numbers `6004` and `6004200`. It shows a nominal `74.93 x 74.93 mm` face/body envelope, a `67 mm` front-panel hole, a `59 mm` rear-panel hole, and an approximately `101.57 mm` overall depth figure. These dimensions support only an early placement screen. They do not release a panel cutout, mounting method, conductor bend, terminal cover, door loom, or service clearance.

## Why no selection is released

1. The actual GST280A12-C6P current-limit/foldback behavior and prospective fault current at `SD1` have not been measured.
2. Operating current, simultaneous stall/acceleration case, regeneration/bus-rise behavior, and the intended make/break duty are not closed.
3. Exact conductor, insulation, length, ambient, bundling, lug order code, crimp tool, stud stack, bend radius, torque process, and pull-test criteria are open.
4. A locking key is not evidence of a padlockable energy-isolation procedure. Key-removal positions, exclusive-key control, zero-energy verification, and jurisdictional lockout acceptance require a qualified disposition.
5. Door, side-wall, external-surface, and backplate placements create different access, flexible-conductor, strain-relief, depth, and human-factors consequences. No location is released.
6. The manufacturer instructions are marine-product instructions and explicitly call for a marine electrical professional. They do not establish suitability for this robot or the Boston installation.

## Required closure evidence

- exact candidate and order code, current data sheet/instructions/drawing, and manufacturer application response;
- measured source fault/current-limit envelope and released actuator operating/regeneration envelope;
- switching-duty statement covering normal OFF, faulted OFF, and prohibited loaded-interruption cases;
- exact conductor/lug/terminal stack, crimp tooling, torque, insulation, bend/service space, strain relief, and thermal result;
- selected physical location with received dimensions, rear cover, guarding, labeling, accessibility, and zero-energy verification point;
- documented lockout/isolation method and qualified Boston/Massachusetts electrical and safety disposition;
- received identity, continuity, voltage-drop, temperature-rise, abnormal-operation, and post-test inspection records;
- synchronized KiCad terminals, wire schedule, BOM, panel layout, assembly traveler, and commissioning procedure.

The controlled blank execution record is `tests/forms/hr-v0-service-disconnect-receiving-application-template.csv`. No row in that form is executed.

## Primary manufacturer evidence

- Blue Sea Systems `6004200` product page, live page with no formal revision displayed, accessed 2026-08-07: https://www.bluesea.com/products/6004200/Single_Circuit_ON-OFF_with_Locking_Key_-_Black
- Blue Sea Systems `6004 / 6004200` instructions, current file accessed 2026-08-07: https://d2pyqm2yd3fw2i.cloudfront.net/files/resources/instructions/6004_web_version.pdf
- Blue Sea Systems dimension drawing `20017 M SWITCH`, revision 0, part numbers 6004/6004200, accessed 2026-08-07: https://d2pyqm2yd3fw2i.cloudfront.net/files/resources/dimensioned_drawing/6004.pdf

Manufacturer facts establish a screening candidate and its limits only. They do not select `SD1`, approve the application, establish lockout compliance, or authorize energization.
