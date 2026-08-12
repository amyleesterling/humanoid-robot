# HR-V0 J2 stop P0.13 exact-normal linear screen

> **PRELIMINARY - NOT APPROVED FOR PROCUREMENT, QUOTATION, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION**

R278 issues `HR-V0-J2-STOP-PAD-POCKET-FEA-P0.1` and supersedes the P0.12 linear result for current structural calculation. The exact CAD normal transforms to `[0, 0, -1]` in C06 local coordinates; C07 receives the equal-and-opposite fixed-frame vector `[0, -0.882948, -0.469470]`.

At the finest 2 mm global mesh, the nominal single-rail 253.607 N screens give 8.336 MPa for C06, 26.610 MPa for the pad-absent C07 metal perimeter, and 26.587 MPa for the C07 pocket floor. The minimum arithmetic ratio to the 240 MPa project MTR threshold is 9.019. These pass the internal geometry-rejection rule only.

The solver is linear elastic with ideal fixed-hole restraints and distributed loads. It does not prove local contact, bolt/frame/extrusion capacity, accepted material allowables, impact, fatigue, tolerances or physical correlation. P0.13 remains unselected.

[Interactive analysis](../release/hr-v0/j2-stop-pad-pocket-fea-p0.1/index.html)
