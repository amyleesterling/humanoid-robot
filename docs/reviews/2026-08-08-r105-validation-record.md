# R105 validation record - FX104-C01 fabrication candidate P0.1

> **PRELIMINARY - NOT RELEASED FOR QUOTATION, PROCUREMENT, MACHINING, ASSEMBLY, CONNECTION, POWERED TEST, MOTION, OR ENERGIZATION.**

R105 issues `HR-V0-FX104-C01-FAB-P0.1` as a part-definition candidate for independent review. It is not a machining release.

The two complete Kaiser PDFs were hash-controlled, rendered at 150 dpi and visually inspected. The 6061 technical sheet is Rev. 05/06 and its values are labeled typical. The engineering-plate sheet prints no revision/date and lists 6061-T651 general-engineering plate from 6.35 through 254 mm.

`tools/check_hr_v0_fx104_adapter.py` passes. It checks:

- both Kaiser source SHA-256 identities and the typical-property caveat;
- ten defined candidate features;
- exact 90 x 160 x 24 mm envelope and six feature axes;
- two M6 thread/depth/position callouts and four Ø6.6 through-hole callouts;
- material certificate, process and trace requirements;
- twelve arithmetic screens without capacity credit;
- three SHA-bound parent artifacts;
- nine unexecuted FAI/proof records;
- five unsent RFIs;
- three partial and seven open holds;
- false DFM, qualified-analysis, manufacturer-acceptance, fastener, FAI and proof states; and
- ten false release flags.

The final drawing was rendered at 1800 x 1250. After moving the two feature leaders and the 100/104 mm dimension lines, splitting the header warning over two lines and raising annotation sizes, final visual inspection showed readable, nonoverlapping and unclipped dimensions, callouts, datums, fabrication notes and warnings. The responsive SVG uses 20 px minimum functional text so its displayed annotations remain at least 12 px at the guide's maximum content width.

The full interactive guide was rendered at 1440 x 5200 from its release directory. The GLB loaded, the exact plate and all six holes were visible, the embedded drawing remained readable, and all cards, table rows, evidence links, release boundary and footer were present without overlap or clipping. Guide text uses 17 px body, 16 px table/code and 14 px metadata minima. Repository-wide results are recorded after configuration validation.

No supplier was contacted. No quote, order, machining, assembly, connection, powered test, motion or energization occurred. Automated checks provide no physical evidence or authorization.

Repository-wide validation passed: 54 non-manifest HR-V0 checks (48 workspace-Python, three CadQuery and three KiCad-runtime), 47 firmware unit tests, 327 hash-controlled generated CAD artifacts, 81 requirements, 40 risks, 109 procedures and 56 release/walking-document procedure references. The energization register remains unchanged at zero closed, 22 partial and eight open gates; all 30 gates through E6 remain unresolved.

The staged candidate manifest passes with 1,380 package files. A clean post-commit manifest check is required before handoff.
