# R243 validation record

**PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION**

Date: 2026-08-11

Configuration: `HR-V0-P121-TERM-P0.1` / `HR-V0-CONFIG-REC-P0.7`

Electrical candidate: P1.21 unaccepted; P1.15 remains current

## Source and mapping validation

- Current official Phoenix Contact catalog records identify ferrule items `3200043` and `3200263`, crimper `1212034`, stripper `1212150`, and torque driver `1212224` with the controlled ranges and order quantities recorded by R243.
- The current official Phoenix Contact ferrule/tool combination overview lists both ferrules with CRIMPFOX 6 for 1.5 mm2 / AWG 16.
- Pilz manual 21396-EN-23 confirms 7 mm and 0.5 N m for 750104 screw terminals. Phoenix item `2967060` records 8 mm and 0.6 to 0.8 N m. Phoenix item `3273114` records the ferruled-conductor range and push-in boundary.
- All fourteen endpoint assignments are derived from the seven R242 two-ended conductor rows. Only `SR1:A1` and `SRA1:A1` receive the 7 mm candidate.
- Phoenix's 40 N / 60 second pull-out basis is applied only to sacrificial crimp coupons. Installed-terminal pull acceptance remains `SELECTION REQUIRED`.

## Machine validation

- R243 package checker: PASS; fourteen endpoints, twelve item `3200043` and two item `3200263` candidates, twelve open holds and twenty unexecuted inspections.
- Standard non-`pcbnew` repository checker sweep: 186/186 PASS.
- Native KiCad/`pcbnew` checker sweep under KiCad 10.0.5: 18/18 PASS; R243 does not modify native ECAD.
- Release manifest: regenerated against the synchronized R243 tree and verified after staging.
- These are repository/connectivity/geometry checks only. They do not provide received-material, tool-calibration, crimp, torque, retention, continuity, isolation, functional-safety or work-authorization evidence.

## Browser validation

- Local served guide inspected at 1280 x 720 and 390 x 844.
- Both viewports had no page-level horizontal overflow and no visible text below 16 CSS pixels.
- At mobile width, each 1000 px data table remains inside its own 343 px horizontally scrollable container; the page itself does not widen.
- Warning text remained visible, the three zoom controls were uniquely addressable, Zoom in changed the diagram from 1163 px to 1453.75 px at desktop, and Reset restored 1163 px.
- Browser console inspection returned zero errors or warnings.

## Result boundary

R243 partially addresses but does not close `R242-H02`. Twelve holds and twenty blank inspections remain. P1.15 remains current; P1.21/R243 remain unaccepted. No procurement, fabrication, assembly, wiring, connection, powered testing, motion, functional-safety credit or energization is authorized.
