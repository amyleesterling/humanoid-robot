# R277 validation record

> **PRELIMINARY - NOT APPROVED FOR PROCUREMENT, QUOTATION, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION**

R277 generated `HR-V0-ARM-ARCH-P0.13-PAD-POCKET-STOP-CANDIDATE`, `HR-V0-J2-PAD-POCKET-P0.1`, their synchronized release copies, configuration reconciliation P0.41 and BOM-111. Rogers 2300327, 3M 467MP, the P0.13 catch and every physical work stage remain unselected.

The complete P0.13 arm/collision generator parsed and regenerated successfully. Exact-kernel comparison against P0.12 found 517.427423 mm3 removed by two rounded pockets, matching the analytical pocket volume within 0.000003 mm3. The C07 gross X/Y/Z envelope remains unchanged. The installed-screen STEP contains exactly three solids: pocketed C07 plus two nominal pads. The full arm retains the nominal 121.643289 degree continuous-contact result and the 115/118 degree provisional soft/metal-stop allocation.

The generated pockets are 12.400 x 40.400 mm with R2.000 corners, centered at X +/-44.000 mm and Z 1.000 mm. Nominal coupons are 40.000 x 12.000 mm with R1.500 corners. The 0.520 mm CAD depth is explicitly a visualization/DFM screen and not a machining dimension. The pad-only tolerance sensitivity spans -0.010 to +0.190 mm protrusion, proving that a fixed nominal depth cannot guarantee first pad contact. The controlled manufacturing rule is therefore dependent on the measured complete received laminated stack: `d_pocket = t_stack - 0.150 mm`, followed by direct installed-height inspection. The candidate 0.100..0.200 mm protrusion band remains subject to qualified acceptance.

Official manufacturer source records bind Rogers publication 17-085 revision 1224-PDF, the current Rogers 17-082 availability brochure and the 3M 467MP September 2024 technical data sheet. The 3M 0.06 mm / 2.3 mil value is recorded as typical, not as a specification tolerance. Exact converter, roll configuration, surface preparation, application approval, lot/CoC, retention proof and life remain open.

Repository validation passed **221/222** non-`pcbnew` checks before staging; the sole expected failure was the staged-manifest checker rejecting the new untracked R277 files. After staging and master-manifest regeneration, the complete sweep passed **222/222**. Native KiCad 10.0.5 regression passed **18/18** currently detected `pcbnew` checks; R277 changes no ECAD source.

Browser QA passed at 1440 x 900 and 390 x 844. Desktop body/table text measured 17/16 px; mobile body/table text measured 16/16 px. Neither viewport had page-level horizontal overflow. The three wide tables fit on desktop and used their own horizontal scrolling on mobile. The warning, dependent-depth prohibition, structural-metal-backup statement, 3D control, dimensioned SVG and calculator were exposed in the rendered DOM. Changing the measured stack from 0.668 to 0.700 mm changed the calculated pocket depth from 0.518 to 0.550 mm; the input was reset. The temporary viewport, tab and local server were reset or closed.

Final staged master manifest: **7,372 package files**.

No physical result, materials/application approval, qualified engineering acceptance or work authorization is claimed. Passing automation does not authorize procurement, fabrication, assembly, connection, powered testing, motion or energization.
