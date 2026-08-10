# R185 validation record

> **PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, DRILLING, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION.**

Artifact: **HR-V0-Q4X-BOX-LAYOUT-P0.1**

Date: **2026-08-10**

## Package checks

- current primary manufacturer source records: **14**;
- controlled dimension records: **17**;
- panel-layout records: **9**;
- hash-bound temporary vendor downloads: **6**, none redistributed;
- closure holds: **12**;
- blank received/layout inspection rows: **10**;
- package-specific checker: **36/36 passed**;
- review proxy STEP bounds: **174.498 x 222.250 x 47.475 mm**, **9 solids**;
- released drill holes: **0**;
- released rail fasteners: **0**;
- authorized procurement/fabrication/connection/energization: **0 / 0 / 0 / 0**; and
- safety-function credit: **0**.

## Repository regression

- ordinary non-`pcbnew` checks in the bundled Python runtime: **115/115 passed** after manifest synchronization;
- CadQuery checks in the controlled HR-V0 CAD runtime: **14/14 passed**;
- complete non-`pcbnew` count: **129/129 passed**;
- native KiCad `pcbnew` checks in KiCad 10.0.5 Python: **13/13 passed**;
- total domain checks: **142/142 passed**; and
- deterministic release manifest after synchronization: **3,166 package files**.

The first general-runtime sweep reported only the three expected CadQuery-routed checkers plus the not-yet-synchronized manifest. All three geometry checks joined the eleven direct CadQuery checks and passed in the controlled CAD environment. The manifest was then regenerated after every R185 file was staged. These are runtime-routing observations, not design failures.

## Manufacturer-document inspection

The official Hammond `PJ1084T` and `14F0907` PDFs and the LAPP gland data sheet were rendered to PNG and visually inspected. The `PJ1084T` drawing issue date is 2014-06-04; the `14F0907` drawing issue date is 2020-01-29; LAPP DB53111000EN is version 17 valid 2023-06-20; and DB53119000EN is version 09 valid 2019-02-19. The official `14F0907` STEP was imported and measured as 174.498 x 222.250 x 3.175 mm. Vendor files were inspected from temporary storage, hash-bound in the register and not added to the repository.

## Interactive-guide validation

The local guide was rendered in the in-app browser at desktop width and with the bundled Playwright runtime at a true 390 x 844 viewport. Both diagram tabs changed the active artifact correctly; both SVGs loaded; body, lead and table text computed to 16 px, 18 px and 14 px respectively at mobile width; the document was 390 px wide with no page-level horizontal overflow; and the warning, headline and metric cards wrapped legibly. The wide technical SVG remains intentionally scrollable inside its bounded viewer.

## Evidence boundary

This validation establishes document transfer, arithmetic, file consistency, proxy-CAD bounds and browser rendering only. It does not establish received identity, panel/enclosure/rail dimensions, realized rail-slot offset, fastener selection, gland bore diameter, G1/G2 coordinates, torque, edge quality, ingress/Type rating, strain relief, thermal behavior, isolation/grounding acceptance, physical assembly, inspection execution, qualified acceptance or permission for any physical work.
