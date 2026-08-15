# R210 validation record

**PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION**

R210 issues `HR-V0-RUNTIME-OBS-CARRIER-P0.4` and supersedes P0.3 for current review. The candidate preserves the four-channel buffered topology while correcting the TI DBV0005A land geometry and replacing the 36.5 kohm GPIO limiter with exact Panasonic 39.0 kohm.

Native KiCad 10.0 parses the root plus four child sheets. ERC reports 0 errors / 0 warnings. PCB DRC reports 0 violations, 0 unconnected pads and 0 footprint errors. The dedicated checker confirms all four buffers use five 1.10 x 0.60 mm lands, 0.95 mm pitch, 1.90 mm three-pin-row span and 2.60 mm row-center spacing; exact resistor identity, connector mapping, planes, authority flags, calculations, exports and manifest also pass.

## Repository validation

Validation was executed against the synchronized staged package on 2026-08-10:

- dedicated R210 checker: PASS;
- standard non-`pcbnew` checker sweep: 150/150 PASS;
- native KiCad/`pcbnew` checker sweep: 17/17 PASS;
- supervisor tests: 67/67 PASS;
- watchdog tests: 11/11 PASS;
- host-deployment tests: 16/16 PASS while retaining `ready:false` and `motion_authority:NONE`;
- full energization-gate audit: 0 closed, 23 partial and 7 open; `--require-ready` returned exit 2;
- interactive guide at desktop 1280 x 900 and mobile 390 x 844: exact warning and R210 correction visible, minimum functional text 14 CSS px, no body overflow, selector changed to the routed-board SVG and the mobile drawing reflowed to 339 px; and
- staged release manifest: 3,801 package files, followed by final manifest/checker revalidation.

Fourteen holds remain open. No physical hardware, qualified approval or work authority was created by this validation.
