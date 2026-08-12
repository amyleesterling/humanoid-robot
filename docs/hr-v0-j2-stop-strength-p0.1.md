# HR-V0 J2 hard-stop strength correction P0.1

> **PRELIMINARY - NOT APPROVED FOR PROCUREMENT, QUOTATION, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION**

R269 records a substantive defect in the P0.8 planning screen: its two 6 mm striker rails were assessed with perfect 50/50 load sharing. A single-rail fault at the ROBOTIS-published 12 V momentary stall endpoint gives approximately 122.688 MPa nominal stress and only 1.956 ratio to the project's provisional 240 MPa material-test-report yield threshold, before notch or impact factors.

The P0.9 candidate widens each moving rail to 12 mm and each fixed catch to 14 mm while retaining the actuator-side hole axes. The regenerated candidate has 61.344 MPa single-rail nominal stress, 3.912 static ratio, 40,001 discrete poses, 69 continuous pairs and 0.765783 mm minimum guaranteed nominal model-space clearance. A 4.0 combined factor produces 245.376 MPa and fails the provisional threshold. That factor has not been selected; this envelope exposes the unresolved sensitivity.

ROBOTIS explicitly describes stall torque as momentary and warns that continuous and real-world output are lower. It is an endpoint screen, not a continuous rating or allowable. P0.9 remains unselected until factor/load allocation, nonlinear contact/prying and fatigue analysis, material certificate, guard/cable regeneration, drawings, DFM, FAI and physical single/two-rail stopping tests are accepted.

Interactive guide: [release package](../release/hr-v0/j2-stop-strength-p0.1/index.html).
