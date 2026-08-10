# R185 independent review request

> **PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, DRILLING, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION.**

Review exact artifact **HR-V0-Q4X-BOX-LAYOUT-P0.1** at the supplied commit. Treat the repository CSVs and source CAD as authoritative; the web guide is presentation only. This is a review-only physical-layout candidate with zero safety credit.

## Required checks

1. Verify Hammond `PJ1084T` and `14F0907` identity, drawing revision/date, official STEP geometry and every transferred panel dimension.
2. Confirm that R185 correctly supersedes R184's 174.75 mm short-side statement with the part-specific 174.498 mm official geometry.
3. Recalculate the four panel-hole coordinates from the 158.750 x 209.550 mm center pattern and verify the 6.350 mm catalog hole diameter.
4. Recalculate the centered 150.000 x 35.000 mm rail envelope, 12.249 mm nominal rail-end clearance and all panel-edge clearances.
5. Verify the 60.800 mm device-group width arithmetic from two `CLIPFIX 35`, one PTCB, six terminal bodies and two end covers. Determine whether installed orientation, cover side/count or retention invalidates that planning sum.
6. Verify Phoenix `1207650` slot size, pitch, minimum cut length and published tolerances. Confirm that R185 does not invent the first slot offset or panel-fastener coordinates.
7. Verify LAPP `53111000` and `53119000` geometry against DB53111000EN version 17 and DB53119000EN version 09.
8. Confirm that the M12x1.5 connection thread is not misrepresented as a released bore diameter or tolerance.
9. Review the required received-enclosure wall/rib/boss/feet/hinge/latch survey, local wall thickness, wrench access, bend radius and separation evidence before G1/G2 coordinates are frozen.
10. Review rail-to-fiberglass fastener selection, washers, retention, torque, creep, vibration, edge finish and isolation. No exact hardware is released.
11. Inspect the proxy STEP/STL and both SVGs. Confirm that rectangular rail/device bodies are labeled review envelopes rather than supplier-faithful CAD or fabrication outputs.
12. Compare Markdown, all CSV/JSON registers, CAD source/outputs, web guide, inspection form, generator and checker for exact consistency.
13. Confirm that modifying the component enclosure does not automatically preserve a completed-assembly ingress/Type rating.
14. Confirm zero procurement, drilling, fabrication, connection, powered-test, motion, energization or safety authority is implied.

Classify every issue BLOCKER / MAJOR / MINOR and cite exact file, row, feature or coordinate. Cite current primary manufacturer documentation and record revision/date. Do not approve procurement, fabrication, drilling, connection, powered testing, motion, energization or functional safety.
