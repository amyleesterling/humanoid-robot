# R104 validation record — X430 brake support P0.1

> **PRELIMINARY — NOT APPROVED FOR QUOTATION, PROCUREMENT, MACHINING, ASSEMBLY, CONNECTION, POWERED TEST, MOTION, OR ENERGIZATION.**

R104 corrects the R102 PT-series thickness interpretation and replaces the generic brake-riser placeholder with a manufacturer accessory route. The official PT profile controls a 20 mm plate thickness; the 14.5 mm value is the lower T-slot width. The current HB/MHB datasheet identifies pillow-block assembly `4866` for `HB/MHB-450M`.

`tools/check_hr_v0_x430_brake_support.py` passes. It checks:

- four official Magtrol source SHA-256 identities;
- the explicit R102 thickness erratum;
- four support topologies, including prohibited clamp/shaft/hand routes;
- seven BOM rows with no selected hardware;
- nine dimension records and the nonfabrication Ø50 visual-clearance boundary;
- six interface records;
- eight non-authorizing calculations;
- the 15-slot drawing-derived PT profile;
- nominal zero-volume intersection records without tolerance/capacity credit;
- eight unsent RFIs;
- two partial and ten open holds;
- eight unexecuted inspection records;
- mandatory final configured H101 testing; and
- ten false release flags.

R102 is regenerated with the corrected 20 mm PT envelope and passes its dedicated checker.

The R104 STEP and GLB export successfully. The final 1600 x 1120 SVG was rendered and inspected: the corrected PT profile, adapter, pillow-block envelope, exact brake placement, 104 mm/100 mm mismatch and warning are visible without clipped or overlapping labels. The interactive guide was inspected at 1440 x 1900 from its generated release directory; the GLB loaded, orbit controls operated, the structured tables reflowed, and the minimum functional text sizes are 17 px body, 16 px table content and 14 px metadata. The 4866 solid remains a simplified drawing-derived envelope, not manufacturer body CAD. The Ø50 center clearance is not a published dimension and is prohibited for fabrication use.

No supplier was contacted. No quote, order, machining, assembly, connection, powered test, motion or energization occurred.

Repository-wide validation passed: 53 non-manifest HR-V0 checks (47 workspace-Python, three CadQuery and three KiCad-runtime), 47 firmware unit tests, 81 requirements, 40 risks, 109 procedures and 56 release/walking-document procedure references. The energization register remains unchanged at zero closed, 22 partial and eight open gates; all 30 gates through E6 remain unresolved.

The staged candidate manifest passes with 1,357 package files. A clean post-commit manifest check is required before handoff. Automated checks provide no physical evidence or energization authority.
