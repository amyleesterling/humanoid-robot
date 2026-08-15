# R276 validation record

> **PRELIMINARY - NOT APPROVED FOR PROCUREMENT, QUOTATION, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION**

R276 generated `HR-V0-J2-SOFT-CONTACT-PAD-P0.2`, its release copy, configuration reconciliation P0.40 and BOM-110. P0.2 supersedes P0.1 only for current force, work, pressure and local-velocity calculation use. Rogers 2300327 remains an unselected test-coupon candidate and the P0.12 metal rails remain the structural backup.

Three SHA-256 bindings connect P0.2 to the exact P0.12 CAD contact-normal evidence, corrected static stop screen and unaccepted inertia record. The nominal contact normal gives a 44.072041 mm J2 moment arm. The current endpoint-plus-worst-sign-gravity screen gives 253.607 N single-rail demand. A local constant-force upper-bound through the complete 0.75 mm contact-to-backup envelope is 0.190205250 J, 1,231.1 times the unaccepted 10 deg/s kinetic estimate. The 0.75 mm envelope is explicitly not represented as an available foam stroke.

At Rogers' published 58 kPa maximum 25% compression-force-deflection boundary, one complete 42 x 12 mm coupon corresponds to 29.232 N and two ideal-sharing coupons to 58.464 N. The P0.12 static demand is respectively 8.676 and 4.338 times those published-force boundaries. Equal sharing receives no fail-safe credit. ACE `MC5M-3-B` remains rejected for the current geometry; its catalog minimum speed is 74.9 times the P0.12 local-normal 10 deg/s approach speed and its 4 mm stroke exceeds the envelope.

The package contains seven separated load cases, two published-force screens, three configuration bindings, twelve unexecuted verification tests, twelve open holds and twelve unexecuted acceptance rows. BOM-110 is an exact material/product candidate hold, not a released cut-piece or converter order.

The staged repository validation passed **220/220** non-`pcbnew` checks. Native KiCad 10.0.5 regression passed **18/18** currently detected `pcbnew` checks; R276 changes no ECAD source. The final staged master-manifest count is recorded below after regeneration.

Browser QA passed at 1440 x 900 and 390 x 844. Body copy was 17.28 px desktop and 16 px mobile; the smallest functional/table text was 14 px. Neither viewport had document-level horizontal overflow, while all four wide tables scrolled within their own containers. The calculator was exercised by changing total reaction torque from 11.177 N m to 10.000 N m; the displayed result changed to 226.901 N and 0.170176 J, then the input was reset. The warning and no-structural-stop boundary remained legible on mobile. The temporary viewport override, local tab and local server were reset or closed.

Final staged master manifest: **7,253 package files**.

No physical result or qualified-review acceptance is claimed. Passing automation does not authorize procurement, fabrication, assembly, connection, powered testing, motion or energization.
