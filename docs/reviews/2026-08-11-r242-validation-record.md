# R242 validation record

**PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION**

Date: 2026-08-11

Configuration: `HR-V0-P121-CONDUCTOR-FILL-P0.1` / `HR-V0-CONFIG-REC-P0.6`

Electrical candidate: P1.21 unaccepted; P1.15 remains current

## Source and arithmetic validation

- Belden's current official 3057 record identifies `3057 BL005` as an active blue 100 ft reel and publishes 16 AWG, 26x30 tinned copper, PVC, 2.3 mm nominal OD, 300 V, -40 to 105 C and 23 mm stationary minimum bend radius.
- Current official Phoenix Contact and Pilz records place approximately 1.31 mm2 flexible conductor inside the published XD24, 750104 and 2967060 terminal ranges. No end-preparation release is inferred.
- All seven endpoint/net mappings match the P1.21/R240 controlled route delta.
- Route-centerline sum independently reproduced: 6723.25 mm.
- WD5 circular-envelope area independently reproduced: 29.08 mm2, or 8.89 percent of 327 mm2 published usable cross-section.
- Largest currently enumerated WD2 segment independently reproduced: five 2.3 mm plus six 1.6 mm conductors = 32.84 mm2, or 2.66 percent of 1235 mm2 published usable cross-section.
- The field and compute bundle route extents are disjoint in the controlled planning model and are not falsely summed at one cross-section.
- DCR, cut lengths, voltage drop, ampacity, protection coordination, total fill and thermal results remain open and are not numerically invented.
- The blue-conductor versus red-XD24/blue-XD0 identification conflict remains an explicit qualified-review hold.

## Machine validation

- `tools/check_hr_v0_p121_conductor_fill_p01.py`: PASS.
- Standard non-pcbnew repository checker sweep: 185/185 PASS.
- Native pcbnew/KiCad checker sweep: 18/18 PASS; R242 does not modify native ECAD.
- Release-candidate manifest generation and check: PASS with all tracked files hash-bound.
- Post-commit clean-manifest verification is required and recorded separately at commit handoff.

## Browser validation

The interactive guide was served locally and inspected in the in-app browser.

- Desktop viewport: 1280 x 720; body, buttons and smallest visible text were 16 px; page scroll width equaled client width; two tables and eleven body rows were present.
- Zoom control changed the diagram from 1163 px to 1453.75 px; Reset returned it to 1163 px.
- Mobile viewport: 390 x 844; body and smallest visible text remained 16 px; page scroll width equaled client width. Each 980 px technical table scrolled inside its own 343 px container instead of shrinking text or overflowing the page.
- Desktop and mobile screenshots showed the preliminary warning, cards and content without observed clipping or collision. The intentionally wide diagram remains horizontally scrollable inside its viewer.

## Result boundary

R242 closes no physical, qualified or Sol blocker. Twelve holds and ten blank inspections remain. P1.15 remains current; P1.21/R242 remain unaccepted. No procurement, fabrication, assembly, wiring, connection, powered testing, motion, functional-safety credit or energization is authorized.
