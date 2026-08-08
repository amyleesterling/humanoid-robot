# HR-V0 elbow actuator and moving-mass trade P0.1

> **PRELIMINARY — NOT APPROVED FOR QUOTATION, PROCUREMENT, FABRICATION, ASSEMBLY, MOTION, CONNECTION, OR ENERGIZATION.**

Date: 2026-08-08

Identifier: `HR-V0-ELBOW-TRADE-P0.1`

Controlled parent: `HR-V0-ARM-ARCH-P0.7` under `HR-V0-MECH-P0.6`

## Decision

Hold custom-metal quotation of P0.7 until the elbow/moving-mass architecture is dispositioned. P0.7 remains the controlled, unreleased geometry; this record does not silently replace its actuator, frames, interfaces, hard stop, limits, firmware, electrical source, or drawings.

Develop a separately identified exact-coordinate P0.8 comparison branch using an XM430-W350-T elbow and compatible FR12 geometry. That branch may be selected only after the twelve holds in `release/hr-v0/elbow-actuator-trade-p0.1/architecture-holds.csv` close and qualified reviewers accept the resulting configuration. No existing P0.7 custom part should be quoted first and redesigned afterward.

## Why the current route is held

`MASS-002` permits 750 g for everything rotating about J1, including the 100 g payload and excluding only the fixed shoulder actuator/base. P0.7 already accounts for 692.758 g, leaving 57.242 g for both H101 frame/idler sets, the S102 frame, all fasteners and spacers, the bumper and retention, the full gripper mechanism/pads/guard, connectors, guides, strain relief, and moving cable. Both link allocation buckets are already exceeded.

The R70 relief study would increase provisional headroom to 115.225 g, but it remains nonselected and lacks the required material, local-load, fatigue/impact, tolerance, FAI, received-fit, mass/COM, proof, and qualified-review evidence. Neither 57.242 g nor 115.225 g is a mass pass.

Replacing only the catalog elbow mass in the same-axis sensitivity saves 83.000 g: XM540 is published as 165 g and XM430 as 82 g. The incomplete subtotal would become 609.758 g with 140.242 g provisional headroom, or 551.775 g with 198.225 g provisional headroom if the separately unselected R70 relief were also credited. Those are planning sensitivities, not P0.8 mass properties; FR12 frame mass, adapters, cabling, fasteners, gripper mechanism, guards, bumper, exact centers of mass, and inertia remain missing.

## Torque, speed, and current screen

The P0.7 elbow load screen is 1.158 N·m after its 2.25 screening multiplier. ROBOTIS publishes the XM430-W350 12 V endpoint as 4.1 N·m at 2.3 A and 46 rpm no-load. Dividing 4.1 by 1.158 gives 3.541, but this is explicitly a **stall-endpoint ratio only**. ROBOTIS states that stall torque is momentary and that actual performance is generally closer to the performance graph; the ratio is not continuous capacity, safety factor, thermal margin, or usable output guarantee.

At the unchanged P0.7 J2-axis radius, removing 83 g reduces the preliminary shoulder gravity term by 0.164866 N·m. The corresponding 2.25-times shoulder screen changes from 4.541 N·m to approximately 4.170 N·m. This is a same-axis mass sensitivity, not a P0.8 load calculation; new frame/adapter mass and geometry could change it.

The three-actuator catalog stall-current sum changes from 11.1 A to 9.0 A in the sensitivity. The XM430's 2.3 A catalog endpoint is below JST's 3 A EH-series headline value, so the specific 4.4 A-versus-3 A conflict would no longer describe J2. That does not release the branch: exact received conductor/contact construction, derating, ambient, bundling, cable length, voltage drop, transient current, duty, temperature rise, protection, regeneration, and external measurement remain open. A summed stall-current number is not a supply or fuse selection.

XM430 is also faster at the catalog no-load endpoint, 46 rpm versus 30 rpm. P0.8 must therefore impose and physically validate its own velocity, acceleration, stopping, overtravel, rebound, and uncertainty limits rather than inheriting P0.7 settings.

## Exact source acquisition

The project acquired the official ROBOTIS X430 idler assembly, FR12-H101K, and FR12-S102K STEP files plus the two frame drawings through the manufacturer download records linked by the current XM430 e-Manual. Hashes, byte counts, embedded identities, and parse results are in `vendor-file-register.csv`. The three STEP files parse in CadQuery 2.8.0.

Acquisition is not dimensional acceptance. The drawings have not yet received a complete independent dimension, datum, tolerance, fastener-stack, or compatibility audit. No STEP volume is used as a component mass, and the OpenMANIPULATOR-X product is only a feasibility precedent: its published 0.70 kg / 711.37 g system and 500 g payload do not prove this different two-axis guarded assembly.

## Supersession boundary

A proposed P0.8 branch would invalidate or require explicit revalidation of at least:

- C01/C04/C05/C06/C07 interfaces and every derived drawing, DXF, STEP, GLB, supplier file, hash, and fit coupon;
- J2 hard-stop contact, bumper, load, tolerance, stopping, collision, cable, receiver, and guard evidence;
- moving-mass ledger, COM, inertia, shoulder/elbow load screens, proof loads, dynamic characterization, and anchor reactions;
- DYNAMIXEL model identity, current limits, speed/acceleration, calibration, software limits, transport/HIL records, and acceptance hash; and
- electrical BOM, actuator branch current/protection/connector evidence, schematics, schedules, and commissioning records.

Until a controlled change explicitly supersedes P0.7, all P0.7 records remain authoritative and unreleased. The interactive guide is `release/hr-v0/elbow-actuator-trade-p0.1/index.html`.

## Primary sources

- ROBOTIS, [XM430-W350-T/R e-Manual](https://emanual.robotis.com/docs/en/dxl/x/xm430-w350/), live page checked 2026-08-08, no document revision shown.
- ROBOTIS, [XM540-W270-T/R e-Manual](https://emanual.robotis.com/docs/en/dxl/x/xm540-w270/), live page checked 2026-08-08, no document revision shown.
- ROBOTIS, [OpenMANIPULATOR-X specification](https://emanual.robotis.com/docs/en/platform/openmanipulator_x/specification/), live page checked 2026-08-08, no document revision shown.
- ROBOTIS, [OpenMANIPULATOR-X assembly](https://emanual.robotis.com/docs/en/platform/openmanipulator_x/assembly/), live page checked 2026-08-08, no document revision shown.
- ROBOTIS, [OpenManipulator-X Frame Set RM-X52](https://www.robotis.us/openmanipulator-x-frame-set-rm-x52/), live page checked 2026-08-08, no document revision shown.
- JST, [EH connector series](https://www.jst-mfg.com/product/index.php?lang=2&series=58), live page checked 2026-08-08, no document revision shown.
