# HR-V0 X430 output interface P0.1

> **PRELIMINARY — OUTPUT-INTERFACE/RFI CANDIDATE ONLY — NOT APPROVED FOR QUOTATION, PROCUREMENT, MACHINING, ASSEMBLY, CONNECTION, POWERED TEST, MOTION, OR ENERGIZATION.**

Identifier: `HR-V0-X430-OUTPUT-IF-P0.1`

Parent: `HR-V0-X430-LOAD-RIG-P0.1`

Date: 2026-08-08

## Decision

Replace R102's anonymous output-adapter placeholder with a controlled, inspectable evidence chain:

1. the exact official ROBOTIS HN12-N101 STEP;
2. the official HN12-N101 reference drawing dated 2019-05-22;
3. `FX103-C01`, a one-piece Ø32 × 8 mm flange with an integral Ø15 × 18 mm stub and eight Ø2.2 mm clearance-hole review axes on PCD Ø16;
4. two proposed Ruland `MJC33-15-A` clamp hubs and one `JD21/33-92Y` spider; and
5. the exact controlled Magtrol HB-450M geometry in provisional coaxial placement.

This is a dimensioned review candidate, not fabrication CAD. It establishes nominal geometry for manufacturer questions, qualified analysis, DFM and metrology planning. It does not select material, tolerance, fastener, process, supplier or powered-test condition.

## Controlled HN12 evidence

The official STEP is locally controlled at SHA-256 `6DE6851B85132EC496F24A177729ECA5CE43416707652E79183BFA51E7F978FD`. Its native bounding box is 19.5 × 4.6000001 × 19.5 mm. The project transform rotates its native axis onto project X and places its nominal axial range at X = 21.35..25.95 mm. Nominal B-Rep intersection with the controlled X430 body is 0 mm³.

The official drawing is locally controlled at SHA-256 `0D6C309F8A45D81FFAABDB45982B7DE0B6E7F74742CAE850CFF4E938B86A81FA`. It states millimetres, `Ø19.5`, `8-M2.0 x 4 TAP THRU`, `P.C.D Ø16`, and the DC12 serration detail. It is marked **FOR REFERENCE ONLY**. It provides no project load capacity, material allowable, installation torque, preload, locking method, interface datum tolerance, runout, fatigue limit or approval for brake characterization.

Therefore `OI-HOLD-01` is only partial: exact horn geometry is controlled, while application acceptance and physical evidence remain absent.

## FX103-C01 review geometry

The candidate begins at the horn's nominal outer plane X = 25.95 mm. Its flange is Ø32 × 8 mm; its integral stub is Ø15 × 18 mm. Eight Ø2.2 mm through holes are placed on PCD Ø16. The STEP encodes nominal geometry only.

The following are explicitly absent and block machining:

- selected material, heat treatment, coating and corrosion control;
- released datums, dimensional tolerances, flatness, perpendicularity, total runout and surface finish;
- root fillet, chamfer, relief, tool-access and balance definitions;
- exact screw order code, class/material, head envelope, engagement, preload, tightening method, locking and reuse policy;
- horn-thread, flange-bearing, joint-slip and serration load analysis;
- adapter static, fatigue, fault-load and stress-concentration analysis;
- manufacturer application acceptance;
- DFM, first-article inspection and proof-test acceptance; and
- received-part and assembled-metrology records.

The review STEP is not a drawing and may not be sent for quote or machining.

## Coupling correction

R102 carried one clamp hub and one set-screw hub. R103 instead proposes **two** `MJC33-15-A` clamp hubs with one `JD21/33-92Y` spider because both candidate shafts are smooth 15 mm interfaces. The product page states a complete coupling uses any two hubs and one spider, but it does not approve this particular pairing, load spectrum or shaft support.

The input stub nominally penetrates the catalog hub envelope 14.95 mm. The brake shaft is provisionally inserted 15 mm. Ruland's catalog fit target of shaft +0/-0.013 mm and hub bore +0.03/0 mm is recorded as a manufacturer-review input, not a released project tolerance. Its full-bearing-support condition, clamp procedure, 0.75 mm hub gap, reversals, starts/stops, duty, alignment and proof remain open.

The set-screw route on the smooth Magtrol h4 shaft is rejected from the current baseline because surface damage, retention and manufacturer acceptance are unresolved. A printed or polymer torque adapter is prohibited for powered characterization. A separately bearing-supported intermediate shaft remains the fallback inquiry if the X430 output cannot satisfy the coupling's support condition.

## Bounded arithmetic

Ideal equal tangential load at eight screws on an 8 mm radius is:

- 50.000 N per screw at 3.2 N·m;
- 64.0625 N per screw at the 4.1 N·m stall endpoint; and
- 123.4375 N per screw at the 7.9 N·m accidental coupling-peak screen.

These values assume perfectly equal sharing. They provide no screw, horn, thread, flange or joint-slip capacity credit.

For an ideal solid 15 mm circular shaft, `τmax = 16T/(πd³)` gives nominal torsional shear of 4.828879 MPa at 3.2 N·m, 6.187001 MPa at 4.1 N·m and 11.921295 MPa at 7.9 N·m. These are arithmetic screens only. Material, section transitions, fillets, surface condition, fatigue, shock, misalignment and manufacturing variation are not included.

## Evidence and remaining holds

The package contains exact source hashes, four topology dispositions, six BOM rows, eight adapter features, seven bounded calculations, five interface/tolerance records, four nominal collision records, eight unsent RFIs, six unexecuted inspection records, one partial hold and eleven open holds.

Nominal B-Rep intersections for HN12/X430, FX103-C01/HN12 and FX103-C01/X430 are 0 mm³. This is a nominal geometry result only; it supplies no tolerance, deformation, wear, assembly or received-hardware evidence.

R103 does not close the brake mount, common bed, guarding, catch, brake control, thermal, instrumentation, FUTEK, Boston site, qualified review or powered-work holds inherited from R102. Direct horn/brake characterization still does not reproduce the final FR12-H101 gravity, bearing, cable and moving-mass configuration. That configured test remains mandatory.

No supplier was contacted. No quote, procurement, machining, assembly, connection, powered test, motion or energization occurred. Every release flag remains false.

Primary manufacturer records checked 2026-08-08:

- ROBOTIS HN12-N101 product page and official download center;
- Ruland MJC33/92A product record; and
- the controlled Magtrol HB-450M STEP and Rev A drawing.

Manufacturer records are evidence inputs, not design approval.
