# HR-V0 fabrication-defined arm architecture P0.4

**PRELIMINARY - CANDIDATE GEOMETRY ONLY - NOT RELEASED FOR QUOTATION, FABRICATION, ASSEMBLY, OR ENERGIZATION**

Date: 2026-08-07

Identifier: `HR-V0-ARM-ARCH-P0.4`

Parent hold: `HR-V0-MECH-P0.3`

## R57 result

R57 converts the P0.3 adapter from a geometry concept into a controlled fabrication candidate without releasing it. The native/generated package now contains a face drawing, DXF profile, ten dimensional/inspection controls, a traceable material route, exact fastener candidates, first-article and receiving templates, and ten analytical joint screens.

The candidate geometry remains `48 x 40 x 9.525 mm` nominal with a finished thickness acceptance of `9.00 to 10.00 mm`. Four M2.5 clearance holes use a `32 x 16 mm` rectangular pattern. Two M5 holes use a `20 mm` vertical pitch and a controlled 90-degree countersink. The minimum controlled residual below the deepest countersink is `5.80 mm`.

## Exact candidate sources

All records were accessed 2026-08-07 and remain on hold:

- OnlineMetals part `1249`, 3/8-inch 6061-T651 plate, ASTM B209 / AMS 4027, with one received heat lot and material test report required: https://www.onlinemetals.com/en/buy/aluminum/0-375-aluminum-plate-6061-t651/pid/1249
- Accu `SHKL-M5-20-A2-R360`, M5 x 20 A2-70 90-degree countersunk Torx screw with pre-applied AccuLock 360: https://accu-components.com/us/torx-countersunk-screws/643760-SHKL-M5-20-A2-R360
- MISUMI `SCB2.5-20`, M2.5 x 20 fully threaded A2-70 socket screw: https://us.misumi-ec.com/vona2/detail/110300239250/?HissuCode=SCB2.5-20
- Accu `HNN-M2.5-A2`, M2.5 A2 nylon-insert locknut: https://accu-components.com/us/hexagon-nylon-locking-nuts/7943-HNN-M2-5-A2
- 80/20 `20-7047` two-hole M5 x 0.8 end-tap service for 20-2040 profile: https://8020.net/20-2040.html

Kaiser Aluminum's Rev. 05/06 6061 sheet/plate values remain reference typical values only, not design allowables. The received MTR must demonstrate at least the project's provisional `240 MPa` yield acceptance before qualified review; that project threshold does not replace an applicable material specification or reviewer-approved allowable.

## Controlled fabrication evidence

`cad/hr-v0/generated/arm-architecture-p0.4/` contains the deterministic combined STEP and GLB, source-part STEP files, a 221-pose collision sweep, interface/fastener/load schedules, and:

- `MV0-C01_adapter-candidate-drawing.svg` - human-readable controlled candidate drawing;
- `parts/MV0-C01_adapter-finished-profile.dxf` - machine-readable 2D candidate profile;
- `adapter-drawing-controls.csv` - dimensions, tolerances, datums and FAI methods;
- `adapter-proof-analysis.csv` - ten analytical demand/capacity screens; and
- `architecture-summary.json` - machine-checkable configuration and open-release boundary.

The current combined STEP SHA-256 is `5D88D1FE73148C50F0DBA67C485BA30F7A51DC56ADE0B17BB02FDA5E602784F2`. It must reproduce from the accepted commit before use.

## Analytical boundary

The project proof-load candidate is `12.5385 N m`, three times the R57 2.25-gravity shoulder screen. The lowest analytical demand/capacity ratio is `1.68` at the M2.5 thread-root shear screen. These are screening calculations, not factors of safety, certified allowables, fatigue qualification, joint-preload validation, proof-test results, or authorization to fabricate.

No credit is taken for friction, preload, prying restraint, fatigue life, impact resistance, material statistical basis, thread reuse, locking performance or physical proof. A qualified mechanical reviewer must accept or replace the load cases, allowables, failure modes and acceptance limits before any article is ordered or machined.

## Release blockers

- qualified acceptance of the drawing, tolerances, material specification, MTR threshold, load cases and analytical method;
- received-source identity, dimensions, certificates and fit for the stock, screws, nuts, actuators, frames and 80/20 service;
- supplier DFM acceptance and one separately authorized first article with completed FAI;
- developed and released installation torque, anti-galling, locking, reuse and witness-mark rules;
- physical joint proof, slip, backlash, fatigue, impact and cycle evidence;
- complete cable/connector/guard envelopes and continuous-between-sample collision proof;
- physical hard stop and measured stopping-overtravel plus uncertainty below first contact; and
- signed qualified mechanical, electrical and functional-safety dispositions at the applicable gates.

R57 closes no procurement, fabrication, assembly, energization or functional-safety gate.
