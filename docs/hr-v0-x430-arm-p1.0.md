# HR-V0 X430 arm clearance candidate P1.0

> **PRELIMINARY — NOT APPROVED FOR QUOTATION, PROCUREMENT, FABRICATION, ASSEMBLY, MOTION, CONNECTION, OR ENERGIZATION.**

Configuration identifier: `HR-V0-ARM-ARCH-P1.0-X430-CLEARANCE-CANDIDATE`

## Decision

P1.0 is a nonselected correction study. P0.7 remains controlled, P0.9 remains the prior integrated comparison, and XM430 is not selected. No quote, purchase, fabrication, assembly, connection, motion or energization is authorized.

R93 proved that P0.9's exact X430-to-moving-striker clearance was 2.674253 mm at the 115° software limit and only 1.083101 mm at nominal 118° stop contact. The interval certificate's 0.862928 mm floor was conservative rather than an exact contact, but the physical stop-sequencing margin was still too small to accept unknown manufacturing variation, fastener projection, play and deformation.

## Contour correction

P1.0 changes only the P09-C02 moving-striker contour:

- the unused central plate top moves from Z=+20 mm to Z=+15 mm;
- a local boss remains from Z=+15 to +17 mm over X=±8 mm around the M5 countersink envelope;
- the original external stop surface beginning at Z=+19.9167 mm is preserved;
- the external lobes extend integrally down to Z=+15 mm, maintaining a continuous 2.5-D machined load path;
- all frame axes at X=±12, Z=±6 and member axes at X=0, Z=±10 remain unchanged.

The nominal first stop contact remains **117.999977°**.

## Certificate supersession

P1.0 does not rerun unchanged evidence merely to create a new-looking package:

- 60 P0.9 continuous pair certificates are retained only where neither solid changed;
- every retained source summary is bound by SHA-256;
- four fixed-catch pair identifiers are renamed because that unchanged solid now carries the P1.0 configuration label;
- all nine pairs involving the changed moving striker are recomputed;
- those nine changed-part pairs must meet a stricter **3.000 mm** nominal continuous floor through J1 −20°…70° and J2 15°…115°.

Results:

- complete pair count: 69;
- retained identical-solid pairs: 60;
- recomputed changed-part pairs: 9;
- complete cell count: 136;
- exact B-Rep distance calls: 94;
- minimum guaranteed clearance among the changed pairs: **3.242248 mm**;
- minimum guaranteed clearance among all pairs: 1.040321 mm, against the retained 0.750 mm P0.9 requirement.

The unchanged global critical pair is now X430 versus the forearm member, not the stop adapter. Cables, connectors, fastener projections, guards, tolerance, compliance, deformation and stopping travel remain excluded.

## Stop sequencing and variation limit

Exact nominal results are:

- X430-to-striker clearance at 115°: **3.942108 mm**;
- X430-to-striker clearance at first stop contact: **2.491516 mm**;
- stop-pair gap at 115°: 1.913782 mm;
- project-required physical residual X430 clearance at first stop contact: **1.000 mm**;
- therefore the total combined adverse variation must be **≤1.491516 mm**.

The 1.491516 mm number is an unallocated upper limit, not proof that the design meets it. Five contributors remain `SELECTION REQUIRED`: machined contour/thickness, received X430/FR12 registration/runout, play/calibration, fastener projection, and elastic/impact/bumper deformation. Their worst-case sum plus measurement uncertainty must preserve at least 1.000 mm physical residual clearance at first stop contact.

## Mass screen

- P1.0 moving-striker CAD estimate: 51.184 g;
- incomplete known/CAD-estimated subtotal: **576.040 g**;
- provisional unresolved headroom: 173.960 g.

This remains incomplete. Received frames, selected fasteners, bumper, complete gripper mechanics, connectors, strain relief and moving harness are absent; assembled mass, COM and inertia remain unmeasured.

## Open evidence

Eight architecture holds remain OPEN and four PARTIAL. No hold is closed. Before P1.0 could be selected, the project still requires:

1. a released material, thickness, contour, tolerance, finish and inspection definition;
2. exact fastener stacks with head/nut/washer projection and access proof;
3. received X430/FR12 joint-stack metrology and uncertainty;
4. worst-case tolerance, play, calibration, wear and temperature closure within 1.491516 mm;
5. accepted stop-load, stress, prying, fatigue, impact and deformation evidence;
6. selected bumper/retention and measured stopping/rebound/overtravel;
7. complete cable, connector, strain-relief, guard and gripper swept envelopes;
8. complete mass/COM/inertia and actuator current/torque/thermal evidence;
9. synchronized firmware/electrical configuration; and
10. independent mechanical, electrical, controls and functional-safety disposition.

## Controlled evidence

- generator: `tools/generate_hr_v0_x430_clearance_arm.py`;
- fail-closed checker: `tools/check_hr_v0_x430_clearance_arm.py`;
- native/generated package: `cad/hr-v0/generated/arm-architecture-p1.0-x430-clearance/`;
- interactive guide: `release/hr-v0/arm-architecture-p1.0-x430-clearance/index.html`;
- independent review request: `docs/reviews/2026-08-08-x430-arm-p1.0-independent-review-request.md`.

Passing CAD checks proves only the stated nominal geometry. It is not fabrication, motion, functional-safety or energization approval.
