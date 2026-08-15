# R278 validation record

> **PRELIMINARY - NOT APPROVED FOR PROCUREMENT, QUOTATION, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION**

R278 generated `HR-V0-J2-STOP-PAD-POCKET-FEA-P0.1`, its synchronized interactive release and configuration reconciliation P0.42. The analysis supersedes P0.12 only for the current linear calculation because P0.12 did not transform the exact P0.13 B-Rep contact normal into each component's local coordinate frame. P0.13, Rogers 2300327, 3M 467MP and every physical work stage remain unselected.

The exact fixed-to-moving world contact normal is `[0, 0.882948412236, 0.469470021759]`. At the 117.9999 degree analysis pose, the resulting one-rail 253.607 N force is `[0, approximately 0, -253.607] N` in C06 local coordinates and `[0, -223.921897982, -119.060883808] N` on fixed C07. The resultant and reaction balance were independently checked; normalized force-balance error is below 1e-9 in every mesh run.

Three separate linear P1-tetrahedral screens were run at 4, 3 and 2 mm target mesh sizes:

- C06 exact-normal top-face loading: 8.336446 MPa and 0.005776 mm maximum displacement at the finest mesh; 28.789 ratio to the project 240 MPa threshold.
- C07 metal-perimeter backup loading with the pad absent or bottomed: 26.609789 MPa and 0.011814 mm maximum displacement; ratio 9.019.
- C07 distributed pocket-floor loading, excluding pad constitutive behavior: 26.586571 MPa and 0.011828 mm maximum displacement; ratio 9.027.

The final-two-mesh global-maximum stress changes were 7.406%, 1.649% and 1.786%, respectively. All three pass only the project's internal geometry filter requiring a ratio of at least 4 to 240 MPa. The 240 MPa threshold is not a controlled material allowable, and these ratios are not safety factors. The model omits nonlinear contact, the bolted/frame/extrusion load path, machining and assembly tolerances, dynamic impact, fatigue, bumper constitutive behavior, measured material properties and physical correlation. It therefore supplies no fabrication, powered-test, motion, energization or safety authority.

Repository validation passed **222/223** non-`pcbnew` checks before staging; the sole expected failure was the staged-manifest checker rejecting the new untracked R278 files. Native KiCad 10.0.5 regression passed **18/18** currently detected `pcbnew` checks; R278 changes no ECAD source. The final post-staging result and master-manifest count are recorded below after configuration closure.

Browser QA passed at 1440 x 900 and 390 x 844. Desktop body/table text measured 17/16 px; mobile body/table text measured 16/16 px. Neither viewport had page-level horizontal overflow. The dimensioned engineering SVG now preserves its 900 px minimum width inside its own horizontal scrolling region: its smallest text remained 23 px at mobile width instead of being scaled below the 12 px interface minimum. The warning, three result cases, 3D model control and three data tables were present in the rendered DOM. The temporary browser tab and local server were closed.

Final post-staging non-`pcbnew` result: **223/223 passed**.

Final staged master manifest: **7,420 package files**.

No physical result, materials/application approval, qualified engineering acceptance or work authorization is claimed. Passing automation does not authorize procurement, fabrication, assembly, connection, powered testing, motion or energization.
