# R211 validation record

**PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION**

R211 issues `HR-V0-RUNTIME-OBS-CARRIER-P0.5` and supersedes P0.4 for current review. P0.5 replaces four permanently enabled push-pull G125 stages with exact open-drain G07 devices, adds four exact 10.0 kohm pull-ups, retains the 39.0 kohm GPIO fault limiters and 330 kohm fail-low biases, and preserves four separately routed diagnostic channels.

Native KiCad 10.0 parses the root plus four child sheets. ERC reports 0 errors / 0 warnings. PCB DRC reports 0 violations, 0 unconnected pads and 0 footprint errors. The dedicated checker confirms the exact G07 pinout, TI DBV land dimensions and spacing, exact resistor identities, connector mapping, planes, authority flags, calculations, exports and manifest.

## Repository validation

Validation executed against the synchronized staged package on 2026-08-10:

- dedicated R211 checker: PASS;
- standard non-`pcbnew` checker sweep: 150/150 PASS;
- native KiCad/`pcbnew` checker sweep: 18/18 PASS;
- native KiCad ERC: 0 errors / 0 warnings;
- native KiCad PCB DRC: 0 violations / 0 unconnected pads / 0 footprint errors;
- supervisor tests: 67/67 PASS;
- watchdog reference-model and compiled-C differential tests: 11/11 PASS;
- fail-closed host-deployment tests: 16/16 PASS while the committed configuration retains `ready:false` and `motion_authority:NONE`;
- full energization-gate audit: 0 closed, 23 partial and 7 open; `--require-ready` returned exit 2;
- E2 boundary audit: 0 closed and 21 partial; `--require-ready` returned exit 2;
- final synchronized release manifest: 3,846 package files, with manifest checker PASS;
- desktop interactive-guide check at 1280 x 900: warning visible, minimum functional text 14 CSS px, no body overflow and schematic/routed-board selector functional; and
- mobile interactive-guide check at 390 x 844: warning visible, minimum functional text 14 CSS px, no body overflow and drawing reflowed to 339 px.

Fourteen P0.5 holds and all 30 full-program energization gates remain unresolved. No physical hardware, manufacturer acceptance, qualified approval or work authority was created by this validation.
