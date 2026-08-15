# R212 validation record

**PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION**

R212 issues `V3-P1.17-OBSERVATION-P0.5-CANDIDATE` and `HR-V0-CONFIG-REC-P0.2`.

Completed checks against the synchronized staged package on 2026-08-10:

- P1.17 generator and dedicated checker: PASS;
- root plus thirteen native child sheets: parsed;
- P1.17 native ERC: 0 errors / 0 warnings;
- P1.15 core parity: 79/79 component definitions unchanged;
- added system references: exactly OBS1 and PIOBS1;
- P0.5 and Pi-carrier selected terminal maps: exact parity;
- subassembly manifest/connector hashes: exact;
- configuration P0.1 historical checker: PASS under explicit supersession handling;
- configuration P0.2 checker: PASS with 15 holds, 12 open acceptance rows and every authority false;
- standard non-`pcbnew` checker sweep: 152/152 PASS;
- native KiCad/`pcbnew` checker sweep: 18/18 PASS;
- supervisor tests: 67/67 PASS;
- watchdog reference-model and compiled-C differential tests: 11/11 PASS;
- fail-closed host-deployment tests: 16/16 PASS while the committed configuration retains `ready:false` and `motion_authority:NONE`;
- full energization-gate audit: 0 closed, 23 partial and 7 open; `--require-ready` returned exit 2;
- E2 boundary audit: 0 closed and 21 partial; `--require-ready` returned exit 2;
- desktop interactive-guide check at 1280 x 720: warning visible, minimum functional text 14 CSS px, no body overflow and five controlled-record links present;
- mobile interactive-guide check at 390 x 844: warning visible, minimum functional text 14 CSS px, no body overflow and the configuration table reflowed to block cells; and
- synchronized release-manifest checker: PASS after the R212 package was staged.

All seven directly affected gates and all 30 full-program energization gates remain unresolved. This record contains no physical evidence, supplier acceptance, executed test, qualified approval or work authority.
