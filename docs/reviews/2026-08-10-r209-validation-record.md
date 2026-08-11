# R209 validation record

**PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION**

R209 issues `HR-V0-RUNTIME-OBS-CARRIER-P0.3` as a source-level correction candidate. It supersedes the P0.2 direct ISO1212-to-harness output topology for downstream review but does not release hardware work.

The candidate uses four independent `SN74LVC1G125DBVR` buffers. Each ISO1212 output is separately limited by 1.50 kohm and biased low by 47.0 kohm. Each buffer output is separately limited by 36.5 kohm and biased low by 330 kohm. Every active-low enable is hard-connected to `COMPUTE_0V`; the path remains ordinary diagnostic circuitry with zero safety credit.

Source calculations reproduce:

- 2.424 mA maximum ISO-side hard-short screen at 3.6 V and -1% RSO;
- 2.518 V buffer-input HIGH floor at the proposed 3.0 V rail endpoint;
- 99.63 uA maximum GPIO-side hard-short screen at 3.6 V and -1% RGP;
- 2.426 V cable-side source-HIGH screen; and
- 6.180 mA conservative steady 3V3 screen, excluding switching current.

Native KiCad 10.0 generated root plus four child sheets, 45 mounted components plus four mounting holes, 195 routed segments and 76 vias. ERC reports 0 errors / 0 warnings. PCB DRC reports 0 violations, 0 unconnected pads and 0 footprint errors. The dedicated checker passes all encoded topology, identity, calculation, authority, manifest and presentation assertions.

Fourteen application, Raspberry Pi, PCB, assembly, harness, power-state, physical-test, software, safety-boundary and work-authority holds remain open. No hardware was procured, fabricated, connected, powered or moved in this validation.

## Repository validation

Validation was executed against the synchronized staged package on 2026-08-10:

- dedicated R209 checker: PASS;
- standard non-`pcbnew` checker sweep: 150/150 PASS under the controlled CadQuery environment;
- native `pcbnew` checker sweep: 16/16 PASS under KiCad 10.0;
- supervisor unit tests: 67/67 PASS;
- watchdog unit tests: 11/11 PASS;
- host-deployment unit tests: 16/16 PASS, with the committed configuration remaining `ready:false` and `motion_authority:NONE`;
- full energization-gate audit: 0 closed, 23 partial and 7 open; `--require-ready` returned exit 2 as required; and
- interactive guide at desktop 1280 x 900 and mobile 390 x 844: warning visible, minimum measured functional text 14 CSS px, no body-level horizontal overflow, schematic/board selector changed the embedded SVG, and the mobile drawing reflowed to 339 px; and
- staged release manifest: 3,756 package files, followed by manifest/checker revalidation.

Passing source and regression checks cannot close physical evidence, application review, qualified review or work authorization. The package remains not ready for procurement, fabrication, connection, powered testing, motion or energization.
